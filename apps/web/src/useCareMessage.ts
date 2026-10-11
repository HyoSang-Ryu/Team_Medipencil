import {useEffect,useState} from 'react';
import {useQuery} from '@tanstack/react-query';
import {api} from './api';
import {careMessage,type DeliveryTiming} from './careMessage';
import {dailyOverview,type BoardData} from './dailyUpdate';
import {useUiLanguage,languageLocales} from './UiLanguage';
export function useCareMessage(board:BoardData|null){
 const {tr,language}=useUiLanguage();const [now,setNow]=useState(()=>new Date());
 useEffect(()=>{const tick=()=>setNow(new Date());const timer=setInterval(tick,10000);document.addEventListener('visibilitychange',tick);return()=>{clearInterval(timer);document.removeEventListener('visibilitychange',tick);};},[]);
 const query=useQuery({queryKey:['delivery-schedules',true],queryFn:()=>api<DeliveryTiming>('/family/residents/aino/delivery-schedule').then(s=>({items:[s]})),refetchInterval:10000});
 const schedule=!query.isError&&navigator.onLine?query.data?.items[0]:undefined;
 const overview=board?dailyOverview(board,now):null;
 const title=board?.language_state==='unavailable'?tr('선택한 언어로 전달된 소식이 없습니다.'):board&&!board.tiles.some(t=>t.display_state!=='not_shared')?tr('현재 공유된 항목이 없습니다.'):tr(careMessage(overview?.hasToday??false,now,schedule));
 const next=schedule?.enabled&&schedule.next_run_at&&Date.parse(schedule.next_run_at)>now.getTime()?`${tr('다음 전달')}: ${new Date(schedule.next_run_at).toLocaleString(languageLocales[language],{timeZone:'Europe/Helsinki'})} · ${tr('핀란드 시간 · 새 내용이 있을 때만 전달')}`:null;
 return {now,title,next};
}
