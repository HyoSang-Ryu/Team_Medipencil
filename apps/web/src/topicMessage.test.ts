import {expect,it} from 'vitest';
import {topicExamples,topicMessage,type CareItem} from './careTopicMessages';
const now=new Date('2026-10-11T14:00:00Z');
it('offers seven distinct topic examples, changing after Helsinki 18:00',()=>{
 expect(Object.keys(topicExamples)).toHaveLength(7);
 for(const topic of Object.keys(topicExamples)){
  const before=topicMessage(topic,now),after=topicMessage(topic,new Date('2026-10-11T15:00:00Z'));
  expect(before.example).toBe(topicExamples[topic][0]);expect(after.example).toBe(topicExamples[topic][1]);
  expect(before.status).toContain('아직');expect(after.status).toContain('현재까지');
 }
});
it('never substitutes an example for a real record, distinguishing prior days and plans',()=>{
 const item={observed_at:'2026-10-10T12:00:00Z',claim_type:'plan'} as CareItem;
 expect(topicMessage('outdoors',now,item)).toEqual({status:'이전 기록입니다. 오늘 상태를 뜻하지 않습니다.',plan:'예정된 내용입니다. 실행이 확인된 것은 아닙니다.',example:null});
 expect(topicMessage('meals',now,{...item,observed_at:'2026-10-11T12:00:00Z',claim_type:'staff_observation'}).plan).toBeNull();
 expect(topicMessage('unknown',now).example).toBeUndefined();
});
