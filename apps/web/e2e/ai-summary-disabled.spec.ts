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

for(const unavailable of ['disabled','failed'] as const){
 test(`EMR draft blocks unavailable local AI (${unavailable}) but keeps manual input`,async({page})=>{
  if(unavailable==='failed')await page.route('**/staff/providers',route=>route.abort());
  await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Koskinen',false);
  await page.getByRole('button',{name:'Start with synthetic EMR'}).click();
  const capture=page.locator('.capture');
  await expect(capture).toContainText('Local AI is not configured.');
  await expect(capture.locator('option[value="local"]')).toHaveJSProperty('disabled',true);
  await capture.locator('select').first().focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');
  await expect(capture.locator('select').first()).toHaveValue('manual');
  await page.getByRole('link',{name:'Add a supplementary note'}).click();
  await capture.locator('textarea').first().fill('Itsenäinen synteettinen havainto.');
  const create=capture.locator('.review-grid button').first();
  await expect(create).toBeEnabled();await create.click();
  await expect(capture.getByTestId('capture-execution')).toContainText('manual');
 });
}
