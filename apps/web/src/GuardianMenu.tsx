import {useEffect,useRef,useState} from 'react';
import {NavLink,useNavigate} from 'react-router-dom';
import {List,X,SignOut} from '@phosphor-icons/react';
import {Avatar} from './Profiles';
import {useUiLanguage,type Language} from './UiLanguage';
import type {Session} from './api';
export function GuardianMenu({viewer,busy,onLogout,onSection}:{viewer:Session;busy:boolean;onLogout:()=>void;onSection:(section:'today'|'history'|'family'|'settings')=>void}){
 const {language,setLanguage,tr}=useUiLanguage(),navigate=useNavigate();
 const [open,setOpen]=useState(false),dialog=useRef<HTMLDialogElement>(null);
 const supplied=viewer.actor_id.startsWith('provided-'),home=supplied?'/family/provided':'/family/residents/aino';
 const t=(ko:string,en:string,fi:string)=>({ko,en,fi}[language]);
 useEffect(()=>{if(open){dialog.current?.showModal();const old=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{document.body.style.overflow=old;};}dialog.current?.close();},[open]);
 function close(){setOpen(false);}
 function section(key:'today'|'history'|'family'|'settings'){onSection(key);navigate(supplied?home+'?view='+({today:'details',history:'details',family:'questions',settings:'settings'}[key]):home+'/details');close();}
 return <><button className="guardian-menu-toggle" data-testid="guardian-menu-toggle" aria-label={t('메뉴 열기','Open menu','Avaa valikko')} onClick={()=>setOpen(true)}><List size={23}/></button><dialog className="guardian-menu-sheet" ref={dialog} onCancel={close} onClose={close} aria-label={t('보호자 메뉴','Family menu','Läheisen valikko')}><div className="guardian-menu-top"><Avatar actor={viewer.actor_id} name={viewer.display_name}/><strong>{viewer.display_name}({tr('보호자')})</strong><button disabled={busy} aria-label={tr('로그아웃')} data-testid="guardian-menu-logout" onClick={()=>{close();onLogout();}}><SignOut size={21}/></button><button autoFocus aria-label={t('메뉴 닫기','Close menu','Sulje valikko')} onClick={close}><X size={23}/></button></div><nav className="guardian-menu-links"><NavLink to={home} onClick={close}>{tr('대시보드')}</NavLink><h2>{tr('상세보기')}</h2>{(['today','history','family','settings'] as const).map((key,i)=><button key={key} onClick={()=>section(key)}>{tr(['오늘의 안부','기간별 안부','가족확인사항','설정(공개범위)'][i])}</button>)}<NavLink to="/manual" onClick={close}>{tr('사용자 매뉴얼')}</NavLink><label>{tr('Interface / 화면 언어')}<select value={language} onChange={e=>setLanguage(e.target.value as Language)}><option value="fi">Suomi</option><option value="ko">한국어</option><option value="en">English</option></select></label></nav></dialog></>;
}
