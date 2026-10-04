import {useUiLanguage} from './UiLanguage';
import content from './manual-content.json';
const labels={fi:{title:'PoC tukitiimin arviointia varten',summary:'Kokeilun vaiheet ja arviointiohjeet',scope:'Itsenäinen synteettinen aineisto · Suora syöttö · Tekoäly ei ole käytössä tällä kierroksella. Automaattiset testit ja tiimin todellinen palaute kirjataan erikseen.'},ko:{title:'온라인 지원팀 검토용 PoC',summary:'한국어 사용 순서와 검토 안내',scope:'독립 합성자료 · 직접 입력 · 이 회차는 AI 미사용. 자동 시험과 지원팀의 실제 의견은 별도로 기록합니다.'},en:{title:'PoC for online support-team review',summary:'English walkthrough and review notes',scope:'Independent synthetic data · Direct input · AI is disabled for this round. Automated tests and actual support-team feedback are recorded separately.'}};
export function PocGuide({compact=false}:{compact?:boolean}){
 const {language}=useUiLanguage();const text=labels[language];const sections=content[language];
 const start=sections.find(s=>s.id==='start')!;const walkthrough=sections.find(s=>s.id==='walkthrough')!;
 return <details className="poc-guide" open={!compact} lang={language} aria-label={text.title}>
  <summary><h2>{text.title}</h2></summary><div className="guide-body"><p>{text.scope}</p><p>{start.steps[0]} {start.steps[1]}</p>
  <details><summary>{text.summary}</summary><ol>{walkthrough.steps.map((step,i)=><li key={i}>{step}</li>)}</ol>{walkthrough.notes.map((note,i)=><p key={i}>{note}</p>)}</details></div>
 </details>;
}
