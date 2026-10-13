// Public PoC credential: explicitly authorized for browser delivery on 2026-10-13.
// Supplied through deployment secrets, never checked into source or sent to our API.
const demoEndpoint=import.meta.env.VITE_KIDE_DEMO_URL||'https://him-tax-shop-pcs.trycloudflare.com';
const demoKey=import.meta.env.VITE_KIDE_DEMO_KEY||'';
const storageKey='kide-direct-session';
let endpoint=demoEndpoint;
let key='';
export function directConfig(){
 if(!key){try{const saved=JSON.parse(sessionStorage.getItem(storageKey)??'null');if(saved?.endpoint&&saved?.key)configureDirect(saved.endpoint,saved.key);}catch{try{sessionStorage.removeItem(storageKey);}catch{/* Storage unavailable. */}}}
 if(!key&&demoKey)configureDirect(demoEndpoint,demoKey);
 return {endpoint,key};
}
export function configureDirect(url:string,secret:string){
 const parsed=new URL(url);
 if(parsed.protocol!=='https:'||parsed.username||parsed.password||parsed.search||parsed.hash||parsed.pathname!=='/')throw new Error('INVALID_KAILAB_URL');
 if(!secret.trim())throw new Error('KAILAB_KEY_REQUIRED');
 endpoint=parsed.origin;key=secret.trim();
 try{sessionStorage.setItem(storageKey,JSON.stringify({endpoint,key}));}catch{/* Memory-only fallback. */}
}
export function clearDirect(){key='';try{sessionStorage.removeItem(storageKey);}catch{/* Storage unavailable. */}}
export function directSocketUrl(){if(!key)throw new Error('KAILAB_KEY_REQUIRED');return endpoint.replace(/^https:/,'wss:')+'/v1/stream?key='+encodeURIComponent(key);}
export async function directRecord(transcript:string,signal:AbortSignal,context:Record<string,unknown>={}){
 if(!key)throw new Error('KAILAB_KEY_REQUIRED');
 const response=await fetch(endpoint+'/v1/record',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':key},body:JSON.stringify({...context,transcript}),credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',signal:AbortSignal.any([signal,AbortSignal.timeout(100000)])});
 if(!response.ok)throw new Error(response.status===401?'KIDE_KEY_INVALID':response.status>=500?'KIDE_ENGINE_FAILED':'KAILAB_RECORD_FAILED');
 const raw=await response.text();if(raw.length>200000)throw new Error('KAILAB_INVALID_RESULT');
 return JSON.parse(raw);
}
