import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('shared PoC does not pretend an unavailable model generated a summary',async({page})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Koskinen',false);
 const panel=page.locator('.publication').filter({hasText:'Synthetic EMR → AI update → family delivery'});
 await expect(panel).toContainText('Local AI is not configured.');
 await expect(panel.getByRole('button',{name:'Generate update with local AI'})).toBeDisabled();
 await panel.getByRole('button',{name:'Load saved AI results'}).click();
 await expect(panel.locator('.guardian-preview')).not.toContainText('AI generated');
});
