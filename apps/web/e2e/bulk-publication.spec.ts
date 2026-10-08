import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('bulk publication keeps guardian scopes and retries a lost response without republishing successes',async({page})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Koskinen');
 await page.getByRole('link',{name:'Record and publish',exact:true}).click();
 const marker='BULK-'+Date.now();
 for(const scope of ['meals','outdoors']){
  await page.getByRole('textbox',{name:'Original text',exact:true}).fill(marker+' '+scope);
  await page.getByRole('combobox',{name:'Information scope',exact:true}).selectOption(scope);
  await page.getByRole('button',{name:'Create draft for review',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Record · Draft · v1'})).toBeVisible();
  await page.getByLabel('I checked the source, meaning, speaker',{exact:false}).check();
  await page.getByRole('button',{name:'Approve record',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Record · Approved · v1'})).toBeVisible();
 }
 const guardians=page.locator('.publication-guardians');
 await expect(guardians.locator('select')).toHaveCount(0);
 await guardians.getByLabel('Select all guardians',{exact:true}).check();
 await expect(guardians.getByLabel('Liisa',{exact:true})).toBeChecked();await expect(guardians.getByLabel('Mikko',{exact:true})).toBeChecked();
 await page.getByRole('button',{name:'Prepare publication',exact:true}).click();
 const liisa=page.locator('.guardian-preview[data-recipient="liisa"]'),mikko=page.locator('.guardian-preview[data-recipient="mikko"]');
 await expect(liisa).toContainText(marker+' meals');await expect(liisa).toContainText(marker+' outdoors');await expect(mikko).toContainText(marker+' meals');await expect(mikko).not.toContainText(marker+' outdoors');
 const calls:string[]=[];let dropped=false;
 await page.route('**/staff/publications/*/publish',async route=>{calls.push(route.request().url());const response=await route.fetch();if(calls.length===2&&!dropped){dropped=true;await route.abort('failed');}else await route.fulfill({response});});
 await page.getByLabel('I checked every sentence',{exact:false}).check();
 await page.getByRole('button',{name:'Publish to selected guardians',exact:true}).click();
 await expect(liisa.getByRole('status')).toContainText('Published.');await expect(mikko.getByRole('alert')).toContainText('Publication needs confirmation');
 await page.getByRole('button',{name:'Publish to selected guardians',exact:true}).click();
 await expect(mikko.getByRole('status')).toContainText('Published.');
 expect(calls).toHaveLength(3);expect(calls[0]).not.toBe(calls[1]);expect(calls[1]).toBe(calls[2]);
 await guardians.getByLabel('Select all guardians',{exact:true}).uncheck();
 await expect(page.getByRole('button',{name:'Prepare publication',exact:true})).toBeDisabled();await expect(page.locator('.guardian-preview')).toHaveCount(0);
});
