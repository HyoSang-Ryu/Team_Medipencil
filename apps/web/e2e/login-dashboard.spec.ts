import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('login dashboard identifies the user and role, logout revokes session',async({page})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('ko');
 await expect(page.getByRole('heading',{name:'로그인',exact:true})).toBeVisible();
 await expect(page.getByTestId('viewer-identity')).toHaveCount(0);
 for(const width of [1280,360]){
  await page.setViewportSize({width,height:900});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:`/tmp/care-loop-login-${width}.png`,fullPage:true});
 }
 await loginAs(page,'Liisa');
 await expect(page.getByTestId('viewer-identity')).toHaveText('Liisa(보호자)');
 await expect(page.getByRole('heading',{name:'Liisa · 나의 대시보드'})).toBeVisible();
 await expect(page.getByRole('link',{name:'기록 작성하기 →'})).toHaveCount(0);
 const logout=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='DELETE');
 await page.getByTestId('logout').click();expect((await logout).status()).toBe(204);
 await expect(page.getByRole('heading',{name:'로그인',exact:true})).toBeVisible();
 expect((await page.request.get('/api/v1/session')).status()).toBe(401);
 await loginAs(page,'Koskinen');
 await expect(page.getByTestId('viewer-identity')).toHaveText('Koskinen(간호사)');
 await expect(page.getByRole('heading',{name:'Koskinen · 나의 대시보드'})).toBeVisible();
 await expect(page.getByRole('link',{name:'기록 작성하기 →'})).toBeVisible();
 await page.setViewportSize({width:1280,height:900});
 await page.screenshot({path:'/tmp/care-loop-staff-dashboard.png',fullPage:true});
});
