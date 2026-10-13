import {it,expect} from 'vitest';
import {hasSerializedText,requireReadableResult} from './kideResultGuard';
it('rejects serialized payloads nested inside prose, notes or legacy results',()=>{
 for(const result of [{nursing_note:[{text_fi:'{"charting": []}'}]},{nursing_note:{arki:'```json\n{"metrics":{}}\n```'}},{family_notices:[{text_ko:'result:\n{"charting": []}'}]}]){
  expect(hasSerializedText(result)).toBe(true);expect(()=>requireReadableResult(result)).toThrow('KIDE_UNREADABLE_RESULT');
 }
});
it('accepts structured fields and preserves ordinary prose, null and zero',()=>{
 const data={metrics:{fluids_ml:0,sleep_hours:null},nursing_note:[{text_fi:'Asukas joi 200 ml.',text_ko:'수분 200 ml 섭취.'}]};expect(requireReadableResult(data)).toBe(data);
});
