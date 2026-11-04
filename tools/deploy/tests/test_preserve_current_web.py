import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from tools.deploy.preserve_current_web import stage_web


def make_bundle(path:Path,commit:str,payload:bytes,digest:str):
    manifest=json.dumps({'commit':commit,'files':{'apps/web/dist/index.html':digest}}).encode()
    with tarfile.open(path,'w:gz') as bundle:
        for name,data in [('release.json',manifest),('apps/web/dist/index.html',payload)]:
            info=tarfile.TarInfo(name);info.size=len(data);bundle.addfile(info,io.BytesIO(data))


def test_preserved_web_must_match_active_release_hash(tmp_path):
    commit='a'*40;payload=b'<html>previous UI</html>'
    archive=tmp_path/'release.tar.gz';make_bundle(archive,commit,payload,hashlib.sha256(payload).hexdigest())
    target=tmp_path/'dist'
    assert stage_web(archive,commit,target)==1
    assert (target/'index.html').read_bytes()==payload
    with pytest.raises(RuntimeError,match='commit mismatch'):stage_web(archive,'b'*40,tmp_path/'wrong')
    make_bundle(archive,commit,payload,'0'*64)
    with pytest.raises(RuntimeError,match='digest mismatch'):stage_web(archive,commit,tmp_path/'wrong')
