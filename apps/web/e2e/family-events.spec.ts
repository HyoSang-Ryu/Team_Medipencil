import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('synthetic hospital notice requires review; separate family sessions acknowledge only permitted events',async({browser})=>{
 test.setTimeout(60000);
 const contexts=await Promise.all([browser.newContext(),browser.newContext(),browser.newContext()]);
 const [staff,liisa,mikko]=await Promise.all(contexts.map(c=>c.newPage()));
 for(const [page,name] of [[staff,'Koskinen'],[liisa,'Liisa'],[mikko,'Mikko']] as const){await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,name);}
 const panel=staff.locator('#family-events');
 await panel.getByRole('button',{name:'Fill example appointment'}).click();
 await panel.getByLabel('External event ID').fill('e2e-synthetic-appointment');
 await panel.getByRole('button',{name:'Import for review'}).click();
 const card=panel.getByTestId('family-event').filter({hasText:'e2e-synthetic-appointment'});
 await expect(card).toBeVisible();await expect(card.getByRole('button',{name:'Publish notice to family'})).toBeDisabled();
 await expect(liisa.locator('#family-events').getByTestId('family-event')).toHaveCount(0);
 await card.getByLabel('Liisa',{exact:true}).check();await card.getByLabel('I checked the schedule',{exact:false}).check();
 await card.getByRole('button',{name:'Publish notice to family'}).click();
 const family=liisa.locator('#family-events').getByTestId('family-event').filter({hasText:'e2e-synthetic-appointment'});
 await expect(family).toBeVisible({timeout:10000});await expect(mikko.locator('#family-events').getByTestId('family-event')).toHaveCount(0);
 await family.getByRole('button',{name:'Acknowledged',exact:true}).click();await expect(family.locator('.event-ack')).toBeVisible();
 await expect(card).toContainText('Acknowledged by family',{timeout:10000});
 await liisa.setViewportSize({width:390,height:844});expect(await liisa.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await card.getByRole('button',{name:'Edit or cancel schedule'}).click();await panel.getByRole('combobox',{name:'Schedule status',exact:true}).selectOption('cancelled');
 await panel.getByRole('button',{name:'Import for review'}).click();await expect(card).toContainText('Awaiting review');
 await expect(family).toHaveCount(0,{timeout:10000});
 await card.getByLabel('I checked the schedule',{exact:false}).check();await card.getByRole('button',{name:'Publish notice to family'}).click();
 await expect(family).toContainText('Appointment cancelled',{timeout:10000});await expect(family.getByRole('button',{name:'Acknowledged',exact:true})).toBeVisible();
 await card.getByRole('button',{name:'Withdraw notice'}).click();await expect(family).toHaveCount(0,{timeout:10000});
 for(const c of contexts)await c.close();
});
