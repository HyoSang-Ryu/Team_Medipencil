import {useEffect,useRef,useState} from 'react';
import {Link} from 'react-router-dom';
import {RoundLoopVoice} from './RoundLoopVoice';
import {clearDirect,directRecord} from './roundloopDirect';
import {useUiLanguage} from './UiLanguage';
export function KideDirectPage(){
 const {language}=useUiLanguage(),t=(ko:string,en:string,fi:string)=>({ko,en,fi}[language]);
 const [text,setText]=useState(''),[result,setResult]=useState<unknown>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const controller=useRef(new AbortController());const pending=useRef(false);
 useEffect(()=>()=>{controller.current.abort();clearDirect();},[]);
 async function summarize(transcript:string){if(pending.current)return;pending.current=true;setText(transcript);setBusy(true);setResult(null);setError('');try{const r=await directRecord(transcript,controller.current.signal);if(!controller.current.signal.aborted)setResult(r);}catch{if(!controller.current.signal.aborted)setError(t('초안 생성에 실패했습니다. 연결 설정을 확인하고 다시 시도하세요.','Draft generation failed. Check the connection and retry.','Luonnoksen luonti epäonnistui. Tarkista yhteys ja yritä uudelleen.'));}finally{pending.current=false;if(!controller.current.signal.aborted)setBusy(false);}}
 function download(){const url=URL.createObjectURL(new Blob([JSON.stringify({transcript:text,result,status:'unreviewed_not_shared'},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='kide-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 return <main><Link to="/">← Päivän kuulumiset</Link><h1>KIDE</h1><RoundLoopVoice subject="direct" disabled={busy} onComplete={s=>void summarize(s)}/>{busy&&<p role="status">{t('핀란드어 초안 생성 중','Generating Finnish draft','Luodaan suomenkielistä luonnosta')}</p>}{error&&<p role="alert">{error}</p>}{text&&<section><h2>{t('전사 원문','Transcript','Litterointi')}</h2><p style={{whiteSpace:'pre-wrap'}}>{text}</p>{!busy&&!result&&<button onClick={()=>void summarize(text)}>{t('다시 정리','Retry','Yritä uudelleen')}</button>}</section>}{result!==null&&<section><h2>{t('핀란드어 초안 · 미검토','Finnish draft · unreviewed','Suomenkielinen luonnos · tarkistamatta')}</h2><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{JSON.stringify(result,null,2)}</pre><button onClick={download}>{t('초안 파일 저장','Download draft','Lataa luonnos')}</button></section>}<p>{t('이 화면의 전사·초안은 현재 화면에만 유지됩니다. 파일로 저장할 수 있으며, DB 저장과 보호자 발송은 하지 않습니다.','Transcript and draft stay in this screen until you leave. Download a copy to keep them. This screen does not save to a database or send to families.','Litterointi ja luonnos säilyvät vain tässä näkymässä. Lataa kopio säilyttämistä varten. Tietokantaan tallennusta tai läheisille lähettämistä ei tehdä.')}</p></main>;
}
