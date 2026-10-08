from .db import insert, one
from .common import now
from .domain import SCOPES

def seed(store, dry_run=False):
    with store.transaction() as db:
        if one(db,'SELECT * FROM units'): raise ValueError('Seed requires an empty TEAM_SYNTHETIC run')
        if dry_run: return {'origin':'TEAM_SYNTHETIC','residents':2,'actors':4,'write':False}
        insert(db,'units',unit_id='demo-unit',name='Synteettinen koti')
        for actor,role,name in [('liisa','family','Liisa'),('mikko','family','Mikko'),('staff','staff','Koskinen'),('admin','demo_admin','Demo admin')]:
            insert(db,'actors',actor_id=actor,role=role,display_name=name,active=int(actor!='mikko'))
        for s,name in [('aino','Aino (synteettinen)'),('other','Toinen (synteettinen)')]:
            insert(db,'residents',subject_id=s,unit_id='demo-unit',display_name=name,data_origin='TEAM_SYNTHETIC')
        for actor in ['liisa','mikko','staff']:
            insert(db,'access_memberships',subject_id='aino',actor_id=actor,can_ask=int(actor!='staff'),can_review=int(actor=='staff'),can_manage_consent=int(actor=='staff'),active=int(actor!='mikko'))
        for recipient,scope in [('liisa',sorted(SCOPES)),('mikko',['meals','movement','care_contact'])]:
            insert(db,'consent_versions',consent_id='consent-'+recipient,version=1,subject_id='aino',recipient_id=recipient,status='confirmed',scopes_json=scope,confirmed_by='staff',confirmed_at=now(),evidence_ref_json={'kind':'TEAM_SYNTHETIC_INITIAL_GRANT'})
        return {'origin':'TEAM_SYNTHETIC','write':True}
