import {useRef,useState} from 'react';
import {api} from './api';
import {useUiLanguage} from './UiLanguage';
import {stateLabel} from './labels';
import type {RecordData} from './Capture';
type Cap={capture_id:string;revision:number};
type Pub={publication_id:string;revision:number;status:string;content_epoch:number;consent_version:number;items:{item_id:string;statement:string;claim_type:string}[];answer_bindings:{candidate_id:string}[]};
export function QuestionReply({questionId,recipient,subject,onPublished}:{questionId:string;recipient:string;subject:string;onPublished:()=>void}){
 const {tr}=useUiLanguage();const [text,setText]=useState(''),[kind,setKind]=useState('observation'),[scope,setScope]=useState('care_contact');
 const [record,setRecord]=useState<RecordData|null>(null),[pub,setPub]=useState<Pub|null>(null),[checked,setChecked]=useState(false),[reviewed,setReviewed]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 // Stable stage keys preserve retry identity after a lost network response.
 const work=useRef<{keys:Record<string,string>;cap?:Cap;source?:Cap;record?:RecordData;approved?:RecordData;context?:{content_epoch:number;consent_version:number};payload?:unknown}>({keys:{}});
 const key=(stage:string)=>work.current.keys[stage]??(work.current.keys[stage]=crypto.randomUUID());
 async function run(fn:()=>Promise<void>){setBusy(true);setError('');try{await fn();}catch(e){setError(String(e));}finally{setBusy(false);}}
 async function draft(){
  const w=work.current;
  w.payload??={occurred_at:new Date().toISOString(),utterances:[{speaker:'carer',text,type:kind,required_scopes:scope.split(',')}]};
  w.cap??=await api<Cap>(`/staff/residents/${subject}/captures`,{input_mode:'text'},undefined,undefined,key('capture'));
  w.source??=await api<Cap>(`/staff/captures/${w.cap.capture_id}/text`,w.payload,w.cap.revision,undefined,key('source'));
  const job=await api<{result_ref:{id:string;version:number}}>(`/staff/captures/${w.source.capture_id}/drafts`,{question_ids:[questionId],processing_mode:'manual'},w.source.revision,undefined,key('draft'));
  w.record??=await api<RecordData>(`/staff/records/${job.result_ref.id}?version=${job.result_ref.version}`);setRecord(w.record);
 }
 async function prepare(){
  if(!record||!checked)return;const w=work.current;
  w.approved??=await api<RecordData>(`/staff/records/${record.record_id}/approve`,{version:record.version,segment_reviews:record.segments.map(s=>({segment_id:s.segment_id,meaning_checked:true,speaker_checked:true,negation_and_tense_checked:true,numbers_checked:true,scopes_checked:true})),candidate_reviews:record.answer_candidates.map(c=>({candidate_id:c.candidate_id,accepted:true,sufficient_answer_checked:true}))},record.revision,undefined,key('approve'));
  w.context??=await api(`/staff/residents/${subject}/publication-context?recipient_id=${recipient}`);
  const c=w.context!;
  const job=await api<{result_ref:{id:string}}>(`/staff/publications/prepare`,{subject_id:subject,recipient_id:recipient,lang:'fi',expected_content_epoch:c.content_epoch,expected_consent_version:c.consent_version},undefined,undefined,key('prepare'));
  setPub(await api<Pub>(`/staff/publications/${job.result_ref.id}`));
 }
 async function publish(){
  if(!pub||!reviewed)return;
  setPub(await api<Pub>(`/staff/publications/${pub.publication_id}/publish`,{reviewed_items:pub.items.map(i=>({item_id:i.item_id,meaning_checked:true,language_checked:true,evidence_checked:true})),accepted_answer_candidate_ids:pub.answer_bindings.map(b=>b.candidate_id),expected_content_epoch:pub.content_epoch,expected_consent_version:pub.consent_version},pub.revision,undefined,key('publish')));onPublished();
 }
 const locked=!!work.current.payload;
 return <div className="question-reply-editor"><h3>{tr('직원 답글 작성')}</h3><p className="muted">{tr('확인한 근거를 직접 입력하세요. 검토·승인 후 발행해야 가족에게 보입니다.')}</p>
 {!record&&<><label>{tr('답글 내용')}<textarea maxLength={2000} value={text} disabled={locked||busy} onChange={e=>setText(e.target.value)}/></label><div className="reply-settings"><label>{tr('Tyyppi')}<select aria-label={tr('Tyyppi')} disabled={locked||busy} value={kind} onChange={e=>setKind(e.target.value)}><option value="observation">{tr('Havainto')}</option><option value="plan">{tr('Suunnitelma — ei toteutunut')}</option></select></label><label>{tr('Tiedon sisältö')}<select disabled={locked||busy} value={scope} onChange={e=>setScope(e.target.value)}>{['care_contact','meals','medication','movement','outdoors','sleep','health_context','outdoors,health_context'].map((s,i)=><option value={s} key={s}>{tr(['Yhteydenotto','Ruokailu','Lääkitys','Liikkuminen','Ulkoilu','Uni','Terveystieto','Ulkoilu ja terveystieto'][i])}</option>)}</select></label></div><button disabled={busy||!text.trim()} onClick={()=>void run(draft)}>{tr('답글 검토')}</button></>}
 {record&&!pub&&<><blockquote>{record.segments.map(s=><p key={s.segment_id}>{s.text} <small>{tr(stateLabel[s.type])}</small></p>)}</blockquote><label><input type="checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}/>{tr('근거·의미·공유 범위와 질문에 대한 답변을 확인했습니다.')}</label><button disabled={busy||!checked} onClick={()=>void run(prepare)}>{tr('답글 승인 및 발행 준비')}</button></>}
 {pub&&<><h4>{tr('가족에게 공개될 내용')}</h4><p className="muted">{tr('이 수신자에게 발행될 전체 내용을 확인하세요. 기존 승인 기록도 포함될 수 있습니다.')}</p>{pub.items.map(i=><p key={i.item_id}>{i.statement} <small>{tr(stateLabel[i.claim_type])}</small></p>)}{pub.status==='draft'?<><label><input type="checkbox" checked={reviewed} onChange={e=>setReviewed(e.target.checked)}/>{tr('전체 내용의 근거·표현·공개 권한을 확인했습니다.')}</label><button disabled={busy||!reviewed} onClick={()=>void run(publish)}>{tr('답글 발행')}</button></>:<p role="status">{tr('답글을 발행했습니다.')}</p>}</>}
 {error&&<p role="alert">{tr(error)}</p>}</div>;
}
