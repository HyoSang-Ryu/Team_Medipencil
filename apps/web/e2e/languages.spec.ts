import {test,expect} from '@playwright/test';

test('three separate languages preserve sessions and input, remember preference and localize every manual',async({browser})=>{
 const base=(process.env.MEDIPENCIL_REVIEW_URL??'http://127.0.0.1:5179').replace(/\/$/,'');
 const context=await browser.newContext();const page=await context.newPage();
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(base);
  const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Koskinen',exact:true}).click();await login;
  const cookie=(await context.cookies()).find(c=>c.name==='mp_session')?.value;expect(cookie).toBeTruthy();
  await page.getByRole('link',{name:'Kirjaa ja julkaise',exact:true}).click();
  const original='SYNTHETIC LANGUAGE TEST: suunnitelma / 계획 / plan';
  await page.getByRole('textbox',{name:'Alkuperäinen teksti',exact:true}).fill(original);
  const languages=[
   {id:'fi',input:'Alkuperäinen teksti',manual:'Käyttöopas',back:'Palaa työskentelyyn',search:'Hae oppaasta',comments:'Tiimin kommentit',alias:'Arvioijan nimimerkki'},
   {id:'ko',input:'원문',manual:'사용자 매뉴얼',back:'사용 화면으로 돌아가기',search:'매뉴얼 검색',comments:'팀 코멘트',alias:'익명 팀원 별칭'},
   {id:'en',input:'Original text',manual:'User manual',back:'Back to work',search:'Search this manual',comments:'Team comments',alias:'Anonymous reviewer alias'},
  ];
  for(const l of languages){
   await page.locator('.interface-control select').selectOption(l.id);
   await expect(page.locator('html')).toHaveAttribute('lang',l.id);
   await expect(page.getByRole('textbox',{name:l.input,exact:true})).toHaveValue(original);
   expect((await context.cookies()).find(c=>c.name==='mp_session')?.value).toBe(cookie);
   await expect(page.getByRole('button',{name:'Koskinen',exact:true})).toHaveAttribute('aria-pressed','true');
   await page.getByRole('link',{name:l.manual,exact:true}).click();
   await expect(page.getByRole('heading',{name:l.manual,exact:true})).toBeVisible();
   await expect(page.locator('.manual-section')).toHaveCount(14);
   await page.getByRole('searchbox',{name:l.search,exact:true}).fill('PROVIDER_NOT_CONFIGURED');
   await expect(page.locator('.manual-section')).toHaveCount(1);
   await page.getByRole('searchbox',{name:l.search,exact:true}).fill('');
   if(l.id==='fi')expect((await page.locator('.user-manual').innerText()).replaceAll('한국어','')).not.toMatch(/[가-힣]/);
   for(const width of [1280,390,360]){
    await page.setViewportSize({width,height:900});
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    if(width===390)await page.screenshot({path:`/tmp/medipencil-language-${l.id}.png`});
   }
   await page.getByRole('button',{name:l.back,exact:true}).first().click();
   await expect(page.getByRole('textbox',{name:l.input,exact:true})).toHaveValue(original);
  }
  await page.getByRole('link',{name:'Team comments',exact:true}).click();
  for(const l of languages){
   await page.locator('.interface-control select').selectOption(l.id);
   await expect(page.getByRole('heading',{name:l.comments,exact:true})).toBeVisible();
   await expect(page.getByRole('textbox',{name:l.alias,exact:true})).toBeVisible();
   await page.getByRole('textbox',{name:l.alias,exact:true}).fill('AUTO-UNSAVED');
  }
  await page.locator('.interface-control select').selectOption('ko');
  await expect(page.getByRole('textbox',{name:'익명 팀원 별칭',exact:true})).toHaveValue('AUTO-UNSAVED');
  await page.reload();
  await expect(page.locator('.interface-control select')).toHaveValue('ko');
  await expect(page.locator('html')).toHaveAttribute('lang','ko');
  await page.getByRole('link',{name:'사용자 매뉴얼',exact:true}).click();
  await expect(page.getByRole('heading',{name:'사용자 매뉴얼',exact:true})).toBeVisible();
  expect(errors).toEqual([]);
 }finally{await context.close();}
});
