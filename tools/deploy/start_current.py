"""Stable systemd launcher, also supporting rollback to manually deployed releases."""
import os
from pathlib import Path
root=Path('/opt/medipencil/current').resolve(strict=True)
python=root/'.venv/bin/python'
if not python.is_file():python=Path('/opt/medipencil/venv/bin/python')
os.chdir(root)
os.execv(str(python),[str(python),str(root/'tools/deploy/run_shared.py')])
