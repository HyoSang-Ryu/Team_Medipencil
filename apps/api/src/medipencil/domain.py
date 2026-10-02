from datetime import datetime, timezone
from .common import Fault
from .db import need
SCOPES = {'meals','medication','movement','outdoors','sleep','care_contact','health_context'}

def timestamp(value, future=False):
    try: dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    except (ValueError,AttributeError): raise Fault('VALIDATION_FAILED')
    if dt.tzinfo is None or (not future and dt > datetime.now(timezone.utc)):
        raise Fault('VALIDATION_FAILED')
    return dt.astimezone(timezone.utc).isoformat()

def scopes(values):
    if not values or not set(values)<=SCOPES: raise Fault('VALIDATION_FAILED')
    return sorted(set(values))

def source_ref(db, ref, subject):
    source=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(ref.get('source_id'),ref.get('source_version')))
    if source['subject_id'] != subject: raise Fault('SUBJECT_MISMATCH',409)
    if not source['valid']: raise Fault('STALE_EVIDENCE',409)
    if source['source_type']=='transcript':
        matches=[u for u in source['payload']['utterances'] if u['utterance_id']==ref.get('utterance_id')]
        if not matches: raise Fault('EVIDENCE_REQUIRED')
        return matches[0]
    return source['payload']

def record_ref(db, ref, subject):
    record=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(ref.get('record_id'),ref.get('version')))
    if record['subject_id'] != subject: raise Fault('SUBJECT_MISMATCH',409)
    if record['status']!='approved': raise Fault('REVIEW_REQUIRED')
    matches=[s for s in record['segments'] if s['segment_id']==ref.get('segment_id')]
    if not matches: raise Fault('EVIDENCE_REQUIRED')
    segment=matches[0]
    for source in segment['evidence_refs']: source_ref(db,source,subject)
    return segment
