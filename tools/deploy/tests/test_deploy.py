import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import tarfile
import pytest

spec=importlib.util.spec_from_file_location('deploy',Path(__file__).parents[1]/'pull_release.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)

@pytest.fixture
def setup(tmp_path):
    root=tmp_path/'app';root.mkdir();old=root/'old';old.mkdir();new=root/'new';new.mkdir()
    (root/'current').symlink_to(old)
    data=tmp_path/'data';data.mkdir();(data/'run.json').write_text('{"run_id":"preserved"}')
    with sqlite3.connect(data/'demo.sqlite') as db:
        db.execute('CREATE TABLE comments (body TEXT)');db.execute("INSERT INTO comments VALUES ('synthetic persisted comment')")
    class Local(d.Deployer):
        fail=False
        def stop(self):assert self.gate.exists()
        def start(self):pass
        def gated(self):return self.gate.exists()
        def healthy(self,commit=None):return not (commit and self.fail)
        def migrate(self,release,data):
            with sqlite3.connect(data/'demo.sqlite') as db:db.execute('ALTER TABLE comments ADD COLUMN reviewed INTEGER DEFAULT 0')
    agent=Local(root,data,tmp_path/'state',tmp_path/'maintenance')
    return agent,old,new


def contents(db):
    with sqlite3.connect(db) as con:
        return con.execute('SELECT * FROM comments').fetchall(),con.execute('PRAGMA table_info(comments)').fetchall()


def test_successful_migration_preserves_data(setup):
    agent,old,new=setup
    agent.activate(new,{'commit':'new'},'tag-new')
    assert (agent.root/'current').resolve()==new
    assert contents(agent.data/'demo.sqlite')[0]==[('synthetic persisted comment',0)]
    assert not agent.gate.exists() and not agent.journal.exists()
    backup=Path(json.loads((agent.state/'active.json').read_text())['backup'])
    assert contents(backup/'demo.sqlite')[0]==[('synthetic persisted comment',)]


def test_unhealthy_release_restores_previous_code_and_actual_sqlite(setup):
    agent,old,new=setup;before=contents(agent.data/'demo.sqlite');agent.fail=True
    with pytest.raises(RuntimeError,match='health'):agent.activate(new,{'commit':'bad'},'tag-bad')
    assert (agent.root/'current').resolve()==old
    assert contents(agent.data/'demo.sqlite')==before
    assert not agent.gate.exists() and not agent.journal.exists()
    assert json.loads((agent.state/'failed.json').read_text())['tag']=='tag-bad'


def test_migration_exception_rolls_back_partial_changes(setup):
    agent,old,new=setup;before=contents(agent.data/'demo.sqlite')
    def broken(release,data):
        with sqlite3.connect(data/'demo.sqlite') as db:db.execute('DELETE FROM comments')
        raise RuntimeError('migration failed')
    agent.migrate=broken
    with pytest.raises(RuntimeError,match='migration failed'):agent.activate(new,{'commit':'bad'},'tag-bad')
    assert contents(agent.data/'demo.sqlite')==before
    assert (agent.root/'current').resolve()==old and not agent.gate.exists()


def test_crash_recovery_restores_backup_before_reopening_ingress(setup):
    agent,old,new=setup
    backup=agent.state/'snapshot';backup.mkdir();d.snapshot(agent.data/'demo.sqlite',backup/'demo.sqlite')
    (backup/'run.json').write_text((agent.data/'run.json').read_text())
    agent.migrate(new,agent.data);agent.switch(new);agent.gate.touch()
    d.atomic_json(agent.journal,{'phase':'backed-up','previous':str(old),'backup':str(backup),'commit':'new','tag':'tag'})
    agent.recover()
    assert contents(agent.data/'demo.sqlite')[0]==[('synthetic persisted comment',)]
    assert (agent.root/'current').resolve()==old and not agent.gate.exists()


def test_committed_recovery_never_rewinds_new_writes(setup):
    agent,old,new=setup;agent.switch(new)
    with sqlite3.connect(agent.data/'demo.sqlite') as db:db.execute("INSERT INTO comments VALUES ('accepted after healthy')")
    d.atomic_json(agent.journal,{'phase':'healthy','previous':str(old),'commit':'new','tag':'tag'})
    agent.recover()
    assert len(contents(agent.data/'demo.sqlite')[0])==2
    assert (agent.root/'current').resolve()==new


@pytest.mark.parametrize('name,kind',[('../outside','file'),('/outside','file'),('linked','symlink')])
def test_archive_rejects_traversal_and_links(tmp_path,name,kind):
    archive=tmp_path/'bad.tar.gz';stage=tmp_path/'stage';stage.mkdir()
    with tarfile.open(archive,'w:gz') as tar:
        info=tarfile.TarInfo(name)
        if kind=='symlink':info.type=tarfile.SYMTYPE;info.linkname='/etc/passwd'
        else:info.size=1
        tar.addfile(info,io.BytesIO(b'x') if kind=='file' else None)
    with pytest.raises(ValueError,match='Unsafe'):d.extract(archive,stage)


def test_archive_requires_matching_digest(tmp_path):
    archive=tmp_path/'bad.tar.gz';stage=tmp_path/'stage';stage.mkdir()
    files={'apps/api/pyproject.toml':'wronghash'}
    payloads={'apps/api/pyproject.toml':b'hello','release.json':json.dumps({'files':files}).encode()}
    with tarfile.open(archive,'w:gz') as tar:
        for name,data in payloads.items():
            info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
    with pytest.raises(ValueError,match='Hash mismatch'):d.extract(archive,stage)

@pytest.mark.parametrize('failure',['branch','build','fork'])
def test_untrusted_or_failed_workflow_never_reaches_deployment(setup,monkeypatch,failure):
    agent,old,new=setup;sha='a'*40;tag=f'sungah-{sha}-100-1'
    workflow={'head_sha':sha,'head_branch':'other' if failure=='branch' else d.BRANCH,'event':'push',
              'path':'.github/workflows/build.yml','head_repository':{'full_name':'outsider/repo' if failure=='fork' else d.REPO}}
    def api(path):
        if path.startswith('/releases'):return [{'draft':False,'tag_name':tag,'target_commitish':sha}]
        if path.endswith('/jobs'):return {'jobs':[{'name':'build','conclusion':'failure'},{'name':'publish-api','conclusion':'success'}]}
        return workflow
    monkeypatch.setattr(d,'api',api)
    agent.prepare=lambda release:pytest.fail('Untrusted release reached prepare')
    if failure=='build':agent.poll()
    else:
        with pytest.raises(ValueError,match='Untrusted'):agent.poll()
    assert (agent.root/'current').resolve()==old
