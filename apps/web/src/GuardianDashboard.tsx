import {KideFamily} from './KideWorkflow';
import {familyResidentLabel,originalFamilyIdentity} from './familyIdentity';
import {DashboardCharts} from './DashboardCharts';
import {isXdDesign} from './designVariant';
import {useEffect,useState} from 'react';
import {Sun,CalendarBlank,ChatCircle} from '@phosphor-icons/react';
import {Link} from 'react-router-dom';
import {api} from './api';
import {useCareMessage} from './useCareMessage';
import {DeliverySchedule} from './DeliverySchedule';
import {Avatar} from './Profiles';
import {TopicMessage} from './TopicMessage';
import {careTopics} from './careTopics';
import {isAiSummary,dailyOverview,type BoardData} from './dailyUpdate';
import {useUiLanguage,languageLocales} from './UiLanguage';
import type {Question} from './App';
type Notice={event_id:string;title:string;starts_at:string;status:string;acknowledged_at:string|null};
export function GuardianDashboard({name,locale,questions,questionsReady}:{name:string;locale:string;questions:Question[];questionsReady:boolean}){
 const {tr,language}=useUiLanguage();
 const [data,setData]=useState<{board:BoardData;notices:Notice[]}|null>(null),[failed,setFailed]=useState(false);
 useEffect(()=>{let active=true;const hide=()=>{setData(null);setFailed(true);};
 const read=async()=>{try{const [board,events]=await Promise.all([api<BoardData>(`/family/residents/aino/board?lang=${locale}`),api<{items:Notice[]}>('/family/residents/aino/family-events')]);if(active&&navigator.onLine){setData({board,notices:events.items});setFailed(false);}}catch{if(active)hide();}};
 setData(null);void read();const timer=setInterval(()=>void read(),5000);window.addEventListener('offline',hide);window.addEventListener('online',read);
 return()=>{active=false;clearInterval(timer);window.removeEventListener('offline',hide);window.removeEventListener('online',read);};},[locale]);
 const message=useCareMessage(data?.board??null);
 const overview=data?dailyOverview(data.board,message.now):null;
 const next=data?.notices.filter(n=>n.status==='scheduled'&&Date.parse(n.starts_at)>=Date.now()).sort((a,b)=>Date.parse(a.starts_at)-Date.parse(b.starts_at))[0];
 const date=(value:string)=>new Date(value).toLocaleDateString(languageLocales[language],{month:'long',day:'numeric',timeZone:'Europe/Helsinki'});
 return <div className="guardian-home" data-testid="guardian-home"><section className="home-hero"><div className="home-person"><Avatar actor="aino" name="Helmi Nieminen" size="lg"/><div><p className="eyebrow">{name} · {tr('보호자')}</p><h1>{familyResidentLabel(originalFamilyIdentity,language)}</h1><p>{tr('나에게 공유된 소식만 모았어요.')}</p></div></div>{isXdDesign&&<p className="home-status-counts">{tr('미확인 안내')}: {data?data.notices.filter(n=>!n.acknowledged_at).length:'—'} · {tr('답변 대기')}: {questionsReady?questions.filter(q=>!q.answer_available).length:'—'}</p>}<Link className="home-detail-link" data-testid="guardian-detail-link" to="/family/residents/aino/details">{tr('상세보기')} →</Link></section>

 <div className="home-summary"><section className="home-latest"><span className="home-card-symbol" aria-hidden="true"><Sun size={26}/></span><h2>{tr('최근 안부')}</h2>{failed?<p role="alert">{tr('연결 또는 권한을 확인하세요. 알림은 숨겨졌습니다.')}</p>:!data?<p role="status">{tr('불러오는 중…')}</p>:<><strong>{message.title}</strong>{isAiSummary(data.board)&&<p>{tr('AI가 기간별 기록을 정리한 안부입니다. 직원 검토 후 공유됐습니다.')}</p>}{message.next&&<p>{message.next}</p>}{overview?.newest&&<p className="latest-quote">{overview.newest.statement}<small>{tr(overview.newest.claim_type==='plan'?'Suunnitelma — ei toteutunut':overview.newest.claim_type==='staff_observation'?'Hoitajan havainto':overview.newest.claim_type)}</small></p>}<p>{overview?.newest?`${tr('최근 기록')}: ${date(overview.newest.observed_at)}`:tr(data.board.language_state==='unavailable'?'선택한 언어로 전달된 소식이 없습니다.':'이 항목은 아직 전달된 소식이 없습니다.')}</p></>}</section>
 <section className="home-care"><div className="home-care-heading"><h2>{tr('공유된 관리 항목')}</h2><Link to="/family/residents/aino/details">{tr('상세보기')} →</Link></div><div className="home-care-grid">{data?.board.tiles.filter(t=>t.display_state!=='not_shared').map(tile=>{const info=careTopics.find(t=>t.key===tile.topic);if(!info)return null;const Icon=info.Icon;const latest=data.board.language_state==='available'?[...tile.items].sort((a,b)=>Date.parse(b.observed_at)-Date.parse(a.observed_at))[0]:undefined;return <Link className="home-care-tile" style={{background:info.tint,borderColor:info.color}} key={tile.topic} to="/family/residents/aino/details"><Icon size={26} weight="duotone" aria-hidden="true"/><div><h3>{tr(info.label)}</h3><span className="mobile-care-count">{tile.items.length} · {tr('기록 건수')}</span>{latest&&<p>{latest.statement}</p>}<TopicMessage topic={tile.topic} now={message.now} item={latest} unavailable={data.board.language_state==='unavailable'}/>{latest&&<small>{date(latest.observed_at)} · {tr(latest.claim_type==='plan'?'Suunnitelma — ei toteutunut':latest.claim_type==='staff_observation'?'Hoitajan havainto':latest.claim_type)}</small>}</div></Link>;})}</div></section>
 <section><span className="home-card-symbol" aria-hidden="true"><CalendarBlank size={26}/></span><h2>{tr('미확인 안내')}</h2><strong className="home-number">{data?data.notices.filter(n=>!n.acknowledged_at).length:'—'}</strong><p>{next?`${date(next.starts_at)} · ${next.title}`:data?tr('예정된 안내가 없습니다.'):failed?'—':tr('불러오는 중…')}</p></section>
 <section><span className="home-card-symbol" aria-hidden="true"><ChatCircle size={26}/></span><h2>{tr('답변 대기')}</h2><strong className="home-number">{questionsReady?questions.filter(q=>!q.answer_available).length:'—'}</strong><p>{tr('문의와 간호사 답글은 상세보기에서 확인하세요.')}</p></section></div>

 {isXdDesign&&<DashboardCharts role="family" compact/>}
 <KideFamily subject="aino"/>
 <DeliverySchedule family/>

 <p className="home-footnote">{tr('안부 원문·어제와 비교·기간 조회·가족확인사항은 상세보기에서 볼 수 있어요.')}</p></div>;
}
