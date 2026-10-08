import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('guardian lands on visual overview, opens details and returns; offline data is hidden',async({page,context})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('ko');await loginAs(page,'Liisa',false);
 await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.daily-board')).toHaveCount(0);await expect(page.locator('#ask-nurse')).toHaveCount(0);
 await expect(page.locator('.trend-chart')).toBeVisible();
 for(const width of [1280,390]){await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:`/tmp/guardian-home-${width}.png`,fullPage:true});}
 await page.getByTestId('guardian-detail-link').click();await expect(page.locator('.daily-board')).toBeVisible();await expect(page.locator('#ask-nurse')).toBeVisible();
 await page.getByRole('link',{name:'대시보드',exact:true}).click();await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.trend-chart')).toBeVisible();await context.setOffline(true);await expect(page.locator('.trend-chart')).toHaveCount(0);await expect(page.locator('.home-number').first()).toHaveText('—');
 await context.setOffline(false);await expect(page.locator('.trend-chart')).toBeVisible();
 await page.getByTestId('logout').click();await expect(page.getByTestId('guardian-home')).toHaveCount(0);
});
test('overview hides restricted topics and language changes preserve navigation',async({page})=>{
 await page.goto('/');await loginAs(page,'Mikko',false);await expect(page.locator('.radar-chart')).toBeVisible();
 await expect(page.locator('.radar-chart')).not.toContainText('Lääkitys');
 await page.locator('.interface-control select').selectOption('en');await expect(page.getByRole('heading',{name:'Aino at a glance'})).toBeVisible();
 await page.getByTestId('guardian-detail-link').click();await expect(page.locator('.daily-board')).toBeVisible();
});
