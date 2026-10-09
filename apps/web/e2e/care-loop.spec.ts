import {loginAs} from './login';
import {test,expect} from '@playwright/test';

test('real API + SQLite care loop, recipient isolation, language, responsive views',async({page})=>{
 await page.setViewportSize({width:1280,height:900});await page.goto('/');
 await loginAs(page,'Liisa');
 await page.getByLabel('Kysymys',{exact:true}).fill('Miten ulkoilu sujui?');
 await page.getByRole('button',{name:'Lähetä kysymys'}).click();
 await expect(page.getByText('Miten ulkoilu sujui?',{exact:true})).toBeVisible();
 await loginAs(page,'Koskinen');
 await expect(page.getByText('Miten ulkoilu sujui?',{exact:true})).toBeVisible();
 await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
 await page.getByLabel('Liitä omaan kysymykseen').selectOption({label:'Miten ulkoilu sujui?'});
 await page.getByLabel('Alkuperäinen teksti').fill('Aino kertoi polven kivusta ulkoillessa.');
 await page.getByLabel('Tiedon sisältö').selectOption('outdoors,health_context');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos'}).click();
 await expect(page.getByRole('heading',{name:'Kirjaus · Luonnos · v1'})).toBeVisible();
 await expect(page.getByRole('button',{name:'Hyväksy kirjaus'})).toBeDisabled();
 await page.getByLabel('Tarkistin lähteen, merkityksen', {exact:false}).check();
 await page.getByRole('button',{name:'Hyväksy kirjaus'}).click();
 await expect(page.getByRole('heading',{name:'Kirjaus · Hyväksytty · v1'})).toBeVisible();
 await page.getByRole('button',{name:'Valmistele julkaisu'}).click();
 await page.getByLabel('Tarkistin jokaisen lauseen', {exact:false}).check();
 await page.getByRole('button',{name:'Julkaise valituille läheisille'}).click();
 await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await page.screenshot({path:'/tmp/medipencil-staff-1280.png',fullPage:true});
 await loginAs(page,'Liisa');
 await expect(page.getByText('Aino kertoi polven kivusta ulkoillessa.',{exact:true})).toBeVisible();
 await page.locator('.daily-entry').filter({hasText:'Aino kertoi polven kivusta ulkoillessa.'}).getByRole('button',{name:'Näytä lähde'}).click();
 await expect(page.getByLabel('Lähde',{exact:true})).toContainText('Aino kertoi');
 await page.getByLabel('Kieli',{exact:true}).selectOption('sv');
 await expect(page.getByText('Valitun kielen julkaisu ei ole saatavilla.',{exact:false})).toBeVisible();
 await expect(page.getByText('Nykyinen käyttäjä:',{exact:false})).toContainText('Liisa');
 await page.getByLabel('Kieli',{exact:true}).selectOption('fi');
 await page.setViewportSize({width:360,height:800});
 await expect(page.getByText('Aino kertoi polven kivusta ulkoillessa.',{exact:true})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:'/tmp/medipencil-family-360.png',fullPage:true});
 const responsePromise=page.waitForResponse(r=>r.url().includes('/family/residents/aino/board')&&r.request().method()==='GET');
 await loginAs(page,'Mikko');
 const raw=await (await responsePromise).text();expect(raw).not.toContain('polven');
 await expect(page.getByText('Aino kertoi polven kivusta ulkoillessa.',{exact:true})).toHaveCount(0);
 await expect(page.locator('.daily-topic-outdoors')).toHaveCount(0);
});

test('record correction hides prior publication immediately',async({page})=>{
 await page.goto('/');await loginAs(page,'Koskinen');await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
 await page.getByLabel('Alkuperäinen teksti').fill('Korjattava synteettinen havainto.');
 await page.getByLabel('Tiedon sisältö').selectOption('outdoors');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos'}).click();
 await page.getByLabel('Tarkistin lähteen, merkityksen',{exact:false}).check();await page.getByRole('button',{name:'Hyväksy kirjaus'}).click();
 await page.getByRole('button',{name:'Valmistele julkaisu'}).click();await page.getByLabel('Tarkistin jokaisen lauseen',{exact:false}).check();await page.getByRole('button',{name:'Julkaise valituille läheisille'}).click();
 await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await page.getByRole('button',{name:'Aloita korjaus ja piilota vanha julkaisu'}).click();
 await expect(page.getByRole('heading',{name:'Kirjaus · Luonnos · v2'})).toBeVisible();
 await loginAs(page,'Liisa');
 await expect(page.getByText('Korjattava synteettinen havainto.',{exact:true})).toHaveCount(0);
});

test('screen 5 simple sharing settings persist and isolate guardians',async({page})=>{
 await page.goto('/');await loginAs(page,'Koskinen');
 await page.locator('.interface-control select').selectOption('en');
 await page.locator('header').getByRole('link',{name:'Consent',exact:true}).click();
 const guardian=page.getByRole('combobox',{name:'Select guardian',exact:true});
 await guardian.selectOption('mikko');
 const outdoors=page.getByRole('checkbox',{name:'Outdoor activity',exact:true});
 await expect(outdoors).not.toBeChecked();await outdoors.check();
 await page.getByRole('textbox',{name:'Confirmation evidence',exact:true}).fill('Synthetic consent: authorized person permits outdoor updates.');
 await page.getByLabel('Consent confirmation date',{exact:true}).fill('2026-09-01');
 const confirm=page.getByRole('checkbox',{name:'I verified the wishes of the person authorized to consent and the changes.',exact:true});
 await confirm.check();await guardian.selectOption('liisa');
 await expect(page.getByRole('button',{name:'Save sharing settings',exact:true})).toBeDisabled();
 await guardian.selectOption('mikko');await expect(outdoors).not.toBeChecked();await outdoors.check();
 await page.getByRole('textbox',{name:'Confirmation evidence',exact:true}).fill('Synthetic consent confirmed by authorized person.');
 await page.getByLabel('Consent confirmation date',{exact:true}).fill('2026-09-01');await confirm.check();
 await page.getByRole('button',{name:'Save sharing settings',exact:true}).click();
 await expect(page.getByRole('status')).toContainText('Sharing settings saved.');
 await expect(outdoors).toBeChecked();await page.reload();await loginAs(page,'Koskinen');await page.locator('header').getByRole('link',{name:'Consent',exact:true}).click();await guardian.selectOption('mikko');await expect(outdoors).toBeChecked();
 await outdoors.uncheck();await page.getByRole('textbox',{name:'Confirmation evidence',exact:true}).fill('Synthetic revocation requested.');
 await page.getByLabel('Consent confirmation date',{exact:true}).fill('2026-09-01');await confirm.check();await page.getByRole('button',{name:'Save sharing settings',exact:true}).click();
 await expect(page.getByRole('status')).toContainText('Sharing settings saved.');await expect(outdoors).not.toBeChecked();
});

test('offline masks content and previous viewer response cannot reappear',async({page,context})=>{
 await page.goto('/');await loginAs(page,'Liisa');await expect(page.getByRole('heading',{name:'Ainon päivän kuulumiset'})).toBeVisible();
 await context.setOffline(true);await page.evaluate(()=>window.dispatchEvent(new Event('offline')));
 await expect(page.getByRole('alert').filter({hasText:'Verkkoyhteys katkesi'})).toBeVisible();
 await context.setOffline(false);await page.evaluate(()=>window.dispatchEvent(new Event('online')));
 // Delay a real server response, rather than fabricate an API result.
 let release!:()=>void;const gate=new Promise<void>(resolve=>{release=resolve;});let started!:()=>void;const seen=new Promise<void>(resolve=>{started=resolve;});
 await page.route('**/family/residents/aino/board?lang=sv',async route=>{const real=await route.fetch();started();await gate;try{await route.fulfill({response:real});}catch{/* browser canceled the old request */}});
 await page.getByLabel('Kieli',{exact:true}).selectOption('sv');await seen;
 await loginAs(page,'Mikko');release();
 await expect(page.getByText('Nykyinen käyttäjä:',{exact:false})).toContainText('Mikko');
 await expect(page.getByText('Aino kertoi polven kivusta ulkoillessa.',{exact:true})).toHaveCount(0);
});

test('explicit local LLM failure leaves manual input available',async({page})=>{
 await page.goto('/');await loginAs(page,'Koskinen');
 await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
 await page.getByLabel('Luonnoksen käsittely').selectOption('local');
 await page.getByLabel('Alkuperäinen teksti').fill('Synteettinen epäonnistumisen testi.');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos',exact:true}).click();
 await expect(page.getByRole('alert')).toContainText('PROVIDER_NOT_CONFIGURED');
 await page.getByLabel('Luonnoksen käsittely').selectOption('manual');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Kirjaus · Luonnos · v1'})).toBeVisible();
});
