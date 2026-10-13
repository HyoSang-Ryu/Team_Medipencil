import {test,expect} from '@playwright/test';
test('direct KIDE screen opens without contacting the service API',async({page})=>{
 const calls:string[]=[];
 await page.route('**/api/v1/**',route=>{calls.push(route.request().url());return route.abort();});
 await page.goto('/kide-direct');
 await expect(page.getByRole('heading',{name:'KIDE',exact:true})).toBeVisible();
 await page.reload();
 await expect(page.locator('input[type=password], input[type=url]')).toHaveCount(0);
 await page.locator('.microphone-panel input[type=checkbox]').check();
 await expect(page.locator('.microphone-panel > button').first()).toBeEnabled();
 // A fresh build connects automatically, including after reload.
 await page.reload();
 await expect(page.locator('.microphone-panel details')).toHaveCount(0);
 await page.locator('.microphone-panel input[type=checkbox]').check();
 await expect(page.locator('.microphone-panel > button').first()).toBeEnabled();
 expect(calls).toEqual([]);
});
