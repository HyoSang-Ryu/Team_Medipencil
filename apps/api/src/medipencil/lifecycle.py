"""Explicit local synthetic run lifecycle. No recursive deletion."""
import fcntl,json
from contextlib import contextmanager
from pathlib import Path
from .common import Fault,uid

def ensure_run(root):
    root=Path(root);manifest=root/'run.json'
    if manifest.is_symlink():raise Fault('INVALID_DATA_ROOT')
    if not manifest.exists():
        if (root/'demo.sqlite').exists():raise Fault('UNRECOGNIZED_RUN')
        with manifest.open('x') as out:json.dump({'run_id':uid(),'data_origin':'TEAM_SYNTHETIC','format':1},out)
    data=json.loads(manifest.read_text())
    if data.get('data_origin')!='TEAM_SYNTHETIC' or data.get('format')!=1:raise Fault('UNRECOGNIZED_RUN')
    return data

@contextmanager
def run_lock(root):
    path=Path(root)/'.run.lock'
    if path.is_symlink():raise Fault('INVALID_DATA_ROOT')
    with path.open('a') as handle:
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise Fault('RUN_IN_USE',409)
        try:yield
        finally:fcntl.flock(handle,fcntl.LOCK_UN)

def cleanup_run(root,confirm=None,dry_run=True):
    root=Path(root)
    if root.is_symlink() or any(p.is_symlink() for p in root.parents):raise Fault('INVALID_DATA_ROOT')
    manifest=root/'run.json'
    if not manifest.exists() or manifest.is_symlink():raise Fault('UNRECOGNIZED_RUN')
    data=json.loads(manifest.read_text())
    if data.get('data_origin')!='TEAM_SYNTHETIC':raise Fault('UNRECOGNIZED_RUN')
    with run_lock(root):
        allowed={'run.json','.run.lock','demo.sqlite','demo.sqlite-wal','demo.sqlite-shm','audio'}
        if any(p.name not in allowed or p.is_symlink() for p in root.iterdir()):raise Fault('UNRECOGNIZED_ARTIFACT')
        paths=[p for p in root.iterdir() if p.name not in ('.run.lock','audio')]
        if (root/'audio').exists():
            from .audio import artifact
            for p in (root/'audio').iterdir():
                if p.suffix!='.wav' or p!=artifact(root,p.stem) or not p.is_file():raise Fault('UNRECOGNIZED_ARTIFACT')
                paths.append(p)
        if any(not p.is_file() for p in paths):raise Fault('UNRECOGNIZED_ARTIFACT')
        if not dry_run:
            if confirm!=data['run_id']:raise Fault('RUN_CONFIRMATION_REQUIRED')
            for path in paths:path.unlink()
        return {'run_id':data['run_id'],'data_origin':'TEAM_SYNTHETIC','dry_run':dry_run,'file_count':len(paths),'deleted_count':0 if dry_run else len(paths),'physical_erasure_guaranteed':False}
