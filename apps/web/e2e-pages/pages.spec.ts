import {loginAs,openCommentsArchive} from '../e2e/login';
import {test,expect} from '@playwright/test';
const base='https://hyosang-ryu.github.io/Team_Medipencil/';

test('GitHub Pages exposes only current residents to staff',async({browser})=>{
 const context=await browser.newContext();const page=await context.newPage();
 try{
  await page.goto(base);
  await page.locator('.interface-control select').selectOption('en');
  await page.getByTestId('staff-login-link').click();
  await page.getByRole('radio',{name:'Heli Koskinen',exact:true}).check();
  await page.getByTestId('login-submit').click();
  await expect(page.getByTestId('viewer-identity')).toContainText('Koskinen');
  const subjects=page.locator('.provided-controls select').first();
  await expect(subjects.locator('option')).toHaveCount(2);
  await expect(subjects.locator('option[value=aino]')).toHaveCount(0);
  for(const subject of ['A','B']){
   await subjects.selectOption(subject);
   await expect(page.locator('.provided-data').first()).toBeVisible();
   await expect(subjects).toHaveValue(subject);
  }
  expect((await context.cookies()).filter(c=>c.name==='mp_session')).toHaveLength(0);
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
  await family.getByTestId('detail-tab-family').click();
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
  await staff.getByRole('button',{name:'Publish to selected guardians',exact:true}).click();
  await expect(staff.getByRole('status',{name:'Publication status'})).toContainText('Published.');
  await family.getByTestId('detail-tab-today').click();
  await expect(family.getByText(source,{exact:true})).toBeVisible({timeout:15000});
  await openCommentsArchive(staff);
  await staff.getByRole('textbox',{name:'Anonymous reviewer alias',exact:true}).fill(marker);
  const comment=`AUTOMATED TEST, NOT HUMAN FEEDBACK: ${marker} GitHub Pages shared database check.`;
  await staff.getByRole('textbox',{name:'Comment',exact:true}).fill(comment);
  const saved=staff.waitForResponse(r=>r.url().endsWith('/poc/comments')&&r.request().method()==='POST');
  await staff.getByRole('button',{name:'Save comment',exact:true}).click();
  expect((await saved).status()).toBe(201);
  await loginAs(family,'Koskinen');
  await openCommentsArchive(family);
  await expect(family.getByText(comment,{exact:true})).toBeVisible();
  await family.reload();await loginAs(family,'Koskinen');
  await openCommentsArchive(family);
  await expect(family.getByText(comment,{exact:true})).toBeVisible();
  console.log('Shared synthetic loop and comment persisted:',marker);
 }finally{await Promise.all(contexts.map(c=>c.close()));}
});


test('GitHub Pages loads and reaches each supplied guardian dashboard',async({browser})=>{
 for(const [subject,guardian,resident] of [['A','Marjut Virtanen','Aino'],['B','Hanna Lehtonen','Eetu']]){
  const context=await browser.newContext();const page=await context.newPage();
  try{
   await page.goto(base+'#/login/family');
   const choice=page.locator('.compact-family-login select').first();
   await expect(choice).toBeVisible();await choice.selectOption(subject);
   await expect(page.locator('.login-single-guardian')).toContainText(guardian);
   await page.getByTestId('login-submit').click();
   await expect(page.getByTestId('viewer-identity')).toContainText(guardian);
   await expect(page.locator('.provided-heading h1')).toContainText(resident,{timeout:15000});
   await expect(page.getByTestId('provided-overview')).toBeVisible();
   await expect(page.locator('.provided-status-card')).toHaveCount(6);
   await expect(page.locator('.provided-charts article')).toHaveCount(0);
   await page.locator('.overview-details').click();
   await expect(page.locator('.provided-charts article')).toHaveCount(6);
   await expect(page.locator('.provided-topic-history')).toHaveCount(3);
   await expect(page.locator('.provided-charts svg')).toHaveCount(3);
   expect((await context.cookies()).filter(c=>c.name==='mp_session')).toHaveLength(0);
  }finally{await context.close();}
 }
});
