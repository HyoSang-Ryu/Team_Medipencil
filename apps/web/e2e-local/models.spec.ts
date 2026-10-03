import {test,expect} from '@playwright/test';
import {mkdtempSync,rmSync,readFileSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';

// Explicit opt-in suite: real installed models, actual API/SQLite, synthetic TTS only.
test('real local speech and LLM reach reviewed family publication; cancellation never creates a source',async({page},testInfo)=>{
 const root=mkdtempSync(join(tmpdir(),'medipencil-browser-local-'));
 try{
  const input='Tämä on synteettinen testi. Ulkoilu ei toteutunut.';
  execFileSync('say',['-v','Eddy (핀란드어(핀란드))','-o',join(root,'speech.aiff'),input]);
  execFileSync('/opt/homebrew/bin/ffmpeg',['-y','-i',join(root,'speech.aiff'),'-ar','16000','-ac','1',join(root,'speech.wav')],{stdio:'ignore'});
  const wav=readFileSync(join(root,'speech.wav'));
  await page.goto('/');await page.getByRole('button',{name:'Koskinen',exact:true}).click();
  await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
  await expect(page.getByText('Paikallinen STT: whisper',{exact:false})).toBeVisible();
  await page.getByLabel('Luonnoksen käsittely').selectOption('manual');
  await page.getByLabel('Alkuperäinen teksti').fill('Synteettisen tallenteen käsittely sallittu.');
  await page.getByRole('button',{name:'Luo tarkistettava luonnos',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Kirjaus · Luonnos · v1'})).toBeVisible();
  await page.getByText('Erillinen äänitallennuksen lupa',{exact:true}).click();
  await page.getByLabel('Olen tarkistanut erillisen äänitallennusluvan',{exact:false}).check();
  await page.getByRole('button',{name:'Vahvista tallennusluvan viite'}).click();
  const code=page.locator('code');await expect(code).toBeVisible();
  const permission=(await code.textContent())!;
  await page.getByLabel('Erillisen tallennusluvan viite',{exact:true}).fill(permission);
  await page.getByLabel('Synteettinen WAV',{exact:false}).setInputFiles({name:'synthetic.wav',mimeType:'audio/wav',buffer:wav});
  await page.getByLabel('Äänen käsittely on ilmoitettu.',{exact:false}).check();
  const jobs:Record<string,unknown>[]=[];
  page.on('response',async r=>{if(/\/staff\/jobs\//.test(r.url())&&r.ok()){const data=(await r.json()).data;if(data.status==='succeeded')jobs.push(data);}});
  await page.getByRole('button',{name:'Litteroi paikallisesti'}).click();
  await expect(page.getByText('STT LIVE · whisper',{exact:false})).toBeVisible({timeout:180000});
  await expect(page.getByRole('heading',{name:'Tarkistettava litterointi — puhuja tuntematon'})).toBeVisible();
  await page.getByLabel('Luonnoksen käsittely').selectOption('local');
  await page.getByRole('button',{name:'Luo litteroinnista luonnos'}).click();
  await expect(page.getByText('LIVE · ollama',{exact:false})).toBeVisible({timeout:180000});
  await expect(page.getByRole('button',{name:'Hyväksy kirjaus'})).toBeDisabled();
  // These clicks are automation, NOT a Finnish expert's semantic approval.
  await page.getByLabel('Tarkistin lähteen, merkityksen',{exact:false}).check();
  await page.getByRole('button',{name:'Hyväksy kirjaus'}).click();
  await page.getByRole('button',{name:'Valmistele julkaisu'}).click();
  await page.getByLabel('Tarkistin jokaisen lauseen',{exact:false}).check();
  await page.getByRole('button',{name:'Julkaise hyväksytty vastaus'}).click();
  await expect(page.getByRole('status',{name:'Julkaisun tila'})).toContainText('Julkaistu.');
  await page.getByRole('button',{name:'Liisa',exact:true}).click();
  await expect(page.getByText('Ulkoilu ei toteutunut.',{exact:false}).first()).toBeVisible();
  await expect(page.getByText('Kertomus — puhuja tuntematon',{exact:false})).toBeVisible();
  await page.getByRole('button',{name:'Näytä lähde'}).click();
  await expect(page.getByLabel('Lähde',{exact:true})).toContainText('Ulkoilu ei toteutunut.');
  await expect(page.getByLabel('Lähde',{exact:true})).not.toContainText('suora syöttö');
  await page.screenshot({path:'/tmp/medipencil-local-family.png',fullPage:true});
  expect(jobs.some((j:any)=>j.execution.provider_id==='whisper'&&j.execution.ai_executed)).toBeTruthy();
  expect(jobs.some((j:any)=>j.execution.provider_id==='ollama'&&j.execution.ai_executed)).toBeTruthy();
  await testInfo.attach('real-model-execution',{body:JSON.stringify({scope:'REAL_LOCAL_BROWSER_TEAM_SYNTHETIC',input,jobs,human_language_review:'NOT_VERIFIED'},null,2),contentType:'application/json'});
  // Start a second actual Whisper job and cancel before it can return a source.
  await page.getByRole('button',{name:'Koskinen',exact:true}).click();await page.getByRole('link',{name:'Kirjaa ja julkaise'}).click();
  await page.getByLabel('Erillisen tallennusluvan viite',{exact:true}).fill(permission);
  await page.getByLabel('Synteettinen WAV',{exact:false}).setInputFiles({name:'cancel.wav',mimeType:'audio/wav',buffer:wav});
  await page.getByLabel('Äänen käsittely on ilmoitettu.',{exact:false}).check();
  const uploadResponse=page.waitForResponse(r=>r.url().endsWith('/audio')&&r.request().method()==='POST');
  const transcribeResponse=page.waitForResponse(r=>r.url().endsWith('/transcribe')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Litteroi paikallisesti'}).click();
  const capture=(await (await uploadResponse).json()).data;
  const queued=(await (await transcribeResponse).json()).data;
  await expect.poll(async()=>((await (await page.request.get('/api/v1/staff/jobs/'+queued.job_id)).json()).data.status)).toBe('running');
  await page.getByRole('button',{name:'Peruuta litterointi'}).click();
  await expect.poll(async()=>((await (await page.request.get('/api/v1/staff/jobs/'+queued.job_id)).json()).data.status)).toBe('canceled');
  await expect.poll(async()=>((await (await page.request.get('/api/v1/staff/captures/'+capture.capture_id+'/audio-status')).json()).data.runtime.deletion_status)).toBe('deleted');
  const canceled=(await (await page.request.get('/api/v1/staff/captures/'+capture.capture_id)).json()).data;
  expect(canceled.status).toBe('canceled');expect(canceled.source_refs).toEqual([]);
  writeFileSync('/tmp/medipencil-local-browser-result.json',JSON.stringify({scope:'REAL_LOCAL_BROWSER_TEAM_SYNTHETIC',input,models:[...new Map(jobs.map((j:any)=>[j.job_id,j.execution])).values()],family_publication:true,evidence_visible:true,explicit_automated_approval:true,cancel_running_stt:{capture_status:canceled.status,source_count:canceled.source_refs.length,local_upload_deleted:true},human_language_review:'NOT_VERIFIED'},null,2)+'\n');
  await testInfo.attach('real-stt-cancel',{body:JSON.stringify({capture_status:canceled.status,source_count:canceled.source_refs.length,job_id:queued.job_id,local_upload_deleted:true}),contentType:'application/json'});
 }finally{rmSync(root,{recursive:true,force:true});}
});
