"""Server-side deploy agent. Public GitHub reads; no VPN or SSH secret in Actions.

Deployment code is installed by the operator, never overwritten by an application
bundle. The maintenance gate remains closed until success or verified rollback.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
import time
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

REPO='HyoSang-Ryu/Team_Medipencil'
BRANCH='poc/remote-validation'
API=f'https://api.github.com/repos/{REPO}'
TAG=re.compile(r'sungah-([0-9a-f]{40})-([0-9]+)-([0-9]+)$')


def fetch(url,limit=100_000_000,headers=None):
    request=Request(url,headers={'User-Agent':'medipencil-deploy',**(headers or {})})
    with urlopen(request,timeout=30) as response:data=response.read(limit+1)
    if len(data)>limit:raise ValueError('Download exceeds limit')
    return data


def api(path):return json.loads(fetch(API+path,5_000_000))


def atomic_json(path,data):
    temp=path.with_suffix('.next')
    with temp.open('w') as stream:
        json.dump(data,stream,indent=2);stream.flush();os.fsync(stream.fileno())
    temp.replace(path)


def snapshot(source,destination):
    if destination.exists():raise ValueError('Snapshot already exists')
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src:
        with sqlite3.connect(destination) as dest:
            src.backup(dest)
            if dest.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid snapshot')
    destination.chmod(0o600)


def restore_db(backup,target):
    info=target.stat();temp=target.with_name('deploy-restore.sqlite')
    temp.unlink(missing_ok=True);shutil.copyfile(backup,temp)
    os.chown(temp,info.st_uid,info.st_gid);temp.chmod(0o600)
    # Call only with service stopped and ingress gated, so no live WAL writer exists.
    for suffix in ('-wal','-shm'):Path(str(target)+suffix).unlink(missing_ok=True)
    temp.replace(target)


def extract(archive,stage):
    with tarfile.open(archive) as tar:
        members=tar.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)) or sum(m.size for m in members)>200_000_000:
            raise ValueError('Invalid archive size or duplicate names')
        for member in members:
            name=PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts or str(name)!=member.name:
                raise ValueError('Unsafe archive member')
        tar.extractall(stage,filter='data')
    manifest=json.loads((stage/'release.json').read_text())
    if set(names)!=set(manifest['files'])|{'release.json'}:raise ValueError('Unexpected archive files')
    for name,digest in manifest['files'].items():
        if hashlib.sha256((stage/name).read_bytes()).hexdigest()!=digest:raise ValueError('Hash mismatch')
    for required in ('apps/api/pyproject.toml','apps/api/requirements.lock.txt','tools/deploy/run_shared.py','apps/web/dist/index.html'):
        if required not in manifest['files']:raise ValueError('Incomplete application bundle')
    return manifest


class Deployer:
    def __init__(self,root,data,state,gate):
        self.root=root;self.data=data;self.state=state;self.gate=gate
        state.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.journal=state/'transaction.json'
        self.host=urlsplit(os.environ.get('MEDIPENCIL_ORIGIN','https://orch.sungah.kr')).hostname

    def command(self,args,**kwargs):
        subprocess.run(args,check=True,timeout=600,**kwargs)

    def stop(self):self.command(['systemctl','stop','medipencil'])
    def start(self):self.command(['systemctl','start','medipencil'])

    def gated(self):
        try:
            fetch('http://127.0.0.1/medipencil/api/v1/health',headers={'Host':self.host})
            return False
        except Exception as error:return getattr(error,'code',None)==503

    def healthy(self,commit=None):
        for _ in range(30):
            try:
                data=json.loads(fetch('http://127.0.0.1:8767/api/v1/health',headers={'Host':self.host}))['data']
                if data['status']=='ok' and (commit is None or data.get('deployment_commit')==commit):return True
            except Exception:pass
            time.sleep(1)
        return False

    def switch(self,target):
        temp=self.root/'current.next';temp.unlink(missing_ok=True)
        temp.symlink_to(target);temp.replace(self.root/'current')

    def migrate(self,release,data):
        # Application and migrations run as the app user, never as root.
        env=dict(os.environ,MEDIPENCIL_DATA_ROOT=str(data))
        self.command(['/usr/sbin/runuser','-u','medipencil','--',str(release/'.venv/bin/python'),'-c',
            'from medipencil.main import create_app; from medipencil.config import Settings; a=create_app(Settings.env()); a.state.store.engine.dispose()'],env=env,cwd=release)

    def prepare(self,release):
        account=pwd.getpwnam('medipencil')
        for path in [release,*release.rglob('*')]:os.chown(path,account.pw_uid,account.pw_gid)
        env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/var/lib/medipencil','PIP_DISABLE_PIP_VERSION_CHECK':'1'}
        prefix=['/usr/sbin/runuser','-u','medipencil','--']
        self.command(prefix+['/usr/bin/python3.12','-m','venv',str(release/'.venv')],env=env)
        python=str(release/'.venv/bin/python')
        self.command(prefix+[python,'-m','pip','install','--require-hashes','-r',str(release/'apps/api/requirements.lock.txt')],env=env)
        self.command(prefix+[python,'-m','pip','install','--no-deps','-e',str(release/'apps/api')],env=env)
        # Test migration against an actual SQLite backup while the old service stays online.
        with tempfile.TemporaryDirectory(prefix='deploy-preflight-',dir=self.data.parent) as name:
            temp=Path(name);os.chown(temp,account.pw_uid,account.pw_gid)
            snapshot(self.data/'demo.sqlite',temp/'demo.sqlite')
            shutil.copy2(self.data/'run.json',temp/'run.json')
            for p in temp.iterdir():os.chown(p,account.pw_uid,account.pw_gid)
            self.migrate(release,temp)
            with sqlite3.connect(temp/'demo.sqlite') as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Preflight DB integrity failed')
        # Keep prior immutable assets for already-open legacy browser tabs.
        for old in (self.root/'current/apps/web/dist/assets').iterdir():
            dest=release/'apps/web/dist/assets'/old.name
            if old.is_file() and not dest.exists():shutil.copy2(old,dest)

    def recover(self):
        if not self.journal.exists():return
        record=json.loads(self.journal.read_text())
        if record['phase']=='healthy':
            # Ingress may already be open. Never restore an older DB after this point.
            if not self.healthy(record['commit']):raise RuntimeError('Previously committed deployment is unhealthy; operator review required')
            self.gate.unlink(missing_ok=True);self.journal.unlink();return
        self.gate.touch(mode=0o644)
        if not self.gated():raise RuntimeError('Maintenance gate is not active; rollback stopped')
        self.stop()
        if record.get('backup'):
            restore_db(Path(record['backup'])/'demo.sqlite',self.data/'demo.sqlite')
            shutil.copy2(Path(record['backup'])/'run.json',self.data/'run.json')
        self.switch(Path(record['previous']));self.start()
        if not self.healthy():raise RuntimeError('Rollback unhealthy; maintenance retained')
        atomic_json(self.state/'failed.json',{'tag':record['tag'],'commit':record['commit']})
        self.gate.unlink(missing_ok=True);self.journal.unlink()
        print('Previous application and database restored',flush=True)

    def activate(self,release,manifest,tag):
        record={'previous':str((self.root/'current').resolve()),'commit':manifest['commit'],'tag':tag,'phase':'armed'}
        atomic_json(self.journal,record)
        try:
            self.gate.touch(mode=0o644)
            if not self.gated():raise RuntimeError('Maintenance gate is not active')
            self.stop()
            backups=self.state/'backups';backups.mkdir(exist_ok=True,mode=0o700)
            backup=backups/(tag+'-'+str(time.time_ns()));backup.mkdir(mode=0o700)
            snapshot(self.data/'demo.sqlite',backup/'demo.sqlite')
            shutil.copy2(self.data/'run.json',backup/'run.json')
            record.update(backup=str(backup),phase='backed-up');atomic_json(self.journal,record)
            self.migrate(release,self.data)
            with sqlite3.connect(self.data/'demo.sqlite') as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise RuntimeError('Migrated DB integrity failed')
            self.switch(release);self.start()
            if not self.healthy(manifest['commit']):raise RuntimeError('New deployment health/version check failed')
            record['phase']='healthy';atomic_json(self.journal,record)
        except Exception:
            self.recover();raise
        # Recovery after this commit point may unblock ingress but will never rewind user writes.
        self.gate.unlink(missing_ok=True);self.journal.unlink()
        atomic_json(self.state/'active.json',{'commit':manifest['commit'],'tag':tag,'backup':str(backup)})
        print('Deployed',manifest['commit'],flush=True)

    def poll(self):
        self.recover()
        releases=[r for r in api('/releases?per_page=30') if not r['draft'] and TAG.fullmatch(r['tag_name'])]
        if not releases:return print('No deployment release')
        release=max(releases,key=lambda r:tuple(map(int,TAG.fullmatch(r['tag_name']).groups()[1:])))
        tag=release['tag_name'];commit,run_id,attempt=TAG.fullmatch(tag).groups()
        active=self.root/'current/release.json'
        if active.is_file() and json.loads(active.read_text())['commit']==commit:return print('Already deployed',commit)
        failed=self.state/'failed.json'
        if failed.is_file() and json.loads(failed.read_text())['tag']==tag:return print('Failed release held; rerun workflow or publish a fix')
        workflow=api(f'/actions/runs/{run_id}')
        if (workflow['head_sha']!=commit or workflow['head_branch']!=BRANCH
            or workflow['event'] not in ('push','workflow_dispatch') or workflow['path']!='.github/workflows/build.yml'
            or workflow['head_repository']['full_name']!=REPO or release['target_commitish']!=commit):
            raise ValueError('Untrusted deployment source')
        jobs=api(f'/actions/runs/{run_id}/attempts/{attempt}/jobs')['jobs']
        if not all(any(j['name']==name and j['conclusion']=='success' for j in jobs) for name in ('build','publish-api')):
            return print('Waiting for successful build and publish jobs')
        comparison=api(f'/compare/{commit}...poc%2Fremote-validation')
        if comparison['status'] not in ('ahead','identical'):raise ValueError('Commit no longer belongs to deploy branch')
        if active.is_file():
            old=json.loads(active.read_text())
            if (int(run_id),int(attempt))<(old['run_id'],old['run_attempt']):return print('Stale release ignored')
        asset=next(a for a in release['assets'] if a['name']=='sungah-release.tar.gz')
        if not asset['browser_download_url'].startswith(f'https://github.com/{REPO}/releases/download/{tag}/'):
            raise ValueError('Invalid asset URL')
        if shutil.disk_usage(self.root).free<800_000_000:raise RuntimeError('Not enough free disk for a new release')
        stage=self.root/'releases'/tag
        try:
            if stage.exists():raise RuntimeError('Incomplete release directory exists; rerun workflow with new attempt')
            with tempfile.TemporaryDirectory(dir=self.root) as name:
                archive=Path(name)/'release.tar.gz';data=fetch(asset['browser_download_url'])
                if asset.get('digest')!='sha256:'+hashlib.sha256(data).hexdigest():raise ValueError('GitHub digest mismatch')
                archive.write_bytes(data);stage.mkdir(mode=0o755)
                manifest=extract(archive,stage)
            if (manifest['commit'],manifest['run_id'],manifest['run_attempt'],manifest['repository'],manifest['branch'])!=(commit,int(run_id),int(attempt),REPO,BRANCH):
                raise ValueError('Manifest identity mismatch')
            self.prepare(stage)
            self.activate(stage,manifest,tag)
        except Exception:
            atomic_json(self.state/'failed.json',{'tag':tag,'commit':commit})
            raise


if __name__=='__main__':
    os.umask(0o022)
    with open('/run/medipencil-deploy.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        Deployer(Path('/opt/medipencil'),Path(os.environ['MEDIPENCIL_DATA_ROOT']),
            Path('/var/lib/medipencil-deploy'),Path('/usr/share/nginx/html/medipencil-maintenance')).poll()
