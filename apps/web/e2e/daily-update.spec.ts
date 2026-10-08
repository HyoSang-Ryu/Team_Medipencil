import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('daily care comes first; date filtering and restricted guardian remain factual',async({page})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Liisa');
 await expect(page.getByTestId('daily-summary')).toBeVisible();
 await expect(page.locator('.dashboard-stats')).toHaveCount(0);
 expect(await page.locator('.daily-board').evaluate(el=>!!(el.compareDocumentPosition(document.querySelector('.question-board')!)&Node.DOCUMENT_POSITION_FOLLOWING))).toBe(true);
 await expect(page.locator('.secondary-insights')).not.toHaveAttribute('open','');
 await expect(page.locator('.recent-day-grid button')).toHaveCount(3);
 await page.locator('.recent-day-grid button').first().click();
 await expect(page.getByRole('button',{name:'Clear date filter'})).toBeVisible();
 await expect(page.locator('.recent-day-grid button').first()).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Clear date filter'}).click();
 for(const width of [1280,390]){
  await page.setViewportSize({width,height:900});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:`/tmp/daily-update-${width}.png`,fullPage:true});
 }
 await loginAs(page,'Mikko');
 await expect(page.locator('.daily-topic-medication')).toHaveCount(0);
 await page.context().setOffline(true);
 await expect(page.getByTestId('daily-summary')).toHaveCount(0);
 await expect(page.locator('.recent-day-grid')).toHaveCount(0);
 await page.context().setOffline(false);
 await expect(page.getByTestId('daily-summary')).toBeVisible();
});
