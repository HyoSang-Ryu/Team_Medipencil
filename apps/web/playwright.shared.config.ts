import {defineConfig} from '@playwright/test';
if(!process.env.MEDIPENCIL_REVIEW_URL || !process.env.MEDIPENCIL_REVIEW_CREDENTIALS) throw new Error('Explicit shared review URL and private credential file required');
export default defineConfig({testDir:'./e2e',testMatch:['poc-sessions.spec.ts','shared-review.spec.ts'],workers:1,timeout:60000,retries:0,use:{trace:'off',screenshot:'off',video:'off'},reporter:'list'});
