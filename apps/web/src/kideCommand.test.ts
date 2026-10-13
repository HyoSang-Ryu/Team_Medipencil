import {describe,it,expect} from 'vitest';
import {hasKideCommand,removeKideCommand} from './kideCommand';
describe('KIDE end signal',()=>{
 it('requires terminal wake name and instruction',()=>{
  expect(hasKideCommand('정리해줘')).toBe(false);
  expect(hasKideCommand('KIDE is the assistant')).toBe(false);
  expect(hasKideCommand('KIDE, 정리해줘라고 말하면 됩니다')).toBe(false);
  for(const end of ['KIDE, 정리해줘.','키데 정리해 주세요','KIDE, summarize!','Kide tee yhteenveto.']){
   expect(hasKideCommand('Breakfast was half. '+end)).toBe(true);
   expect(removeKideCommand('Breakfast was half. '+end)).toBe('Breakfast was half.');
  }
 });
});
