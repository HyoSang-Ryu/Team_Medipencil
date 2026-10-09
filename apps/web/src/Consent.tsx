import {useUiLanguage} from './UiLanguage';
import {useEffect,useState} from 'react';
import {api} from './api';
type Grant={recipient_id:string;display_name:string;version:number;scopes:string[]};
type History={recipient_id:string;version:number;scopes:string[];confirmed_at:string;confirmed_by:string;evidence_ref:Record<string,unknown>};
type Candidate={candidate_id:string;recipient_id:string;proposed_scopes:string[];disposition:string;utterance_ref:Record<string,unknown>};
type Data={grants:Grant[];history:History[];candidates:Candidate[]};
const names:Record<string,string>={meals:'식사',sleep:'수면',movement:'이동',outdoors:'야외 활동',health_context:'건강 정보',medication:'복약',care_contact:'돌봄 연락'};
export function Consent(){
 const {tr}=useUiLanguage();
 const [data,setData]=useState<Data>({grants:[],history:[],candidates:[]}),[recipient,setRecipient]=useState('liisa'),[scopes,setScopes]=useState<string[]>([]);
 const [method,setMethod]=useState('written'),[date,setDate]=useState(''),[note,setNote]=useState(''),[checked,setChecked]=useState(false),[busy,setBusy]=useState(true),[error,setError]=useState(''),[saved,setSaved]=useState(false);
 const grant=data.grants.find(g=>g.recipient_id===recipient),added=scopes.filter(s=>!grant?.scopes.includes(s)),removed=(grant?.scopes??[]).filter(s=>!scopes.includes(s));
 const changed=added.length+removed.length>0;
 function reset(){setChecked(false);setDate('');setNote('');setMethod('written');setSaved(false);setError('');}
 async function load(){setBusy(true);setError('');try{const next=await api<Data>('/staff/residents/aino/consents');setData(next);const g=next.grants.find(g=>g.recipient_id===recipient)??next.grants[0];setRecipient(g?.recipient_id??'');setScopes(g?.scopes??[]);setChecked(false);return true;}catch(e){setData({grants:[],history:[],candidates:[]});setError(String(e));return false;}finally{setBusy(false);}}
 useEffect(()=>{void load();},[]);
 async function save(){if(!grant||!checked||!changed||busy)return;setBusy(true);setError('');try{await api(`/staff/residents/aino/consents/${encodeURIComponent(recipient)}/settings`,{scopes,expected_consent_version:grant.version,confirmation_method:method,confirmation_date:date,confirmation_note:note,consent_checked:checked});if(await load()){reset();setSaved(true);}}catch(e){setError(String(e));setChecked(false);}finally{setBusy(false);}}
 const list=(items:string[])=>items.map(s=>tr(names[s]??s)).join(', ')||tr('없음');
 return <section className="consent-settings"><h2>{tr('보호자 공유 설정')}</h2><p>{tr('보호자에게 공유할 정보를 선택하세요.')}</p>{error&&<p role="alert">{error} · {tr('최신 설정을 다시 불러온 뒤 확인하세요.')}</p>}{saved&&<p role="status">{tr('공유 설정을 저장했습니다.')}</p>}
 <fieldset disabled={busy}><label>{tr('보호자 선택')}<select value={recipient} onChange={e=>{setRecipient(e.target.value);setScopes(data.grants.find(g=>g.recipient_id===e.target.value)?.scopes??[]);reset();}}>{data.grants.map(g=><option key={g.recipient_id} value={g.recipient_id}>{g.display_name}</option>)}</select></label>
 <button type="button" onClick={()=>{reset();void load();}}>{tr('최신 설정 불러오기')}</button>
 {grant&&<><h3>Aino → {grant.display_name}</h3><div className="consent-options">{Object.entries(names).map(([key,label])=><label key={key}><input type="checkbox" checked={scopes.includes(key)} onChange={e=>{setScopes(e.target.checked?[...scopes,key]:scopes.filter(s=>s!==key));setChecked(false);setSaved(false);}}/>{tr(label)}</label>)}</div>
 <p>{tr('추가')}: {list(added)} · {tr('해제')}: {list(removed)}</p>
 {changed&&<div className="consent-confirmation"><p>{tr('공유 설정을 변경하면 기존 발행물은 숨겨지며 다시 발행해야 합니다.')}</p><label>{tr('동의 확인 방법')}<select value={method} onChange={e=>{setMethod(e.target.value);setChecked(false);}}><option value="written">{tr('서면 확인')}</option><option value="in_person">{tr('대면 확인')}</option><option value="phone">{tr('전화 확인')}</option></select></label><label>{tr('동의 확인 날짜')}<input type="date" value={date} onChange={e=>{setDate(e.target.value);setChecked(false);}}/></label><label>{tr('확인 근거')}<input value={note} maxLength={1000} onChange={e=>{setNote(e.target.value);setChecked(false);}}/></label><p>{tr('동의한 사람과 확인한 내용을 간단히 기록하세요. 실제 개인정보는 입력하지 마세요.')}</p><label className="consent-check"><input type="checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}/>{tr('동의 권한이 있는 사람의 의사와 변경 항목을 확인했습니다.')}</label></div>}
 <button disabled={!changed||!checked||!date||!note.trim()} onClick={()=>void save()}>{tr('공유 설정 저장')}</button>
 <details><summary>{tr('상세 이력 및 기존 근거')}</summary>{data.history.filter(h=>h.recipient_id===recipient).slice().reverse().map(h=><article key={h.version}><p>v{h.version} · {h.confirmed_at} · {h.confirmed_by}</p><p>{list(h.scopes)}</p><pre>{JSON.stringify(h.evidence_ref,null,2)}</pre></article>)}{data.candidates.filter(c=>c.recipient_id===recipient).map(c=><article key={c.candidate_id}><p>{tr('이전 동의 후보')} · {c.disposition} · {list(c.proposed_scopes)}</p><pre>{JSON.stringify(c.utterance_ref,null,2)}</pre></article>)}</details></>}
 {!busy&&!data.grants.length&&<p>{tr('선택할 보호자가 없습니다.')}</p>}</fieldset><p>{tr('Paikallinen demomenettely. Oikeudellista pätevyyttä ei ole vahvistettu.')}</p></section>;
}
