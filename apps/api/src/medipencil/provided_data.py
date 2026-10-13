"""Optional local-only supplied scenarios. Never seed, publish or send to a model."""
from contextlib import closing
import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Request
from .common import Fault, envelope
from .security import session

FILENAME = 'provided-scenarios.sqlite'
KINDS = ('daily_log', 'clinical_events', 'social_contacts')

def import_bundle(archive: Path, personas: Path, root: Path):
    from .config import REPO
    root = root.resolve()
    if root == REPO or REPO in root.parents:
        raise ValueError('Import destination must be outside repository')
    # Read documentation as provenance, never as executable import instructions.
    provenance = hashlib.sha256(personas.read_bytes()).hexdigest()
    fingerprint = hashlib.sha256(archive.read_bytes()).hexdigest()
    entries = []
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or any(Path(n).is_absolute() or '..' in Path(n).parts for n in names):
            raise ValueError('Unsafe archive members')
        def read(name):
            info = bundle.getinfo('out/' + name)
            if info.file_size > 10_000_000:
                raise ValueError('Input too large')
            return bundle.read(info).decode('utf-8-sig')
        subjects = json.loads(read('summary.json'))
        families = json.loads(read('family.json'))
        if set(subjects) != {'A', 'B'}:
            raise ValueError('Expected scenarios A and B')
        ids = [s['asiakas_id'] for s in subjects.values()]
        if len(set(ids)) != 2 or set(families) != set(ids):
            raise ValueError('Subject relationship mismatch')
        for key, subject in subjects.items():
            for kind in KINDS:
                for line in read(f'{kind}_{key}.jsonl').splitlines():
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    observed = date.fromisoformat(row['date'])
                    if row['asiakas_id'] != subject['asiakas_id']:
                        raise ValueError('Cross-subject record')
                    if observed.year == 2026:
                        entries.append((key, kind, observed.isoformat(), json.dumps(row, ensure_ascii=False)))
    root.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='provided-', suffix='.sqlite', dir=root)
    os.close(fd)
    try:
        with sqlite3.connect(temporary) as db:
            db.executescript('CREATE TABLE metadata(payload TEXT); CREATE TABLE subjects(id TEXT PRIMARY KEY,payload TEXT,family TEXT); CREATE TABLE entries(subject TEXT,kind TEXT,day TEXT,payload TEXT); CREATE INDEX period ON entries(subject,day);')
            db.execute('INSERT INTO metadata VALUES (?)', (json.dumps({'origin':'SUPPLIED_VEIL_DERIVED','synthetic':True,'ai_processed':False,'year':2026,'archive_sha256':fingerprint,'personas_sha256':provenance}),))
            for key, subject in subjects.items():
                # Summary totals describe 2024–26 and must not be shown as 2026 totals.
                profile = {k:subject[k] for k in ('asiakas_id','label','unit','move_in')}
                db.execute('INSERT INTO subjects VALUES (?,?,?)', (key,json.dumps(profile,ensure_ascii=False),json.dumps(families[subject['asiakas_id']],ensure_ascii=False)))
            db.executemany('INSERT INTO entries VALUES (?,?,?,?)',entries)
        os.replace(temporary, root/FILENAME)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {'subjects':2,'records_2026':len(entries),'counts':{k:sum(e[1]==k for e in entries) for k in KINDS},'archive_sha256':fingerprint}

def available(settings):
    return not settings.shared_review and not settings.pages_origin and (settings.root/FILENAME).is_file()

def connect(request):
    with request.app.state.store.transaction() as db:
        session(request, db, 'staff')
    if not available(request.app.state.settings):
        raise Fault('RESOURCE_NOT_FOUND',404)
    return sqlite3.connect((request.app.state.settings.root/FILENAME).as_uri()+'?mode=ro', uri=True)

router = APIRouter(prefix='/api/v1/staff/provided-data')

@router.get('')
def catalogue(request: Request):
    with closing(connect(request)) as db:
        subjects = []
        for key,payload,_ in db.execute('SELECT * FROM subjects ORDER BY id'):
            totals = {k:n for k,n in db.execute('SELECT kind,count(*) FROM entries WHERE subject=? GROUP BY kind',(key,))}
            subjects.append({'id':key,**json.loads(payload),'counts':totals})
        metadata = json.loads(db.execute('SELECT payload FROM metadata').fetchone()[0])
    return envelope({'subjects':subjects,'metadata':metadata,'today':datetime.now(ZoneInfo('Europe/Helsinki')).date().isoformat()})

@router.get('/{subject}')
def period(request: Request, subject: str, start: date, end: date):
    with closing(connect(request)) as db:
        if start.year != 2026 or end.year != 2026 or start > end or (end-start).days > 365:
            raise Fault('INVALID_DATE_RANGE')
        found = db.execute('SELECT family FROM subjects WHERE id=?',(subject,)).fetchone()
        if not found:
            raise Fault('RESOURCE_NOT_FOUND',404)
        today = datetime.now(ZoneInfo('Europe/Helsinki')).date().isoformat()
        records = {k:[] for k in KINDS}
        for kind,day,payload in db.execute('SELECT kind,day,payload FROM entries WHERE subject=? AND day>=? AND day<=? ORDER BY day',(subject,start.isoformat(),end.isoformat())):
            records[kind].append({**json.loads(payload),'future_scenario':day>today})
        # Dataset scope text is descriptive, never a live grant or family account.
        families = [{k:r.get(k) for k in ('family_id','name','relation_fi','relation_ko','primary_contact','consent_scope')} for r in json.loads(found[0])]
    return envelope({**records,'family':families,'start':start.isoformat(),'end':end.isoformat(),'today':today,'published':False})
