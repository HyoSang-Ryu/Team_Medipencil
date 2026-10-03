import {createContext,useContext,useEffect,useState,type ReactNode} from 'react';
import english from './english.json';
type Language='fi'|'en';
const translations:Record<string,string>=english;
const UiContext=createContext<{language:Language;setLanguage:(value:Language)=>void;tr:(text:string)=>string}>({language:'fi',setLanguage:()=>{},tr:text=>text});
export function UiLanguageProvider({children}:{children:ReactNode}){
 const [language,setLanguage]=useState<Language>('fi');
 useEffect(()=>{document.documentElement.lang=language;},[language]);
 return <UiContext.Provider value={{language,setLanguage,tr:text=>language==='en'?(translations[text]??text):text}}>{children}</UiContext.Provider>;
}
export const useUiLanguage=()=>useContext(UiContext);
