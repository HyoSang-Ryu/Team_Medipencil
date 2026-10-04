import { defineConfig } from 'vite';
export default defineConfig({base:process.env.MEDIPENCIL_WEB_BASE??'/',server:{host:'127.0.0.1', proxy:{'/api':`http://127.0.0.1:${process.env.MEDIPENCIL_API_PORT??'8000'}`}}});
