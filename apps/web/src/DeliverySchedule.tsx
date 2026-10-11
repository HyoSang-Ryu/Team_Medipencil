import {useEffect,useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {api} from './api';
import {useUiLanguage,languageLocales} from './UiLanguage';
type Schedule={recipient_id:string;display_name:string;enabled:boolean;revision:number;next_run_at:string|null;last_run_at:string|null;last_result:string|null;exceptions:{source_id:string;text:string;reason:string}[]};
export function DeliverySchedule({family=false}:{family?:boolean}){
 const {tr,language}=useUiLanguage();const [busy,setBusy]=useState(''),[error,setError]=useState('');
 const [online,setOnline]=useState(navigator.onLine);useEffect(()=>{const update=()=>setOnline(navigator.onLine);window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{window.removeEventListener('online',update);window.removeEventListener('offline',update);};},[]);
 const query=useQuery({queryKey:['delivery-schedules',family],queryFn:()=>family?api<Schedule>('/family/residents/aino/delivery-schedule').then(s=>({items:[s]})):api<{items:Schedule[]}>('/staff/residents/aino/delivery-schedules'),refetchInterval:10000});
 const time=(v:string|null)=>v?new Date(v).toLocaleString(languageLocales[language],{timeZone:'Europe/Helsinki'}):'—';
 async function toggle(s:Schedule){setBusy(s.recipient_id);setError('');try{await api(`/staff/residents/aino/delivery-schedules/${s.recipient_id}`,{enabled:!s.enabled,expected_revision:s.revision});await query.refetch();}catch(e){setError(String(e));await query.refetch();}finally{setBusy('');}}
 const result=(s:Schedule)=>tr(s.last_result?.startsWith('blocked:')?'전달 차단 · 직원 확인 필요':s.last_result==='delivered'?'전달 완료':s.last_result==='no_new_content'?'새 전달 내용 없음':s.last_result==='no_permission'?'공유 권한 없음':s.last_result==='already_processed'?'이미 처리됨':'아직 실행 전');
 return <section className="delivery-schedule" data-testid={family?'family-delivery-schedule':'delivery-schedule'}><h2>{tr('매일 안부 자동 전달')}</h2><p>{tr('매일 오후 6시 · 핀란드 시간')}</p>{!family&&<p>{tr('최초 한 번 시작하면 확인된 EMR 일상 기록을 자동 전달합니다. 매번 승인할 필요가 없습니다.')}</p>}
 {error&&<p role="alert">{error}</p>}{(!online||query.isError)?<p role="alert">{tr('연결 또는 권한을 확인하세요. 검토 자료를 숨겼습니다.')}</p>:!query.data?<p>{tr('불러오는 중…')}</p>:query.data.items.map((s,i)=><article key={s.recipient_id??i}><h3>{!family&&`${s.display_name} · `} {tr(s.enabled?'정기 전달 켜짐':'정기 전달 중지')}</h3><p>{tr('다음 전달')}: {time(s.next_run_at)}</p><p>{tr('최근 결과')}: {result(s)} {s.last_run_at&&` · ${time(s.last_run_at)}`}</p>{!family&&<><button disabled={!!busy} onClick={()=>void toggle(s)}>{tr(s.enabled?'정기 전달 중지하기':'정기 전달 시작하기')}</button>{s.exceptions.length>0&&<details open><summary>{tr('직원 확인 필요')} · {s.exceptions.length}</summary>{s.exceptions.map((e,j)=><p key={j}>{e.text}<small> · {tr('실행 미확인 또는 자동 전달 대상 아님')}</small></p>)}</details>}</>}</article>)}
 <small>{tr('합성 EMR 시연 · 확인된 식사·이동 원문만 자동 전달 · 실제 EMR·AI·문자 발송 없음')}</small></section>;
}
