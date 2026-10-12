import {ReviewText} from './ReviewText';
import {useUiLanguage} from './UiLanguage';
import {useState,useEffect} from 'react';
import {api,sessionSignal} from './api';
import {waitJob,type Job} from './jobs';
import {DeliverySchedule} from './DeliverySchedule';
import {stateLabel} from './labels';
type Pub={recipient_id:string;publication_id:string;revision:number;status:string;content_epoch:number;consent_version:number;items:{item_id:string;statement:string;claim_type:string;source_excerpt?:string}[];generation_meta?:{model?:string;ai_executed?:boolean};answer_bindings:{candidate_id:string}[]};
type Guardian={recipient_id:string;display_name:string};
type Delivery={guardian:Guardian;pub:Pub|null;error:string;publishKey:string};
export function Publication({showSchedule=true,ai=false}:{showSchedule?:boolean;ai?:boolean}){
 const {tr}=useUiLanguage();
 const [days,setDays]=useState(3);
 const [provider,setProvider]=useState<{backend:string;model:string|null}|null>(null);
 useEffect(()=>{if(!ai)return;let active=true;void api<{llm:{backend:string;model:string|null}}>('/staff/providers').then(r=>{if(active)setProvider(r.llm);}).catch(()=>{if(active)setProvider({backend:'disabled',model:null});});return()=>{active=false;};},[ai]);
 const [recipients,setRecipients]=useState<Guardian[]>([]),[selected,setSelected]=useState<string[]>(['liisa']);
 const [deliveries,setDeliveries]=useState<Delivery[]>([]),[checked,setChecked]=useState(false),[error,setError]=useState(''),[busy,setBusy]=useState(false),[loaded,setLoaded]=useState(false);
 useEffect(()=>{let active=true;void api<{grants:Guardian[]}>('/staff/residents/aino/consents').then(r=>{if(active){setRecipients(r.grants);setSelected(ids=>ids.filter(id=>r.grants.some(g=>g.recipient_id===id)));setLoaded(true);}}).catch(e=>{if(active){setError(String(e));setLoaded(true);}});return()=>{active=false;};},[]);
 function select(ids:string[]){setSelected(ids);setDeliveries([]);setChecked(false);setError('');}
 async function prepare(){
  setBusy(true);setDeliveries([]);setChecked(false);setError('');const signal=sessionSignal();const results:Delivery[]=[];
  try{for(const guardian of recipients.filter(r=>selected.includes(r.recipient_id))){
   if(signal.aborted)break;
   const entry:Delivery={guardian,pub:null,error:'',publishKey:crypto.randomUUID()};
   try{const ctx=await api<{content_epoch:number;consent_version:number}>(`/staff/residents/aino/publication-context?recipient_id=${encodeURIComponent(guardian.recipient_id)}`);
    const job=ai?await waitJob(await api<Job>('/staff/residents/aino/ai-summary',{recipient_id:guardian.recipient_id,days})):await api<{result_ref:{id:string}}>('/staff/publications/prepare',{subject_id:'aino',recipient_id:guardian.recipient_id,lang:'fi',expected_content_epoch:ctx.content_epoch,expected_consent_version:ctx.consent_version});
    entry.pub=await api<Pub>(`/staff/publications/${job.result_ref!.id}`);
   }catch(e){entry.error=String(e);}
   results.push(entry);if(!signal.aborted)setDeliveries([...results]);
  }}finally{setBusy(false);}
 }
 async function restore(){setBusy(true);setChecked(false);setError('');try{
  const saved=await api<{items:Pub[]}>('/staff/residents/aino/ai-summaries');
  setDeliveries(recipients.filter(r=>selected.includes(r.recipient_id)).map(guardian=>({guardian,pub:saved.items.find(p=>p.recipient_id===guardian.recipient_id)??null,error:'',publishKey:crypto.randomUUID()})));
 }catch(e){setError(String(e));}finally{setBusy(false);}}
 async function publish(){
  if(!checked||busy)return;setBusy(true);const signal=sessionSignal();const results=[...deliveries];
  try{for(let i=0;i<results.length;i++){
   if(signal.aborted)break;
   const entry=results[i],pub=entry.pub;if(!pub||pub.status!=='draft')continue;
   try{const saved=await api<Pub>(`/staff/publications/${pub.publication_id}/publish`,{reviewed_items:pub.items.map(item=>({item_id:item.item_id,meaning_checked:true,language_checked:true,evidence_checked:true})),accepted_answer_candidate_ids:pub.answer_bindings.map(b=>b.candidate_id),expected_content_epoch:pub.content_epoch,expected_consent_version:pub.consent_version},pub.revision,undefined,entry.publishKey);results[i]={...entry,pub:saved,error:''};
   }catch(e){results[i]={...entry,error:String(e)};}
   if(!signal.aborted)setDeliveries([...results]);
  }}finally{setBusy(false);}
 }
 const pending=deliveries.filter(d=>d.pub?.status==='draft');
 const completed=deliveries.filter(d=>d.pub?.status==='published');
 return <>{showSchedule&&<DeliverySchedule/>}<section className="publication"><h2>{tr(ai?'합성 EMR → AI 안부 → 보호자 전달':'4 · Tarkista ja julkaise perheelle')}</h2>
 {ai&&<><p>{provider?.backend==='disabled'?tr('로컬 AI가 설정되지 않았습니다. 서버 모델 설정 후 사용할 수 있습니다.'):provider?provider.model:tr('불러오는 중…')}</p><p>{tr('설치된 로컬 모델로 기간별 합성 기록을 정리합니다. 생성 문장을 원문과 대조한 후 발행하세요.')}</p><label>{tr('기간')} <select disabled={busy} value={days} onChange={e=>{setDays(Number(e.target.value));setDeliveries([]);setChecked(false);}}>{[1,3,7,30].map(n=><option key={n} value={n}>{n} {tr('일')}</option>)}</select></label></>}
 <fieldset className="publication-guardians" disabled={busy}><legend>{tr('보호자')}</legend>
 {!loaded&&<p role="status">{tr('불러오는 중…')}</p>}{loaded&&!error&&recipients.length===0&&<p>{tr('선택할 보호자가 없습니다.')}</p>}
 {recipients.length>0&&<label className="guardian-select-all"><input type="checkbox" checked={recipients.every(r=>selected.includes(r.recipient_id))} onChange={e=>select(e.target.checked?recipients.map(r=>r.recipient_id):[])}/>{tr('보호자 전체 선택')}</label>}
 <div className="guardian-options">{recipients.map(r=><label key={r.recipient_id}><input type="checkbox" checked={selected.includes(r.recipient_id)} onChange={e=>select(e.target.checked?[...selected,r.recipient_id]:selected.filter(id=>id!==r.recipient_id))}/>{r.display_name}</label>)}</div></fieldset>
 <p className="muted">{tr('선택한 보호자별 공개 범위로 미리보기를 만들고 한 번에 발행합니다.')}</p>
 <button disabled={busy||!selected.length||!loaded||(ai&&(!provider||provider.backend==='disabled'))} onClick={()=>void prepare()}>{tr(ai?(busy?'AI 처리 중…':'로컬 AI로 안부 만들기'):'Valmistele julkaisu')}</button>{ai&&<button disabled={busy||!loaded} onClick={()=>void restore()}>{tr('저장된 AI 결과 불러오기')}</button>}{error&&<p role="alert">{error}</p>}
 {deliveries.map(d=><article className="guardian-preview" key={d.guardian.recipient_id} data-recipient={d.guardian.recipient_id}><h3>{tr('Esikatselu ·')} {d.guardian.display_name} {d.pub&&<>· <span className="badge" data-state={d.pub.status}>{tr(stateLabel[d.pub.status])}</span></>}</h3>{d.error&&<p role="alert">{tr(d.pub?'발행 실패 · 완료된 보호자는 다시 발행하지 않습니다.':'미리보기 실패 · 이 보호자에게는 발행하지 않습니다.')} {d.error}</p>}{d.pub?.generation_meta&&<p>{d.pub.generation_meta.model} · {tr(d.pub.generation_meta.ai_executed?(d.pub.status==='published'?'실제 AI 생성 · 직원 검토 후 발행':'실제 AI 생성 · 원문 검토 필요'):'AI 미실행')}</p>}{d.pub?.items.map(i=><div key={i.item_id}><p><ReviewText text={i.statement}/> <small>{tr(stateLabel[i.claim_type])}</small></p>{i.source_excerpt&&<details open><summary>{tr('근거 원문')}</summary><p style={{whiteSpace:'pre-line'}}><ReviewText text={i.source_excerpt}/></p></details>}</div>)}{d.pub?.status==='published'&&<p role="status" aria-label={tr('Julkaisun tila')}>{tr('Julkaistu. Perheen näkymä tarkistaa oikeudet uudelleen.')}</p>}</article>)}
 {pending.length>0&&<div className="bulk-publication"><label><input type="checkbox" disabled={busy} checked={checked} onChange={e=>setChecked(e.target.checked)}/>{tr('Tarkistin jokaisen lauseen merkityksen, lähteen, suomen kielen ja vastauksen riittävyyden.')}</label><button disabled={!checked||busy} onClick={()=>void publish()}>{tr('선택 보호자에게 일괄 발행')}</button></div>}
 {deliveries.length>0&&<p aria-live="polite">{tr('발행 완료')}: {completed.length} / {deliveries.length}</p>}
 </section></>;
}
