import {useUiLanguage} from './UiLanguage';
export function PocGuide(){
 const {language}=useUiLanguage();
 if(language==='en')return <section lang="en" aria-label="English PoC review guide">
 <h1>PoC for online support-team review</h1>
 <p>Independent synthetic data · Direct input · AI is disabled for this round. Automated tests and actual support-team feedback are recorded separately.</p>
 <p>Use separate browsers or separate browser profiles for family and staff. Two tabs in the same profile share login cookies and are not independent sessions.</p>
 <details><summary>English walkthrough and review notes</summary><ol>
 <li>In the family browser, select <strong>Liisa</strong>. Enter a synthetic Question and choose Send question.</li>
 <li>In the staff browser, select <strong>Koskinen</strong>. Check the question queue. Schedule review sets a planned review time; Keep unanswered leaves the question open.</li>
 <li>Open Record and publish, link the question and enter Original text. Select Plan — not completed for a plan. Direct processing — no LLM uses no AI.</li>
 <li>Create draft for review. Check the source, speaker, tense and sharing limits. Save any edits and check the review box again before choosing Approve record. Approval alone does not disclose anything to the family.</li>
 <li>Prepare publication, check the recipient and each sentence, then Publish approved answer. Refresh the family view and choose Show source.</li>
 </ol><p>Mikko has different sharing permissions. Changing interface or publication language does not change the user. Consent contains separate candidate, confirmation and revocation steps.</p>
 <p>Synthetic example: “Was a walk completed today?” Source: “A walk with staff is planned after lunch.” Do not mark the walk completed without a later confirmed observation. Never enter real people’s or facilities’ information.</p>
 <p>Interface translation does not translate submitted questions, records or evidence. The publication content channel remains Finnish; English publication translation is not implemented.</p>
 <p>For feedback, record the blocked screen, reproduction steps, expected result and actual result using the team’s existing channel. This app does not send feedback externally. Finnish and English specialist wording reviews remain pending.</p>
 </details></section>;
return <section lang="ko" aria-label="한국어 PoC 검토 안내">
 <h1>온라인 지원팀 검토용 PoC</h1>
 <p>독립 합성자료 · 직접 입력 · 이 회차는 AI 미사용. 자동 시험과 지원팀의 실제 의견은 별도로 기록합니다.</p>
 <p>가족과 직원은 서로 다른 브라우저 또는 분리된 브라우저 프로필을 사용하세요. 같은 프로필의 탭 두 개는 로그인 쿠키를 공유하므로 독립 세션이 아닙니다.</p>
 <details><summary>한국어 사용 순서와 화면 용어</summary>
 <ol>
 <li>가족 창에서 <strong>Liisa</strong> 선택 → Kysymys(질문)에 합성 질문 입력 → Lähetä kysymys(보내기).</li>
 <li>직원 창에서 <strong>Koskinen</strong> 선택 → 질문 큐 확인. Sovi tarkistus는 확인 예정, Jätä odottamaan은 미답변 유지입니다.</li>
 <li>Kirjaa ja julkaise(기록·발행) → 질문 연결 → Alkuperäinen teksti(원문) 입력. Tyyppi의 Suunnitelma는 계획이며 완료가 아닙니다. Suora käsittely는 AI 없는 직접 처리입니다.</li>
 <li>Luo tarkistettava luonnos(초안 만들기) → 원문·화자·계획·공개 범위 검토 → Hyväksy kirjaus(기록 승인). 승인만으로 가족에게 공개되지 않습니다.</li>
 <li>Valmistele julkaisu(발행 미리보기) → 수신자와 각 문장 검토 → Julkaise hyväksytty vastaus(발행). 가족 창에서 새로고침 → Näytä lähde(근거 보기).</li>
 </ol>
 <p>Mikko는 건강정보 공개 범위가 다른 가족입니다. 언어 선택은 사용자 변경이 아닙니다. Suostumukset는 동의 후보·확인·철회 화면입니다.</p>
 <p>예시 질문: “오늘 산책을 했나요?” / 오전 원문: “점심 후 직원과 산책할 계획이다.” 오후 확인 전에는 완료로 바꾸지 마세요. 실제 사람·시설 정보는 입력하지 않습니다.</p>
 <p>피드백에는 막힌 화면, 재현 순서, 기대한 결과, 실제 결과를 적어 담당자에게 전달하세요. 이 앱은 피드백을 외부로 전송하지 않습니다. FI 문구의 전문 검수는 미완료입니다.</p>
 </details>
 </section>;}
