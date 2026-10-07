import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./e2e-pages',workers:1,timeout:60000,retries:0,
 use:{trace:'off',screenshot:'off',video:'off'},reporter:'list'});
