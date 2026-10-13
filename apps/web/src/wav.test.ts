import {describe,it,expect} from 'vitest';
import {encodeWav} from './wav';
describe('local microphone WAV contract',()=>{
 it('writes mono PCM16 with exact frames, sample rate, clipping and silence',()=>{
  const wav=encodeWav([new Float32Array([-2,-1,0]),new Float32Array([1,2])],48000),v=new DataView(wav);
  expect(new TextDecoder().decode(wav.slice(0,4))).toBe('RIFF');
  expect(new TextDecoder().decode(wav.slice(8,12))).toBe('WAVE');
  expect(v.getUint16(22,true)).toBe(1);expect(v.getUint32(24,true)).toBe(48000);
  expect(v.getUint32(40,true)).toBe(10);expect(wav.byteLength).toBe(54);
  expect([0,1,2,3,4].map(i=>v.getInt16(44+2*i,true))).toEqual([-32768,-32768,0,32767,32767]);
 });
});
