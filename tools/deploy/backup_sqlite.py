"""Consistent SQLite backup; requires explicitly provided paths outside the repo."""
import argparse
import os
import sqlite3
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('source',type=Path)
parser.add_argument('destination',type=Path)
args=parser.parse_args()
if not args.source.is_absolute() or not args.source.is_file() or not args.destination.is_absolute():
    parser.error('Existing absolute source and absolute destination are required')
os.umask(0o077)
# Never overwrite a previous recovery point.
fd=os.open(args.destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
with sqlite3.connect(args.source.as_uri()+'?mode=ro',uri=True) as source:
    with sqlite3.connect(args.destination) as target:
        source.backup(target)
        if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise SystemExit('Backup integrity check failed')
print('SQLite backup integrity: ok')
