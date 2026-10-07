import {expect,type Page} from '@playwright/test';
export async function loginAs(page:Page,name:string){
 const logout=page.getByTestId('logout');
 if(await logout.isVisible())await logout.click();
 await page.getByRole('button',{name,exact:true}).click();
 await expect(page.getByTestId('viewer-identity')).toContainText(name);
}
