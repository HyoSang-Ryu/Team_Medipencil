import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('selected design keeps role login and family navigation working',async({page})=>{
 const xd=process.env.VITE_MEDIPENCIL_DESIGN==='xd';
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');
 await expect(page.locator('.xd-login')).toHaveCount(xd?1:0);
 await expect(page.locator('.login-portals a')).toHaveCount(2);
 await loginAs(page,'Liisa',false);
 await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.home-status-counts')).toHaveCount(xd?1:0);
 await page.getByTestId('guardian-detail-link').click();
 await page.getByTestId('detail-tab-history').click();
 await expect(page.locator('.date-presets')).toBeVisible();
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
