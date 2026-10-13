import {loginAs,logoutCurrent,setInterfaceLanguage} from './login';
import {test,expect} from '@playwright/test';

test('English review loop preserves identity, draft input, source text and sharing boundaries',async({browser})=>{
 test.setTimeout(60000);
 const contexts=await Promise.all([browser.newContext(),browser.newContext(),browser.newContext()]);
 const [family,staff,restricted]=await Promise.all(contexts.map(c=>c.newPage()));
 const base='http://127.0.0.1:5179';
 const question='English review: was the planned walk completed?';
 const source='Iltapäivän ulkoilu on suunnitteilla. Toteutumista ei ole vielä vahvistettu.';
 try{
  for(const [page,actor] of [[family,'Liisa'],[staff,'Koskinen'],[restricted,'Mikko']] as const){
   await page.goto(base);
   await expect(page.locator('a[href$="/kide-direct"]')).toHaveCount(0);
   const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await loginAs(page,actor);
   await login;await expect(page.getByTestId('viewer-identity')).toContainText(actor);
   const cookie=(await page.context().cookies()).find(c=>c.name==='mp_session')?.value;
   await setInterfaceLanguage(page,'en');
   await expect(page.locator('html')).toHaveAttribute('lang','en');
   expect(Boolean(cookie)).toBe(true);
   expect((await page.context().cookies()).find(c=>c.name==='mp_session')?.value===cookie).toBe(true);
   await expect(page.getByRole('heading',{name:'PoC for online support-team review'})).toHaveCount(actor==='Koskinen'?1:0);
   await expect(page.locator('.context-bar')).toHaveCount(actor==='Koskinen'?1:0);
   await expect(page.locator('a[href$="/kide-direct"]')).toHaveCount(actor==='Koskinen'?1:0);
  }
  await family.getByTestId('detail-tab-family').click();
  await family.getByRole('textbox',{name:'Question',exact:true}).fill(question);
  await setInterfaceLanguage(family,'fi');
  await expect(family.getByRole('textbox',{name:'Kysymys',exact:true})).toHaveValue(question);
  await setInterfaceLanguage(family,'en');
  await expect(family.getByRole('textbox',{name:'Question',exact:true})).toHaveValue(question);
  await family.getByRole('button',{name:'Send question'}).click();
  await expect(staff.getByText(question,{exact:true})).toBeVisible({timeout:10000});
  await staff.getByRole('link',{name:'Record and publish'}).click();
  await staff.getByLabel('Link to a question').selectOption({label:question});
  await staff.getByLabel('Original text').fill(source);
  await staff.getByRole('combobox',{name:'Type',exact:true}).selectOption('plan');
  await staff.getByLabel('Information scope').selectOption('outdoors,health_context');
  const draft=staff.waitForResponse(r=>r.url().endsWith('/drafts')&&r.request().method()==='POST');
  await staff.getByRole('button',{name:'Create draft for review',exact:true}).click();
  expect((await (await draft).json()).data.execution.ai_executed).toBe(false);
  await expect(staff.getByRole('heading',{name:'Record · Draft · v1'})).toBeVisible();
  await staff.getByLabel('I checked the source, meaning, speaker',{exact:false}).check();
  await staff.getByRole('button',{name:'Approve record',exact:true}).click();
  await expect(staff.getByRole('heading',{name:'Record · Approved · v1'})).toBeVisible();
  expect(await (await contexts[0].request.get(base+'/api/v1/family/residents/aino/board')).text()).not.toContain(source);
  await staff.getByRole('button',{name:'Prepare publication'}).click();
  await staff.getByLabel('I checked every sentence',{exact:false}).check();
  await staff.getByRole('button',{name:'Publish to selected guardians'}).click();
  await expect(staff.getByRole('status',{name:'Publication status'})).toContainText('Published.');
  await family.getByTestId('detail-tab-today').click();
  await expect(family.getByText(source,{exact:true})).toBeVisible({timeout:10000});
  const card=family.locator('article > div').filter({has:family.getByText(source,{exact:true})});
  await expect(card).toContainText('Plan · completion not confirmed');
  await card.getByRole('button',{name:'Show source'}).click();
  await expect(family.getByLabel('Source',{exact:true})).toContainText(source);
  const board=(await (await contexts[0].request.get(base+'/api/v1/family/residents/aino/board')).json()).data;
  const item=board.tiles.flatMap((t:any)=>t.items).find((i:any)=>i.statement===source);
  expect(item.action_status).toBe('planned');
  expect(await (await contexts[2].request.get(base+'/api/v1/family/residents/aino/board')).text()).not.toContain(source);
  expect((await contexts[2].request.get(base+'/api/v1/family/items/'+item.item_id+'/evidence')).status()).toBe(404);
  const unavailable=await contexts[0].request.get(base+'/api/v1/family/residents/aino/board?lang=sv');
  expect((await unavailable.json()).data.language_state).toBe('unavailable');
  expect((await (await contexts[0].request.get(base+'/api/v1/session')).json()).data.actor_id).toBe('liisa');
  await expect(family.getByLabel('Publication language')).toHaveCount(0);
  await expect(family.getByText(source,{exact:true})).toBeVisible();
  await family.screenshot({path:'/tmp/medipencil-poc-english.png',fullPage:true});
 }finally{await Promise.allSettled(contexts.map(c=>c.close()));}
});

test('family login header has no KIDE entry',async({page})=>{
 await page.goto('/login/family');
 await expect(page.getByTestId('login-submit')).toBeVisible();
 await expect(page.locator('a[href$="/kide-direct"]')).toHaveCount(0);
});
