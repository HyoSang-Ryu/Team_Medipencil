import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('time-sensitive empty update refreshes while home remains open (synthetic response fixture)',async({page})=>{
 await page.clock.install({time:new Date('2026-10-11T14:59:40Z')});
 await page.route('**/family/residents/aino/board?*',async route=>{
  const response=await route.fetch();const body=await response.json();
  body.data.language_state='available';body.data.tiles=body.data.tiles.map((t:Record<string,unknown>)=>({...t,items:[]}));
  await route.fulfill({response,json:body});
 });
 await page.route('**/family/residents/aino/delivery-schedule',route=>route.fulfill({json:{data:{recipient_id:'liisa',enabled:false,next_run_at:null,last_run_at:null,last_result:null,exceptions:[]}}}));
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Liisa',false);
 await expect(page.locator('.home-latest')).toContainText('Today’s update has not arrived yet.');
 await page.clock.fastForward(30000);
 await expect(page.locator('.home-latest')).toContainText('No update for today has arrived as of now.');
 await expect(page.locator('.home-latest')).not.toContainText('Next delivery');
 await page.getByTestId('guardian-detail-link').click();
 await expect(page.getByTestId('daily-summary')).toContainText('No update for today has arrived as of now.');
});
