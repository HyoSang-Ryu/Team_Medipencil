import {uiText} from './UiLanguage';
import {BedIcon,DropIcon,PersonSimpleWalkIcon,ForkKnifeIcon,SmileyIcon,UsersIcon,ArrowUpIcon,ArrowDownIcon,MinusIcon,QuestionMarkIcon} from '@phosphor-icons/react';
import {useUiLanguage} from './UiLanguage';
import {latestPair,numericChange,recordedStatus,type DailyRow} from './dailyStatus';
export function ProvidedOverview({rows,today,onDetails}:{rows:DailyRow[];today:string;onDetails:(topic?:string)=>void}){
 const {language}=useUiLanguage(),t=(ko:string,en:string,fi:string)=>uiText(language,ko,en,fi);
 const {latest,previous}=latestPair(rows,today);
 if(!latest)return <p>{t('아직 공유된 생활 기록이 없습니다.','No shared daily records yet.','Ei vielä jaettuja päiväkirjauksia.')}</p>;

 const cards=[
  {key:'sleep_hours',label:t('수면','Sleep','Uni'),unit:'h',factor:1,source:'sleep_quality',Icon:BedIcon},
  {key:'fluids_dl',label:t('수분','Fluids','Nesteet'),unit:'ml',factor:100,source:'',Icon:DropIcon},
  {key:'outdoor_minutes',label:t('야외 활동','Outdoors','Ulkoilu'),unit:'min',factor:1,source:'',Icon:PersonSimpleWalkIcon},
  {key:'breakfast',label:t('식사','Meals','Ruokailu'),unit:'',factor:1,source:'',Icon:ForkKnifeIcon},
  {key:'mood_label',label:t('기분','Mood','Mieliala'),unit:'',factor:1,source:'mood_label',Icon:SmileyIcon},
  {key:'social_interaction',label:t('교류','Social interaction','Vuorovaikutus'),unit:'',factor:1,source:'',Icon:UsersIcon,ArrowUpIcon,ArrowDownIcon,MinusIcon,QuestionMarkIcon},
 ];
 const visible=cards.filter(c=>c.key in latest||(c.source&&c.source in latest)||(c.key==='breakfast'&&['lunch','dinner'].some(k=>k in latest)));
 const format=(n:number)=>new Intl.NumberFormat(language,{maximumFractionDigits:2}).format(n);
 const move=numericChange(latest,previous,'outdoor_minutes');
 const headline=move.delta!==null&&move.delta!==0?t(`야외 활동이 직전 기록보다 ${move.delta>0?'늘었어요.':'줄었어요.'}`,`Outdoor time ${move.delta>0?'increased':'decreased'} compared with the previous record.`,`Ulkoilua ${move.delta>0?'enemmän':'vähemmän'} kuin edellisessä kirjauksessa.`):t('가장 최근의 생활 모습을 확인하세요.','See the latest picture of daily life.','Katso arjen viimeisimmät kuulumiset.');
 const translateValue=(v:unknown)=>{const values:Record<string,[string,string,string]>={syöty:['식사함','Ate','syöty'],kohtalainen:['보통','Fair','kohtalainen'],tyytyväinen:['만족','Content','tyytyväinen'],hyvä:['좋음','Good','hyvä'],huono:['나쁨','Poor','huono'],'ruokailu yhteisessä tilassa':['공용 공간에서 식사','Meal in a shared space','ruokailu yhteisessä tilassa']};const a=values[String(v)];return a?t(...a):String(v??empty);};
 const empty=t('기록 없음','Not recorded','Ei kirjausta');
 return <section className="provided-overview" data-testid="provided-overview">
 <div className="provided-latest"><span>{t('마지막 기록 기준','Latest recorded update','Viimeisimmän kirjauksen mukaan')} · {String(latest.date)}</span><h2>{headline}</h2><p>{previous?t('비교 기록','Compared with','Vertailukirjaus')+' · '+String(previous.date):t('이전 기록이 없어 아직 비교할 수 없습니다.','No previous record to compare.','Ei aiempaa vertailukirjausta.')}</p>{latest.date!==today&&<p>{t('오늘 기록은 아직 없습니다. 아래는 마지막 기록이며 현재 상태를 뜻하지 않습니다.','No record for today yet. These are the latest records, not a live status.','Tältä päivältä ei ole kirjausta. Alla ovat viimeisimmät tiedot, eivät reaaliaikainen tila.')}</p>}</div>
 <div className="provided-status-list">{visible.map(({key,label,unit,factor,source,Icon})=>{
 const status=recordedStatus(source?latest[source]:undefined),change=numericChange(latest,previous,key,factor);
 const value=unit?(change.value===null?empty:`${format(change.value)} ${unit}`):key==='breakfast'?['breakfast','lunch','dinner'].filter(k=>k in latest).map(k=>({breakfast:t('아침','Breakfast','Aamu'),lunch:t('점심','Lunch','Lounas'),dinner:t('저녁','Dinner','Ilta')}[k])+': '+translateValue(latest[k])).join(' · '):translateValue(latest[key]);
 const ranks={poor:0,normal:1,good:2};
 const beforeStatus=recordedStatus(source?previous?.[source]:undefined);
 const comparison=unit?change.delta:status!=='unknown'&&beforeStatus!=='unknown'?ranks[status]-ranks[beforeStatus]:previous&&(key==='breakfast'?['breakfast','lunch','dinner'].filter(k=>k in latest).every(k=>latest[k]!=null&&previous[k]!=null&&latest[k]===previous[k]):latest[key]!=null&&previous[key]!=null&&latest[key]===previous[key])?0:null;
 const direction=comparison===null?'unknown':comparison>0?'up':comparison<0?'down':'same';
 const TrendIcon={up:ArrowUpIcon,down:ArrowDownIcon,same:MinusIcon,unknown:QuestionMarkIcon}[direction];
 const trendLabel={up:t('이전 기록보다 상승','Up from previous record','Noussut edellisestä kirjauksesta'),down:t('이전 기록보다 하락','Down from previous record','Laskenut edellisestä kirjauksesta'),same:t('변화 없음','Unchanged','Ennallaan'),unknown:t('비교 자료 없음','No comparison','Ei vertailutietoa')}[direction];

 return <button className="provided-status-card" key={key} onClick={()=>onDetails(key)}><Icon size={28} aria-hidden/><span className="provided-status-copy"><strong>{label}</strong><span>{value}</span>{source&&source!==key&&latest[source]!=null&&<small>{translateValue(latest[source])}</small>}</span><span className="provided-status-end"><span className={'provided-trend '+direction} role="img" aria-label={trendLabel} title={trendLabel}><TrendIcon size={28} weight="bold" aria-hidden/></span></span></button>;
 })}</div><p className="muted overview-key">{t('화살표는 이전 기록과의 변화입니다. 건강의 호전·악화를 뜻하지 않습니다. 자세한 수치는 상세 기록에서 확인하세요.','Arrows compare with the previous record, not health improvement or decline. See detailed records for values.','Nuolet kuvaavat muutosta edelliseen kirjaukseen, eivät terveyden paranemista tai heikkenemistä. Tarkat arvot löytyvät kirjauksista.')}</p><button className="overview-details" onClick={()=>onDetails()}>{t('기간별 그래프·상세 기록 보기','View trends and detailed records','Katso trendit ja kirjaukset')} →</button>
 </section>;
}
