export type DailyRow=Record<string,unknown>;
export function latestPair(rows:DailyRow[],today:string){
 const sorted=rows.filter(r=>typeof r.date==='string'&&/^2026-\d{2}-\d{2}$/.test(r.date)&&r.date<=today&&!r.future_scenario).sort((a,b)=>String(a.date).localeCompare(String(b.date)));
 return {latest:sorted.at(-1),previous:sorted.at(-2)};
}
export function numericChange(latest:DailyRow,previous:DailyRow|undefined,key:string,factor=1){
 const value=latest[key],before=previous?.[key];
 if(typeof value!=='number'||!Number.isFinite(value))return {value:null,delta:null};
 return {value:value*factor,delta:typeof before==='number'&&Number.isFinite(before)?Math.round((value-before)*factor*100)/100:null};
}
// Only explicit source labels are classified. A larger measurement is not automatically better.
export function recordedStatus(value:unknown):'good'|'normal'|'poor'|'unknown'{
 if(typeof value!=='string')return 'unknown';
 const s=value.trim().toLocaleLowerCase('fi');
 if(['hyvä','hyvin','tyytyväinen','good','좋음'].includes(s))return 'good';
 if(['normaali','tavallinen','kohtalainen','normal','보통'].includes(s))return 'normal';
 if(['huono','huonosti','poor','bad','나쁨'].includes(s))return 'poor';
 return 'unknown';
}
