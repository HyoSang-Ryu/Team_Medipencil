import {KideContext,KideV4Details,type V4} from './KideV4';
import {useEffect,useRef,useState} from 'react';
import {Link} from 'react-router-dom';
import {RoundLoopVoice} from './RoundLoopVoice';
import {directRecord} from './roundloopDirect';
import {useUiLanguage} from './UiLanguage';
export function KideDirectPage(){
 const {language}=useUiLanguage(),t=(ko:string,en:string,fi:string)=>({ko,en,fi}[language]);
 const [text,setText]=useState(''),[result,setResult]=useState<unknown>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const [context,setContext]=useState<Record<string,unknown>>({});
 const controller=useRef(new AbortController());const pending=useRef(false);
 useEffect(()=>()=>{controller.current.abort();},[]);
 async function summarize(transcript:string){if(pending.current)return;pending.current=true;setText(transcript);setBusy(true);setResult(null);setError('');try{const r=await directRecord(transcript,controller.current.signal,context);if(!r||typeof r!=='object'||!['charting','nursing_note','missing_questions','family_notices','family_filter_excluded'].every(k=>Array.isArray((r as Record<string,unknown>)[k])))throw new Error('INVALID_RESULT');if(!controller.current.signal.aborted)setResult(r);}catch{if(!controller.current.signal.aborted)setError(t('초안을 표시할 수 없습니다. 전사 내용을 확인하고 다시 정리하세요.','The draft could not be displayed. Check the transcript and regenerate.','Luonnosta ei voida näyttää. Tarkista litterointi ja luo uudelleen.'));}finally{pending.current=false;if(!controller.current.signal.aborted)setBusy(false);}}
 return <main><Link to="/">← Päivän kuulumiset</Link><h1>KIDE</h1><KideContext onChange={setContext} disabled={busy}/><RoundLoopVoice subject="direct" disabled={busy} onComplete={s=>void summarize(s)}/>{busy&&<p role="status">{t('핀란드어 초안 생성 중','Generating Finnish draft','Luodaan suomenkielistä luonnosta')}</p>}{error&&<p role="alert">{error}</p>}{text&&<section><h2>{t('전사 원문','Transcript','Litterointi')}</h2><p style={{whiteSpace:'pre-wrap'}}>{text}</p>{!busy&&!result&&<button onClick={()=>void summarize(text)}>{t('다시 정리','Retry','Yritä uudelleen')}</button>}</section>}{result!==null&&<section><h2>{t('핀란드어 초안 · 미검토','Finnish draft · unreviewed','Suomenkielinen luonnos · tarkistamatta')}</h2>{typeof result==='object'&&result&&'charting' in result&&Array.isArray((result as V4).nursing_note)&&<KideV4Details data={result as V4}/>}</section>}<p>{t('이 화면의 전사·초안은 현재 화면에만 유지됩니다. DB 저장과 보호자 발송은 직원 기록 화면에서 진행하세요.','Transcript and draft stay in this screen until you leave. Use the staff record screen to save and share after review.','Litterointi ja luonnos säilyvät vain tässä näkymässä. Tallenna ja jaa tarkistuksen jälkeen henkilöstön kirjausnäkymässä.')}</p></main>;
}
