import {afterEach,expect,test} from 'vitest';
import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import {UiLanguageProvider,useUiLanguage,uiText,swedishText,type Language} from './UiLanguage';
afterEach(()=>{cleanup();localStorage.clear();});
function Probe(){const {language,setLanguage,tr}=useUiLanguage();return <><span data-testid="language">{language}</span><p>{tr('사용자 매뉴얼')}</p><p>{uiText(language,'가족확인사항','Family questions','Läheisten kysymykset')}</p><input aria-label="draft"/>{(['fi','sv','ko','en'] as Language[]).map(l=><button key={l} onClick={()=>setLanguage(l)}>{l}</button>)}</>}
test('Finnish default and four persistent interface languages keep entered data',()=>{
 localStorage.clear();render(<UiLanguageProvider><Probe/></UiLanguageProvider>);
 expect(screen.getByTestId('language').textContent).toBe('fi');
 fireEvent.change(screen.getByLabelText('draft'),{target:{value:'Untranslated source'}});
 for(const [locale,manual] of [['sv','Användarhandbok'],['ko','사용자 매뉴얼'],['en','User manual'],['fi','Käyttöopas']]){
  fireEvent.click(screen.getByRole('button',{name:locale}));
  expect(screen.getByText(manual)).toBeTruthy();expect(document.documentElement.lang).toBe(locale);
  expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe('Untranslated source');
  expect(localStorage.getItem('medipencil.ui-language')).toBe(locale);
 }
});
test('Swedish UI substitutes numbers without rewriting content',()=>{
 expect(swedishText('Last 7 days')).toBe('Senaste 7 dagarna');
 expect(uiText('sv','수면','Sleep','Uni')).toBe('Sömn');
 expect(swedishText('An unknown original record')).toBe('An unknown original record');
 localStorage.setItem('medipencil.ui-language','sv');render(<UiLanguageProvider><Probe/></UiLanguageProvider>);
 expect(screen.getByTestId('language').textContent).toBe('sv');expect(screen.getByText('Närståendes frågor')).toBeTruthy();
});
