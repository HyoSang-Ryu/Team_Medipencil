import { defineConfig } from 'vite';
import {fileURLToPath} from 'node:url';
export default defineConfig({base:process.env.MEDIPENCIL_WEB_BASE??'/',resolve:{alias:{'@sungah-family-style':fileURLToPath(new URL(process.env.VITE_MEDIPENCIL_SUNGAH_FAMILY_SCREEN==='1'?'./src/sungah-family.css':'./src/sungah-empty.css',import.meta.url))}},server:{host:'127.0.0.1', proxy:{'/api':`http://127.0.0.1:${process.env.MEDIPENCIL_API_PORT??'8000'}`}}});
