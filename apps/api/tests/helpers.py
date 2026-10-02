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
