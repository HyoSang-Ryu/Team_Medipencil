import {test,expect} from '@playwright/test';
import {loginAs,logoutCurrent,setInterfaceLanguage} from './login';
test('guardian lands on visual overview, opens details and returns; offline data is hidden',async({page,context})=>{
 await page.goto('/');await setInterfaceLanguage(page,'ko');await loginAs(page,'Liisa',false);
 await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.daily-board')).toHaveCount(0);await expect(page.locator('#ask-nurse')).toHaveCount(0);
 await expect(page.locator('.home-care-tile').first()).toBeVisible();await expect(page.locator('.trend-chart')).toHaveCount(0);
 for(const width of [1280,390,320]){await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:`/tmp/guardian-home-${width}.png`,fullPage:true});}
 expect(await page.locator('.guardian-mobile').evaluate(el=>el.getBoundingClientRect().width)).toBeLessThanOrEqual(430);
 await page.getByTestId('guardian-detail-link').click();await expect(page.locator('.daily-board')).toBeVisible();await expect(page.locator('#ask-nurse')).toBeHidden();await page.getByTestId('detail-tab-family').click();await expect(page.locator('#ask-nurse')).toBeVisible();
 await page.getByTestId('guardian-menu-toggle').click();await page.getByRole('link',{name:'대시보드',exact:true}).click();await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.home-care-tile').first()).toBeVisible();await expect(page.locator('.trend-chart')).toHaveCount(0);await context.setOffline(true);await expect(page.locator('.trend-chart')).toHaveCount(0);await expect(page.locator('.home-number').first()).toHaveText('—');
 await context.setOffline(false);await expect(page.locator('.home-care-tile').first()).toBeVisible();await expect(page.locator('.trend-chart')).toHaveCount(0);
 await logoutCurrent(page);await expect(page.getByTestId('guardian-home')).toHaveCount(0);
});
test('overview hides restricted topics and language changes preserve navigation',async({page})=>{
 await page.goto('/');await loginAs(page,'Mikko',false);await expect(page.locator('.home-care-tile')).toHaveCount(3);
 await expect(page.locator('.home-care')).not.toContainText('Lääkitys');
 await setInterfaceLanguage(page,'en');await expect(page.getByRole('heading',{name:'Mom(Helmi Nieminen, 84 years)'})).toBeVisible();
 await page.getByTestId('guardian-detail-link').click();await expect(page.locator('.daily-board')).toBeVisible();
});
