import type {Segment} from './Capture';
// Preserve each segment's identity, classification, and evidence independently.
export async function prepareSegmentEdits(
 segments:Segment[],texts:Record<string,string>,correction:boolean,
 saveSource:(segment:Segment,text:string,refs:unknown[])=>Promise<{source_id:string;version:number}>
):Promise<Segment[]>{
 const result:Segment[]=[];
 for(const segment of segments){
  const text=texts[segment.segment_id]??segment.text;
  if(!correction&&text===segment.text){result.push(segment);continue;}
  const source=await saveSource(segment,text,correction?[]:segment.evidence_refs);
  result.push({...segment,text,evidence_refs:[{kind:'source',source_id:source.source_id,source_version:source.version}]});
 }
 return result;
}
