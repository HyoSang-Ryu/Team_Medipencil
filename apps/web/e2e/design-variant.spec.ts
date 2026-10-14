import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('selected design keeps role login and family navigation working',async({page})=>{
 const xd=process.env.VITE_MEDIPENCIL_DESIGN==='xd';
 const sungah=process.env.VITE_MEDIPENCIL_SUNGAH_FAMILY_SCREEN==='1';
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');
 await expect(page.locator('.xd-login')).toHaveCount(xd?1:0);
 await expect(page.locator('.login-portals a')).toHaveCount(2);
 await loginAs(page,'Liisa',false);
 await expect(page.getByTestId('guardian-home')).toBeVisible();
 await expect(page.locator('.home-status-counts')).toHaveCount(xd&&!sungah?1:0);
 const chart=page.locator('.guardian-home .dashboard-charts');
 await expect(chart).toHaveCount(xd&&!sungah?1:0);
 if(sungah){
  await expect(page.locator('.sungah-resident-card')).toBeVisible();
  await expect(page.locator('.sungah-update')).toBeVisible();
  await expect(page.locator('.sungah-original-topics a').first()).toBeVisible();
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.screenshot({path:'/tmp/sungah-family-original-dashboard.png',fullPage:true});
  await page.getByRole('navigation',{name:'Family navigation'}).getByRole('link',{name:'Messages'}).click();
  await expect(page.getByTestId('detail-tab-family')).toHaveAttribute('aria-pressed','true');
  await page.goBack();
 }
 if(xd&&!sungah){
  await expect(chart.locator('.trend-chart')).toBeVisible();
  await expect(chart.locator('.topic-bars>div')).toHaveCount(7);
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await chart.locator('select').selectOption('meals');
  await expect(chart.locator('select')).toHaveValue('meals');
  await page.context().setOffline(true);
  await expect(chart.getByRole('alert')).toBeVisible();
  await expect(chart.getByRole('img')).toHaveCount(0);
  await page.context().setOffline(false);
  await expect(chart.locator('.trend-chart')).toBeVisible();
 }
 await page.getByTestId('guardian-detail-link').click();
 await page.getByTestId('detail-tab-history').click();
 await expect(page.locator('.daily-board .date-presets')).toBeVisible();
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});
