import {expect,type Page} from '@playwright/test';
export async function loginAs(page:Page,name:string,details=true){
 const display=({Liisa:'Liisa Nieminen',Koskinen:'Heli Koskinen'} as Record<string,string>)[name]??name;
 await logoutCurrent(page);
 if(!await page.getByRole('radio',{name:display,exact:true}).isVisible())await page.getByTestId(name==='Koskinen'?'staff-login-link':'family-login-link').click();
 await page.getByRole('radio',{name:display,exact:true}).check();
 await page.getByTestId('login-submit').click();
 await expect(page.getByTestId('viewer-identity')).toContainText(name);
 // Existing workflow tests explicitly open the detailed care workspace.
 if(details&&name==='Koskinen')await page.locator('header a[href$="/staff/queue"]').click();
 if(details&&name!=='Koskinen')await page.getByTestId('guardian-detail-link').click();
}

export async function logoutCurrent(page:Page){
 if(await page.getByTestId('guardian-menu-toggle').isVisible()){
  await page.getByTestId('guardian-menu-toggle').click();
  await page.getByTestId('guardian-menu-logout').click();
 }else if(await page.getByTestId('logout').isVisible())await page.getByTestId('logout').click();
}
export async function setInterfaceLanguage(page:Page,language:string){
 if(await page.getByTestId('guardian-menu-toggle').isVisible()){
  await page.getByTestId('guardian-menu-toggle').click();
  await page.locator('.guardian-menu-links select').selectOption(language);
  await page.locator('.guardian-menu-top button').last().click();
 }else await page.locator('.interface-control select').selectOption(language);
}
