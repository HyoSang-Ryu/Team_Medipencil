import {test,expect} from '@playwright/test';
test.use({launchOptions:{args:['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']}});
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

test('unavailable speech engine gives an actionable error and permits retry',async({page})=>{
 await page.routeWebSocket('wss://him-tax-shop-pcs.trycloudflare.com/**',ws=>ws.send(JSON.stringify({type:'error',message:'engine unavailable'})));
 await page.goto('/kide-direct');
 await page.locator('.microphone-panel input[type=checkbox]').check();
 await page.locator('.microphone-panel > button').first().click();
 await expect(page.getByRole('alert')).toContainText('Puheentunnistusmoottori ei ole käytettävissä');
 await expect(page.locator('.microphone-panel > button').first()).toBeEnabled();
 await expect(page.getByTestId('kide-result')).toHaveCount(0);
});
