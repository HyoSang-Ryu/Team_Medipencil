import {expect,type Page} from '@playwright/test';
export async function loginAs(page:Page,name:string,details=true){
 const logout=page.getByTestId('logout');
 if(await logout.isVisible())await logout.click();
 if(!await page.getByRole('radio',{name,exact:true}).isVisible())await page.getByTestId(name==='Koskinen'?'staff-login-link':'family-login-link').click();
 await page.getByRole('radio',{name,exact:true}).check();
 await page.getByTestId('login-submit').click();
 await expect(page.getByTestId('viewer-identity')).toContainText(name);
 // Existing workflow tests explicitly open the detailed care workspace.
 if(details&&name!=='Koskinen')await page.getByTestId('guardian-detail-link').click();
}
