import {afterEach,expect,test,vi} from 'vitest';
import {api,resetSession,setSession} from './api';
afterEach(()=>{vi.unstubAllGlobals();resetSession();});
test('late sensitive response after session switch is discarded even if transport ignores abort',async()=>{
 let finish!:(value:unknown)=>void;
 vi.stubGlobal('fetch',vi.fn(()=>new Promise(resolve=>{finish=resolve;})));
 setSession({actor_id:'liisa',role:'family',display_name:'Liisa',csrf_token:'test'});
 const pending=api('/family/residents/aino/board');
 resetSession();setSession({actor_id:'mikko',role:'family',display_name:'Mikko',csrf_token:'test2'});
 finish({ok:true,json:async()=>({data:{sensitive:'old viewer'}})});
 await expect(pending).rejects.toThrow('SESSION_CHANGED');
});
test('network errors never return stale data',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('offline')));
 await expect(api('/family/residents/aino/board')).rejects.toThrow('offline');
});
test('session switch during JSON decoding also discards the response',async()=>{
 let finish!:(value:unknown)=>void;let decoding!:()=>void;const started=new Promise<void>(resolve=>{decoding=resolve;});
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,status:200,json:()=>{decoding();return new Promise(resolve=>{finish=resolve;});}}));
 const pending=api('/family/residents/aino/board');await started;resetSession();finish({data:{private:'old'}});
 await expect(pending).rejects.toThrow('SESSION_CHANGED');
});
test('job polling ends on session switch before querying with the new session',async()=>{
 const {waitJob}=await import('./jobs');vi.useFakeTimers();
 try{
  const fetch=vi.fn();vi.stubGlobal('fetch',fetch);
  const pending=waitJob({job_id:'old-staff-job',status:'running',error_code:null,result_ref:null,execution:{}});
  const rejected=expect(pending).rejects.toThrow('SESSION_CHANGED');
  resetSession();await rejected;await vi.advanceTimersByTimeAsync(2000);
  expect(fetch).not.toHaveBeenCalled();
 }finally{vi.useRealTimers();}
});
test('Pages session token is sent in memory and removed on role reset',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,status:200,json:async()=>({data:{}})});
 vi.stubGlobal('fetch',fetch);
 setSession({actor_id:'staff',role:'staff',display_name:'Staff',csrf_token:'csrf',access_token:'synthetic-token'});
 await api('/session');
 expect(fetch.mock.calls[0][1].headers.Authorization).toBe('Bearer synthetic-token');
 resetSession();await api('/health');
 expect(fetch.mock.calls[1][1].headers.Authorization).toBeUndefined();
});
test('logout accepts an empty 204 response',async()=>{
 const json=vi.fn();vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,status:204,json}));
 await expect(api('/demo/session',undefined,undefined,'DELETE')).resolves.toBeUndefined();
 expect(json).not.toHaveBeenCalled();
});
