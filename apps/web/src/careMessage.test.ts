import {expect,it} from 'vitest';
import {careMessage} from './careMessage';
it('changes at Helsinki 18:00 in summer and winter without promising delivery',()=>{
 for(const [before,after] of [['2026-10-11T14:59:59Z','2026-10-11T15:00:00Z'],['2026-12-11T15:59:59Z','2026-12-11T16:00:00Z']]){
  expect(careMessage(false,new Date(before))).toBe('오늘 소식은 아직 전달되지 않았어요.');
  expect(careMessage(false,new Date(after))).toBe('현재까지 전달된 오늘 소식이 없어요.');
 }
});
it('announces only a confirmed enabled future schedule today',()=>{
 const now=new Date('2026-10-11T14:00:00Z');const schedule={enabled:true,next_run_at:'2026-10-11T15:00:00Z'};
 expect(careMessage(false,now,schedule)).toContain('새 내용이 있으면');
 for(const s of [{...schedule,enabled:false},{...schedule,next_run_at:null},{...schedule,next_run_at:'2026-10-12T15:00:00Z'}])expect(careMessage(false,now,s)).toBe('오늘 소식은 아직 전달되지 않았어요.');
 expect(careMessage(false,new Date(schedule.next_run_at),schedule)).toBe('현재까지 전달된 오늘 소식이 없어요.');
 expect(careMessage(true,now,schedule)).toBe('오늘의 기록이 공유됐어요.');
});
it('returns to today pending after Helsinki midnight',()=>{
 expect(careMessage(false,new Date('2026-10-11T21:00:00Z'))).toBe('오늘 소식은 아직 전달되지 않았어요.');
});
