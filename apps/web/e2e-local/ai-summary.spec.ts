import {test,expect} from '@playwright/test';
import {loginAs} from '../e2e/login';
test('REAL local AI synthetic records -> reviewed publication -> separate guardian browser',async({browser})=>{
 const staffContext=await browser.newContext(),familyContext=await browser.newContext();
 const staff=await staffContext.newPage(),family=await familyContext.newPage();
 try{
 await staff.goto('/');await staff.locator('.interface-control select').selectOption('en');await loginAs(staff,'Koskinen',false);
 await family.goto('/');await family.locator('.interface-control select').selectOption('en');await loginAs(family,'Liisa',false);
 const panel=staff.locator('.publication').filter({hasText:'Synthetic EMR → AI update → family delivery'});
 await panel.getByRole('button',{name:'Generate update with local AI',exact:true}).click();
 await expect(panel.getByText('AI generated · source review required',{exact:false})).toBeVisible({timeout:230000});
 await expect(panel.locator('details')).toHaveCount(4);
 // Synthetic automated transport validation; not human Finnish review.
 await panel.getByRole('checkbox',{name:'I checked every sentence’s meaning, source, Finnish wording and answer sufficiency.'}).check();
 await panel.getByRole('button',{name:'Publish to selected guardians'}).click();
 await expect(panel.getByLabel('Publication status')).toBeVisible();
 await staff.reload();await loginAs(staff,'Koskinen',false);
 await panel.getByRole('button',{name:'Load saved AI results'}).click();
 await expect(panel.getByLabel('Publication status')).toBeVisible();
 await expect(family.locator('.home-care-tile')).toContainText(['Meals']);
 await expect(family.locator('.home-care-grid')).toContainText('Aino',{timeout:15000});
 await expect(family.locator('.home-latest')).toContainText('AI summarized records over the selected period.');
 await family.getByTestId('guardian-detail-link').click();
 await family.getByRole('button',{name:'Show source',exact:true}).first().click();
 await expect(family.getByRole('complementary',{name:'Source',exact:true})).toContainText(/\d{4}-\d{2}-\d{2}/);
 await staff.screenshot({path:'/tmp/ai-summary-staff.png',fullPage:true});
 await family.screenshot({path:'/tmp/ai-summary-family.png',fullPage:true});
 }finally{await staffContext.close();await familyContext.close();}
});
