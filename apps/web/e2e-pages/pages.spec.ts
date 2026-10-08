import {loginAs} from '../e2e/login';
import {test,expect} from '@playwright/test';
const base='https://hyosang-ryu.github.io/Team_Medipencil/';

test('GitHub Pages loads and reaches shared API without VPN or third-party cookies',async({browser})=>{
 const context=await browser.newContext();const page=await context.newPage();
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(base);
  await page.locator('.interface-control select').selectOption('en');
  for(const actor of ['Liisa','Koskinen']){
   const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await loginAs(page,actor,false);
   if(actor==='Koskinen'){await expect(page.getByTestId('staff-review')).toBeVisible();await page.locator('a[href$="/staff/queue"]').first().click();}
   if(actor==='Liisa'){await expect(page.getByTestId('guardian-home')).toBeVisible();await expect(page.locator('.daily-board')).toHaveCount(0);await page.getByTestId('guardian-detail-link').click();}
   const response=await login;expect(response.status()).toBe(201);
   expect((await response.json()).data.access_token).toBeTruthy();
   await expect(page.getByTestId('viewer-identity')).toContainText(actor);
   await expect(page.locator('.question-board h2')).toBeVisible();
   if(actor!=='Koskinen')await page.getByText('Explore record counts by date',{exact:true}).click();
   await expect(page.getByRole('region',{name:'Care records at a glance'}).locator('.care-topic-card')).toHaveCount(6);
  }
  await page.getByRole('link',{name:'Team comments',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Team comments',exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Refresh comments',exact:true})).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
  await page.getByRole('link',{name:'User manual',exact:true}).click();
  await expect(page.locator('.manual-section')).toHaveCount(15);
  await page.reload();
  await expect(page.getByRole('heading',{name:'User manual',exact:true})).toBeVisible();
  expect((await context.cookies()).filter(c=>c.name==='mp_session')).toHaveLength(0);
  expect(await page.evaluate(()=>Object.keys(localStorage))).toEqual(['medipencil.ui-language']);
  expect(errors).toEqual([]);
 }finally{await context.close();}
});

test('Pages family and staff share a real question, approved publication and saved comment',async({browser})=>{
 test.skip(process.env.MEDIPENCIL_PAGES_WRITE_TEST!=='1','Explicit synthetic write verification only');
 const contexts=await Promise.all([browser.newContext(),browser.newContext()]);
 const [family,staff]=await Promise.all(contexts.map(c=>c.newPage()));
 const marker='AUTO-PAGES-'+Date.now();const source=`${marker}: A walk is planned; completion is not confirmed.`;
 try{
  for(const [page,actor] of [[family,'Liisa'],[staff,'Koskinen']] as const){
   await page.goto(base);await page.locator('.interface-control select').selectOption('en');
   const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await loginAs(page,actor);await login;
  }
  await family.getByRole('textbox',{name:'Question',exact:true}).fill(marker+': Is a walk planned?');
  await family.getByRole('button',{name:'Send question',exact:true}).click();
  await expect(staff.getByText(marker+': Is a walk planned?',{exact:true})).toBeVisible({timeout:15000});
  await staff.getByRole('link',{name:'Record and publish',exact:true}).click();
  await staff.getByLabel('Link to a question').selectOption({label:marker+': Is a walk planned?'});
  await staff.getByRole('textbox',{name:'Original text',exact:true}).fill(source);
  await staff.getByRole('combobox',{name:'Type',exact:true}).selectOption('plan');
  await staff.getByLabel('Information scope').selectOption('outdoors');
  const draft=staff.waitForResponse(r=>r.url().endsWith('/drafts')&&r.request().method()==='POST');
  await staff.getByRole('button',{name:'Create draft for review',exact:true}).click();
  expect((await (await draft).json()).data.execution.ai_executed).toBe(false);
  await staff.getByLabel('I checked the source, meaning, speaker',{exact:false}).check();
  await staff.getByRole('button',{name:'Approve record',exact:true}).click();
  await expect(staff.getByRole('heading',{name:'Record · Approved · v1'})).toBeVisible();
  await expect(family.getByText(source,{exact:true})).toHaveCount(0);
  await staff.getByRole('button',{name:'Prepare publication',exact:true}).click();
  await staff.getByLabel('I checked every sentence',{exact:false}).check();
  await staff.getByRole('button',{name:'Publish approved answer',exact:true}).click();
  await expect(staff.getByRole('status',{name:'Publication status'})).toContainText('Published.');
  await expect(family.getByText(source,{exact:true})).toBeVisible({timeout:15000});
  await staff.getByRole('link',{name:'Team comments',exact:true}).click();
  await staff.getByRole('textbox',{name:'Anonymous reviewer alias',exact:true}).fill(marker);
  const comment=`AUTOMATED TEST, NOT HUMAN FEEDBACK: ${marker} GitHub Pages shared database check.`;
  await staff.getByRole('textbox',{name:'Comment',exact:true}).fill(comment);
  const saved=staff.waitForResponse(r=>r.url().endsWith('/poc/comments')&&r.request().method()==='POST');
  await staff.getByRole('button',{name:'Save comment',exact:true}).click();
  expect((await saved).status()).toBe(201);
  await loginAs(family,'Koskinen');
  await family.getByRole('link',{name:'Team comments',exact:true}).click();
  await expect(family.getByText(comment,{exact:true})).toBeVisible();
  await family.reload();await loginAs(family,'Koskinen');
  await family.getByRole('link',{name:'Team comments',exact:true}).click();
  await expect(family.getByText(comment,{exact:true})).toBeVisible();
  console.log('Shared synthetic loop and comment persisted:',marker);
 }finally{await Promise.all(contexts.map(c=>c.close()));}
});
