export type Session={actor_id:string; role:string; display_name:string; csrf_token:string};
let csrf=''; let generation=0; let controller=new AbortController();
export function resetSession(){generation++;controller.abort();controller=new AbortController();csrf='';}
export function setSession(s:Session){csrf=s.csrf_token;}
export async function api<T>(path:string,body?:unknown,revision?:number,method?:string,key?:string):Promise<T>{
  const epoch=generation;
  const response=await fetch('/api/v1'+path,{method:method??(body===undefined?'GET':'POST'),credentials:'same-origin',signal:controller.signal,cache:'no-store',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':key??crypto.randomUUID(),...(revision===undefined?{}:{'If-Match':`"${revision}"`})},body:body===undefined?undefined:JSON.stringify(body)});
  if(epoch!==generation)throw new Error('SESSION_CHANGED');
  const result=await response.json();
  if(!response.ok)throw new Error(result.error?.code??'REQUEST_FAILED');
  return result.data as T;
}

export async function upload<T>(path:string,file:File,revision:number):Promise<T>{
  const epoch=generation;const form=new FormData();form.append('file',file);
  const response=await fetch('/api/v1'+path,{method:'POST',credentials:'same-origin',signal:controller.signal,headers:{'X-CSRF-Token':csrf,'Idempotency-Key':crypto.randomUUID(),'If-Match':`"${revision}"`},body:form});
  if(epoch!==generation)throw new Error('SESSION_CHANGED');
  const result=await response.json();if(!response.ok)throw new Error(result.error?.code??'REQUEST_FAILED');return result.data as T;
}
