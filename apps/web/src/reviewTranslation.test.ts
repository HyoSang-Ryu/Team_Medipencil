import {expect,test} from 'vitest';
import {koreanReviewTranslation as translate} from './reviewTranslation';
test('synthetic plans remain unconfirmed and amounts retain exact values',()=>{
 expect(translate('Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vielä vahvistettu.')).toBe('오후에 야외 활동이 예정되어 있습니다. 실제로 진행했는지는 아직 확인되지 않았습니다.');
 expect(translate('Aino söi aamupalasta 50 prosenttia.')).toContain('50%');
 expect(translate('Yövuoron kirjauksen mukaan Aino heräsi yön aikana 0 kertaa.')).toContain('0회');
});
test('dated evidence keeps its date and unknown or altered prose is not guessed',()=>{
 const prefix='2026-10-12T08:00:00+03:00 · ';
 expect(translate(prefix+'Aino käveli hoitajan kanssa 15 minuuttia.')).toBe(prefix+'아이노는 간호사와 함께 15분 동안 걸었습니다.');
 expect(translate('Aino ei käveli hoitajan kanssa käytävällä.')).toBeNull();
 expect(translate('AI-generated summary.')).toBeNull();
 expect(translate('Aino söi aamupalasta 80 prosenttia.')).toBeNull();
});
