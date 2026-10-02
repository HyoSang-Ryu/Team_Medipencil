import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import {api,resetSession,setSession,type Session} from './api';
import './style.css';
type Question={question_id:string;text:string;status:string;revision:number;subject_id:string;recipient_id?:string};
function App(){
 const [session,saveSession]=useState<Session|null>(null),[questions,setQuestions]=useState<Question[]>([]),[text,setText]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function refresh(s:Session){const r=await api<{items:Question[]}>(s.role==='family'?'/family/residents/aino/questions':'/staff/question-queue');setQuestions(r.items);}
 async function login(actor:string){resetSession();saveSession(null);setQuestions([]);setText('');setError('');try{const s=await api<Session>('/demo/session',{demo_actor_id:actor});setSession(s);saveSession(s);await refresh(s);}catch(e){setError(String(e));}}
 async function send(){if(!session)return;setBusy(true);try{await api('/family/residents/aino/questions',{text});setText('');await refresh(session);}catch(e){setError(String(e));}finally{setBusy(false);}}
 return <><header><span className="brand">Päivän kuulumiset</span><span>SYNTHETIC DEMO · paikallinen testi</span></header><main><nav aria-label="Demo-käyttäjä">{['liisa','mikko','staff'].map(a=><button key={a} onClick={()=>void login(a)}>{a==='staff'?'Koskinen':a}</button>)}</nav><p>Nykyinen käyttäjä: {session?.display_name??'Valitse käyttäjä'} · Aino (synteettinen)</p><p className="notice">Tämä on paikallinen demosessio. Ei tuotantokäyttöön.</p>{error&&<p role="alert">{error}</p>}{session?.role==='family'&&<section><h1>Kysy hoitajalta</h1><p>Ei kiireellisiin asioihin. Käytä hoitopaikan vahvistettua yhteydenottotapaa.</p><label>Kysymys<textarea value={text} maxLength={2000} onChange={e=>setText(e.target.value)}/></label><button disabled={busy||!text.trim()} onClick={()=>void send()}>Lähetä kysymys</button></section>}{session&&<section><h2>{session.role==='staff'?'Hoitajan kysymysjono':'Omat kysymykset'}</h2>{questions.length===0&&<p>Ei kysymyksiä.</p>}{questions.map(q=><article key={q.question_id}><p>{q.text}</p><small>{q.status}</small></article>)}</section>}</main><footer>Suomen kielen ihmisarvio: odottaa · AI ei käytössä</footer></>;
}
createRoot(document.getElementById('root')!).render(<App/>);
