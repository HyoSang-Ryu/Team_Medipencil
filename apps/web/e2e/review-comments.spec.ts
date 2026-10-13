import {loginAs} from './login';
import {test,expect} from '@playwright/test';

test('team comments persist across reviewers, retry safely, and stay staff-only',async({browser})=>{
 const contexts=await Promise.all([browser.newContext(),browser.newContext(),browser.newContext()]);
 const [first,second,family]=await Promise.all(contexts.map(c=>c.newPage()));
 const base='http://127.0.0.1:5179';
 const comment='AUTOMATED TEST ONLY: <script>throw new Error("not executable")</script>\nPlease clarify the publish button.';
 try{
  for(const page of [first,second]){
   await page.goto(base);await loginAs(page,'Koskinen');
   await page.locator('.interface-control select').selectOption('en');
   await page.getByRole('link',{name:'Team comments',exact:true}).click();
  }
  await first.getByRole('textbox',{name:'Anonymous reviewer alias'}).fill('reviewer-auto');
  await first.getByRole('combobox',{name:'Screen under review'}).selectOption('publication');
  await first.getByRole('textbox',{name:'Comment',exact:true}).fill(comment);
  // Simulate a lost acknowledgement after a real successful server commit.
  await first.route('**/api/v1/poc/comments',async route=>{
   if(route.request().method()==='POST'){
    await route.fetch();await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({error:{code:'TEST_LOST_ACK'}})});
   }else await route.continue();
  });
  await first.getByRole('button',{name:'Save comment',exact:true}).click();
  await expect(first.getByRole('alert')).toContainText('TEST_LOST_ACK');
  await expect(first.getByRole('textbox',{name:'Comment',exact:true})).toHaveValue(comment);
  await first.unroute('**/api/v1/poc/comments');
  await first.getByRole('button',{name:'Save comment',exact:true}).click();
  await expect(first.getByRole('status')).toHaveText('Comment saved.');
  await second.getByRole('button',{name:'Refresh comments'}).click();
  await expect(second.getByText(comment,{exact:true})).toHaveCount(1);
  await second.getByRole('combobox',{name:'Filter by screen'}).selectOption('consent');
  await expect(second.getByText(comment,{exact:true})).toHaveCount(0);
  await second.getByRole('combobox',{name:'Filter by screen'}).selectOption('publication');
  await expect(second.getByText(comment,{exact:true})).toBeVisible();
  await second.reload();await loginAs(second,'Koskinen');
  await second.getByRole('link',{name:'Team comments',exact:true}).click();
  await expect(second.getByText(comment,{exact:true})).toBeVisible();
  await family.goto(base);await loginAs(family,'Liisa');
  await expect(family.getByRole('heading',{name:'Äiti(Helmi Nieminen, 84 v)'})).toBeVisible();
  await expect(family.getByRole('link',{name:'Tiimin kommentit',exact:true})).toHaveCount(0);
  expect((await contexts[2].request.get(base+'/api/v1/poc/comments')).status()).toBe(403);
  await second.setViewportSize({width:390,height:844});
  expect(await second.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await second.screenshot({path:'/tmp/medipencil-comments-mobile.png',fullPage:true});
 }finally{await Promise.allSettled(contexts.map(c=>c.close()));}
});

test('team comments stays reachable with a supplied resident selected',async({page})=>{
 await page.route('**/api/v1/health',async route=>{
  const response=await route.fetch();const body=await response.json();
  body.data.provided_data_available=true;
  body.data.provided_accounts=[{actor_id:'provided-test',display_name:'Synthetic guardian',subject:'A',resident:'Synthetic resident',relation:'child'}];
  await route.fulfill({json:body});
 });
 await page.route('**/api/v1/provided/A/board?*',route=>route.fulfill({json:{data:{subject:{label:'Synthetic resident',unit:'Test'},daily:[],notes:[],questions:[],groups:[],today:'2026-10-13'}}}));
 await page.route('**/api/v1/staff/provided-data',route=>route.fulfill({json:{data:{today:'2026-10-13',subjects:[]}}}));
 await page.route('**/api/v1/provided/A/sharing',route=>route.fulfill({json:{data:{items:[]}}}));
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');
 await page.getByTestId('staff-login-link').click();await page.getByRole('radio',{name:'Heli Koskinen',exact:true}).check();await page.getByTestId('login-submit').click();
 await expect(page.locator('.provided-heading h1').first()).toHaveText('Synthetic resident');
 await page.getByRole('link',{name:'Team comments',exact:true}).click();
 await expect(page.getByRole('textbox',{name:'Anonymous reviewer alias',exact:true})).toBeVisible();
 await expect(page.locator('.provided-heading')).toHaveCount(0);
});

test('slow resident load is not discarded by background polling',async({page})=>{
 await page.route('**/api/v1/health',async route=>{
  const response=await route.fetch();const body=await response.json();
  body.data.provided_data_available=true;
  body.data.provided_accounts=[{actor_id:'provided-test',display_name:'Synthetic guardian',subject:'A',resident:'Synthetic resident',relation:'child'}];
  await route.fulfill({json:body});
 });
 let boardCalls=0;
 await page.route('**/api/v1/provided/A/board?*',async route=>{boardCalls++;await new Promise(resolve=>setTimeout(resolve,11000));return route.fulfill({json:{data:{subject:{label:'Synthetic resident',unit:'Test'},daily:[],notes:[],questions:[],groups:[],today:'2026-10-13'}}});});
 await page.route('**/api/v1/staff/provided-data',route=>route.fulfill({json:{data:{today:'2026-10-13',subjects:[]}}}));
 await page.route('**/api/v1/provided/A/sharing',route=>route.fulfill({json:{data:{items:[]}}}));
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');
 await page.getByTestId('staff-login-link').click();await page.getByRole('radio',{name:'Heli Koskinen',exact:true}).check();await page.getByTestId('login-submit').click();
 await expect(page.locator('.provided-heading h1').first()).toHaveText('Synthetic resident',{timeout:15000});
 // React development StrictMode can start two initial reads. No polling overlap.
 expect(boardCalls).toBeLessThanOrEqual(2);
});
