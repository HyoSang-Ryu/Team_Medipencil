"""Daily snapshots for the explicitly configured synthetic review database."""
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
root=Path(os.environ['MEDIPENCIL_DATA_ROOT'])
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
destination=root.parent/'backups'/f'{root.name}-{stamp}.sqlite'
subprocess.run([sys.executable,str(Path(__file__).with_name('backup_sqlite.py')),str(root/'demo.sqlite'),str(destination)],check=True)
os.umask(0o077)
shutil.copyfile(root/'run.json',destination.with_suffix('.run.json'))
