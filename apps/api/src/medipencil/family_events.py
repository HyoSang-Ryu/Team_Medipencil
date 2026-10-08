"""Synthetic EMR concept only. No external EMR connection or outbound notifications."""
from typing import Literal
from fastapi import APIRouter, Request
from pydantic import Field
from .common import Input, Fault, envelope, now, uid
from .db import one, many, need, insert, dump, audit
from .domain import scopes, timestamp
from .security import session, access, grant, permitted, revision, execute

router = APIRouter(prefix='/api/v1')


class EventInput(Input):
    external_id: str = Field(min_length=1, max_length=80)
    source_version: int = Field(ge=1, strict=True)
    title: str = Field(min_length=1, max_length=160)
    starts_at: str
    location: str = Field(min_length=1, max_length=160)
    details: str = Field(min_length=1, max_length=2000)
    status: Literal['scheduled', 'cancelled'] = 'scheduled'
    required_scopes: list[str] = Field(min_length=1, max_length=7)


class Import(Input):
    data_origin: Literal['TEAM_SYNTHETIC']
    events: list[EventInput] = Field(min_length=1, max_length=50)


class Publish(Input):
    recipients: list[str] = Field(min_length=1, max_length=20)
    reviewed: bool


def actor_for(request, db, subject, role):
    actor = session(request, db, role)
    access(db, actor, subject, 'can_review' if role == 'staff' else None)
    return actor


def visible(db, event, delivery):
    g = grant(db, event['subject_id'], delivery['recipient_id'])
    membership = one(db, 'SELECT * FROM access_memberships WHERE subject_id=? AND actor_id=? AND active=1',
                     (event['subject_id'], delivery['recipient_id']))
    return bool(membership and event['state'] == 'published'
                and event['revision'] == delivery['event_revision']
                and g['version'] == delivery['consent_version']
                and permitted(db, event['subject_id'], delivery['recipient_id'], event['payload']['required_scopes']))


def dto(db, event, actor):
    deliveries = many(db, 'SELECT * FROM family_event_deliveries WHERE event_id=?', (event['event_id'],))
    base = {k: event[k] for k in ('event_id', 'revision', 'state', 'external_id', 'source_version')}
    base.update(event['payload'])
    base['integration_mode'] = 'SIMULATED'
    if actor['role'] == 'staff':
        base['deliveries'] = [d | {'visible': visible(db, event, d)} for d in deliveries]
    else:
        d = next((d for d in deliveries if d['recipient_id'] == actor['actor_id']), None)
        if not d or not visible(db, event, d):
            raise Fault('RESOURCE_NOT_FOUND', 404)
        base['acknowledged_at'] = d['acknowledged_at']
        base['published_at'] = d['published_at']
    return base


@router.get('/{role}/residents/{s}/family-events')
def listing(role: Literal['staff', 'family'], s: str, request: Request):
    with request.app.state.store.transaction() as db:
        actor = actor_for(request, db, s, role)
        rows = many(db, 'SELECT * FROM family_events WHERE subject_id=? ORDER BY updated_at DESC,event_id', (s,))
        items = []
        for event in rows:
            if role == 'family':
                d = one(db, 'SELECT * FROM family_event_deliveries WHERE event_id=? AND recipient_id=?', (event['event_id'], actor['actor_id']))
                if not d or not visible(db, event, d): continue
            items.append(dto(db, event, actor))
        return envelope({'items': items, 'integration_mode': 'SIMULATED', 'emr_connected': False})


@router.post('/staff/residents/{s}/family-events/import')
def import_events(s: str, body: Import, request: Request):
    with request.app.state.store.transaction() as db:
        actor = actor_for(request, db, s, 'staff')
        def operation():
            ids = []
            if len({e.external_id for e in body.events}) != len(body.events): raise Fault('VALIDATION_FAILED')
            for item in body.events:
                payload = item.model_dump(exclude={'external_id', 'source_version'})
                payload['starts_at'] = timestamp(item.starts_at, future=True)
                payload['required_scopes'] = scopes(item.required_scopes + ['care_contact'])
                old = one(db, 'SELECT * FROM family_events WHERE subject_id=? AND external_id=?', (s, item.external_id))
                if old:
                    if item.source_version < old['source_version'] or (item.source_version == old['source_version'] and old['payload'] != payload):
                        raise Fault('STALE_EVENT_SOURCE', 409)
                    eid = old['event_id']
                    if item.source_version > old['source_version']:
                        db.execute("UPDATE family_events SET source_version=?,payload_json=?,revision=revision+1,state='draft',updated_at=? WHERE event_id=?",
                                   (item.source_version, dump(payload), now(), eid))
                        audit(db, actor['actor_id'], 'family_event.update', s, eid)
                else:
                    eid = uid()
                    insert(db, 'family_events', event_id=eid, subject_id=s, external_id=item.external_id,
                           source_version=item.source_version, payload_json=payload, created_at=now(), updated_at=now())
                    audit(db, actor['actor_id'], 'family_event.import', s, eid)
                ids.append(eid)
            return {'ids': ids}
        return envelope(execute(request, db, actor, body.model_dump(), operation,
            lambda ref: {'items': [dto(db, need(db, 'SELECT * FROM family_events WHERE event_id=?', (eid,)), actor) for eid in ref['ids']]}))


@router.post('/staff/family-events/{eid}/publish')
def publish(eid: str, body: Publish, request: Request):
    with request.app.state.store.transaction() as db:
        actor = session(request, db, 'staff')
        event = need(db, 'SELECT * FROM family_events WHERE event_id=?', (eid,))
        access(db, actor, event['subject_id'], 'can_review')
        def operation():
            revision(request, event)
            if not body.reviewed: raise Fault('REVIEW_REQUIRED')
            if event['state'] != 'draft': raise Fault('INVALID_STATE', 409)
            for recipient in set(body.recipients):
                access(db, {'actor_id': recipient}, event['subject_id'])
                target = need(db, 'SELECT * FROM actors WHERE actor_id=? AND active=1', (recipient,))
                if target['role'] != 'family' or not permitted(db, event['subject_id'], recipient, event['payload']['required_scopes']):
                    raise Fault('EVENT_SHARING_NOT_ALLOWED', 422)
            db.execute('DELETE FROM family_event_deliveries WHERE event_id=?', (eid,))
            for recipient in sorted(set(body.recipients)):
                insert(db, 'family_event_deliveries', event_id=eid, recipient_id=recipient, event_revision=event['revision'],
                       consent_version=grant(db, event['subject_id'], recipient)['version'], published_by=actor['actor_id'], published_at=now())
            db.execute("UPDATE family_events SET state='published',updated_at=? WHERE event_id=?", (now(), eid))
            audit(db, actor['actor_id'], 'family_event.publish', event['subject_id'], eid)
            return {'id': eid}
        return envelope(execute(request, db, actor, body.model_dump(), operation,
            lambda ref: dto(db, need(db, 'SELECT * FROM family_events WHERE event_id=?', (ref['id'],)), actor)))


@router.post('/staff/family-events/{eid}/withdraw')
def withdraw(eid: str, request: Request):
    with request.app.state.store.transaction() as db:
        actor = session(request, db, 'staff')
        event = need(db, 'SELECT * FROM family_events WHERE event_id=?', (eid,))
        access(db, actor, event['subject_id'], 'can_review')
        def operation():
            revision(request, event)
            db.execute("UPDATE family_events SET state='draft',revision=revision+1,updated_at=? WHERE event_id=?", (now(), eid))
            audit(db, actor['actor_id'], 'family_event.withdraw', event['subject_id'], eid)
            return {'id': eid}
        return envelope(execute(request, db, actor, {}, operation,
            lambda ref: dto(db, need(db, 'SELECT * FROM family_events WHERE event_id=?', (ref['id'],)), actor)))


@router.post('/family/family-events/{eid}/acknowledge')
def acknowledge(eid: str, request: Request):
    with request.app.state.store.transaction() as db:
        actor = session(request, db, 'family')
        event = need(db, 'SELECT * FROM family_events WHERE event_id=?', (eid,))
        access(db, actor, event['subject_id'])
        dto(db, event, actor)  # Current permission and publication checked even on retries.
        def operation():
            revision(request, event)
            db.execute('UPDATE family_event_deliveries SET acknowledged_at=COALESCE(acknowledged_at,?) WHERE event_id=? AND recipient_id=?', (now(), eid, actor['actor_id']))
            audit(db, actor['actor_id'], 'family_event.acknowledge', event['subject_id'], eid)
            return {'id': eid}
        return envelope(execute(request, db, actor, {}, operation,
            lambda ref: dto(db, need(db, 'SELECT * FROM family_events WHERE event_id=?', (ref['id'],)), actor)))
