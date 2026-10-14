import {createContext,useContext,useEffect,useState,type ReactNode} from 'react';
import english from './english.json';
import korean from './korean.json';
import finnish from './finnish.json';
import swedish from './swedish.json';
export type Language='fi'|'ko'|'en'|'sv';
export const languageLocales={fi:'fi-FI',ko:'ko-KR',en:'en-GB',sv:'sv-FI'};
const translations:Record<Language,Record<string,string>>={fi:finnish,ko:korean,en:english,sv:swedish};
const storageKey='medipencil.ui-language';
function initialLanguage():Language{
 try{const saved=localStorage.getItem(storageKey);if(saved==='fi'||saved==='ko'||saved==='en'||saved==='sv')return saved;}catch{/* Storage may be disabled; switching still works in memory. */}
 return 'fi';
}
const UiContext=createContext<{language:Language;setLanguage:(value:Language)=>void;tr:(text:string)=>string}>({language:'fi',setLanguage:()=>{},tr:text=>text});
export function UiLanguageProvider({children}:{children:ReactNode}){
 const [language,setLanguage]=useState<Language>(initialLanguage);
 useEffect(()=>{document.documentElement.lang=language;try{localStorage.setItem(storageKey,language);}catch{/* Language persistence is optional. */}},[language]);
 return <UiContext.Provider value={{language,setLanguage,tr:text=>language==='sv'?swedishText(text):translations[language][text]??text}}>{children}</UiContext.Provider>;
}
export const useUiLanguage=()=>useContext(UiContext);

// UI text only. Never pass patient records or transcripts through this lookup.
export function swedishText(text:string):string {
 const catalog:Record<string,string>=swedish;
 if(catalog[text])return catalog[text];
 for(const [pattern,translated] of Object.entries(catalog)){
  if(!pattern.includes('{0}'))continue;
  const names:string[]=[];
  const escaped=pattern.replace(/[.*+?^$()|[\]\\]/g,'\\$&').replace(/\{(\d+)\}/g,(_,n)=>{names.push(n);return '(.*?)';});
  const match=text.match(new RegExp('^'+escaped+'$'));
  if(match)return translated.replace(/\{(\d+)\}/g,(token,n)=>{const index=names.indexOf(n);return index<0?token:match[index+1];});
 }
 return text;
}
export function uiText(language:Language,ko:string,en:string,fi:string):string {
 return language==='sv'?swedishText(en):({ko,en,fi}[language]);
}
