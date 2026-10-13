/** Mono PCM16 WAV, accepted by the existing local STT upload contract. */
export function encodeWav(chunks:Float32Array[],sampleRate:number):ArrayBuffer {
 const count=chunks.reduce((n,c)=>n+c.length,0),buffer=new ArrayBuffer(44+count*2),view=new DataView(buffer);
 const text=(offset:number,value:string)=>{for(let i=0;i<value.length;i++)view.setUint8(offset+i,value.charCodeAt(i));};
 text(0,'RIFF');view.setUint32(4,36+count*2,true);text(8,'WAVE');text(12,'fmt ');view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,sampleRate,true);view.setUint32(28,sampleRate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);text(36,'data');view.setUint32(40,count*2,true);
 let offset=44;for(const chunk of chunks)for(const value of chunk){const s=Math.max(-1,Math.min(1,value));view.setInt16(offset,s<0?s*32768:s*32767,true);offset+=2;}return buffer;
}
