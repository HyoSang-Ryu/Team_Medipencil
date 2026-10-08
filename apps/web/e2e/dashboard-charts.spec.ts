import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('care charts show real seven-day data, filter access and remain responsive',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');await page.locator('.interface-control select').selectOption('ko');
 await loginAs(page,'Koskinen');
 const chart=page.getByRole('region',{name:'돌봄 기록 시각화'});
 await expect(chart.locator('.care-topic-card')).toHaveCount(6);
 await expect(chart.getByRole('img',{name:'날짜별 기록 건수'})).toBeVisible();
 await chart.locator('.care-topic-card').nth(4).click();
 await expect(chart.getByLabel('그래프 항목')).toHaveValue('sleep');
 await chart.getByText('날짜별 수치 보기',{exact:true}).click();
 await expect(chart.locator('tbody tr')).toHaveCount(6);
 await expect(chart.locator('tbody tr').first().locator('td')).toHaveCount(7);
 for(const width of [1280,390,360]){
  await page.setViewportSize({width,height:900});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await chart.screenshot({path:`/tmp/care-charts-${width}.png`});
 }
 await loginAs(page,'Mikko');
 await page.getByText('기간별 기록 분포 자세히 보기',{exact:true}).click();
 await expect(chart.locator('.care-topic-card')).toHaveCount(3);
 await expect(chart.getByLabel('그래프 항목').locator('option[value=outdoors]')).toHaveCount(0);
 await expect(chart.getByText('비공유',{exact:true})).toHaveCount(0);
 await chart.getByText('날짜별 수치 보기',{exact:true}).click();await expect(chart.locator('tbody tr')).toHaveCount(3);
 await expect(chart.locator('.radar-chart text').filter({hasText:'야외 활동'})).toHaveCount(0);
 await page.context().setOffline(true);
 await expect(chart.getByRole('alert')).toBeVisible();
 await expect(chart.getByRole('img')).toHaveCount(0);
 await page.context().setOffline(false);
 expect(errors).toEqual([]);
});
