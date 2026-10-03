import {createRoot} from 'react-dom/client';
import {BrowserRouter} from 'react-router-dom';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {UiLanguageProvider} from './UiLanguage';
import {App} from './App';
import './style.css';
const queryClient=new QueryClient({defaultOptions:{queries:{retry:false,gcTime:0}}});
createRoot(document.getElementById('root')!).render(<QueryClientProvider client={queryClient}><BrowserRouter><UiLanguageProvider><App/></UiLanguageProvider></BrowserRouter></QueryClientProvider>);
