import {careTopics,personaNames} from './careTopics';
import {useQuery} from '@tanstack/react-query';
import {useEffect,useState} from 'react';
import {api} from './api';
import {useUiLanguage} from './UiLanguage';
const categories:Record<string,string>={meals:'Ruokailu',movement:'Liikkuminen',care_contact:'Yhteydenotto',medication:'Lääkitys',sleep:'Uni',outdoors:'Ulkoilu',health_context:'건강 관련 정보'};
type Grant={recipient_id:string;scopes:string[]};
export function SharingSummary({role,name,actor}:{role:string;name:string;actor:string}){
 const {tr}=useUiLanguage();
 const [online,setOnline]=useState(navigator.onLine);
 useEffect(()=>{const on=()=>setOnline(true),off=()=>setOnline(false);window.addEventListener('online',on);window.addEventListener('offline',off);return()=>{window.removeEventListener('online',on);window.removeEventListener('offline',off);};},[]);
 const query=useQuery({queryKey:['sharing-summary',role,actor],refetchInterval:5000,queryFn:async()=>role==='staff'?(await api<{grants:Grant[]}>('/staff/residents/aino/consents')).grants:[{recipient_id:actor,scopes:(await api<{scopes:string[]}>('/family/residents/aino/sharing')).scopes}]});
 return <section className="sharing-summary" aria-label={tr('현재 공유 범위')}><h2>{tr(role==='staff'?'보호자별 공유 범위':'현재 공유 범위')}</h2>{query.isError||!online?<p role="alert">{tr('현재 권한을 확인할 수 없습니다.')}</p>:query.isPending?<p role="status">…</p>:query.data?.map(g=><div key={g.recipient_id}><h3>{personaNames[g.recipient_id]??name}({tr('보호자')}) · Helmi Nieminen</h3><div className="sharing-categories">{careTopics.filter(({key})=>role==='staff'||g.scopes.includes(key)).map(({key,label})=><span key={key} className="badge" data-testid={'scope-'+g.recipient_id.toLowerCase()+'-'+key} data-shared={g.scopes.includes(key)}>{tr(label)} · {tr(g.scopes.includes(key)?'공유됨':'비공개')}</span>)}</div></div>)}<p className="muted">{tr('현재 공유 권한과 근거가 확인된 정보만 표시합니다.')}</p></section>;
}
