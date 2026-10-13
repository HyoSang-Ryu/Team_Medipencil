// Credentials stay in this tab's memory; never in builds, browser storage or our API.
let endpoint='https://him-tax-shop-pcs.trycloudflare.com';
let key='';
export function directConfig(){return {endpoint,key};}
export function configureDirect(url:string,secret:string){
 const parsed=new URL(url);
 if(parsed.protocol!=='https:'||parsed.username||parsed.password||parsed.search||parsed.hash||parsed.pathname!=='/')throw new Error('INVALID_KAILAB_URL');
 endpoint=parsed.origin;key=secret.trim();
}
export function clearDirect(){key='';}
export function directSocketUrl(){if(!key)throw new Error('KAILAB_KEY_REQUIRED');return endpoint.replace(/^https:/,'wss:')+'/v1/stream?key='+encodeURIComponent(key);}
export async function directRecord(transcript:string,signal:AbortSignal){
 if(!key)throw new Error('KAILAB_KEY_REQUIRED');
 const response=await fetch(endpoint+'/v1/record',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':key},body:JSON.stringify({transcript}),credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',signal:AbortSignal.any([signal,AbortSignal.timeout(100000)])});
 if(!response.ok)throw new Error('KAILAB_RECORD_FAILED');
 const raw=await response.text();if(raw.length>200000)throw new Error('KAILAB_INVALID_RESULT');
 return JSON.parse(raw);
}
