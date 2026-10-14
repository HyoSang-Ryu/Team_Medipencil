import {render,screen,cleanup} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {MemoryRouter} from 'react-router-dom';
import {UiLanguageProvider} from './UiLanguage';
import {ProvidedWorkspace} from './ProvidedWorkspace';
vi.mock('./KideWorkflow',()=>({KideWorkflow:()=>null,KideFamily:()=>null}));
vi.mock('./api',()=>({api:vi.fn(async(path:string)=>path.includes('/sharing')?{items:[]}:{subject:{label:'Independent synthetic resident',unit:'Test'},daily:[{date:'2026-10-13',sleep_hours:7,fluids_dl:12,outdoor_minutes:10,breakfast:'syöty',mood_label:'hyvä',social_interaction:'Perhe vieraili.'}],questions:[],notes:[],groups:[],today:'2026-10-14'}),upload:vi.fn()}));
afterEach(cleanup);
it('details includes all six overview topics with categorical source records',async()=>{
 localStorage.setItem('medipencil.ui-language','en');
 render(<MemoryRouter initialEntries={['/family/provided?view=details']}><UiLanguageProvider><ProvidedWorkspace subject="A" staff={false} page="/family/provided"/></UiLanguageProvider></MemoryRouter>);
 for(const name of ['Sleep','Fluids','Outdoors','Meals','Mood','Social interaction'])expect(await screen.findByRole('heading',{name})).toBeTruthy();
 expect(screen.getAllByText('Perhe vieraili.').length).toBeGreaterThan(0);
});
