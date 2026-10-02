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
