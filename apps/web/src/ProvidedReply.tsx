import {useState} from 'react';
import {useUiLanguage} from './UiLanguage';
export function ProvidedReply({id,busy,save}:{id:string;busy:boolean;save:(text:string)=>Promise<void>}){
 const {language}=useUiLanguage(),t=(ko:string,en:string,fi:string)=>({ko,en,fi}[language]);
 const [text,setText]=useState(''),[checked,setChecked]=useState(false);
 return <form className="provided-reply" onSubmit={e=>{e.preventDefault();if(busy||!checked||!text.trim())return;void save(text.trim()).then(()=>{setText('');setChecked(false);}).catch(()=>{/* Parent displays error; keep this draft for retry. */});}}>
 <label htmlFor={'reply-'+id}>{t('핀란드어 답변 · 일상생활 범위만','Finnish reply · daily-living scope only','Vastaus suomeksi · vain arjen tiedot')}</label>
 <textarea id={'reply-'+id} maxLength={2000} value={text} disabled={busy} onChange={e=>{setText(e.target.value);setChecked(false);}}/>
 <label className="provided-reply-check"><input type="checkbox" checked={checked} disabled={busy} onChange={e=>setChecked(e.target.checked)}/><span>{t('핀란드어·일상생활 범위를 확인했습니다.','I checked Finnish and daily-living scope.','Tarkistin suomen ja arkitietojen rajauksen.')}</span></label>
 <button type="submit" disabled={busy||!checked||!text.trim()}>{t('답변 저장','Save reply','Tallenna vastaus')}</button>
 </form>;
}
