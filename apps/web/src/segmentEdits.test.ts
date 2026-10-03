import {expect,test,vi} from 'vitest';
import {prepareSegmentEdits} from './segmentEdits';
const segments=[{segment_id:'plan',text:'Walk planned.',type:'plan',speaker:'carer',required_scopes:['outdoors'],evidence_refs:[{source_id:'plan-source'}]},{segment_id:'statement',text:'Resident declined.',type:'statement',speaker:'resident',required_scopes:['health_context'],evidence_refs:[{source_id:'resident-source'}]}];
test('editing one segment cannot overwrite another statement or its evidence',async()=>{
 const save=vi.fn().mockResolvedValue({source_id:'new-source',version:1});
 const result=await prepareSegmentEdits(segments,{plan:'Walk planned tomorrow.'},false,save);
 expect(save).toHaveBeenCalledTimes(1);
 expect(result[0].text).toBe('Walk planned tomorrow.');
 expect(result[1]).toEqual(segments[1]);expect(result[0].evidence_refs).not.toEqual(result[1].evidence_refs);
 expect(segments[0].text).toBe('Walk planned.');
});
test('correction replaces each invalidated source separately without mixing scopes',async()=>{
 const save=vi.fn().mockResolvedValueOnce({source_id:'new-plan',version:1}).mockResolvedValueOnce({source_id:'new-statement',version:1});
 const result=await prepareSegmentEdits(segments,{},true,save);
 expect(result[0].evidence_refs).toEqual([{kind:'source',source_id:'new-plan',source_version:1}]);
 expect(result[1].evidence_refs).toEqual([{kind:'source',source_id:'new-statement',source_version:1}]);
 expect(result[1].required_scopes).toEqual(['health_context']);
 expect(save.mock.calls.every(c=>c[2].length===0)).toBe(true);
});
