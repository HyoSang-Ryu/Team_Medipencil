from medipencil.common import now

def data(response,status=200):
    assert response.status_code==status,response.text
    return response.json()['data']

def draft(b,question=None,text='Synteettinen havainto.',kind='observation',scopes=None):
    cap=data(b.post('/staff/residents/aino/captures',{'input_mode':'text'}),201)
    cap=data(b.post('/staff/captures/'+cap['capture_id']+'/text',{'occurred_at':now(),'utterances':[{'speaker':'carer','text':text,'type':kind,'required_scopes':scopes or ['outdoors']}]},rev=cap['revision']),201)
    job=data(b.post('/staff/captures/'+cap['capture_id']+'/drafts',{'question_ids':[question] if question else []},rev=cap['revision']),202)
    ref=job['result_ref']
    return data(b.get('/staff/records/'+ref['id']+'?version=1'))

def approve_body(record):
    return {'version':record['version'],'segment_reviews':[{'segment_id':s['segment_id'],'meaning_checked':True,'speaker_checked':True,'negation_and_tense_checked':True,'numbers_checked':True,'scopes_checked':True} for s in record['segments']],'candidate_reviews':[{'candidate_id':c['candidate_id'],'accepted':True,'sufficient_answer_checked':True} for c in record['answer_candidates']]}

def approve(b,record):return data(b.post('/staff/records/'+record['record_id']+'/approve',approve_body(record),rev=record['revision']))

def prepare(b,recipient='liisa'):
    ctx=data(b.get('/staff/residents/aino/publication-context?recipient_id='+recipient))
    job=data(b.post('/staff/publications/prepare',{'subject_id':'aino','recipient_id':recipient,'lang':'fi','expected_content_epoch':ctx['content_epoch'],'expected_consent_version':ctx['consent_version']}),202)
    return data(b.get('/staff/publications/'+job['result_ref']['id']))

def publish_body(p):return {'reviewed_items':[{'item_id':i['item_id'],'meaning_checked':True,'language_checked':True,'evidence_checked':True} for i in p['items']],'accepted_answer_candidate_ids':[b['candidate_id'] for b in p['answer_bindings']],'expected_content_epoch':p['content_epoch'],'expected_consent_version':p['consent_version']}

def publish(b,p):return data(b.post('/staff/publications/'+p['publication_id']+'/publish',publish_body(p),rev=p['revision']))
