import {createContext,useContext,useEffect,useState,type ReactNode} from 'react';
import english from './english.json';
import korean from './korean.json';
import finnish from './finnish.json';
export type Language='fi'|'ko'|'en';
export const languageLocales={fi:'fi-FI',ko:'ko-KR',en:'en-GB'};
const translations:Record<Language,Record<string,string>>={fi:finnish,ko:korean,en:english};
const storageKey='medipencil.ui-language';
function initialLanguage():Language{
 try{const saved=localStorage.getItem(storageKey);if(saved==='fi'||saved==='ko'||saved==='en')return saved;}catch{/* Storage may be disabled; switching still works in memory. */}
 return 'fi';
}
const UiContext=createContext<{language:Language;setLanguage:(value:Language)=>void;tr:(text:string)=>string}>({language:'fi',setLanguage:()=>{},tr:text=>text});
export function UiLanguageProvider({children}:{children:ReactNode}){
 const [language,setLanguage]=useState<Language>(initialLanguage);
 useEffect(()=>{document.documentElement.lang=language;try{localStorage.setItem(storageKey,language);}catch{/* Language persistence is optional. */}},[language]);
 return <UiContext.Provider value={{language,setLanguage,tr:text=>translations[language][text]??text}}>{children}</UiContext.Provider>;
}
export const useUiLanguage=()=>useContext(UiContext);
