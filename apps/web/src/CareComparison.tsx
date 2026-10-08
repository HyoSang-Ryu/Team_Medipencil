import {useUiLanguage,languageLocales} from './UiLanguage';
import {compareCareDays,type BoardData} from './dailyUpdate';
const names:Record<string,string>={meals:'Ruokailu',medication:'Lääkitys',movement:'Liikkuminen',outdoors:'Ulkoilu',sleep:'Uni',care_contact:'Yhteydenotto'};
export function CareComparison({board,now,onAsk,onEvidence}:{board:BoardData;now:Date;onAsk:(text:string)=>void;onEvidence:(id:string)=>void}){
 const {tr,language}=useUiLanguage();const rows=compareCareDays(board,now);const paired=rows.filter(r=>r.today&&r.yesterday);
 const missingToday=rows.filter(r=>!r.today);
 const sentence=(key:string,topics:string[])=>tr(key).replace('{topics}',topics.map(t=>tr(names[t])).join(', '));
 return <div className="care-comparison" id="day-comparison"><h2>{tr('어제와 비교해 무엇이 달라졌나요?')}</h2>
 {paired.length>0&&<p className="comparison-lead">{sentence('{topics}: 어제와 오늘의 내용을 함께 확인할 수 있어요.',paired.map(r=>r.topic))}</p>}
 {missingToday.length>0&&<p>{sentence('{topics}: 오늘 기록은 아직 공유되지 않았어요.',missingToday.map(r=>r.topic))}</p>}
 {rows.length===0?<p>{tr('어제와 오늘의 공개된 안부를 기다리고 있어요.')}</p>:rows.map(row=><details key={row.topic} open={paired[0]?.topic===row.topic} className="comparison-item"><summary>{tr(names[row.topic])} · {tr(row.today&&row.yesterday?'어제·오늘 비교':row.today?'오늘 새로 공유된 기록':'오늘 기록 대기')}</summary><div className="comparison-pair">{(['yesterday','today'] as const).map(day=><div key={day}><h3>{tr(day==='today'?'오늘':'어제')}</h3>{row[day]?<><time dateTime={row[day].observed_at}>{new Date(row[day].observed_at).toLocaleDateString(languageLocales[language],{timeZone:'Europe/Helsinki'})}</time><blockquote>{tr(day==='today'?'오늘':'어제')}: {row[day].statement}</blockquote><small>{tr(row[day].claim_type==='plan'||row[day].claim_type==='contact_plan'?'계획 · 실행 확인 전':'공개된 기록 원문')}</small><button onClick={()=>onEvidence(row[day]!.item_id)}>{tr('Näytä lähde')}</button></>:<p>{tr('이 날짜에 공개된 기록이 없습니다.')}</p>}</div>)}</div><button className="comparison-ask" onClick={()=>onAsk(tr('{topic} 기록에서 어제와 오늘 달라진 점을 알려주세요.').replace('{topic}',tr(names[row.topic])))}>{tr('이 항목을 간호사에게 질문')}</button></details>)}
 <p className="muted">{tr('공개된 기록을 나란히 보여드립니다. 변화의 의미가 궁금하면 간호사에게 질문하세요.')}</p>
 </div>;
}
