import {BedIcon,DropIcon,PersonSimpleWalkIcon,ForkKnifeIcon,SmileyIcon,UsersIcon} from '@phosphor-icons/react';
import {useUiLanguage} from './UiLanguage';
import {latestPair,numericChange,recordedStatus,type DailyRow} from './dailyStatus';
export function ProvidedOverview({rows,today,onDetails}:{rows:DailyRow[];today:string;onDetails:()=>void}){
 const {language}=useUiLanguage(),t=(ko:string,en:string,fi:string)=>({ko,en,fi}[language]);
 const {latest,previous}=latestPair(rows,today);
 if(!latest)return <p>{t('아직 공유된 생활 기록이 없습니다.','No shared daily records yet.','Ei vielä jaettuja päiväkirjauksia.')}</p>;
 const labels={good:t('좋음','Good','Hyvä'),normal:t('보통','Normal','Normaali'),poor:t('나쁨','Poor','Huono'),unknown:t('판단 기록 없음','Not assessed','Ei arviota')};
 const cards=[
  {key:'sleep_hours',label:t('수면','Sleep','Uni'),unit:'h',factor:1,source:'sleep_quality',Icon:BedIcon},
  {key:'fluids_dl',label:t('수분','Fluids','Nesteet'),unit:'ml',factor:100,source:'',Icon:DropIcon},
  {key:'outdoor_minutes',label:t('야외 활동','Outdoors','Ulkoilu'),unit:'min',factor:1,source:'',Icon:PersonSimpleWalkIcon},
  {key:'breakfast',label:t('식사','Meals','Ruokailu'),unit:'',factor:1,source:'',Icon:ForkKnifeIcon},
  {key:'mood_label',label:t('기분','Mood','Mieliala'),unit:'',factor:1,source:'mood_label',Icon:SmileyIcon},
  {key:'social_interaction',label:t('교류','Social interaction','Vuorovaikutus'),unit:'',factor:1,source:'',Icon:UsersIcon},
 ];
 const visible=cards.filter(c=>c.key in latest||(c.source&&c.source in latest)||(c.key==='breakfast'&&['lunch','dinner'].some(k=>k in latest)));
 const format=(n:number)=>new Intl.NumberFormat(language,{maximumFractionDigits:2}).format(n);
 const move=numericChange(latest,previous,'outdoor_minutes');
 const headline=move.delta!==null&&move.delta!==0?t(`야외 활동이 직전 기록보다 ${format(Math.abs(move.delta))}분 ${move.delta>0?'늘었어요.':'줄었어요.'}`,`Outdoor time ${move.delta>0?'increased':'decreased'} by ${format(Math.abs(move.delta))} minutes.`,`Ulkoilua ${format(Math.abs(move.delta))} minuuttia ${move.delta>0?'enemmän':'vähemmän'} kuin edellisessä kirjauksessa.`):t('가장 최근의 생활 모습을 확인하세요.','See the latest picture of daily life.','Katso arjen viimeisimmät kuulumiset.');
 const translateValue=(v:unknown)=>{const values:Record<string,[string,string,string]>={syöty:['식사함','Ate','syöty'],kohtalainen:['보통','Fair','kohtalainen'],tyytyväinen:['만족','Content','tyytyväinen'],hyvä:['좋음','Good','hyvä'],huono:['나쁨','Poor','huono'],'ruokailu yhteisessä tilassa':['공용 공간에서 식사','Meal in a shared space','ruokailu yhteisessä tilassa']};const a=values[String(v)];return a?t(...a):String(v??empty);};
 const empty=t('기록 없음','Not recorded','Ei kirjausta');
 return <section className="provided-overview" data-testid="provided-overview">
 <div className="provided-latest"><span>{t('마지막 기록 기준','Latest recorded update','Viimeisimmän kirjauksen mukaan')} · {String(latest.date)}</span><h2>{headline}</h2><p>{previous?t('비교 기록','Compared with','Vertailukirjaus')+' · '+String(previous.date):t('이전 기록이 없어 아직 비교할 수 없습니다.','No previous record to compare.','Ei aiempaa vertailukirjausta.')}</p>{latest.date!==today&&<p>{t('오늘 기록은 아직 없습니다. 아래는 마지막 기록이며 현재 상태를 뜻하지 않습니다.','No record for today yet. These are the latest records, not a live status.','Tältä päivältä ei ole kirjausta. Alla ovat viimeisimmät tiedot, eivät reaaliaikainen tila.')}</p>}</div>
 <div className="provided-status-list">{visible.map(({key,label,unit,factor,source,Icon})=>{
 const status=recordedStatus(source?latest[source]:undefined),change=numericChange(latest,previous,key,factor);
 const value=unit?(change.value===null?empty:`${format(change.value)} ${unit}`):key==='breakfast'?['breakfast','lunch','dinner'].filter(k=>k in latest).map(k=>({breakfast:t('아침','Breakfast','Aamu'),lunch:t('점심','Lunch','Lounas'),dinner:t('저녁','Dinner','Ilta')}[k])+': '+translateValue(latest[k])).join(' · '):translateValue(latest[key]);
 const delta=unit?(change.delta===null?t('비교 자료 없음','No comparison','Ei vertailutietoa'):change.delta===0?t('±0 · 변화 없음','±0 · Unchanged','±0 · Ennallaan'):`${change.delta>0?'+':'−'}${format(Math.abs(change.delta))} ${unit}`):previous&&latest[key]!=null&&previous[key]!=null?(latest[key]===previous[key]?t('변화 없음','Unchanged','Ennallaan'):t('기록 변경','Record changed','Kirjaus muuttunut')):t('비교 자료 없음','No comparison','Ei vertailutietoa');
 return <button className="provided-status-card" key={key} onClick={onDetails}><Icon size={28} aria-hidden/><span className="provided-status-copy"><strong>{label}</strong><span>{value}</span>{source&&source!==key&&status==='unknown'&&latest[source]!=null&&<small>{translateValue(latest[source])}</small>}<small>{delta}</small></span><span className={'provided-state '+status}>{value===empty?empty:status!=='unknown'?labels[status]:unit&&change.delta!==null?(change.delta===0?t('유지','Stable','Ennallaan'):change.delta>0?t('증가','Increased','Lisääntynyt'):t('감소','Decreased','Vähentynyt')):t('기록 확인','Recorded','Kirjattu')}</span></button>;
 })}</div><p className="muted overview-key">{t('좋음·보통·나쁨은 기록에 명시된 평가입니다. +/−는 수치 변화이며 건강의 호전·악화를 뜻하지 않습니다.','Good/normal/poor reflect explicit recorded assessments. +/− shows measurement changes, not health improvement or decline.','Hyvä/normaali/huono perustuvat kirjattuun arvioon. +/− kertoo arvon muutoksen, ei terveyden paranemisesta tai heikkenemisestä.')}</p><button className="overview-details" onClick={onDetails}>{t('기간별 그래프·상세 기록 보기','View trends and detailed records','Katso trendit ja kirjaukset')} →</button>
 </section>;
}
