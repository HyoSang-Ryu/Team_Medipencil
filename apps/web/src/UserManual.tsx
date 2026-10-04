import {useEffect,useRef,useState} from 'react';
import {useUiLanguage} from './UiLanguage';
import content from './manual-content.json';

const manualLabels={
  "en": {
    "title": "User manual",
    "description": "Step-by-step guidance for family, staff and team reviewers.",
    "back": "Back to work",
    "flow": "Question → Review → Approve → Publish → Read",
    "scope": "Public synthetic PoC · Direct input · STT/LLM disabled · Guide updated 4 October 2026",
    "search": "Search this manual",
    "placeholder": "Try approval, consent, comment…",
    "contentsLabel": "Manual contents",
    "contents": "Contents",
    "empty": "No matching sections",
    "tryAgain": "Try a shorter term or clear the search to view all sections.",
    "clear": "Clear search"
  },
  "ko": {
    "title": "사용자 매뉴얼",
    "description": "가족·직원·팀 검토자를 위한 화면별 상세 사용 안내",
    "back": "사용 화면으로 돌아가기",
    "flow": "질문 → 직원 확인 → 승인 → 발행 → 가족 열람",
    "scope": "계정 없는 합성자료 PoC · 직접 입력 · STT/LLM 미사용 · 안내 기준 2026-10-04",
    "search": "매뉴얼 검색",
    "placeholder": "승인, 동의, 코멘트 등을 검색하세요",
    "contentsLabel": "매뉴얼 목차",
    "contents": "목차",
    "empty": "검색 결과가 없습니다",
    "tryAgain": "짧은 단어로 다시 검색하거나 검색어를 지워 전체 목차를 확인하세요.",
    "clear": "검색어 지우기"
  },
  "fi": {
    "title": "Käyttöopas",
    "description": "Vaiheittaiset ohjeet perheelle, hoitajille ja tiimin arvioijille.",
    "back": "Palaa työskentelyyn",
    "flow": "Kysymys → Tarkistus → Hyväksyntä → Julkaisu → Perheen näkymä",
    "scope": "Julkinen synteettinen PoC · Suora syöttö · STT/LLM ei käytössä · Päivitetty 4.10.2026",
    "search": "Hae oppaasta",
    "placeholder": "Hae esimerkiksi hyväksyntä, suostumus, kommentti…",
    "contentsLabel": "Oppaan sisällysluettelo",
    "contents": "Sisällysluettelo",
    "empty": "Ei hakutuloksia",
    "tryAgain": "Kokeile lyhyempää hakusanaa tai tyhjennä haku nähdäksesi kaikki osiot.",
    "clear": "Tyhjennä haku"
  }
};

type Section={id:string;title:string;paragraphs:string[];steps:string[];notes:string[];table:string[][]};
export function UserManual({onClose}:{onClose:()=>void}){
 const {language}=useUiLanguage();const text=manualLabels[language];
 const [search,setSearch]=useState('');const heading=useRef<HTMLHeadingElement>(null);
 useEffect(()=>{heading.current?.focus();window.scrollTo(0,0);},[]);
 const sections:Section[]=content[language];
 useEffect(()=>setSearch(''),[language]);
 const query=search.trim().toLocaleLowerCase();
 const visible=sections.filter(s=>!query||[s.title,...s.paragraphs,...s.steps,...s.notes,...s.table.flat()].join(' ').toLocaleLowerCase().includes(query));
 return <div className="user-manual" lang={language}>
  <div className="manual-heading"><div><p className="manual-eyebrow">MediPencil · PoC</p><h1 ref={heading} tabIndex={-1}>{text.title}</h1><p>{text.description}</p></div><button onClick={onClose}>{text.back}</button></div>
  <div className="manual-summary"><strong>{text.flow}</strong><p>{text.scope}</p></div>
  <label className="manual-search">{text.search}<input type="search" value={search} onChange={e=>setSearch(e.target.value)} placeholder={text.placeholder}/></label>
  <p className="manual-result" role="status">{language==='ko'?`전체 ${sections.length}개 중 ${visible.length}개 항목`:language==='fi'?`${visible.length} / ${sections.length} osiota`:`${visible.length} of ${sections.length} sections`}</p>
  <div className="manual-layout"><nav className="manual-toc" aria-label={text.contentsLabel}><h2>{text.contents}</h2><ol>{visible.map(s=><li key={s.id}><a href={`#manual-${s.id}`} onClick={e=>{e.preventDefault();const target=document.getElementById(`manual-${s.id}`);target?.scrollIntoView({block:'start'});target?.focus({preventScroll:true});}}>{s.title}</a></li>)}</ol></nav>
  <div className="manual-sections">{visible.length===0&&<section><h2>{text.empty}</h2><p>{text.tryAgain}</p><button onClick={()=>setSearch('')}>{text.clear}</button></section>}{visible.map(s=><section className="manual-section" key={s.id} aria-labelledby={`manual-${s.id}`}><h2 id={`manual-${s.id}`} tabIndex={-1}>{s.title}</h2>{s.paragraphs.map((p,i)=><p key={i}>{p}</p>)}{s.steps.length>0&&<ol className="manual-steps">{s.steps.map((p,i)=><li key={i}>{p}</li>)}</ol>}{s.table.length>0&&<div className="manual-table"><table><thead><tr>{s.table[0].map((cell,i)=><th scope="col" key={i}>{cell}</th>)}</tr></thead><tbody>{s.table.slice(1).map((row,i)=><tr key={i}>{row.map((cell,j)=>j===0?<th scope="row" key={j}>{cell}</th>:<td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>}{s.notes.map((p,i)=><p className="manual-note" key={i}>{p}</p>)}</section>)}<button className="manual-bottom-back" onClick={onClose}>{text.back}</button></div></div>
 </div>;
}
