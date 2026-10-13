"""Independent tiny fixtures only: never copy supplied source rows to the repo."""
import json
import zipfile
from pathlib import Path
import pytest
from conftest import Browser
from medipencil.provided_data import import_bundle, FILENAME, available

def fixture_bundle(tmp_path, cross=False, unsafe=False):
    archive=tmp_path/'fixture.zip'; personas=tmp_path/'PERSONAS.md'
    personas.write_text('Independent test fixture; no supplied records.')
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('out/summary.json',json.dumps({k:dict(asiakas_id=k,label='Test '+k,unit='Test unit',move_in='2025-01-01') for k in ('A','B')}))
        z.writestr('out/family.json',json.dumps({k:[dict(family_id=k+'-family',name='Test relative',consent_scope='arki',notes='not returned')] for k in ('A','B')}))
        for k in ('A','B'):
            z.writestr('out/daily_log_'+k+'.jsonl','\n'.join(json.dumps(dict(asiakas_id='wrong' if cross else k,date=d,sleep_hours=7,fluids_dl=15)) for d in ('2025-12-31','2026-01-01','2026-12-31')))
            for kind in ('clinical_events','social_contacts'):
                z.writestr(f'out/{kind}_{k}.jsonl','')
        if unsafe:z.writestr('../escape','no')
    return archive,personas

def test_import_filter_replace_and_scope(app,tmp_path):
    archive,personas=fixture_bundle(tmp_path)
    for _ in range(2):
        result=import_bundle(archive,personas,app.state.settings.root)
        assert result['records_2026']==4
    staff=Browser(app)
    data=staff.get('/staff/provided-data').json()['data']
    assert data['metadata']['origin']=='SUPPLIED_VEIL_DERIVED'
    assert data['metadata']['ai_processed'] is False
    assert data['subjects'][0]['counts']['daily_log']==2
    data=staff.get('/staff/provided-data/A?start=2026-01-01&end=2026-12-31').json()['data']
    assert all(r['asiakas_id']=='A' for r in data['daily_log'])
    assert data['published'] is False
    assert 'notes' not in data['family'][0]
    assert data['daily_log'][-1]['future_scenario']==('2026-12-31'>data['today'])
    assert Browser(app,'liisa').get('/staff/provided-data').status_code==403
    assert Browser(app,'liisa').get('/staff/provided-data/A?start=2026-01-01&end=2026-01-02').status_code==403
    assert staff.get('/staff/provided-data/C?start=2026-01-01&end=2026-01-02').status_code==404
    for query in ('start=2025-01-01&end=2026-01-01','start=2026-02-01&end=2026-01-01'):
        assert staff.get('/staff/provided-data/A?'+query).status_code==422
    app.state.settings.shared_review=True
    assert not available(app.state.settings)
    app.state.settings.shared_review=False
    app.state.settings.pages_origin='https://example.invalid'
    assert staff.get('/staff/provided-data').status_code==404

@pytest.mark.parametrize('cross,unsafe',[(True,False),(False,True)])
def test_bad_import_keeps_previous(app,tmp_path,cross,unsafe):
    archive,personas=fixture_bundle(tmp_path)
    import_bundle(archive,personas,app.state.settings.root)
    before=(app.state.settings.root/FILENAME).read_bytes()
    archive,personas=fixture_bundle(tmp_path,cross,unsafe)
    with pytest.raises(ValueError):import_bundle(archive,personas,app.state.settings.root)
    assert (app.state.settings.root/FILENAME).read_bytes()==before

def test_absent(app):
    assert not available(app.state.settings)
    assert Browser(app).get('/staff/provided-data').status_code==404


def test_explicit_shared_dataset_pin_and_pages_isolation(tmp_path):
    import hashlib
    from fastapi.testclient import TestClient
    from medipencil.config import Settings
    from medipencil.main import create_app
    archive,personas=fixture_bundle(tmp_path)
    root=tmp_path/'shared';import_bundle(archive,personas,root)
    pin=hashlib.sha256((root/FILENAME).read_bytes()).hexdigest()
    settings=Settings(root,secret='s'*32,origin='https://care.example',poc_mode=True,shared_review=True,public_review=True,pages_origin='https://pages.example',shared_supplied_sha256=pin)
    app=create_app(settings)
    with TestClient(app,base_url=settings.origin) as client:
        health=client.get('/api/v1/health').json()['data']
        profiles=health['provided_accounts'];assert len(profiles)==2
        a,b=profiles
        client.headers['origin']=settings.pages_origin
        login=client.post('/api/v1/demo/session',json={'demo_actor_id':a['actor_id']})
        assert login.status_code==201
        client.headers['authorization']='Bearer '+login.json()['data']['access_token']
        assert client.get('/api/v1/provided/A/board?start=2026-01-01&end=2026-12-31').status_code==200
        assert client.get('/api/v1/provided/B/board?start=2026-01-01&end=2026-12-31').status_code==403
        settings.shared_supplied_sha256='0'*64
        assert not available(settings)
        assert client.get('/api/v1/provided/A/board?start=2026-01-01&end=2026-12-31').status_code==404
        assert client.post('/api/v1/demo/session',json={'demo_actor_id':b['actor_id']}).status_code==403
        settings.shared_supplied_sha256=pin
        with (root/FILENAME).open('ab') as f:f.write(b'changed')
        assert not available(settings)
