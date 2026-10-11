import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('daily schedule is persistent, visible to its guardian and can be paused',async({browser})=>{
 const a=await browser.newContext(),b=await browser.newContext();const staff=await a.newPage(),family=await b.newPage();
 try{
 await staff.goto('/');await staff.locator('.interface-control select').selectOption('en');await loginAs(staff,'Koskinen',false);
 const panel=staff.getByTestId('delivery-schedule');const liisa=panel.locator('article').filter({hasText:'Liisa'});
 await liisa.getByRole('button',{name:'Start automatic delivery',exact:true}).click();
 await expect(liisa.getByRole('heading')).toContainText('Automatic delivery on');await expect(liisa).toContainText('Next delivery');
 await staff.reload();await loginAs(staff,'Koskinen',false);await expect(liisa.getByRole('heading')).toContainText('Automatic delivery on');
 await family.goto('/');await family.locator('.interface-control select').selectOption('en');await loginAs(family,'Liisa',false);
 const status=family.getByTestId('family-delivery-schedule');await expect(status).toContainText('Automatic delivery on');await expect(status.getByRole('button')).toHaveCount(0);
 await liisa.getByRole('button',{name:'Pause automatic delivery',exact:true}).click();await expect(liisa.getByRole('heading')).toContainText('Automatic delivery paused');
 await expect(status).toContainText('Automatic delivery paused',{timeout:15000});
 }finally{await a.close();await b.close();}
});
