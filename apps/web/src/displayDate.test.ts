import {describe,it,expect} from 'vitest';
import {displayDate} from './displayDate';
import {familyResidentLabel} from './familyIdentity';

describe('Finnish display conventions',()=>{
 it('formats date-only labels without timezone conversion or changing other locales',()=>{
  expect(displayDate('2026-01-02','fi')).toBe('02-01-2026');
  expect(displayDate('2026-12-31','fi')).toBe('31-12-2026');
  for(const locale of ['ko','en','sv'] as const)expect(displayDate('2026-01-02',locale)).toBe('2026-01-02');
  expect(displayDate(null,'fi')).toBe('—');
 });
 it('separates the Finnish relationship from the parenthesis',()=>{
  expect(familyResidentLabel({name:'Aino',age:75,relationship:'mother'},'fi')).toBe('Äiti (Aino, 75 v)');
 });
});
