/** MediPencil's silence-aware splitting, shortened for the three-minute care note. */
export class ChunkBoundary {
 private elapsed=0;private silence=0;
 push(samples:Float32Array,rate:number){
  let squares=0;for(const sample of samples)squares+=sample*sample;
  const duration=samples.length/rate;this.elapsed+=duration;
  this.silence=samples.length&&Math.sqrt(squares/samples.length)<.01?this.silence+duration:0;
  return (this.elapsed>=6&&this.silence>=.6)||this.elapsed>=12;
 }
 reset(){this.elapsed=0;this.silence=0;}
}
