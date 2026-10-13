import {it,expect} from 'vitest';
import {ChunkBoundary} from './audioChunking';
it('waits for a speech boundary after six seconds and forces a cut at twelve',()=>{
 const cut=new ChunkBoundary();
 expect(cut.push(new Float32Array(6000).fill(.2),1000)).toBe(false);
 expect(cut.push(new Float32Array(500),1000)).toBe(false);
 expect(cut.push(new Float32Array(100),1000)).toBe(true);
 cut.reset();expect(cut.push(new Float32Array(11900).fill(.2),1000)).toBe(false);
 expect(cut.push(new Float32Array(100).fill(.2),1000)).toBe(true);
});
