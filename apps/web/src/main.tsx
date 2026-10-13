import {createRoot} from 'react-dom/client';
import {BrowserRouter,HashRouter,useLocation} from 'react-router-dom';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {UiLanguageProvider} from './UiLanguage';
import {KideDirectPage} from './KideDirectPage';
import {App} from './App';
import './style.css';
import {isXdDesign} from './designVariant';
if(isXdDesign)await import('./xd-theme.css');
const Router=import.meta.env.VITE_MEDIPENCIL_HASH_ROUTER==='1'?HashRouter:BrowserRouter;
const routerProps=import.meta.env.VITE_MEDIPENCIL_HASH_ROUTER==='1'?{}:{basename:import.meta.env.BASE_URL};
function Entry(){const location=useLocation();return location.pathname==='/kide-direct'?<KideDirectPage/>:<App/>;}
const queryClient=new QueryClient({defaultOptions:{queries:{retry:false,gcTime:0}}});
createRoot(document.getElementById('root')!).render(<QueryClientProvider client={queryClient}><Router {...routerProps}><UiLanguageProvider><Entry/></UiLanguageProvider></Router></QueryClientProvider>);
