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
