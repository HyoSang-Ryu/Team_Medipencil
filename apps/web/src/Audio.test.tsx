// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {act,cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {Audio} from './Audio';
import {api,upload} from './api';
vi.mock('./api',()=>({api:vi.fn(),upload:vi.fn(),sessionSignal:()=>new AbortController().signal}));
vi.mock('./UiLanguage',async importOriginal=>({...await importOriginal<typeof import('./UiLanguage')>(),useUiLanguage:()=>({language:'en',tr:(x:string)=>x})}));
vi.mock('./Microphone',()=>({Microphone:({onBeforeStart,onChunk,onActive,onFile}:{onBeforeStart:()=>Promise<void>;onChunk:(f:File)=>void;onActive:(v:boolean)=>void;onFile:(f:File)=>void})=><button onClick={async()=>{await onBeforeStart();onActive(true);const file=new File(['test'],'fixture.wav');onChunk(file);onChunk(file);onActive(false);onFile(file);}}>Synthetic recording fixture</button>}));
beforeEach(()=>{vi.clearAllMocks();vi.mocked(api).mockImplementation(async(path)=>path==='/staff/providers'?{stt:{backend:'whisper',model:'test'}}:{capture_id:'test',revision:1});});
afterEach(cleanup);
it('sends chunks serially and waits for the last chunk before enabling final STT',async()=>{
 let resolve!:(v:unknown)=>void;
 vi.mocked(upload).mockReturnValueOnce(new Promise(r=>{resolve=r;})).mockResolvedValueOnce({sequence:1,text:'Second chunk'});
 render(<Audio onTranscribed={vi.fn()}/>);
 fireEvent.change(screen.getByLabelText('Erillisen tallennusluvan viite'),{target:{value:'synthetic-test'}});
 fireEvent.click(screen.getByLabelText('Äänen käsittely on ilmoitettu. Aineisto on itsenäinen synteettinen testi.'));
 fireEvent.click(screen.getByText('Synthetic recording fixture'));
 await waitFor(()=>expect(upload).toHaveBeenCalledTimes(1));
 expect(screen.getByText('Litteroi paikallisesti').hasAttribute('disabled')).toBe(true);
 await act(async()=>resolve({sequence:0,text:'First chunk'}));
 await waitFor(()=>expect(screen.getByText('2. Second chunk')).toBeTruthy());
 expect(screen.getByText('1. First chunk')).toBeTruthy();
 expect(vi.mocked(upload).mock.calls[1][0]).toContain('sequence=1');
 expect(screen.getByText('Litteroi paikallisesti').hasAttribute('disabled')).toBe(false);
});
it('discards a late result and stops draining after leaving the page',async()=>{
 let resolve!:(v:unknown)=>void;
 vi.mocked(upload).mockReturnValue(new Promise(r=>{resolve=r;}));
 const view=render(<Audio onTranscribed={vi.fn()}/>);
 fireEvent.click(screen.getByText('Synthetic recording fixture'));
 await waitFor(()=>expect(upload).toHaveBeenCalledOnce());view.unmount();
 await act(async()=>resolve({sequence:0,text:'Late text'}));
 expect(upload).toHaveBeenCalledOnce();expect(screen.queryByText('Late text')).toBeNull();
});
