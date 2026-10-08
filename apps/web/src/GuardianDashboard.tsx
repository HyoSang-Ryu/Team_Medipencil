import {useEffect,useState} from 'react';
import {Sun,CalendarBlank,ChatCircle,ForkKnife,Pill,PersonSimpleWalk,Tree,Bed,Heart} from '@phosphor-icons/react';
import {Link} from 'react-router-dom';
import {api} from './api';
import {Avatar} from './Profiles';
import {DashboardCharts} from './DashboardCharts';
import {dailyOverview,type BoardData} from './dailyUpdate';
import {useUiLanguage,languageLocales} from './UiLanguage';
import type {Question} from './App';
const topicCards:Record<string,{label:string;Icon:typeof Heart}>={meals:{label:'Ruokailu',Icon:ForkKnife},medication:{label:'Lääkitys',Icon:Pill},movement:{label:'Liikkuminen',Icon:PersonSimpleWalk},outdoors:{label:'Ulkoilu',Icon:Tree},sleep:{label:'Uni',Icon:Bed},care_contact:{label:'Yhteydenotto',Icon:ChatCircle}};
type Notice={event_id:string;title:string;starts_at:string;status:string;acknowledged_at:string|null};
export function GuardianDashboard({name,locale,questions,questionsReady}:{name:string;locale:string;questions:Question[];questionsReady:boolean}){
 const {tr,language}=useUiLanguage();
 const [data,setData]=useState<{board:BoardData;notices:Notice[]}|null>(null),[failed,setFailed]=useState(false);
 useEffect(()=>{let active=true;const hide=()=>{setData(null);setFailed(true);};
 const read=async()=>{try{const [board,events]=await Promise.all([api<BoardData>(`/family/residents/aino/board?lang=${locale}`),api<{items:Notice[]}>('/family/residents/aino/family-events')]);if(active&&navigator.onLine){setData({board,notices:events.items});setFailed(false);}}catch{if(active)hide();}};
 setData(null);void read();const timer=setInterval(()=>void read(),5000);window.addEventListener('offline',hide);window.addEventListener('online',read);
 return()=>{active=false;clearInterval(timer);window.removeEventListener('offline',hide);window.removeEventListener('online',read);};},[locale]);
 const overview=data?dailyOverview(data.board):null;
 const next=data?.notices.filter(n=>n.status==='scheduled'&&Date.parse(n.starts_at)>=Date.now()).sort((a,b)=>Date.parse(a.starts_at)-Date.parse(b.starts_at))[0];
 const date=(value:string)=>new Date(value).toLocaleDateString(languageLocales[language],{month:'long',day:'numeric',timeZone:'Europe/Helsinki'});
 return <div className="guardian-home" data-testid="guardian-home"><section className="home-hero"><div className="home-person"><Avatar actor="aino" name="Aino" size="lg"/><div><p className="eyebrow">{name} · {tr('보호자')}</p><h1>{tr('Aino의 안부 한눈에')}</h1><p>{tr('나에게 공유된 소식만 모았어요.')}</p></div></div><Link className="home-detail-link" data-testid="guardian-detail-link" to="/family/residents/aino/details">{tr('상세보기')} →</Link></section>
 <div className="home-summary"><section className="home-latest"><span className="home-card-symbol" aria-hidden="true"><Sun size={26}/></span><h2>{tr('최근 안부')}</h2>{failed?<p role="alert">{tr('연결 또는 권한을 확인하세요. 알림은 숨겨졌습니다.')}</p>:!data?<p role="status">{tr('불러오는 중…')}</p>:<><strong>{tr(overview?.hasToday?'오늘의 기록이 공유됐어요.':'오늘의 안부를 기다리고 있어요.')}</strong>{overview?.newest&&<p className="latest-quote">{overview.newest.statement}<small>{tr(overview.newest.claim_type==='plan'?'Suunnitelma — ei toteutunut':overview.newest.claim_type==='staff_observation'?'Hoitajan havainto':overview.newest.claim_type)}</small></p>}<p>{overview?.newest?`${tr('최근 기록')}: ${date(overview.newest.observed_at)}`:tr('공유된 기록을 기다리고 있어요.')}</p></>}</section>
 <section className="home-care"><div className="home-care-heading"><h2>{tr('공유된 관리 항목')}</h2><Link to="/family/residents/aino/details">{tr('상세보기')} →</Link></div><div className="home-care-grid">{data?.board.tiles.filter(t=>t.display_state!=='not_shared').map(tile=>{const info=topicCards[tile.topic];if(!info)return null;const Icon=info.Icon;const latest=data.board.language_state==='available'?[...tile.items].sort((a,b)=>Date.parse(b.observed_at)-Date.parse(a.observed_at))[0]:undefined;return <Link className="home-care-tile" key={tile.topic} to="/family/residents/aino/details"><Icon size={26} weight="duotone" aria-hidden="true"/><div><h3>{tr(info.label)}</h3><p>{latest?latest.statement:tr('공유된 기록을 기다리고 있어요.')}</p>{latest&&<small>{date(latest.observed_at)} · {tr(latest.claim_type==='plan'?'Suunnitelma — ei toteutunut':latest.claim_type==='staff_observation'?'Hoitajan havainto':latest.claim_type)}</small>}</div></Link>;})}</div></section>
 <section><span className="home-card-symbol" aria-hidden="true"><CalendarBlank size={26}/></span><h2>{tr('미확인 안내')}</h2><strong className="home-number">{data?data.notices.filter(n=>!n.acknowledged_at).length:'—'}</strong><p>{next?`${date(next.starts_at)} · ${next.title}`:data?tr('예정된 안내가 없습니다.'):failed?'—':tr('불러오는 중…')}</p></section>
 <section><span className="home-card-symbol" aria-hidden="true"><ChatCircle size={26}/></span><h2>{tr('답변 대기')}</h2><strong className="home-number">{questionsReady?questions.filter(q=>!q.answer_available).length:'—'}</strong><p>{tr('문의와 간호사 답글은 상세보기에서 확인하세요.')}</p></section></div>

 <DashboardCharts role="family" compact/>
 <p className="home-footnote">{tr('안부 원문·어제와 비교·기간 조회·가족확인사항은 상세보기에서 볼 수 있어요.')}</p></div>;
}
