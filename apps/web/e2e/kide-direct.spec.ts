import {test,expect} from '@playwright/test';
test('direct KIDE screen opens without contacting the service API',async({page})=>{
 const calls:string[]=[];
 await page.route('**/api/v1/**',route=>{calls.push(route.request().url());return route.abort();});
 await page.goto('/kide-direct');
 await expect(page.getByRole('heading',{name:'KIDE',exact:true})).toBeVisible();
 const settings=page.locator('.microphone-panel details');
 await expect(page.locator('input[type=password]')).not.toBeVisible();
 await settings.locator('summary').click();
 await expect(page.locator('input[type=password]')).toBeVisible();
 await page.locator('input[type=password]').fill('synthetic-ui-test-key');
 await settings.getByRole('button').click();
 await expect(settings).toHaveCount(0);
 await expect(page.locator('input[type=password]')).toHaveCount(0);
 await page.locator('.microphone-panel input[type=checkbox]').check();
 await expect(page.locator('.microphone-panel > button').first()).toBeEnabled();
 // A reload really clears the memory-only key; never imply a global key was installed.
 await page.reload();
 await expect(page.locator('.microphone-panel details')).toHaveCount(1);
 await expect(page.locator('input[type=password]')).not.toBeVisible();
 await expect(page.locator('.microphone-panel > button').first()).toBeDisabled();
 expect(calls).toEqual([]);
});
