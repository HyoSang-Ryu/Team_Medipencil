import {useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {Link} from 'react-router-dom';
import {api} from './api';
import {Capture,type EmrBundle,type ReviewEntry} from './Capture';
import {DeliverySchedule} from './DeliverySchedule';
import {Publication} from './Publication';
import {useUiLanguage} from './UiLanguage';
import {stateLabel} from './labels';
type ReviewData={bundle:EmrBundle;items:ReviewEntry[]};
export function StaffReview({questions,onApproved,online}:{questions:{question_id:string;text:string}[];onApproved:()=>void;online:boolean}){
 const {tr}=useUiLanguage();const [selected,setSelected]=useState<ReviewEntry|null>(null),[working,setWorking]=useState(false),[cycle,setCycle]=useState(0);
 const query=useQuery({queryKey:['emr-review'],queryFn:()=>api<ReviewData>('/staff/residents/aino/emr-review'),refetchInterval:5000});
 const residents=useQuery({queryKey:['staff-residents'],queryFn:()=>api<{items:{subject_id:string;display_name:string;unit_name:string}[]}>('/staff/residents'),refetchInterval:10000});
 const refresh=()=>{void query.refetch();onApproved();};
 const data=!online||query.isError?null:query.data;
 return <div className="staff-review" data-testid="staff-review"><section><p className="eyebrow">Heli Koskinen · {tr('간호사')}</p><h1>{tr('정기 전달 및 확인함')}</h1><p>{tr('일상 기록은 자동 전달하고, 확인이 필요한 내용만 검토하세요.')}</p><ol className="review-process">{['EMR 자료','일상 기록 자동 확인','예외만 직원 확인','매일 오후 6시 전달'].map((x,i)=><li key={x}><b>{i+1}</b>{tr(x)}</li>)}</ol><p className="notice">{tr('합성 EMR 시연 · 실제 병원 연동 없음. AI 실행 여부는 초안마다 표시합니다.')}</p><div className="row"><Link to="/staff/queue">{tr('가족확인사항·문의 처리')}</Link><Link to="/staff/residents/aino/capture">{tr('보충 기록 직접 입력')}</Link></div></section>
 <section className="ward-list"><h2>{tr('담당 병동 · 환자 목록')}</h2><p>{tr('현재 접근 권한이 있는 환자만 표시합니다.')}</p>{!online||residents.isError?<p role="alert">{tr('연결 또는 권한을 확인하세요. 검토 자료를 숨겼습니다.')}</p>:residents.isPending?<p role="status">{tr('불러오는 중…')}</p>:residents.data?.items.map(resident=><button key={resident.subject_id} aria-pressed={resident.subject_id==='aino'} onClick={()=>document.getElementById('resident-review')?.scrollIntoView({behavior:'smooth'})}><strong>{resident.display_name}</strong><span>{resident.unit_name}</span></button>)}</section><div id="resident-review"><p className="muted">{tr('EMR 예시 어댑터')}: Synthetic EMR v1 · {tr('실제 병원 연동 없음')}</p><DeliverySchedule/></div>
 <Publication ai showSchedule={false}/>
 {!data?<section><p role={query.isError||!online?'alert':'status'}>{tr(query.isError||!online?'연결 또는 권한을 확인하세요. 검토 자료를 숨겼습니다.':'불러오는 중…')}</p></section>:<><section><div className="home-care-heading"><h2>Aino Nieminen · {tr('검토할 자료')}</h2><button onClick={()=>{setSelected(null);setWorking(true);setCycle(n=>n+1);}}>{tr('합성 EMR 자료로 시작')}</button></div><p>{tr('최근 100개 기록 · 초안과 승인 기록을 다시 열 수 있습니다.')}</p><div className="review-inbox">{data.items.length===0?<p>{tr('저장된 초안이 없습니다. EMR 자료로 시작하세요.')}</p>:data.items.map(entry=><button className="review-inbox-card" key={entry.record.record_id} onClick={()=>{setSelected(entry);setWorking(true);setCycle(n=>n+1);}}><strong>{tr(stateLabel[entry.record.status])} · v{entry.record.version}</strong><span>{entry.record.segments[0]?.text}</span><small>{tr(entry.execution?.ai_executed?'AI 실행':'AI 미실행')} · {entry.execution?.model??entry.execution?.provider_id??'—'}</small></button>)}</div></section>
 {working&&<><Capture key={cycle} emr={data.bundle} resume={selected??undefined} questions={questions} onApproved={refresh}/><Publication showSchedule={false}/></>}</>}
 </div>;
}
