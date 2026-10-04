import {useEffect,useRef,useState} from 'react';
import {useUiLanguage} from './UiLanguage';
import content from './manual-content.json';

type Section={id:string;title:string;paragraphs:string[];steps:string[];notes:string[];table:string[][]};
export function UserManual({onClose}:{onClose:()=>void}){
 const {language}=useUiLanguage();const english=language==='en';
 const [search,setSearch]=useState('');const heading=useRef<HTMLHeadingElement>(null);
 useEffect(()=>{heading.current?.focus();window.scrollTo(0,0);},[]);
 const sections:Section[]=content[english?'en':'ko'];
 const query=search.trim().toLocaleLowerCase();
 const visible=sections.filter(s=>!query||[s.title,...s.paragraphs,...s.steps,...s.notes,...s.table.flat()].join(' ').toLocaleLowerCase().includes(query));
 return <div className="user-manual" lang={english?'en':'ko'}>
  <div className="manual-heading"><div><p className="manual-eyebrow">MediPencil · PoC</p><h1 ref={heading} tabIndex={-1}>{english?'User manual':'사용자 매뉴얼'}</h1><p>{english?'Step-by-step guidance for family, staff and team reviewers.':'가족·직원·팀 검토자를 위한 화면별 상세 사용 안내'}</p></div><button onClick={onClose}>{english?'Back to work':'사용 화면으로 돌아가기'}</button></div>
  <div className="manual-summary"><strong>{english?'Question → Review → Approve → Publish → Read':'질문 → 직원 확인 → 승인 → 발행 → 가족 열람'}</strong><p>{english?'Public synthetic PoC · Direct input · STT/LLM disabled · Guide updated 4 October 2026':'계정 없는 합성자료 PoC · 직접 입력 · STT/LLM 미사용 · 안내 기준 2026-10-04'}</p></div>
  <label className="manual-search">{english?'Search this manual':'매뉴얼 검색'}<input type="search" value={search} onChange={e=>setSearch(e.target.value)} placeholder={english?'Try approval, consent, comment…':'승인, 동의, 코멘트 등을 검색하세요'}/></label>
  <p className="manual-result" role="status">{english?`${visible.length} of ${sections.length} sections`:`전체 ${sections.length}개 중 ${visible.length}개 항목`}</p>
  <div className="manual-layout"><nav className="manual-toc" aria-label={english?'Manual contents':'매뉴얼 목차'}><h2>{english?'Contents':'목차'}</h2><ol>{visible.map(s=><li key={s.id}><a href={`#manual-${s.id}`} onClick={e=>{e.preventDefault();const target=document.getElementById(`manual-${s.id}`);target?.scrollIntoView({block:'start'});target?.focus({preventScroll:true});}}>{s.title}</a></li>)}</ol></nav>
  <div className="manual-sections">{visible.length===0&&<section><h2>{english?'No matching sections':'검색 결과가 없습니다'}</h2><p>{english?'Try a shorter term or clear the search to view all sections.':'짧은 단어로 다시 검색하거나 검색어를 지워 전체 목차를 확인하세요.'}</p><button onClick={()=>setSearch('')}>{english?'Clear search':'검색어 지우기'}</button></section>}{visible.map(s=><section className="manual-section" key={s.id} aria-labelledby={`manual-${s.id}`}><h2 id={`manual-${s.id}`} tabIndex={-1}>{s.title}</h2>{s.paragraphs.map((p,i)=><p key={i}>{p}</p>)}{s.steps.length>0&&<ol className="manual-steps">{s.steps.map((p,i)=><li key={i}>{p}</li>)}</ol>}{s.table.length>0&&<div className="manual-table"><table><thead><tr>{s.table[0].map((cell,i)=><th scope="col" key={i}>{cell}</th>)}</tr></thead><tbody>{s.table.slice(1).map((row,i)=><tr key={i}>{row.map((cell,j)=>j===0?<th scope="row" key={j}>{cell}</th>:<td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>}{s.notes.map((p,i)=><p className="manual-note" key={i}>{p}</p>)}</section>)}<button className="manual-bottom-back" onClick={onClose}>{english?'Back to work':'사용 화면으로 돌아가기'}</button></div></div>
 </div>;
}
