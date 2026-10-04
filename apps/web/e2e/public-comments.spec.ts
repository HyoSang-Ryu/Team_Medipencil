import {test,expect} from '@playwright/test';
import {writeFileSync} from 'node:fs';

test('live team comment saves and remains visible in a separate session after reload',async({browser})=>{
 const base=process.env.MEDIPENCIL_REVIEW_URL!.replace(/\/$/,'');
 const marker='AUTO-COMMENT-CHECK-'+Date.now();
 const body=`[자동 저장 시험 · 실제 팀원 피드백 아님] ${marker}\n운영 화면에서 저장 → 별도 브라우저 세션 조회 → 새로고침 후 유지 확인.`;
 const contexts=await Promise.all([browser.newContext(),browser.newContext()]);
 const [writer,reader]=await Promise.all(contexts.map(c=>c.newPage()));
 try{
  for(const page of [writer,reader]){
   await page.goto(base);
   await page.locator('.interface-control select').selectOption('ko');
   const login=page.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
   await page.getByRole('button',{name:'Koskinen',exact:true}).click();await login;
   await page.getByRole('link',{name:'팀 코멘트',exact:true}).click();
   await expect(page.getByRole('heading',{name:'팀 코멘트',exact:true})).toBeVisible();
  }
  await writer.getByRole('textbox',{name:'익명 팀원 별칭',exact:true}).fill(marker);
  await writer.getByRole('textbox',{name:'코멘트',exact:true}).fill(body);
  const saved=writer.waitForResponse(r=>r.url().endsWith('/poc/comments')&&r.request().method()==='POST');
  await writer.getByRole('button',{name:'코멘트 저장',exact:true}).click();
  const response=await saved;expect(response.status()).toBe(201);
  const comment=(await response.json()).data;
  expect(comment.body).toBe(body);expect(comment.reviewer_alias).toBe(marker);
  await expect(writer.getByRole('status').filter({hasText:'코멘트를 저장했습니다.'})).toHaveText('코멘트를 저장했습니다.');
  await reader.getByRole('button',{name:'목록 새로고침',exact:true}).click();
  await expect(reader.getByText(body,{exact:true})).toHaveCount(1);
  await reader.reload();
  const login=reader.waitForResponse(r=>r.url().endsWith('/demo/session')&&r.request().method()==='POST');
  await reader.getByRole('button',{name:'Koskinen',exact:true}).click();await login;
  await reader.getByRole('link',{name:'팀 코멘트',exact:true}).click();
  await expect(reader.getByText(body,{exact:true})).toBeVisible();
  const stored=await contexts[1].request.get(base+'/api/v1/poc/comments?screen=general');
  expect(stored.status()).toBe(200);
  const matches=(await stored.json()).data.items.filter((c:{comment_id:string})=>c.comment_id===comment.comment_id);
  expect(matches).toHaveLength(1);expect(matches[0].body).toBe(body);
  const evidence={marker,comment_id:comment.comment_id,created_at:comment.created_at,post_status:response.status(),get_status:stored.status(),separate_session:true,reload_persisted:true,matching_rows:matches.length};
  writeFileSync('/tmp/medipencil-live-comment-check.json',JSON.stringify(evidence,null,2));
  console.log(JSON.stringify(evidence));
 }finally{await Promise.all(contexts.map(c=>c.close()));}
});
