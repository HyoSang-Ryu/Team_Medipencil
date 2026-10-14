import {render,screen,cleanup} from '@testing-library/react';
import {afterEach,it,expect} from 'vitest';
import {UiLanguageProvider} from './UiLanguage';
import {KideV4Details,type V4} from './KideV4';
afterEach(cleanup);
const empty:V4={charting:[{area:'1_daily_living',topic:'assistance',value_fi:'ei kirjattu',value_ko:'기록되지 않음',claim_type:'missing',source_ko:null}],missing_questions:[{area:'1_daily_living',topic:'assistance',question_ko:'지원이 필요했나요?',question_fi:'Tarvittiinko apua?',if_unanswered_fi:'Ei kirjattu'}],nursing_note:[{area:'1_daily_living',text_fi:'Ruokailu: ei kirjattu.',text_ko:'식사: 기록되지 않음.'}],metrics:{meals_eaten:0,sleep_hours:null},family_notices:[],family_filter_excluded:[]};
function show(data:V4){localStorage.setItem('medipencil.ui-language','ko');return render(<UiLanguageProvider><KideV4Details data={data}/></UiLanguageProvider>);}
it('omits follow-up questions, empty records and placeholder metrics',()=>{const {container}=show(empty);expect(screen.getByRole('status').textContent).toContain('ei ole riittävästi');expect(screen.queryByText('Tarvittiinko apua?')).toBeNull();expect(screen.queryByText('Ruokailu: ei kirjattu.')).toBeNull();expect(container.querySelector('pre')).toBeNull();expect(container.textContent).not.toContain('meals_eaten');});
it('renders only Finnish result even when interface and speech are Korean',()=>{const {container}=show({...empty,charting:[{...empty.charting[0],claim_type:'plan',value_fi:'Ulkoilu suunniteltu.',value_ko:'산책 예정.',source_ko:'산책할 예정입니다.'}],nursing_note:[{area:'1_daily_living',text_fi:'Ulkoilu suunniteltu.',text_ko:'산책 예정입니다.'}]});expect(container.textContent).not.toMatch(/[가-힣]/);expect(screen.getByText('Suunnitelma · toteutumista ei vahvistettu')).toBeTruthy();expect(screen.getByText('Unen kesto')).toBeTruthy();expect(screen.getByText('Ei kirjattu')).toBeTruthy();expect(container.querySelector('pre')).toBeNull();});

it('never renders JSON strings embedded in provider note text',()=>{const {container}=show({...empty,nursing_note:[{area:'1_daily_living',text_fi:'{"charting": []}',text_ko:'번역'}]});expect(screen.getByRole('alert').textContent).toContain('muoto');expect(container.textContent).not.toContain('charting');});

it('does not display Korean returned inside Finnish result fields',()=>{
 const {container}=show({...empty,
  charting:[{...empty.charting[0],claim_type:'observation',value_fi:'한국어 값',source_ko:'한국어 발화 근거'}],
  nursing_note:[{area:'1_daily_living',text_fi:'한국어 간호기록',text_ko:'검토용 한국어'}],
  family_notices:[{guardian:'Demo guardian',relation:'lapsi',send:true,text_fi:'한국어 보호자 안내',text_ko:'한국어',reason_ko:'한국어'}],
 });
 expect(container.textContent).not.toMatch(/[가-힣]/);
 expect(container.textContent).toContain('Suomenkielinen teksti puuttuu.');
});
