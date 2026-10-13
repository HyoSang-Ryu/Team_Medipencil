import {test,expect} from '@playwright/test';
test('direct KIDE screen opens without contacting the service API',async({page})=>{
 const calls:string[]=[];
 await page.route('**/api/v1/**',route=>{calls.push(route.request().url());return route.abort();});
 await page.goto('/kide-direct');
 await expect(page.getByRole('heading',{name:'KIDE',exact:true})).toBeVisible();
 await expect(page.locator('input[type=password]')).toBeVisible();
 expect(calls).toEqual([]);
});
