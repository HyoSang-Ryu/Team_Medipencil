import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {UiLanguageProvider} from './UiLanguage';
import {ProvidedOverview} from './ProvidedOverview';
import {isSungahFamilyScreen} from './designVariant';

afterEach(cleanup);

it('keeps the Sungah-only visual variant tied to shared dated records and details',()=>{
 localStorage.setItem('medipencil.ui-language','en');
 const onDetails=vi.fn();
 render(<UiLanguageProvider><ProvidedOverview rows={[
  {date:'2026-10-11',sleep_hours:6,outdoor_minutes:10,fluids_dl:9},
  {date:'2026-10-12',sleep_hours:7,outdoor_minutes:20,fluids_dl:10},
  {date:'2026-10-13',sleep_hours:8,outdoor_minutes:30,fluids_dl:11,mood_label:'hyvä'},
 ]} today="2026-10-14" onDetails={onDetails}/></UiLanguageProvider>);
 const preview=document.querySelector('.sungah-three-day');
 expect(!!preview).toBe(isSungahFamilyScreen);
 if(isSungahFamilyScreen){
  expect(screen.getByText('No record for today yet.')).toBeTruthy();
  expect(preview?.querySelectorAll('.sungah-three-day-card').length).toBe(3);
  expect(preview?.textContent).toContain('30 min');
  expect(document.querySelectorAll('.sungah-topic').length).toBe(4);
  fireEvent.click(screen.getByRole('button',{name:/Outdoors: 30 min/}));
  expect(onDetails).toHaveBeenCalledWith('outdoor_minutes');
 }else{
  expect(document.querySelector('.sungah-update')).toBeNull();
 }
});
