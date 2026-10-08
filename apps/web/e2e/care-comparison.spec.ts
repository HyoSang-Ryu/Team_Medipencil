import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('pitch portraits and comparison lead to an editable question, never an automatic send',async({page})=>{
 await page.goto('/');await loginAs(page,'Koskinen');await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
 await page.getByLabel('Alkuperäinen teksti').fill('Synteettinen vertailu: ulkoilu on suunnitteilla.');await page.getByLabel('Tiedon sisältö').selectOption('outdoors');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos'}).click();await page.getByLabel('Tarkistin lähteen, merkityksen',{exact:false}).check();await page.getByRole('button',{name:'Hyväksy kirjaus'}).click();
 await page.getByRole('button',{name:'Valmistele julkaisu'}).click();await page.getByLabel('Tarkistin jokaisen lauseen',{exact:false}).check();await page.getByRole('button',{name:'Julkaise valituille läheisille'}).click();await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await page.locator('.interface-control select').selectOption('ko');await loginAs(page,'Liisa');
 await expect(page.getByRole('img',{name:'Aino 시연 사진'})).toBeVisible();await expect(page.getByRole('img',{name:'Liisa 시연 사진'})).toBeVisible();
 const image=page.locator('.aino-portrait img');expect(await image.evaluate(el=>(el as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
 // This test publishes its own independent synthetic entry through the real care loop.
 const row=page.locator('.comparison-item').filter({hasText:'야외 활동'});
 await row.locator('summary').click();
 let sent=0;page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/questions'))sent++;});
 await row.getByRole('button',{name:'이 항목을 간호사에게 질문'}).click();
 const field=page.locator('#ask-nurse textarea');await expect(field).toHaveValue('야외 활동 기록에서 어제와 오늘 달라진 점을 알려주세요.');expect(sent).toBe(0);
 await field.fill('작성 중인 질문을 보존합니다.');await row.getByRole('button',{name:'이 항목을 간호사에게 질문'}).click();await expect(field).toHaveValue('작성 중인 질문을 보존합니다.');expect(sent).toBe(0);
 await loginAs(page,'Mikko');await expect(page.getByRole('img',{name:'Mikko 시연 사진'})).toBeVisible();await expect.poll(()=>page.locator('.mikko-portrait').evaluate(el=>(el as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);await expect(page.getByRole('img',{name:'Liisa 시연 사진'})).toHaveCount(0);await expect(page.locator('.comparison-item').filter({hasText:'야외 활동'})).toHaveCount(0);await expect(page.locator('#ask-nurse textarea')).toHaveValue('');
});
