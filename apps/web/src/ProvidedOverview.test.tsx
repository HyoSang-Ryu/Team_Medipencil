import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {UiLanguageProvider} from './UiLanguage';
import {ProvidedOverview} from './ProvidedOverview';
afterEach(cleanup);
it('shows only shared topics, explicit assessment and dated deltas, with details navigation',()=>{
 localStorage.setItem('medipencil.ui-language','en');const open=vi.fn();
 render(<UiLanguageProvider><ProvidedOverview rows={[{date:'2026-10-01',sleep_hours:8},{date:'2026-10-02',sleep_hours:7,sleep_quality:'huono'}]} today="2026-10-13" onDetails={open}/></UiLanguageProvider>);
 expect(screen.getByText('Poor')).toBeTruthy();expect(screen.getByText('−1 h')).toBeTruthy();expect(screen.queryByText('Fluids')).toBeNull();expect(screen.getByText(/No record for today/)).toBeTruthy();expect(document.querySelectorAll('svg[role=img]').length).toBe(0);
 fireEvent.click(screen.getByRole('button',{name:/View trends/}));expect(open).toHaveBeenCalledOnce();
});

it('uses up, down and minus icons while keeping missing comparisons distinct',()=>{
 localStorage.setItem('medipencil.ui-language','en');
 render(<UiLanguageProvider><ProvidedOverview rows={[{date:'2026-10-12',sleep_hours:8,fluids_dl:10,outdoor_minutes:20},{date:'2026-10-13',sleep_hours:7,fluids_dl:12,outdoor_minutes:20,mood_label:'hyvä'}]} today="2026-10-13" onDetails={()=>{}}/></UiLanguageProvider>);
 expect(screen.getByRole('img',{name:'Up from previous record'})).toBeTruthy();
 expect(screen.getByRole('img',{name:'Down from previous record'})).toBeTruthy();
 expect(screen.getByRole('img',{name:'Unchanged'})).toBeTruthy();
 expect(screen.getByRole('img',{name:'No comparison'})).toBeTruthy();
});
