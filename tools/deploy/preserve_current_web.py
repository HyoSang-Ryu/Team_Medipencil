"""Keep Sungah's active web UI byte-for-byte during a one-time API-only release."""
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[2]
REPO='HyoSang-Ryu/Team_Medipencil'
HEALTH='https://orch.sungah.kr/medipencil/api/v1/health'

def active_commit():
    with urllib.request.urlopen(HEALTH,timeout=15) as response:
        payload=json.load(response)['data']
    commit=payload.get('deployment_commit','')
    if payload.get('status')!='ok' or not re.fullmatch(r'[0-9a-f]{40}',commit):
        raise RuntimeError('Sungah API does not report a healthy immutable commit')
    return commit

def latest_release(commit):
    output=subprocess.check_output(['gh','release','list','--repo',REPO,'--limit','100','--json','tagName'],text=True)
    tags=[entry['tagName'] for entry in json.loads(output)]
    pattern=re.compile(rf'sungah-{commit}-(\d+)-(\d+)')
    matches=[(int(m[1]),int(m[2]),tag) for tag in tags if (m:=pattern.fullmatch(tag))]
    if not matches:raise RuntimeError('No verified release matches the active Sungah commit')
    return max(matches)[2]

def stage_web(archive,commit,target):
    with tarfile.open(archive,'r:gz') as bundle:
        manifest=json.load(bundle.extractfile('release.json'))
        if manifest['commit']!=commit:raise RuntimeError('Active release commit mismatch')
        names={member.name:member for member in bundle.getmembers()}
        sources={name:digest for name,digest in manifest['files'].items() if name.startswith('apps/web/dist/')}
        if 'apps/web/dist/index.html' not in sources:raise RuntimeError('Release has no web entry point')
        for name,digest in sources.items():
            relative=PurePosixPath(name).relative_to('apps/web/dist')
            member=names.get(name)
            if not member or not member.isfile() or '..' in relative.parts or member.size>20_000_000:
                raise RuntimeError('Unsafe or missing web asset')
            data=bundle.extractfile(member).read()
            if hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('Web asset digest mismatch')
            output=target.joinpath(*relative.parts)
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_bytes(data)
    return len(sources)

def main():
    commit=active_commit();tag=latest_release(commit)
    with tempfile.TemporaryDirectory(prefix='medipencil-preserve-web-') as directory:
        temp=Path(directory)
        subprocess.run(['gh','release','download',tag,'--repo',REPO,'--pattern','sungah-release.tar.gz','--dir',str(temp)],check=True)
        staged=temp/'dist'
        count=stage_web(temp/'sungah-release.tar.gz',commit,staged)
        destination=ROOT/'apps/web/dist'
        if destination.exists():shutil.rmtree(destination)
        shutil.copytree(staged,destination)
    print('Preserved Sungah web UI from',commit,'with',count,'assets')

if __name__=='__main__':main()
