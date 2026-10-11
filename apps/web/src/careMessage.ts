import {careDay} from './dailyUpdate';
export type DeliveryTiming={enabled:boolean;next_run_at:string|null};
export function careMessage(hasToday:boolean,now:Date,schedule?:DeliveryTiming){
 if(hasToday)return '오늘의 기록이 공유됐어요.';
 if(schedule?.enabled&&schedule.next_run_at){
  const next=new Date(schedule.next_run_at);
  if(next.getTime()>now.getTime()&&careDay(next)===careDay(now))return '오늘 소식은 정기 전달 시간에 새 내용이 있으면 도착해요.';
 }
 const hour=Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Helsinki',hour:'2-digit',hourCycle:'h23'}).format(now));
 return hour<18?'오늘 소식은 아직 전달되지 않았어요.':'현재까지 전달된 오늘 소식이 없어요.';
}
