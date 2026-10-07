import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('question board saves the post, staff replies in-thread and only published reply is visible',async({browser})=>{
 const family=await browser.newPage(),staff=await browser.newPage(),other=await browser.newPage();
 const text='SYNTHETIC BOARD: When is the planned family call?';const reply='SYNTHETIC BOARD: A call is planned for tomorrow; it has not taken place.';
 try{
  for(const [p,name] of [[family,'Liisa'],[staff,'Koskinen'],[other,'Mikko']] as const){await p.goto('/');await p.locator('.interface-control select').selectOption('en');await loginAs(p,name);}
  await family.getByLabel('Question',{exact:true}).fill(text);await family.getByRole('button',{name:'Send question',exact:true}).click();
  const post=family.locator('.question-post').filter({hasText:text});await expect(post).toBeVisible();await expect(post).toContainText('Liisa');
  await family.reload();await loginAs(family,'Liisa');await expect(post).toBeVisible();
  const staffPost=staff.locator('.question-post').filter({hasText:text});await expect(staffPost).toBeVisible({timeout:10000});
  await staffPost.getByRole('button',{name:'Write a reply',exact:true}).click();
  await staffPost.getByLabel('Reply text',{exact:true}).fill(reply);await staffPost.getByLabel('Type',{exact:true}).selectOption('plan');
  await staffPost.getByRole('button',{name:'Review reply',exact:true}).click();
  await expect(family.getByText(reply,{exact:true})).toHaveCount(0);
  await staffPost.getByLabel('I checked the evidence, meaning, sharing scope and adequacy of the answer.',{exact:true}).check();
  await staffPost.getByRole('button',{name:'Approve reply and prepare publication',exact:true}).click();
  await expect(family.getByText(reply,{exact:true})).toHaveCount(0);
  await staffPost.getByLabel('I reviewed the evidence, wording and sharing permission for all content.',{exact:true}).check();
  await staffPost.getByRole('button',{name:'Publish reply',exact:true}).click();
  await expect(post.getByRole('button',{name:'Read reply',exact:true})).toBeVisible({timeout:10000});
  await post.getByRole('button',{name:'Read reply',exact:true}).click();
  await expect(post.locator('.published-reply')).toContainText(reply);await expect(post.locator('.published-reply')).toContainText('Koskinen');
  await expect(other.locator('.question-post').filter({hasText:text})).toHaveCount(0);
  await expect(other.getByText(reply,{exact:true})).toHaveCount(0);
  await family.setViewportSize({width:390,height:900});expect(await family.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await family.locator('.question-board').screenshot({path:'/tmp/care-question-board-390.png'});
  await family.reload();await loginAs(family,'Liisa');await post.getByRole('button',{name:'Read reply',exact:true}).click();await expect(post.locator('.published-reply')).toContainText(reply);
 }finally{await family.close();await staff.close();await other.close();}
});
