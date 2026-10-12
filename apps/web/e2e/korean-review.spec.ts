import {test,expect} from '@playwright/test';
import {loginAs} from './login';
test('Korean staff sees synthetic content translation without replacing Finnish evidence',async({page})=>{
 await page.goto('/');await page.locator('.interface-control select').selectOption('en');await loginAs(page,'Koskinen',false);
 await page.getByRole('button',{name:'Start with synthetic EMR'}).click();
 await page.locator('.interface-control select').selectOption('ko');
 const capture=page.locator('.capture');
 await expect(capture.locator('.emr-original')).toContainText('아이노는 식당에서 아침 식사를 했습니다.');
 await expect(capture.locator('.emr-original')).toContainText('실제로 진행했는지는 아직 확인되지 않았습니다.');
 await expect(capture.locator('.emr-original [lang="fi"]').first()).toContainText('Aino söi aamupalan ruokasalissa.');
 await capture.getByRole('button',{name:'원문 기반 시연 초안 만들기 · AI 미실행'}).click();
 const draft=capture.locator('.review-grid article');
 await expect(draft).toContainText('아이노는 간호사와 함께 복도를 걸었습니다.');
 await expect(draft.locator('textarea').first()).toHaveValue('Aino söi aamupalan ruokasalissa.');
 await page.locator('.interface-control select').selectOption('fi');
 await expect(capture.locator('.review-korean')).toHaveCount(0);
 await expect(draft).toContainText('Aino käveli hoitajan kanssa käytävällä.');
});
