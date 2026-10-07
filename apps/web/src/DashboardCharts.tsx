import {useEffect,useState} from 'react';
import {DateRange,recentPeriod} from './DateRange';
import {api} from './api';
import {ForkKnife,Pill,PersonSimpleWalk,Tree,Bed,ChatCircle} from '@phosphor-icons/react';
import {useUiLanguage,languageLocales} from './UiLanguage';
type Topic={topic:string;shared:boolean;total:number|null;daily:(number|null)[]};
type Data={dates:string[];topics:Topic[];basis:string};
const names:Record<string,string>={meals:'Ruokailu',medication:'Lääkitys',movement:'Liikkuminen',outdoors:'Ulkoilu',sleep:'Uni',care_contact:'Yhteydenotto'};
const icons=[ForkKnife,Pill,PersonSimpleWalk,Tree,Bed,ChatCircle];
const palette=['#aa5b08','#3267bf','#24785a','#638133','#7958bd','#bc486b'];
const tints=['#fff4e6','#edf4ff','#eaf6ef','#f2f6e6','#f2edff','#fff0f4'];
const point=(i:number,r:number)=>[180+Math.sin(i*Math.PI/3)*r,160-Math.cos(i*Math.PI/3)*r];
const polygon=(r:number)=>Array.from({length:6},(_,i)=>point(i,r).join(',')).join(' ');
export function DashboardCharts({role}:{role:string}){
 const [period,setPeriod]=useState(()=>recentPeriod(7));
 const {tr,language}=useUiLanguage();const [data,setData]=useState<Data|null>(null),[failed,setFailed]=useState(false),[selected,setSelected]=useState('all');
 useEffect(()=>{let active=true;const hide=()=>{setData(null);setFailed(true);};
 setData(null);
 async function read(){try{const result=await api<Data>(`/${role}/residents/aino/dashboard?start_date=${period.start}&end_date=${period.end}`);if(active&&navigator.onLine){setData(result);setFailed(false);}}catch{if(active)hide();}}
 void read();const timer=setInterval(()=>void read(),5000);window.addEventListener('offline',hide);window.addEventListener('online',read);
 return()=>{active=false;clearInterval(timer);window.removeEventListener('offline',hide);window.removeEventListener('online',read);};},[role,period.start,period.end]);
 const format=(date:string)=>new Intl.DateTimeFormat(languageLocales[language],{month:'numeric',day:'numeric',timeZone:'Europe/Helsinki'}).format(new Date(date+'T12:00:00Z'));
 const topic=data?.topics.find(t=>t.topic===selected);
 const values=data?.dates.map((_,i)=>selected==='all'?(data.topics.some(t=>t.shared)?data.topics.reduce((n,t)=>n+(t.daily[i]??0),0):null):(topic?.daily[i]??null))??[];
 const max=Math.max(1,...(data?.topics.map(t=>t.total??0)??[]));const ymax=Math.max(1,...values.map(n=>n??0));
 const xy=(v:number,i:number)=>`${48+i*420/Math.max(1,(data?.dates.length??1)-1)},${190-v/ymax*150}`;
 return <section className="dashboard-charts" aria-label={tr('돌봄 기록 시각화')}><div className="chart-section-heading"><div><h2>{tr('돌봄 기록 시각화')}</h2><p>{tr('선택 기간 · Europe/Helsinki')}</p></div><span className="badge">{tr('기록 건수')}</span></div><p className="muted">{tr(role==='family'?'현재 나에게 공개된 최신 발행의 기록을 관찰일별로 집계합니다.':'현재 유효한 승인 기록을 관찰일별로 집계합니다.')}</p><p className="muted">{tr('계획도 기록에 포함됩니다. 건수는 건강 점수나 돌봄 완료율이 아닙니다.')}</p>
 <DateRange value={period} onChange={p=>{setData(null);setPeriod(p);}}/>
 {failed?<p role="alert">{tr('연결 또는 권한을 확인할 수 없어 그래프를 숨겼습니다.')}</p>:!data?<p role="status">{tr('기록을 불러오는 중…')}</p>:<><div className="care-topic-cards">{data.topics.map((t,i)=>{const Icon=icons[i];return <button key={t.topic} className="care-topic-card" aria-pressed={selected===t.topic} onClick={()=>setSelected(selected===t.topic?'all':t.topic)} style={{background:tints[i],borderColor:selected===t.topic?palette[i]:'transparent'}}><span className="care-topic-icon" style={{color:palette[i]}}><Icon size={30} weight="fill" aria-hidden="true"/></span><span className="care-topic-copy"><strong>{tr(names[t.topic])}</strong><span>{t.shared?`${t.total} · ${tr('기록 건수')}`:tr('비공유')}</span></span>{data.dates.length<=7&&<span className="care-mini-bars" aria-hidden="true">{t.daily.map((v,j)=><span key={j} style={{height:v===null?'3px':`${4+(v/Math.max(1,...t.daily.map(n=>n??0)))*20}px`,background:v===null?'var(--input-border)':palette[i],opacity:v?1:.25}}/>)}</span>}</button>;})}</div><div className="chart-grid"><div className="chart-panel"><h3>{tr('6개 관리 항목')}</h3><svg className="radar-chart" viewBox="0 0 360 320" role="img" aria-label={tr('항목별 선택 기간 기록 건수')}>
 {[.25,.5,.75,1].map(r=><polygon key={r} points={polygon(100*r)} fill="none" stroke="var(--border)"/>)}
 {data.topics.map((t,i)=>{const [x,y]=point(i,100),[lx,ly]=point(i,132);return <g key={t.topic}><line x1="180" y1="160" x2={x} y2={y} stroke="var(--border)"/><text x={lx} y={ly-4} textAnchor="middle" className="chart-label">{tr(names[t.topic])}</text><text x={lx} y={ly+14} textAnchor="middle" className="chart-number">{t.shared?t.total:tr('비공유')}</text></g>;})}
 {data.topics.every(t=>t.shared)&&<polygon points={data.topics.map((t,i)=>point(i,(t.total??0)/max*100).join(',')).join(' ')} fill="var(--primary)" fillOpacity=".14" stroke="var(--primary)" strokeWidth="2"/>}
 {data.topics.filter(t=>t.shared).map(t=>{const i=data.topics.indexOf(t),[x,y]=point(i,(t.total??0)/max*100);return <circle key={t.topic} cx={x} cy={y} r="4" fill="var(--primary)"><title>{tr(names[t.topic])}: {t.total}</title></circle>;})}</svg><p className="muted">{tr('바깥 눈금')}: {max} · {tr('0 = 해당 기간 기록 없음 · 비공유 = 집계 제외')}</p></div>
 <div className="chart-panel"><h3>{tr('선택 기간의 기록 변화')}</h3><label className="chart-filter">{tr('그래프 항목')}<select value={selected} onChange={e=>setSelected(e.target.value)}><option value="all">{tr('공개 가능 항목 전체')}</option>{data.topics.map(t=><option key={t.topic} value={t.topic}>{tr(names[t.topic])}{t.shared?'':` (${tr('비공유')})`}</option>)}</select></label>
 {values.every(v=>v===null)?<p className="chart-empty">{tr('공유되지 않은 항목입니다.')}</p>:<svg className="trend-chart" viewBox="0 0 510 240" role="img" aria-label={tr('날짜별 기록 건수')}>
 {(ymax===1?[0,1]:[0,.5,1]).map(f=><g key={f}><line x1="48" y1={190-f*150} x2="468" y2={190-f*150} stroke="var(--border)"/><text x="36" y={195-f*150} textAnchor="end" className="chart-label">{Number((ymax*f).toFixed(1))}</text></g>)}
 <polyline points={values.map((v,i)=>xy(v??0,i)).join(' ')} fill="none" stroke="var(--primary)" strokeWidth="3"/>
 {values.map((v,i)=><g key={data.dates[i]}><circle cx={48+i*420/Math.max(1,(data?.dates.length??1)-1)} cy={190-(v??0)/ymax*150} r="4" fill="var(--primary)"><title>{data.dates[i]}: {v}</title></circle><text style={{display:data.dates.length>14?'none':undefined}} x={48+i*420/Math.max(1,(data?.dates.length??1)-1)} y={180-(v??0)/ymax*150} textAnchor="middle" className="chart-number">{v}</text><text style={{display:data.dates.length>7&&i!==data.dates.length-1&&i%Math.ceil(data.dates.length/6)!==0?'none':undefined}} x={48+i*420/Math.max(1,(data?.dates.length??1)-1)} y="225" textAnchor="middle" className={`chart-label date-label date-${i}`}>{format(data.dates[i])}</text></g>)}</svg>}
 <p className="muted">{tr('기록이 없다는 뜻이며 상태 악화나 활동 미실시를 뜻하지 않습니다.')}</p></div></div>
 <details className="chart-table"><summary>{tr('날짜별 수치 보기')}</summary><div className="chart-table-scroll"><table><caption>{tr('항목별 선택 기간 기록 건수')}</caption><thead><tr><th>{tr('그래프 항목')}</th>{data.dates.map(d=><th key={d}>{format(d)}</th>)}</tr></thead><tbody>{data.topics.map(t=><tr key={t.topic}><th>{tr(names[t.topic])}</th>{t.daily.map((n,i)=><td key={i}>{n??tr('비공유')}</td>)}</tr>)}</tbody></table></div></details></>}
 </section>;
}
