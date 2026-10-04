import {test,expect} from '@playwright/test';
test('public PoC loads without credentials and lets visitor choose all synthetic roles',async({browser,request})=>{
 const base=process.env.MEDIPENCIL_REVIEW_URL!.replace(/\/$/,'');
 const response=await request.get(base+'/');
 expect(response.status()).toBe(200);expect(response.headers()['www-authenticate']).toBeUndefined();
 const context=await browser.newContext();const page=await context.newPage();
 try {
  await page.goto(base+'/');
  await expect(page.locator('.role-picker button')).toHaveCount(3);
  for(const actor of ['Liisa','Mikko','Koskinen']) {
   const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await page.getByRole('button',{name:actor,exact:true}).click();
   const logged=await login;expect(logged.status()).toBe(201);
   expect((await logged.json()).data.authentication).toBe('PUBLIC_SYNTHETIC_POC');
   await expect(page.getByRole('button',{name:actor,exact:true})).toBeEnabled();
  }
  await page.getByRole('link',{name:'팀 코멘트',exact:true}).click();
  await expect(page.getByRole('heading',{name:'팀 코멘트',exact:true})).toBeVisible();
  await page.screenshot({path:'/tmp/medipencil-public-poc.png',fullPage:true});
 } finally {await context.close();}
});
