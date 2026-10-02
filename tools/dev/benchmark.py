"""Synthetic real TCP baseline; never clinical efficacy or provider performance."""
import json,os,secrets,socket,subprocess,sys,tempfile,time,urllib.request,platform
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from datetime import datetime,timezone
repo=Path(__file__).resolve().parents[2]
class Client:
    def __init__(self,origin,actor):
        self.origin=origin;self.cookie='';self.csrf=''
        self.csrf=self.call('POST','/demo/session',{'demo_actor_id':actor})['csrf_token']
    def call(self,method,path,body=None,revision=None):
        headers={'Origin':self.origin,'Content-Type':'application/json','Cookie':self.cookie,'X-CSRF-Token':self.csrf,'Idempotency-Key':str(uuid4())}
        if revision is not None:headers['If-Match']=f'"{revision}"'
        request=urllib.request.Request(self.origin+'/api/v1'+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
        with urllib.request.urlopen(request,timeout=10) as response:
            if response.headers.get('Set-Cookie'):self.cookie=response.headers['Set-Cookie'].split(';')[0]
            return json.load(response)['data']
with tempfile.TemporaryDirectory(prefix='medipencil-benchmark-') as directory:
    root=Path(directory).resolve()
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    origin=f'http://127.0.0.1:{port}'
    env=os.environ|{'MEDIPENCIL_DATA_ROOT':str(root),'MEDIPENCIL_SESSION_SECRET':secrets.token_urlsafe(48),'MEDIPENCIL_ORIGIN':origin}
    for args in [['migrate'],['seed-demo','--confirm','TEAM_SYNTHETIC']]:subprocess.run([sys.executable,'-m','medipencil.cli',*args],env=env,cwd=repo,check=True,stdout=subprocess.DEVNULL)
    server=subprocess.Popen([sys.executable,'-m','uvicorn','medipencil.main:app','--host','127.0.0.1','--port',str(port),'--workers','1','--no-access-log'],env=env,cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:urllib.request.urlopen(origin+'/api/v1/health',timeout=.2).close();break
            except OSError:time.sleep(.05)
        f=Client(origin,'liisa');s=Client(origin,'staff');q=f.call('POST','/family/residents/aino/questions',{'text':'Synteettinen kysymys'})
        cap=s.call('POST','/staff/residents/aino/captures',{'input_mode':'text'})
        cap=s.call('POST','/staff/captures/'+cap['capture_id']+'/text',{'occurred_at':datetime.now(timezone.utc).isoformat(),'utterances':[{'speaker':'carer','text':'Synteettinen ulkoiluhavainto.','type':'observation','required_scopes':['outdoors']}]},cap['revision'])
        job=s.call('POST','/staff/captures/'+cap['capture_id']+'/drafts',{'question_ids':[q['question_id']]},cap['revision']);r=s.call('GET','/staff/records/'+job['result_ref']['id']+'?version=1')
        s.call('POST','/staff/records/'+r['record_id']+'/approve',{'version':1,'segment_reviews':[{'segment_id':r['segments'][0]['segment_id'],'meaning_checked':True,'speaker_checked':True,'negation_and_tense_checked':True,'numbers_checked':True,'scopes_checked':True}],'candidate_reviews':[{'candidate_id':r['answer_candidates'][0]['candidate_id'],'accepted':True,'sufficient_answer_checked':True}]},r['revision'])
        ctx=s.call('GET','/staff/residents/aino/publication-context?recipient_id=liisa')
        job=s.call('POST','/staff/publications/prepare',{'subject_id':'aino','recipient_id':'liisa','lang':'fi','expected_content_epoch':ctx['content_epoch'],'expected_consent_version':ctx['consent_version']});p=s.call('GET','/staff/publications/'+job['result_ref']['id'])
        s.call('POST','/staff/publications/'+p['publication_id']+'/publish',{'reviewed_items':[{'item_id':p['items'][0]['item_id'],'meaning_checked':True,'language_checked':True,'evidence_checked':True}],'accepted_answer_candidate_ids':[p['answer_bindings'][0]['candidate_id']],'expected_content_epoch':p['content_epoch'],'expected_consent_version':p['consent_version']},p['revision'])
        results={}
        for actor,path in [('liisa','/family/residents/aino/board'),('staff','/staff/question-queue')]:
            clients=[Client(origin,actor) for _ in range(5)]
            def batch(client):
                timings=[]
                for _ in range(10):
                    start=time.perf_counter();client.call('GET',path);timings.append((time.perf_counter()-start)*1000)
                return timings
            with ThreadPoolExecutor(5) as pool:times=sorted(v for batch_times in pool.map(batch,clients) for v in batch_times)
            results[path]={'requests':len(times),'concurrent_sessions':5,'p95_ms':round(times[47],2),'max_ms':round(max(times),2),'target_under_1000ms':times[47]<1000}
        report={'scope':'TEAM_SYNTHETIC_LOCAL_TCP_BASELINE','machine':platform.machine(),'platform':platform.system(),'api_processes':1,'residents':2,'questions':1,'approved_records':1,'publications':1,'ai_calls':0,'measurements':results}
        print(json.dumps(report,indent=2))
    finally:server.terminate();server.wait(timeout=10)
