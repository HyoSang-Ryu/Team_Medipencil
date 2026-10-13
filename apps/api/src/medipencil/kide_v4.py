"""v4 candidates remain unapproved; trend inputs come only from staff-reviewed DB rows."""
import math
from datetime import date
AREAS=['1_daily_living','2_health','3_medication','4_psychosocial','5_family_contact']
NUMBERS={'sleep_hours':24,'meals_eaten':3,'meals_partial':3,'meals_skipped':3,'fluids_ml':20000,'mood_score':5,'pain_score':10,'outdoor_minutes':1440}

def text(v,nullable=False):
    if v is None and nullable:return None
    if not isinstance(v,str) or len(v)>5000:raise ValueError('text')
    return v

def rows(v,limit=100):
    if not isinstance(v,list) or len(v)>limit or any(not isinstance(x,dict) for x in v):raise ValueError('rows')
    return v

def metrics(v):
    if not isinstance(v,dict):raise ValueError('metrics')
    out={}
    for k,maximum in NUMBERS.items():
        n=v.get(k)
        if n is not None and (type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=maximum):raise ValueError('metric')
        out[k]=n
    for k in ('mood_label','sleep_quality'):out[k]=text(v.get(k),True)
    def strings(x):
        if x is None:return None
        if not isinstance(x,list) or len(x)>100:raise ValueError('list')
        return [text(s) for s in x]
    for k in ('visitors','calls','clinical_events'):out[k]=strings(v.get(k))
    meds=v.get('meds')
    if meds is not None and not isinstance(meds,dict):raise ValueError('meds')
    out['meds']={k:strings((meds or {}).get(k)) for k in ('taken','delayed','not_taken','unconfirmed')}
    return out

def normalize(raw,scopes):
    notes=rows(raw.get('nursing_note'),5)
    if [n.get('area') for n in notes]!=AREAS:raise ValueError('five areas required')
    chart=[]
    for c in rows(raw.get('charting')):
        if c.get('area') not in AREAS or c.get('claim_type') not in ('observation','plan','missing','reported','inference'):raise ValueError('claim')
        chart.append({k:text(c.get(k),k=='source_ko') for k in ('area','topic','value_fi','value_ko','claim_type','source_ko')})
    missing=[]
    for q in rows(raw.get('missing_questions',[])):
        if q.get('area') not in AREAS:raise ValueError('area')
        missing.append({k:text(q.get(k)) for k in ('area','topic','question_ko','question_fi','if_unanswered_fi')})
    notices=[];cards={}
    for i,n in enumerate(rows(raw.get('family_notices',[]),20)):
        if type(n.get('send')) is not bool:raise ValueError('send')
        notice={k:text(n.get(k),k in ('text_fi','text_ko','reason_ko')) for k in ('guardian','relation','text_fi','text_ko','reason_ko')}
        notice['send']=n['send'];notices.append(notice)
        # No guessed evidence or recipient identity. Staff must bind and verify each notice.
        cards[f'notice_{i}']={'teksti':notice['text_fi'] or '', 'lahde':'','kasitelty':n['send'],'scopes':scopes,'recipient_id':''}
    excluded=raw.get('family_filter_excluded',[])
    if not isinstance(excluded,list) or len(excluded)>100:raise ValueError('excluded')
    v4={'charting':chart,'missing_questions':missing,'nursing_note':[{k:text(n.get(k)) for k in ('area','text_fi','text_ko')} for n in notes],'metrics':metrics(raw.get('metrics')),'family_notices':notices,'family_filter_excluded':[text(x) for x in excluded]}
    return {'schema_version':4,'v4':v4,'missing_reviewed':False,'nursing_note':{n['area']:n['text_fi'] for n in notes},'laheiskortti':cards,'huomiot_hoitajalle':v4['family_filter_excluded']}

def validate(value,scopes):
    if isinstance(value.get('nursing_note'),list):return normalize(value,scopes)
    base=normalize(value.get('v4',{}),scopes)
    if set(value.get('nursing_note',{}))!=set(AREAS) or set(value.get('laheiskortti',{}))!=set(base['laheiskortti']):raise ValueError('shape')
    base['nursing_note']={k:text(value['nursing_note'][k]) for k in AREAS}
    base['missing_reviewed']=value.get('missing_reviewed') is True
    for k,c in base['laheiskortti'].items():
        edit=value['laheiskortti'][k]
        if type(edit.get('kasitelty')) is not bool:raise ValueError('included')
        c.update({x:text(edit.get(x,'')) for x in ('teksti','lahde','recipient_id')})
        c['kasitelty']=edit['kasitelty']
        if c['kasitelty'] and not base['v4']['family_notices'][int(k.split('_')[1])]['send']:raise ValueError('not a send candidate')
    return base

def context(value):
    """Only explicitly entered context; never load supplied EMR/identities for transmission."""
    if not isinstance(value,dict) or set(value)-{'resident','date','weekday','slot','recorded_by','guardians','medications'}:raise ValueError('context')
    out={}
    for k in ('date','weekday','slot','recorded_by'):
        if k in value:out[k]=text(value[k])
    if 'date' in out and date.fromisoformat(out['date']).year!=2026:raise ValueError('2026 only')
    if 'resident' in value:
        r=value['resident']
        if not isinstance(r,dict) or set(r)-{'id','name','spoken_name'}:raise ValueError('resident')
        out['resident']={k:text(v) for k,v in r.items()}
    if 'guardians' in value:
        out['guardians']=[]
        for g in rows(value['guardians'],20):
            if set(g)-{'name','spoken_name','relation','relation_ko','scope','notify'}:raise ValueError('guardian')
            if g.get('notify') not in ('päivittäin (ilta)','viikkokooste (sunnuntai)','vain tapahtumat','ei ilmoituksia'):raise ValueError('notify')
            scopes=g.get('scope')
            if not isinstance(scopes,list) or len(scopes)>20:raise ValueError('scope')
            out['guardians'].append({**{k:text(v) for k,v in g.items() if k!='scope'},'scope':[text(s) for s in scopes]})
    if 'medications' in value:
        out['medications']=[]
        for m in rows(value['medications']):
            if set(m)!={'name','purpose','sensitive'} or type(m['sensitive']) is not bool:raise ValueError('medication')
            out['medications'].append({'name':text(m['name']),'purpose':text(m['purpose']),'sensitive':m['sensitive']})
    return out
