import {useState} from 'react';
import {useUiLanguage} from './UiLanguage';
import {careDay} from './dailyUpdate';
export type Period={start:string;end:string};
export function recentPeriod(days:number):Period{const end=careDay(new Date());const d=new Date(end+'T12:00:00Z');d.setUTCDate(d.getUTCDate()-days+1);return {start:d.toISOString().slice(0,10),end};}
export function periodDates(p:Period){const start=Date.parse(p.start+'T12:00:00Z'),end=Date.parse(p.end+'T12:00:00Z');const count=(end-start)/86400000+1;if(!Number.isInteger(count)||count<1||count>90||p.end>careDay(new Date()))return [];return Array.from({length:count},(_,i)=>new Date(start+i*86400000).toISOString().slice(0,10));}
export function DateRange({value,onChange}:{value:Period;onChange:(p:Period)=>void}){
 const {tr}=useUiLanguage();const [draft,setDraft]=useState(value);const valid=periodDates(draft).length>0;
 function apply(p:Period){setDraft(p);onChange(p);}
 return <div className="date-range"><div className="date-presets">{[3,7,30].map(n=><button type="button" key={n} aria-pressed={JSON.stringify(value)===JSON.stringify(recentPeriod(n))} onClick={()=>apply(recentPeriod(n))}>{tr('최근 일수').replace('{days}',String(n))}</button>)}</div><div className="date-inputs"><label>{tr('시작일')}<input type="date" max={careDay(new Date())} value={draft.start} onChange={e=>setDraft({...draft,start:e.target.value})}/></label><label>{tr('종료일')}<input type="date" max={careDay(new Date())} value={draft.end} onChange={e=>setDraft({...draft,end:e.target.value})}/></label><button type="button" disabled={!valid} onClick={()=>apply(draft)}>{tr('기간 적용')}</button></div>{!valid&&<p role="alert">{tr('오늘까지 최대 90일, 시작일이 종료일 이전인 기간을 선택하세요.')}</p>}<p className="muted">{value.start} – {value.end} · Europe/Helsinki</p></div>;
}
