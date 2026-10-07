"""Create an allowlisted deploy bundle; no runtime data, credentials or model files."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

root=Path(__file__).resolve().parents[2]
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
files=[root/'apps/api/pyproject.toml',root/'apps/api/requirements.lock.txt']
files+=sorted((root/'apps/api/src').rglob('*.py'))
files+=sorted((root/'tools/deploy').glob('*.py'))
files+=sorted(p for p in (root/'apps/web/dist').rglob('*') if p.is_file())
assert (root/'apps/web/dist/index.html').is_file()
manifest={'commit':commit,'run_id':int(os.environ['GITHUB_RUN_ID']),
          'run_attempt':int(os.environ.get('GITHUB_RUN_ATTEMPT','1')),
          'repository':'HyoSang-Ryu/Team_Medipencil','branch':'poc/remote-validation',
          'files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
out=root/'build';out.mkdir(exist_ok=True)
(out/'release.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(out/'sungah-release.tar.gz','w:gz') as archive:
    for p in files:archive.add(p,arcname=str(p.relative_to(root)),recursive=False)
    archive.add(out/'release.json',arcname='release.json')
print('Packaged',commit,len(files),'files')
