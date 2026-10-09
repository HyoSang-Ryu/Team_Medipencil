import {loginAs} from './login';
import {test,expect} from '@playwright/test';

test('manual is public, searchable and multilingual; returning preserves the record input',async({browser})=>{
 const base=(process.env.MEDIPENCIL_REVIEW_URL??'http://127.0.0.1:5179').replace(/\/$/,'');
 const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 try {
  await page.goto(base+'/manual');
  await page.locator('.interface-control select').selectOption('ko');
  await expect(page.getByRole('heading',{name:'사용자 매뉴얼',exact:true})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'매뉴얼 목차'}).getByRole('link')).toHaveCount(15);
  await page.getByLabel('매뉴얼 검색',{exact:true}).fill('PROVIDER_NOT_CONFIGURED');
  await expect(page.locator('.manual-section')).toHaveCount(1);
  await expect(page.getByRole('heading',{name:'문제 해결 · 버튼이 안 눌리거나 내용이 안 보일 때'})).toBeVisible();
  await page.getByLabel('매뉴얼 검색',{exact:true}).fill('no-such-manual-topic-xyz');
  await expect(page.getByRole('heading',{name:'검색 결과가 없습니다'})).toBeVisible();
  await page.getByRole('button',{name:'검색어 지우기',exact:true}).click();
  await page.getByRole('navigation',{name:'매뉴얼 목차'}).getByRole('link',{name:'보호자 공유 설정',exact:true}).click();
  await expect(page.locator('#manual-consent')).toBeFocused();
  await page.locator('.interface-control select').selectOption('en');
  await expect(page.getByRole('heading',{name:'User manual',exact:true})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Manual contents'}).getByRole('link')).toHaveCount(15);
  await page.getByRole('button',{name:'Back to work',exact:true}).first().click();
  const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
  await loginAs(page,'Koskinen');await login;
  await page.getByRole('link',{name:'Record and publish',exact:true}).click();
  const draft='Manual navigation must keep this unsaved synthetic text.';
  await page.getByRole('textbox',{name:'Original text',exact:true}).fill(draft);
  await page.getByRole('link',{name:'User manual',exact:true}).click();
  await expect(page.getByRole('heading',{name:'User manual',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Back to work',exact:true}).first().click();
  await expect(page.getByRole('textbox',{name:'Original text',exact:true})).toHaveValue(draft);
  await page.getByRole('link',{name:'User manual',exact:true}).click();
  await page.goBack();
  await expect(page.getByRole('textbox',{name:'Original text',exact:true})).toHaveValue(draft);
  await page.getByRole('link',{name:'User manual',exact:true}).click();
  await page.locator('.interface-control select').selectOption('fi');
  for(const width of [1280,390,360]){
   await page.setViewportSize({width,height:900});
   await page.evaluate(()=>window.scrollTo(0,0));
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
   await page.screenshot({path:`/tmp/medipencil-manual-${width}.png`});
  }
  expect(errors).toEqual([]);
 } finally {await context.close();}
});
