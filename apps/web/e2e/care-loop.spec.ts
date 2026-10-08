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
 await page.getByRole('button',{name:'Julkaise hyväksytty vastaus'}).click();
 await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await page.screenshot({path:'/tmp/medipencil-staff-1280.png',fullPage:true});
 await loginAs(page,'Liisa');
 await expect(page.getByText('Aino kertoi polven kivusta ulkoillessa.',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Näytä lähde'}).click();
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
 await page.getByRole('button',{name:'Valmistele julkaisu'}).click();await page.getByLabel('Tarkistin jokaisen lauseen',{exact:false}).check();await page.getByRole('button',{name:'Julkaise hyväksytty vastaus'}).click();
 await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await page.getByRole('button',{name:'Aloita korjaus ja piilota vanha julkaisu'}).click();
 await expect(page.getByRole('heading',{name:'Kirjaus · Luonnos · v2'})).toBeVisible();
 await loginAs(page,'Liisa');
 await expect(page.getByText('Korjattava synteettinen havainto.',{exact:true})).toHaveCount(0);
});

test('screen 5 candidate and revocation change actual API visibility',async({page})=>{
 await page.goto('/');await loginAs(page,'Koskinen');await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
 await page.getByLabel('Alkuperäinen teksti').fill('Mikko saa ulkoilutiedon.');await page.getByLabel('Tiedon sisältö').selectOption('outdoors');
 await page.getByRole('button',{name:'Luo tarkistettava luonnos'}).click();await page.getByLabel('Tarkistin lähteen, merkityksen',{exact:false}).check();await page.getByRole('button',{name:'Hyväksy kirjaus'}).click();await expect(page.getByRole('heading',{name:'Kirjaus · Hyväksytty · v1'})).toBeVisible();
 await page.getByRole('link',{name:'Suostumukset',exact:true}).click();await page.getByRole('button',{name:'Lataa suostumukset ja lähteet'}).click();
 await page.getByLabel('Valitse omainen',{exact:true}).selectOption('mikko');await page.getByLabel('Suostumuksen lähdelausuma').selectOption({label:'Mikko saa ulkoilutiedon.'});await page.getByRole('button',{name:'Luo ulkoilun jakamisehdotus'}).click();
 await expect(page.getByText('Lisättävä: mikko → outdoors')).toBeVisible();
 await page.getByLabel('Vahvistan henkilöt',{exact:false}).check();await page.getByRole('button',{name:'Vahvista rajattu jakaminen'}).click();
 await expect(page.getByText('mikko · v2:',{exact:false})).toContainText('outdoors');
 await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();await page.getByLabel('Vastaanottaja',{exact:false}).selectOption('mikko');
 await page.getByRole('button',{name:'Valmistele julkaisu'}).click();await page.getByLabel('Tarkistin jokaisen lauseen',{exact:false}).check();await page.getByRole('button',{name:'Julkaise hyväksytty vastaus'}).click();await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
 await loginAs(page,'Mikko');await expect(page.getByText('Mikko saa ulkoilutiedon.',{exact:true})).toBeVisible();
 await loginAs(page,'Koskinen');await page.getByRole('link',{name:'Suostumukset',exact:true}).click();await page.getByRole('button',{name:'Lataa suostumukset ja lähteet'}).click();
 await page.getByLabel('Vahvistan henkilöt',{exact:false}).check();await page.getByRole('button',{name:'Peru mikko: outdoors',exact:true}).click();
 await expect(page.getByText('mikko · v3:',{exact:false})).not.toContainText('outdoors');
 await loginAs(page,'Mikko');await expect(page.getByText('Mikko saa ulkoilutiedon.',{exact:true})).toHaveCount(0);
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
