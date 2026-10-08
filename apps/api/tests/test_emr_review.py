from conftest import Browser

def test_synthetic_emr_import_is_durable_deduplicated_and_staff_only(app):
    staff=Browser(app);family=Browser(app,'liisa')
    assert family.get('/staff/residents/aino/emr-review').status_code==403
    assert family.post('/staff/residents/aino/emr-review/import').status_code==403
    first=staff.get('/staff/residents/aino/emr-review').json()['data']
    assert first['bundle']['integration_mode']=='SIMULATED'
    assert first['bundle']['emr_connected'] is False
    cap=staff.post('/staff/residents/aino/emr-review/import').json()['data']
    again=staff.post('/staff/residents/aino/emr-review/import').json()['data']
    assert cap['capture_id']==again['capture_id']
    result=staff.post(f"/staff/captures/{cap['capture_id']}/drafts",{'processing_mode':'manual'},cap['revision'])
    assert result.status_code==202,result.text
    job=result.json()['data'];assert job['execution']['ai_executed'] is False
    inbox=Browser(app).get('/staff/residents/aino/emr-review').json()['data']
    entry=next(x for x in inbox['items'] if x['record']['record_id']==job['result_ref']['id'])
    assert entry['record']['status']=='draft'
    assert len(entry['record']['segments'])==3
    assert 'Toteutumista ei ole vielä vahvistettu' in entry['source_text']
    assert entry['execution']['ai_executed'] is False
    board=family.get('/family/residents/aino/board?lang=fi').json()['data']
    assert not any(t['items'] for t in board['tiles'])
    with app.state.store.transaction() as db:
        assert db.execute('SELECT COUNT(*) FROM captures WHERE capture_id=?',(cap['capture_id'],)).fetchone()[0]==1
    assert staff.get('/staff/residents/unknown/emr-review').status_code in (403,404)
