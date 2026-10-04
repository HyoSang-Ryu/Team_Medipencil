import {useEffect,useRef,useState} from 'react';
import {api} from './api';
import {useUiLanguage} from './UiLanguage';
type Comment={comment_id:string;reviewer_alias:string;screen:string;body:string;created_at:string};
const screens:Record<string,string>={general:'전체 흐름',family:'가족 상황판',questions:'직원 질문 큐',record:'기록·검토',publication:'발행',consent:'동의'};
export function ReviewComments(){
 const {tr,language}=useUiLanguage();
 const [alias,setAlias]=useState(''),[screen,setScreen]=useState('general'),[body,setBody]=useState('');
 const [filter,setFilter]=useState(''),[items,setItems]=useState<Comment[]>([]),[loading,setLoading]=useState(true),[busy,setBusy]=useState(false),[error,setError]=useState(''),[saved,setSaved]=useState(false),[reload,setReload]=useState(0);
 const pending=useRef({payload:'',key:''});
 useEffect(()=>{let active=true;setLoading(true);setItems([]);setError('');
  void api<{items:Comment[]}>('/poc/comments'+(filter?'?screen='+filter:'')).then(r=>{if(active)setItems(r.items);}).catch(e=>{if(active)setError(String(e));}).finally(()=>{if(active)setLoading(false);});
  return()=>{active=false;};
 },[filter,reload]);
 async function submit(){
  const payload={reviewer_alias:alias.trim(),screen,body:body.trim()};const serialized=JSON.stringify(payload);
  if(pending.current.payload!==serialized)pending.current={payload:serialized,key:crypto.randomUUID()};
  setBusy(true);setError('');setSaved(false);
  try{await api<Comment>('/poc/comments',payload,undefined,undefined,pending.current.key);setBody('');pending.current={payload:'',key:''};setSaved(true);setReload(n=>n+1);}
  catch(e){setError(String(e));}finally{setBusy(false);}
 }
 return <section className="workspace comments" lang={language==='en'?'en':'ko'}><h1>{tr('팀 코멘트')}</h1>
 <p>{tr('PoC 검토 의견을 이 회차의 서버 DB에 저장합니다. 직원 역할 검토자들이 함께 볼 수 있습니다. 별칭은 본인 인증이 아닙니다.')}</p>
 <p className="privacy-note">{tr('화면 사용성만 기록하세요. 실제 이름·연락처·돌봄 기록·비공개 근거를 복사하지 마세요. 코멘트 등록은 검증 완료나 수정 확정을 뜻하지 않습니다.')}</p>
 <div className="comment-grid"><div className="panel"><form onSubmit={e=>{e.preventDefault();void submit();}}>
 <div className="comment-fields"><label>{tr('익명 팀원 별칭')}<input required maxLength={40} value={alias} disabled={busy} onChange={e=>setAlias(e.target.value)}/></label>
 <label>{tr('검토 화면')}<select value={screen} disabled={busy} onChange={e=>setScreen(e.target.value)}>{Object.entries(screens).map(([key,label])=><option key={key} value={key}>{tr(label)}</option>)}</select></label>
 </div><label>{tr('코멘트')}<textarea required maxLength={3000} rows={5} value={body} disabled={busy} onChange={e=>{setBody(e.target.value);setSaved(false);}}/></label>
 <p className="muted">{tr('막힌 동작 → 재현 순서 → 기대 결과 → 실제 결과 → 개선 제안을 적어주세요.')}</p>
 <button disabled={busy||!alias.trim()||!body.trim()}>{tr(busy?'저장 중…':'코멘트 저장')}</button>
 </form>
 {error&&<p role="alert">{tr('요청 실패. 입력은 유지됩니다. 다시 시도하세요.')} ({error})</p>}
 {saved&&<p role="status">{tr('코멘트를 저장했습니다.')}</p>}
 </div><div className="panel"><h2>{tr('검토 의견 목록')}</h2><div className="row"><label>{tr('화면 필터')}<select value={filter} onChange={e=>setFilter(e.target.value)}><option value="">{tr('모든 화면')}</option>{Object.entries(screens).map(([key,label])=><option key={key} value={key}>{tr(label)}</option>)}</select></label><button type="button" className="secondary" style={{alignSelf:'center'}} onClick={()=>setReload(n=>n+1)}>{tr('목록 새로고침')}</button></div>
 <p className="muted">{tr('선택한 화면의 최근 200건을 표시합니다. 자동 시험 코멘트는 실제 팀원 피드백과 구분하세요.')}</p>
 {loading?<p role="status">{tr('불러오는 중…')}</p>:!error&&items.length===0?<p>{tr('아직 코멘트가 없습니다.')}</p>:items.map(c=><article key={c.comment_id} style={{overflowWrap:'anywhere'}}><p><strong>{c.reviewer_alias}</strong> · {tr(screens[c.screen])} · <time dateTime={c.created_at}>{new Date(c.created_at).toLocaleString(language==='en'?'en-GB':'ko-KR',{timeZone:'Europe/Helsinki'})}</time></p><p style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{c.body}</p><small>{c.comment_id}</small></article>)}
 </div></div></section>;
}
