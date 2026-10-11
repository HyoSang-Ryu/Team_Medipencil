import {careDay,type BoardData} from './dailyUpdate';
export const topicExamples:Record<string,[string,string]>={
 meals:["아침 식사를 식당에서 했어요.", "저녁 식사를 절반 정도 드셨어요."],
 medication:["아침 약 복용이 기록되어 있어요.", "저녁 약 복용이 기록되어 있어요."],
 movement:["직원과 복도를 걸었어요.", "오후에는 방에서 쉬었어요."],
 outdoors:["오후에 정원 산책이 예정되어 있어요. 아직 실행 확인은 없어요.", "직원과 정원에서 10분간 산책했어요."],
 sleep:["지난밤 중간에 한 번 깬 것으로 기록되어 있어요.", "오후에 30분간 낮잠을 잤어요."],
 care_contact:["오늘 오후 간호사 면담이 예정되어 있어요.", "간호사 면담을 마쳤다는 기록이 있어요."],
 health_context:["오전에 피곤하다고 말씀하셨어요.", "저녁에 불편한 곳이 없다고 말씀하셨어요."],
};
export type CareItem=BoardData['tiles'][number]['items'][number];
export function topicMessage(topic:string,now:Date,item?:CareItem){
 const evening=Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Helsinki',hour:'2-digit',hourCycle:'h23'}).format(now))>=18;
 return {
  status:item?careDay(item.observed_at)===careDay(now)?'오늘 날짜의 기록입니다.':'이전 기록입니다. 오늘 상태를 뜻하지 않습니다.':evening?'현재까지 전달된 {topic} 소식이 없습니다.':'오늘 {topic} 소식은 아직 전달되지 않았어요.',
  plan:item?.claim_type==='plan'?'예정된 내용입니다. 실행이 확인된 것은 아닙니다.':null,
  example:item?null:topicExamples[topic]?.[evening?1:0],
 };
}
