import {defineConfig} from '@playwright/test';
if(!process.env.MEDIPENCIL_REVIEW_URL || process.env.MEDIPENCIL_REVIEW_CREDENTIALS) throw new Error('Public review requires an explicit URL and no credential file');
export default defineConfig({testDir:'./e2e',testMatch:['poc-sessions.spec.ts','public-review.spec.ts'],workers:1,timeout:60000,retries:0,use:{trace:'off',screenshot:'off',video:'off'},reporter:'list'});
