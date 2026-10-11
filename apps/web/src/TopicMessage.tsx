import {careTopics} from './careTopics';
import {topicMessage,type CareItem} from './careTopicMessages';
import {useUiLanguage} from './UiLanguage';
export function TopicMessage({topic,now,item,unavailable=false}:{topic:string;now:Date;item?:CareItem;unavailable?:boolean}){
 const {tr}=useUiLanguage();
 if(unavailable)return <p>{tr('선택한 언어로 전달된 소식이 없습니다.')}</p>;
 const info=careTopics.find(t=>t.key===topic);if(!info)return null;
 const message=topicMessage(topic,now,item);
 return <div className="topic-message"><p>{tr(message.status).replace('{topic}',tr(info.label))}</p>{message.plan&&<p>{tr(message.plan)}</p>}{message.example&&<div className="topic-example"><small>{tr('표시 예시 · 실제 돌봄 기록 아님')}</small><p>{tr(message.example)}</p></div>}</div>;
}
