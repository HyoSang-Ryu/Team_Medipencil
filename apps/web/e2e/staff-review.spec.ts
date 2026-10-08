import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('EMR review is staff landing; synthetic source persists through review and family publication',async({browser})=>{
 const sc=await browser.newContext(),fc=await browser.newContext();const staff=await sc.newPage(),family=await fc.newPage();
 try{
 await staff.goto('/');await staff.locator('.interface-control select').selectOption('en');await loginAs(staff,'Koskinen',false);
 await expect(staff.getByTestId('staff-review')).toBeVisible();
 await staff.getByRole('button',{name:'Start with synthetic EMR',exact:true}).click();
 await expect(staff.locator('.emr-original')).toContainText('Aino söi aamupalan');
 await staff.getByRole('button',{name:'Create source-based demo draft · No AI',exact:true}).click();
 await expect(staff.locator('.capture')).toContainText('AI not');
 await expect(staff.locator('.review-inbox-card').filter({hasText:'Aino söi aamupalan'})).toBeVisible();
 await staff.reload();await loginAs(staff,'Koskinen',false);
 await staff.locator('.review-inbox-card').filter({hasText:'Aino söi aamupalan'}).click();
 await expect(staff.locator('.emr-original')).toContainText('Toteutumista ei ole vielä vahvistettu');
 const approve=staff.getByRole('button',{name:'Approve record',exact:true});await expect(approve).toBeDisabled();
 await staff.getByLabel('I checked the source, meaning, speaker',{exact:false}).check();await approve.click();
 await expect(staff.getByRole('heading',{name:'Record · Approved · v1'})).toBeVisible();
 await staff.getByRole('button',{name:'Prepare publication',exact:true}).click();
 await staff.getByLabel('I checked every sentence',{exact:false}).check();await staff.getByRole('button',{name:'Publish approved answer',exact:true}).click();
 await expect(staff.getByRole('status',{name:'Publication status'})).toContainText('Published.');
 await family.goto('/');await loginAs(family,'Liisa',false);
 await expect(family.locator('.home-care-tile').filter({hasText:'Aino söi aamupalan'})).toBeVisible();
 await family.getByTestId('guardian-detail-link').click();await family.locator('.history-toggle').click();
 await expect(family.locator('.daily-entry').filter({hasText:'Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vielä vahvistettu.'})).toBeVisible();
 }finally{await sc.close();await fc.close();}
});
