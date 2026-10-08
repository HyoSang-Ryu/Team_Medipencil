import {describe,it,expect} from 'vitest';
import {careDay,dailyOverview,type BoardData} from './dailyUpdate';
const empty:BoardData={subject:{subject_id:'aino',display_name:'Aino'},viewer:{actor_id:'liisa',display_name:'Liisa'},lang:'fi',display_timezone:'Europe/Helsinki',board_state:'empty',language_state:'available',tiles:[],answers:[],publication_id:null,published_at:null,can_ask:true,execution:{}};
describe('daily update dates and evidence',()=>{
 it('uses Helsinki days across UTC midnight and month boundaries',()=>{
  expect(careDay('2026-09-30T22:30:00Z')).toBe('2026-10-01');
  expect(dailyOverview(empty,new Date('2026-09-30T22:30:00Z')).dates).toEqual(['2026-09-29','2026-09-30','2026-10-01']);
 });
 it('never treats a publication today as an observation today or invents a positive state',()=>{
  const board:BoardData={...empty,published_at:'2026-10-08T09:00:00Z',tiles:[{topic:'outdoors',display_state:'available',items:[{item_id:'one',topic:'outdoors',statement:'A walk is planned.',claim_type:'plan',status:'none',observed_at:'2026-10-07T10:00:00Z',action_status:'planned',evidence_handle:'one'}]}]};
  const result=dailyOverview(board,new Date('2026-10-08T12:00:00Z'));
  expect(result.hasToday).toBe(false);expect(result.days[1].topics).toEqual(['outdoors']);expect(result.days[2].topics).toEqual([]);
  expect(result.newest?.claim_type).toBe('plan');
  expect(dailyOverview({...board,language_state:'unavailable'},new Date('2026-10-08T12:00:00Z')).newest).toBeUndefined();
 });
});

import {compareCareDays} from './dailyUpdate';
it('compares current permitted originals without turning plans or missing entries into outcomes',()=>{
 const item=(id:string,date:string,statement:string)=>({item_id:id,topic:'meals',statement,status:'none' as const,claim_type:'plan' as const,observed_at:date,action_status:'planned' as const,evidence_handle:id});
 const board:BoardData={...empty,tiles:[{topic:'meals',display_state:'available',items:[item('a','2026-10-07T10:00:00Z','Plan yesterday'),item('b','2026-10-08T10:00:00Z','Plan today')]},{topic:'sleep',display_state:'available',items:[{...item('c','2026-10-07T10:00:00Z','Reported sleep'),'topic':'sleep'}]},{topic:'medication',display_state:'not_shared',items:[item('hidden','2026-10-08T10:00:00Z','Must not compare')]}]};
 const rows=compareCareDays(board,new Date('2026-10-08T12:00:00Z'));
 expect(rows.map(r=>r.topic)).toEqual(['meals','sleep']);expect(rows[0].today?.statement).toBe('Plan today');expect(rows[0].today?.claim_type).toBe('plan');expect(rows[1].today).toBeUndefined();expect(compareCareDays({...board,language_state:'unavailable'})).toEqual([]);
});
