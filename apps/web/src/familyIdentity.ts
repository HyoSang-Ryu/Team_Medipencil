import {type Language,uiText} from './UiLanguage';
export type FamilyIdentity={name:string;age:number|null;relationship:string};
// Independent original demo persona: final design v1.1 §4 (84 years, Liisa's mother).
// Display-name change keeps that persona's identity and age; not supplied Aino's age.
export const originalFamilyIdentity:FamilyIdentity={name:'Helmi Nieminen',age:84,relationship:'mother'};
export function familyResidentLabel(person:FamilyIdentity,language:Language){
 const terms:Record<string,[string,string,string]>={mother:['엄마','Mom','Äiti'],father:['아빠','Dad','Isä'],son:['아들','Son','Poika'],daughter:['딸','Daughter','Tytär'],parent:['부모님','Parent','Vanhempi'],child:['자녀','Child','Lapsi'],spouse:['배우자','Spouse','Puoliso'],family:['가족','Family member','Läheinen']};
 const relation=uiText(language,...(terms[person.relationship]??terms.family));
 const age=person.age===null?uiText(language,'나이 미등록','age not recorded','ikä puuttuu'):`${person.age}${language==='sv'?' år':uiText(language,'세',' years',' v')}`;
 return `${relation}(${person.name}, ${age})`;
}
