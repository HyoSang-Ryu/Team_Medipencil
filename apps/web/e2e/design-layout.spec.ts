import {test,expect} from '@playwright/test';
test('Finnish Minimal responsive layout retains all working screens',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.getByRole('button',{name:'Koskinen',exact:true}).click();
 await page.getByLabel('Interface / 화면 언어').selectOption('en');
 for(const width of [1280,390,360]){
  await page.setViewportSize({width,height:900});
  for(const name of ['Questions','Record and publish','Consent','Team comments']){
   await page.getByRole('link',{name,exact:true}).click();
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
   if(name==='Team comments'){
    const grid=page.locator('.comment-grid');
    const columns=await grid.evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length);
    expect(columns).toBe(width===1280?2:1);
    await page.screenshot({path:`/tmp/medipencil-finnish-comments-${width}.png`,fullPage:true});
   }
  }
 }
 await page.getByRole('button',{name:'Liisa',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Aino’s daily update'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 expect(errors).toEqual([]);
});
