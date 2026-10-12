// Display-only translations of the independent synthetic fixture vocabulary.
// Never translate unknown/generated prose by guessing, or change stored evidence.
const korean:Record<string,string>={
 'Aino söi aamupalan ruokasalissa.':'아이노는 식당에서 아침 식사를 했습니다.',
 'Aino käveli hoitajan kanssa käytävällä.':'아이노는 간호사와 함께 복도를 걸었습니다.',
 'Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vielä vahvistettu.':'오후에 야외 활동이 예정되어 있습니다. 실제로 진행했는지는 아직 확인되지 않았습니다.',
 'Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vahvistettu.':'오후에 야외 활동이 예정되어 있습니다. 실제로 진행했는지는 확인되지 않았습니다.',
};
for(const n of [50,75,100])korean[`Aino söi aamupalasta ${n} prosenttia.`]=`아이노는 아침 식사의 ${n}%를 먹었습니다.`;
for(const n of [5,10,15])korean[`Aino käveli hoitajan kanssa ${n} minuuttia.`]=`아이노는 간호사와 함께 ${n}분 동안 걸었습니다.`;
for(const n of [0,1,2])korean[`Yövuoron kirjauksen mukaan Aino heräsi yön aikana ${n} kertaa.`]=`야간 근무 기록에 따르면 아이노는 밤에 ${n}회 깼습니다.`;
export function koreanReviewTranslation(text:string):string|null{
 const lines=text.split('\n').map(line=>{
  const dated=line.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z) · )(.*)$/);
  const translated=korean[dated?dated[2]:line];
  return translated?(dated?dated[1]:'')+translated:null;
 });
 return lines.every(line=>line!==null)?lines.join('\n'):null;
}
