import {useState,useEffect} from 'react';
import {api,upload} from './api';
import {waitJob,type Job} from './jobs';
export type AudioCap={capture_id:string;revision:number;utterances?:{text:string}[]};
export function Audio({onTranscribed}:{onTranscribed:(cap:AudioCap)=>void}){
 const [file,setFile]=useState<File|null>(null),[permission,setPermission]=useState(''),[ack,setAck]=useState(false),[result,setResult]=useState(''),[busy,setBusy]=useState(false),[cap,setCap]=useState<AudioCap|null>(null),[language,setLanguage]=useState('fi'),[model,setModel]=useState('');
 useEffect(()=>{void api<{stt:{backend:string;model:string|null}}>('/staff/providers').then(r=>setModel(`${r.stt.backend} · ${r.stt.model??'ei mallia'}`));},[]);
 async function run(){if(!file||!ack||!permission)return;setBusy(true);setResult('Litterointi käynnissä. Voit peruuttaa.');let current:AudioCap|null=null;try{
 current=await api<AudioCap>('/staff/residents/aino/captures',{input_mode:'audio',disclosure_ack:ack,recording_permission_ref:permission});current=await upload<AudioCap>(`/staff/captures/${current.capture_id}/audio`,file,current.revision);setCap(current);
 const job=await waitJob(await api<Job>(`/staff/captures/${current.capture_id}/transcribe`,{language,occurred_at:new Date().toISOString()},current.revision));
 const saved=await api<AudioCap>(`/staff/captures/${current.capture_id}`);onTranscribed(saved);setResult(`STT ${job.execution.execution_mode} · ${job.execution.provider_id} · ${job.execution.model}. Tarkista litterointi ennen hyväksyntää.`);
 }catch(e){setResult(`${String(e)}. Suora tekstisyöttö on käytettävissä.`);}finally{
 if(current){try{const cleanup=await api<{runtime:{deletion_status:string;deleted_at:string|null}}>(`/staff/captures/${current.capture_id}/audio-status`);setResult(v=>`${v} Paikallinen tiedosto: ${cleanup.runtime.deletion_status}; ${cleanup.runtime.deleted_at??'poistoa ei vahvistettu'}.`);}catch{/* session errors are handled centrally */}}
 setBusy(false);setCap(null);}}
 async function cancel(){if(!cap)return;try{const latest=await api<AudioCap>(`/staff/captures/${cap.capture_id}`);await api(`/staff/captures/${cap.capture_id}/cancel`,{},latest.revision);setResult('Peruutus pyydetty.');}catch(e){setResult(String(e));}}
 return <section><h2>Äänitiedoston käsittely</h2><p>Paikallinen STT: {model}. Vain itsenäinen synteettinen aineisto. Puhuja ja merkitys on tarkistettava.</p><label>Erillisen tallennusluvan viite<input value={permission} onChange={e=>setPermission(e.target.value)}/></label><label>Äänen kieli<select value={language} onChange={e=>setLanguage(e.target.value)}><option value="fi">Suomi</option><option value="en">English</option><option value="sv">Svenska</option><option value="ko">한국어</option></select></label><label>Synteettinen WAV (enintään 20 MiB / 180 s)<input type="file" accept="audio/wav" onChange={e=>setFile(e.target.files?.[0]??null)}/></label><label><input type="checkbox" checked={ack} onChange={e=>setAck(e.target.checked)}/>Äänen käsittely on ilmoitettu. Aineisto on itsenäinen synteettinen testi.</label><button disabled={busy||!file||!ack||!permission} onClick={()=>void run()}>Litteroi paikallisesti</button>{busy&&<button disabled={!cap} onClick={()=>void cancel()}>Peruuta litterointi</button>}{result&&<p role="status">{result}</p>}</section>;
}
