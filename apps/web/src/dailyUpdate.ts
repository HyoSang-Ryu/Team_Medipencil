import type {components} from './generated-api';
export type BoardData=components['schemas']['FamilyBoardDTO'];
export const careDay=(date:string|Date)=>new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Helsinki',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(date));
export function dailyOverview(board:BoardData,now=new Date(),selectedDates?:string[]){
 const today=careDay(now);
 const dates=selectedDates??[2,1,0].map(offset=>{const day=new Date(today+'T12:00:00Z');day.setUTCDate(day.getUTCDate()-offset);return day.toISOString().slice(0,10);});
 const items=board.language_state==='available'?board.tiles.flatMap(t=>t.items):[];
 const newest=[...items].sort((a,b)=>new Date(b.observed_at).getTime()-new Date(a.observed_at).getTime())[0];
 return {today,dates,newest,hasToday:items.some(i=>careDay(i.observed_at)===today),days:dates.map(date=>({date,topics:board.tiles.filter(t=>board.language_state==='available'&&t.items.some(i=>careDay(i.observed_at)===date)).map(t=>t.topic)}))};
}

// Compare only items already filtered by the server's current publication/consent checks.
export function compareCareDays(board:BoardData,now=new Date()){
 const today=careDay(now);const previous=new Date(today+'T12:00:00Z');previous.setUTCDate(previous.getUTCDate()-1);const yesterday=previous.toISOString().slice(0,10);
 if(board.language_state!=='available')return [];
 return board.tiles.filter(t=>t.display_state!=='not_shared').map(t=>{
  const latestFor=(day:string)=>t.items.filter(i=>careDay(i.observed_at)===day).sort((a,b)=>Date.parse(b.observed_at)-Date.parse(a.observed_at))[0];
  return {topic:t.topic,today:latestFor(today),yesterday:latestFor(yesterday)};
 }).filter(row=>row.today||row.yesterday);
}
