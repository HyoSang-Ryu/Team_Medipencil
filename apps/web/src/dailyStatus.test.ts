import {expect,it} from 'vitest';
import {latestPair,numericChange,recordedStatus} from './dailyStatus';
it('compares latest dated records, excludes future records, does not require today',()=>{
 const p=latestPair([{date:'2026-10-14',sleep_hours:12},{date:'2026-10-01',sleep_hours:8},{date:'2026-10-06',sleep_hours:7}], '2026-10-13');
 expect(p.latest?.date).toBe('2026-10-06');expect(p.previous?.date).toBe('2026-10-01');expect(numericChange(p.latest!,p.previous,'sleep_hours').delta).toBe(-1);
});
it('keeps zero distinct from absent measurements and converts dL consistently',()=>{
 expect(numericChange({fluids_dl:0},{fluids_dl:12},'fluids_dl',100)).toEqual({value:0,delta:-1200});
 expect(numericChange({fluids_dl:null},{fluids_dl:12},'fluids_dl',100)).toEqual({value:null,delta:null});
 expect(numericChange({sleep_hours:8},{},'sleep_hours')).toEqual({value:8,delta:null});
});
it('does not turn numeric increases or ambiguous descriptions into good health',()=>{
 expect(recordedStatus(8)).toBe('unknown');expect(recordedStatus('ei hyvä')).toBe('unknown');expect(recordedStatus('hyvä')).toBe('good');expect(recordedStatus('huono')).toBe('poor');expect(recordedStatus('normaali')).toBe('normal');
});
