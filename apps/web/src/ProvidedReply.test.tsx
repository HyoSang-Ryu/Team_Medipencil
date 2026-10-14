import {render,screen,fireEvent,cleanup,waitFor,within} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {UiLanguageProvider} from './UiLanguage';
import {ProvidedReply} from './ProvidedReply';
afterEach(cleanup);
it('binds independent reply and review state to each question, and resets review after an edit',async()=>{
 localStorage.setItem('medipencil.ui-language','en');const first=vi.fn().mockResolvedValue(undefined),second=vi.fn().mockResolvedValue(undefined);
 render(<UiLanguageProvider><article data-testid="one"><ProvidedReply id="one" busy={false} save={first}/></article><article data-testid="two"><ProvidedReply id="two" busy={false} save={second}/></article></UiLanguageProvider>);
 const a=within(screen.getByTestId('one')),b=within(screen.getByTestId('two'));
 fireEvent.change(a.getByRole('textbox'),{target:{value:'Asukas söi aamupalan.'}});fireEvent.click(a.getByRole('checkbox'));
 expect((a.getByRole('button') as HTMLButtonElement).disabled).toBe(false);expect((b.getByRole('button') as HTMLButtonElement).disabled).toBe(true);
 fireEvent.change(a.getByRole('textbox'),{target:{value:'Asukas söi lounaan.'}});expect((a.getByRole('button') as HTMLButtonElement).disabled).toBe(true);
 fireEvent.click(a.getByRole('checkbox'));fireEvent.click(a.getByRole('button'));
 await waitFor(()=>expect(first).toHaveBeenCalledWith('Asukas söi lounaan.'));expect(second).not.toHaveBeenCalled();await waitFor(()=>expect((a.getByRole('textbox') as HTMLTextAreaElement).value).toBe(''));
});
it('retains the answer on failure for retry',async()=>{
 localStorage.setItem('medipencil.ui-language','en');const save=vi.fn().mockRejectedValue(new Error('network'));
 render(<UiLanguageProvider><ProvidedReply id="retry" busy={false} save={save}/></UiLanguageProvider>);
 fireEvent.change(screen.getByRole('textbox'),{target:{value:'Asukas ulkoili.'}});fireEvent.click(screen.getByRole('checkbox'));fireEvent.click(screen.getByRole('button'));
 await waitFor(()=>expect(save).toHaveBeenCalledOnce());expect((screen.getByRole('textbox') as HTMLTextAreaElement).value).toBe('Asukas ulkoili.');
});
