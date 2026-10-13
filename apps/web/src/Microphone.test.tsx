// @vitest-environment jsdom
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {act,cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {Microphone} from './Microphone';
vi.mock('./UiLanguage',()=>({useUiLanguage:()=>({language:'en'})}));
let node:{port:{onmessage:((e:{data:Float32Array})=>void)|null}};
const stopTrack=vi.fn(),closeContext=vi.fn(),onFile=vi.fn(),onActive=vi.fn();
const stream={getTracks:()=>[{stop:stopTrack}]};
beforeEach(()=>{
 vi.clearAllMocks();
 Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:vi.fn().mockResolvedValue(stream)}});
 vi.stubGlobal('AudioContext',class{sampleRate=48000;state='running';audioWorklet={addModule:vi.fn().mockResolvedValue(undefined)};destination={};resume=vi.fn().mockResolvedValue(undefined);close=closeContext;createMediaStreamSource=()=>({connect:vi.fn(),disconnect:vi.fn()});});
 vi.stubGlobal('AudioWorkletNode',class{port={onmessage:null};constructor(){node=this;}connect(){}disconnect(){}});
 URL.createObjectURL=vi.fn(()=> 'blob:synthetic-test');URL.revokeObjectURL=vi.fn();
});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
it('captures only after user action and closes microphone before returning WAV',async()=>{
 render(<Microphone disabled={false} onFile={onFile} onActive={onActive}/>);
 expect(navigator.mediaDevices.getUserMedia).not.toHaveBeenCalled();
 fireEvent.click(screen.getByText('Start recording'));
 await waitFor(()=>expect(screen.getByText('Stop recording').hasAttribute('disabled')).toBe(false));
 act(()=>node.port.onmessage?.({data:new Float32Array([0,.1,-.1])}));
 fireEvent.click(screen.getByText('Stop recording'));
 expect(stopTrack).toHaveBeenCalledOnce();expect(closeContext).toHaveBeenCalledOnce();
 expect(onFile.mock.calls[0][0].type).toBe('audio/wav');expect(onFile.mock.calls[0][0].size).toBe(50);
 expect(onActive).toHaveBeenLastCalledWith(false);
});
it('releases permission-granted stream after leaving while permission was pending',async()=>{
 let resolve!:(value:MediaStream)=>void;
 vi.mocked(navigator.mediaDevices.getUserMedia).mockReturnValue(new Promise(r=>{resolve=r;}) as Promise<MediaStream>);
 const view=render(<Microphone disabled={false} onFile={onFile} onActive={onActive}/>);
 fireEvent.click(screen.getByText('Start recording'));view.unmount();
 await act(async()=>resolve(stream as unknown as MediaStream));expect(stopTrack).toHaveBeenCalledOnce();expect(onFile).not.toHaveBeenCalled();
});
it('permission denial does not create a recording or upload',async()=>{
 vi.mocked(navigator.mediaDevices.getUserMedia).mockRejectedValue(new Error('NotAllowedError'));
 render(<Microphone disabled={false} onFile={onFile} onActive={onActive}/>);
 fireEvent.click(screen.getByText('Start recording'));
 await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('Microphone unavailable'));
 expect(onFile).not.toHaveBeenCalled();expect(onActive).toHaveBeenLastCalledWith(false);
});
