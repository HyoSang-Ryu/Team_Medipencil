import {afterEach,expect,it,vi} from 'vitest';
import {clearDirect,configureDirect,directRecord,directSocketUrl} from './roundloopDirect';
afterEach(()=>{clearDirect();vi.unstubAllGlobals();});
it('calls KaiLab directly with only transcript and no service credentials',async()=>{
 configureDirect('https://example.com','synthetic-test-key');
 const fetcher=vi.fn().mockResolvedValue({ok:true,text:async()=>JSON.stringify({nursing_note:{}})});vi.stubGlobal('fetch',fetcher);
 await directRecord('Synthetic speech',new AbortController().signal);
 expect(fetcher).toHaveBeenCalledWith('https://example.com/v1/record',expect.objectContaining({credentials:'omit',redirect:'error',headers:{'Content-Type':'application/json','X-API-Key':'synthetic-test-key'},body:'{"transcript":"Synthetic speech"}'}));
 expect(directSocketUrl()).toBe('wss://example.com/v1/stream?key=synthetic-test-key');
 clearDirect();expect(()=>directSocketUrl()).toThrow('KAILAB_KEY_REQUIRED');
});
it('rejects non-HTTPS and URLs with embedded credentials',()=>{
 expect(()=>configureDirect('http://example.com','x')).toThrow();expect(()=>configureDirect('https://user:pass@example.com','x')).toThrow();
});

it('restores tab configuration after reload and clears it on logout',async()=>{
 configureDirect('https://example.com','synthetic-session-key');
 vi.resetModules();
 const reloaded=await import('./roundloopDirect');
 expect(reloaded.directConfig().key).toBe('synthetic-session-key');
 reloaded.clearDirect();
 expect(sessionStorage.getItem('kide-direct-session')).toBeNull();
 expect(reloaded.directConfig().key).toBe('');
});

it('sends only explicitly applied context with the transcript',async()=>{
 configureDirect('https://example.com','synthetic-key');
 const fetcher=vi.fn().mockResolvedValue({ok:true,text:async()=>'{}'});vi.stubGlobal('fetch',fetcher);
 await directRecord('Independent demo',new AbortController().signal,{date:'2026-10-13',resident:{name:'Demo',spoken_name:'데모'},guardians:[]});
 expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({transcript:'Independent demo',date:'2026-10-13',resident:{name:'Demo',spoken_name:'데모'},guardians:[]});
});
