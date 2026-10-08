import {loginAs} from './login';
import {test,expect} from '@playwright/test';
import {readFileSync,writeFileSync} from 'node:fs';

test('shared HTTPS rejects unauthenticated access, identity spoofing and role escalation; comments persist',async({browser,playwright})=>{
 const base=process.env.MEDIPENCIL_REVIEW_URL!.replace(/\/$/,'');
 const creds=JSON.parse(readFileSync(process.env.MEDIPENCIL_REVIEW_CREDENTIALS!,'utf8'));
 const origin=new URL(base).origin;
 const anonymous=await playwright.request.newContext();
 const contexts=await Promise.all(['staff','liisa'].map(actor=>browser.newContext({httpCredentials:{username:'mp-'+actor,password:creds['mp-'+actor].password}})));
 try {
  expect((await anonymous.get(base+'/')).status()).toBe(401);
  expect((await anonymous.get(base+'/api/v1/health',{headers:{'X-Medipencil-Reviewer':'mp-staff','X-Medipencil-Proxy-Key':'forged'}})).status()).toBe(401);
  const pages=await Promise.all(contexts.map(c=>c.newPage()));
  for(const [index,name] of ['Koskinen','Liisa'].entries()){
   await pages[index].goto(base+'/');
   await pages[index].getByTestId(name==='Koskinen'?'staff-login-link':'family-login-link').click();
   await expect(pages[index].getByRole('radio')).toHaveCount(1);
   const login=pages[index].waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await loginAs(pages[index],name);
   expect((await login).status()).toBe(201);
   const cookie=(await contexts[index].cookies()).find(c=>c.name==='mp_session')!;
   expect(cookie.secure).toBe(true);expect(cookie.httpOnly).toBe(true);expect(cookie.path).toBe('/medipencil/');
  }
  expect((await contexts[1].request.post(base+'/api/v1/demo/session',{headers:{Origin:origin,'X-Medipencil-Reviewer':'mp-staff'},data:{demo_actor_id:'staff'}})).status()).toBe(403);
  expect((await contexts[1].request.get(base+'/api/v1/poc/comments')).status()).toBe(403);
  await contexts[1].addCookies((await contexts[0].cookies()).filter(c=>c.name==='mp_session'));
  expect((await contexts[1].request.get(base+'/api/v1/staff/residents')).status()).toBe(401);
  await pages[0].getByRole('link',{name:'팀 코멘트',exact:true}).click();
  const session=(await (await contexts[0].request.get(base+'/api/v1/session')).json()).data;
  const body={reviewer_alias:'AUTO-SA-DEPLOY',screen:'general',body:'Automated deployment verification; not support-team feedback. '+Date.now()};
  const response=await contexts[0].request.post(base+'/api/v1/poc/comments',{headers:{Origin:origin,'X-CSRF-Token':session.csrf_token,'Idempotency-Key':crypto.randomUUID()},data:body});
  expect(response.status()).toBe(201);
  const created=(await response.json()).data;
  await pages[0].reload();
  const login=pages[0].waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
  await loginAs(pages[0],'Koskinen');await login;
  await pages[0].getByRole('link',{name:'팀 코멘트',exact:true}).click();
  await expect(pages[0].getByText(body.body,{exact:true})).toBeVisible();
  await pages[0].setViewportSize({width:390,height:844});
  expect(await pages[0].evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await pages[0].screenshot({path:'/tmp/medipencil-sa-app-comments.png',fullPage:true});
  writeFileSync('/tmp/medipencil-sa-shared-check.json',JSON.stringify({comment:created,https:true,anonymous_denied:true,role_escalation_denied:true,identity_spoofing_denied:true,cookie_theft_between_reviewers_denied:true,mobile_overflow:false,reviewer:'AUTOMATION_NOT_SUPPORT_TEAM',feedback_ids:[]},null,2));
 } finally {await anonymous.dispose();await Promise.all(contexts.map(c=>c.close()));}
});
