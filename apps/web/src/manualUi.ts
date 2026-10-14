import content from './manual-content.json';
import {swedishText,type Language} from './UiLanguage';
export function manualSections(language:Language){
 if(language!=='sv')return content[language];
 return content.en.map(s=>({...s,title:swedishText(s.title),paragraphs:s.paragraphs.map(swedishText),steps:s.steps.map(swedishText),notes:s.notes.map(swedishText),table:s.table.map(row=>row.map(swedishText))}));
}
export function swedishLabels<T extends Record<string,string>>(labels:T):T{return Object.fromEntries(Object.entries(labels).map(([k,v])=>[k,swedishText(v)])) as T;}
