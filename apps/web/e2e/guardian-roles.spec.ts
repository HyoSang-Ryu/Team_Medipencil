import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('Aino has no login; separate guardians see server-defined sharing permissions',async({browser})=>{
 const contexts=await Promise.all([browser.newContext(),browser.newContext(),browser.newContext()]);
 try{
  const pages=await Promise.all(contexts.map(c=>c.newPage()));
  for(const page of pages){await page.goto('/');await page.locator('.interface-control select').selectOption('ko');}
  await expect(pages[0].getByRole('button',{name:'Aino',exact:true})).toHaveCount(0);
  await expect(pages[0].getByText('Aino는 돌봄 대상자이며 로그인하지 않습니다. 보호자 2명과 간호사 1명이 사용합니다.')).toBeVisible();
  await loginAs(pages[0],'Liisa');await loginAs(pages[1],'Mikko');await loginAs(pages[2],'Koskinen');
  await expect(pages[0].getByTestId('viewer-identity')).toHaveText('Liisa(보호자)');
  await expect(pages[1].getByTestId('viewer-identity')).toHaveText('Mikko(보호자)');
  await expect(pages[2].getByTestId('viewer-identity')).toHaveText('Koskinen(간호사)');
  await expect(pages[0].getByTestId('scope-liisa-medication')).toHaveAttribute('data-shared','true');
  await expect(pages[1].getByTestId('scope-mikko-medication')).toHaveAttribute('data-shared','false');
  await expect(pages[1].getByTestId('scope-mikko-meals')).toHaveAttribute('data-shared','true');
  await expect(pages[2].getByRole('heading',{name:'보호자별 공유 범위'})).toBeVisible();
  await expect(pages[2].getByTestId('scope-mikko-medication')).toHaveAttribute('data-shared','false');
  for(const page of pages.slice(0,2))expect((await page.request.get('/api/v1/staff/residents/aino/consents')).status()).toBe(403);
  await pages[1].setViewportSize({width:390,height:844});
  expect(await pages[1].evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await pages[1].screenshot({path:'/tmp/care-loop-mikko-permissions.png',fullPage:true});
 }finally{await Promise.all(contexts.map(c=>c.close()));}
});
