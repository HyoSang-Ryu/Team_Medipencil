# PoC 검증 기록

## PC-00 · 출발점 / 2026-10-03

- 실행 기준: 최신 main `4802e81534f273e1ed2507129a91badf93c64f2a`의 AGENTS.md, docs/poc/README.md와 docs/development/README.md를 읽었다. 기존 v1.1/01~03은 승인·근거·권한 추적 참고이며 구현 개수 목표가 아니다.
- 명령: `git status --short --branch`, `git remote -v`, `git fetch origin main`, `git rev-parse origin/main`, `git show origin/main:AGENTS.md`, `git show origin/main:docs/poc/README.md` → 성공.
- 기존 HEAD `e28a746`, branch `codex/care-loop-mvp`, 작업 트리 clean. FastAPI/SQLite/React 직접 입력·로컬 모델·권한/정정 테스트가 이미 있었다. 기존 코드·전체 커밋·작성 시점·설계 SVG를 보존한다. 과거 구현 규모를 새 PoC 요구로 간주하지 않는다.
- `git switch -c poc/remote-validation`; `git merge --no-commit origin/main` → README.md 충돌1. 최신 main의 PoC 우선 구조를 채택하고 기존 로컬 구현·실행 링크를 사실대로 연결하여 해결. AGENTS/PoC README/개발 README는 최신 main을 그대로 반영한다.
- 재사용 선택: 이미 동작하는 서버·DB·세션·승인·발행을 재사용한다. schema/API 추가나 전체 재작성·기존 작업 삭제는 하지 않는다. 이번 검증 범위는 PC-01 직접 입력 + PC-02 핵심 공개 경계다. 이전 실제 AI 시험은 과거 별도 증거이며 PC-01 성공의 조건이 아니다.
- PC-04 공유 서버·배포 권한·접근 제한 방식 미지정. 로컬까지 진행한다. 지원팀 실제 피드백 없음(FB-ID 미발급); PC-05 사람 피드백 기반 재시험/PC-06 명세 결정은 NOT_RUN/AFTER_FEEDBACK.
- 내부 PoC와 대회 사전제작·반입 허용은 별개로 UNCONFIRMED. 공개 배포·주최 측 승인·지원팀 의견을 만들어 보고하지 않는다.


PC-00 최신 main 통합/기록 commit: **35425cc**. 기존 개발 branch 이력은 이 merge의 부모로 보존했다.

## PC-01 / PC-02 · PC01-AUTO-01 · 로컬 검토 준비 완료

| 항목 | 기록 |
|---|---|
| 환경 | macOS arm64, Python3.12, Node22.16, Chromium, FastAPI/Uvicorn + 파일 SQLite + React/Vite |
| build | 기준35425cc + 아래 변경; 구현 commit은 말미에 기록 |
| 회차·역할 | PC01-AUTO-01, 자동화가 Liisa/직원/Mikko 역할 수행. 지원팀 검토자 없음 |
| 모드 | MANUAL_NO_AI, 독립 합성자료. STT/LLM disabled. SIMULATED AI 결과 없음 |
| 독립 세션 | Chromium BrowserContext3개, 서로 다른 실제 session cookie3개 확인. cookie/CSRF 값은 증거에 남기지 않음 |
| 시나리오 | 가족 질문→직원 큐→미답변 유지→직접 입력 계획→문구 수정/저장→별도 승인→미리보기→발행→가족 답/근거→재접속 조회 |
| 공개 경계 | 초안/승인/미리보기 가족 미노출, 질문은 발행 후 answered, 계획은 planned 유지, Mikko raw JSON 비공개/evidence404 |
| 결과 | PASS, 표본1, 해당 자동 흐름11,003ms. 사람 검토·수정 시간은 null/미측정 |
| 증거 | docs/poc/evidence/pc01-independent-sessions.json; 로컬 screenshot /tmp/medipencil-poc-family.png, /tmp/medipencil-poc-staff.png |
| 피드백 | 실제 지원팀 피드백0건, FB-ID 없음. 자동시험을 사람 피드백으로 대체하지 않음 |

### 구현 범위와 변경 이유

- 기존 구현을 재사용하며 schema/table/API 추가 없이 PoC 모드와 검토 안내·시험을 추가. `run_demo.py --poc`는 사용자 로컬 모델 프로필을 읽지 않고 양쪽 provider를 disabled로 시작한다. Settings에서도 PoC 모드일 때 disabled를 강제해 표시와 실제 실행을 일치시킨다.
- 기존 health에 poc_mode 표시를 추가하고 화면 상단에 한국어 사용 순서·FI 용어·독립 세션 설명을 제공. 완전한 UI 한국어 번역·FI 전문가 검수 완료를 주장하지 않는다.
- `review-guide.md`에 로컬 실행/회차 재개/직접 사용 시나리오/공유 환경 미결/실제 의견 양식을 정리. `feedback-register.md`는 실제 의견0건 상태로 준비했다. 별도 피드백 플랫폼이나 새 상세명세를 만들지 않았다.

### 실패와 같은 사례 재시험

| ID | 발견 경로 | 원인/조치 | 재시험 |
|---|---|---|---|
| AUTO-01 (FB 아님) | 최초 독립 세션 시험30초 timeout | Tyyppi exact label이 option 텍스트 때문에 매칭되지 않음. 해당 label selector를 정확한 필드에 맞게 수정. 독립 세션 polling 흐름에60초 한도 지정; 검증 assertion 유지 | 같은 시험을 재실행 |
| AUTO-02 (제품 결함, FB 아님) | 두 번째 시험에서 발행 내용이 수정 전 문구 | Capture 수정 저장이 PATCH 대신 POST라405. 화면 편집값은 남았지만 이전 기록 승인 가능. PATCH로 수정하고 dirty 편집값이 있으면 승인 차단 | PATCH200/DB 반환 수정문 일치, 미저장 승인 버튼 disabled, 발행 후 가족의 수정문/근거 일치까지 PASS |
| AUTO-03 (계약 시험 정합화) | pytest health equality1 FAIL/63 PASS | poc_mode 필드 추가를 기존 기대값에 반영. PoC에서 모델 강제 disabled를 별도 검증 |65 PASS |

AUTO 번호는 개발 중 발견 기록이며 지원팀의 FB-ID가 아니다. 제품 결함 수정·재시험은 했지만 PC-05의 실제 피드백 처리 완료로 보고하지 않는다.

### 실제 실행 명령

- `npm --prefix apps/web run typecheck` → exit0 (Node22 PATH).
- `.venv/bin/python -m pytest apps/api/tests -q` → 최종 **65 PASS**,1.34초. Starlette/httpx deprecation 경고1.
- `npm --prefix apps/web run test:run` → **6 PASS**,547ms.
- `npm --prefix apps/web run test:e2e` → 처음5 PASS/1 timeout, 다음5 PASS/1 실제 편집·발행 불일치, 수정 후 **6 PASS**,17.9초. 신규 독립 세션 사례11.0초. 모든 suite는 실제 API/DB이며 서버 종료 확인.
- `npm --prefix apps/web run build > /tmp/medipencil-poc-build.log 2>&1` → exit0. 기존 dependency use-client 경고 유지.
- `.venv/bin/python tools/dev/run_demo.py --poc --port 8767` → 실제 빌드 앱 loopback 시작. Python httpx로 health(poc_mode=true)/정적 HTML/직원 세션/providers 모두 확인 → `BUILT_POC_LOOPBACK_START_HEALTH_STATIC_MANUAL_MODE=PASS`. Ctrl+C 후 정상 종료. 공유 서버는 아님.
- standalone 로컬 실행은 `~/.local/share/medipencil/runs/1cd3a2ec-03af-4a05-95c1-d1de2c0a8d9e`에 합성 DB를 남김. 임의 reset/삭제하지 않음. 자동 E2E는 별도 임시 DB를 사용·종료했다.
- `git diff --check` → exit0. screenshot 시각 검사에서 한국어 안내/수정된 계획/질문 답변 상태 확인. 스크린샷·DB·음성·키는 commit하지 않음.

### 단계별 현재 상태

| 단계 | 상태 | 남은 사항 |
|---|---|---|
| PC-00 | DONE | 최신 main 지침 확인, 별도 branch·기존 이력 보존 |
| PC-01 | LOCAL_PASS | 세 독립 세션 실제 서버/DB 직접 입력 흐름·재접속 검증 |
| PC-02 | LOCAL_PASS_IN_TESTED_SCOPE | 기존 권한/철회/저장 실패/중복 회귀와 신규 미저장 승인 경계 확인. 전체55항목 완료 아님 |
| PC-03 | NOT_RUN_THIS_ROUND | 이번 회차는 AI 미사용. 이전 branch의 실제 Whisper/Ollama 증거는 별도 보존, FI 전문 품질 미검증 |
| PC-04 | WAITING_FOR_SHARED_ENV_AND_REVIEWERS | 서버·배포 권한·접근 제한·HTTPS/VPN·회차/reset 담당·검토 일정/채널 미지정 |
| PC-05 | WAITING_FOR_ACTUAL_FEEDBACK | 지원팀 실제 의견 수집 후 FB-ID 기반 수정/같은 사례 재시험 |
| PC-06 | AFTER_FEEDBACK | 의견 수집 전 결정안/새 상세명세 확정 안 함 |

제출/원격 배포/주최 측 회신·승인은 실행하거나 확인하지 않았다. 내부 PoC의 대회 사전제작·반입 허용은 UNCONFIRMED를 유지한다. 사람 피드백이 없으므로 전체 PoC 실증 완료가 아니라 **로컬 검토 준비 완료**다.

### 변경 파일

- `apps/api/src/medipencil/config.py`
- `apps/api/src/medipencil/main.py`
- `apps/api/tests/test_foundation.py`
- `apps/web/e2e/poc-sessions.spec.ts`
- `apps/web/src/App.tsx`
- `apps/web/src/Capture.tsx`
- `apps/web/src/PocGuide.tsx`
- `docs/poc/evidence/pc01-independent-sessions.json`
- `docs/poc/feedback-register.md`
- `docs/poc/review-guide.md`
- `docs/poc/validation-log.md`
- `tools/dev/e2e_api.py`
- `tools/dev/run_demo.py`

PC-01/PC-02 구현·결함 수정·검증 build commit: **d4a1dd3**. 증거 JSON에도 이 코드 build를 연결했다. 뒤따르는 기록 commit은 실행 로직을 변경하지 않는다. branch `poc/remote-validation`, remote push/공유 배포 미실행.

## PC-04 준비 · LOCAL-REVIEW-02 / 2026-10-04 Asia/Tokyo

- 사용자 “진행해” 지시에 따라 지원팀 검토에 앞선 로컬 접속을 준비했다. 출발 HEAD `8d9804159b3bb18f225ee9f54649a09933ec4a04`, `poc/remote-validation`, clean. 실행 코드 build는 d4a1dd3이며 새 기능·명세 변경 없음.
- `git status --short --branch`, `git rev-parse HEAD`, 빌드 index 확인. `lsof -nP -iTCP:8767 -sTCP:LISTEN`은 listener 없음(exit1)을 확인했으며 기존 서버를 종료하지 않았다.
- `.venv/bin/python tools/dev/run_demo.py --poc --port 8767` 실행. loopback `http://127.0.0.1:8767`, STT/LLM 모두 disabled. 새 합성 회차 ID `34087081-13cd-4c64-be07-4848f8500c88`, 저장소 밖 `~/.local/share/medipencil/runs/34087081-13cd-4c64-be07-4848f8500c88`. 이전 회차 DB를 삭제·초기화하지 않았다.
- Python httpx 실제 GET으로 health(poc_mode=true), 빌드 HTML, JS asset HTTP200 및 한국어 PoC 안내 포함 확인 → `LOCAL_REVIEW_READY ... PASS`. 이 회차에서는 전체 회귀 suite나 실제 AI를 재실행하지 않았다.
- Codex browser 열기 도구에 URL 전달 → queued. 도구가 사용자의 실제 열람·검토 완료를 증명하는 것은 아니다. 사용자에게 직접 클릭할 로컬 URL을 제공했다.
- 검토용 서버는 켜 둔다. 명령 실행 세션에서 Ctrl+C로 중지할 수 있고 DB는 유지된다. 앱/장비 종료 이후 지속 실행을 보장하거나 자동 재시작을 설정한 것은 아니다.
- 승인된 공유 서버·HTTPS/VPN·접근 제한 방식·기존 피드백 채널을 사용자에게 확인 요청했다. 아직 답을 받지 않았으며 외부 배포·터널 개설·지원팀 메시지 발송은 하지 않았다.
- 실제 지원팀 피드백0건/FB-ID 없음/사람 사용성 시간 null. PC-04 원격 직접 사용, PC-05 실제 피드백 수정·재시험, PC-06 결정안·명세 확정은 여전히 대기한다. 이번 결과는 로컬 접속 준비이며 실증 완료가 아니다.

## 영어 검토 화면 · EN-AUTO-01 / 2026-10-04 Asia/Tokyo

- 사용자 “영어로도 해줘” 요청에 따라 기존 PoC의 영어 안내와 화면 1~5 주요 문구 전환을 추가했다. 출발 HEAD `65f7c1b`, branch `poc/remote-validation`, clean. 전체 다국어 제품이나 영어 발행 번역을 새로 구현한 것은 아니다.
- 변경: `apps/web/src/UiLanguage.tsx`, `english.json`, `App.tsx`, `Board.tsx`, `Capture.tsx`, `Publication.tsx`, `Consent.tsx`, `Audio.tsx`, `PocGuide.tsx`, `main.tsx`; `apps/web/e2e/english.spec.ts`; `docs/poc/review-guide.md`, `review-guide.en.md`, 이 검증 기록.
- UI 언어와 서버 발행 언어를 분리했다. 문구 사전은 화면 라벨에만 적용하고 질문·기록·근거 발췌를 번역하지 않는다. 세션 쿠키·사용자·권한·API payload를 언어 전환 때문에 변경하지 않는다. 새로고침 후 UI 선택은 기본 FI/한국어 안내로 돌아간다.
- 환경: 기존 macOS, Python 3.12.15, Node 22.16.0. 아래 npm 명령은 `export PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH` 후 실행했다. 자동 브라우저 시험은 별도 임시 SQLite와 실제 Uvicorn/Vite, 독립 Chromium contexts 3개를 사용한다. 사용자 검토 회차 DB는 reset하지 않았다.
- 모드: MANUAL_NO_AI / AUTOMATION_NOT_SUPPORT_TEAM. 관련 T-ID: T-01 계획, T-03 원문 충실, T-04 승인/발행, T-06 사용자/언어/응답 경계, T-10 시연 정직성의 해당 사례. 전체 수용 기준 완료라는 뜻은 아니다.
- `npm --prefix apps/web run typecheck` → PASS; `npm --prefix apps/web run test:run` → 6 PASS; `npm --prefix apps/web run build` → PASS. 기존 dependency의 use-client bundling 경고가 남는다.
- `npm --prefix apps/web run test:e2e` 1차 → 6 PASS / 영어 시험1 FAIL(18.8s): 로그인 응답 전 쿠키를 읽은 시험의 경합. 로그인 응답과 버튼 활성화를 기다리도록 수정. 비교 실패 메시지에 세션 값을 출력하지 않도록 boolean 비교로 변경.
- 동일 E2E 2차 → 6 PASS / 영어 시험1 FAIL(24.1s): 값이 들어간 textarea의 label 텍스트 selector가 재렌더 후 요소를 찾지 못함. 접근성 snapshot에서는 `textbox Kysymys`와 입력 보존을 확인했고, 정확한 role/name selector로 수정했다.
- 로컬 서버 `http://127.0.0.1:8767`에 새 dist 반영 후 `.venv/bin/python` + httpx로 `/api/v1/health`, HTML, JS asset을 GET: HTTP200, poc_mode=true, 영어 안내 포함 → PASS. 서버 재시작/기존 회차 데이터 변경 없음.
- 실제 STT/LLM 재시험, 전문 언어 검수, 공유 배포, 지원팀 직접 사용은 이번 회차 미실행. 실제 지원팀 피드백0건/FB-ID 없음. 사용자 영어 요청은 구현 지시이며 지원팀 실증 피드백으로 대체하지 않는다. PC-04~06의 기존 대기 조건은 유지한다.
- 동일 E2E 3차 → 6 PASS / 영어 시험1 FAIL(1.3m): select의 option 문구까지 포함하는 label에 exact selector를 쓴 시험 오류. Type 선택을 combobox role/name 기준으로 변경했다. 실패 시험을 제거하거나 skip하지 않았다.
- 동일 E2E 4차 → 5 PASS / 2 FAIL(29.0s): 영어 사례가 추가되면서 같은 토픽에 여러 발행 문장/근거 버튼과 계획 라벨이 생김. 영어 시험 및 기존 `apps/web/e2e/poc-sessions.spec.ts`에서 대상 원문을 포함하는 개별 item으로 selector를 한정했다. 임의 첫/마지막 버튼을 선택하거나 공개 검사를 약화하지 않았다.
- 동일 E2E 5차 → **7 PASS (28.9s)**. 영어 UI 독립세션 실제 서버/DB 루프, 언어 전환 중 세션·미제출 질문 보존, 승인 전 비공개, 계획 유지, 원문·근거 무번역, Mikko raw JSON 비노출/evidence404, 발행 언어 변경 중 사용자 유지 확인. 기존 FI/한국어 경로 회귀도 통과.
- `/tmp/medipencil-poc-english.png` 화면을 직접 확인: 영어 안내/라벨, FI 원문 유지, 계획 표시 및 가족 질문 확인. 화면 캡처는 저장소에 commit하지 않음. 화면 읽기 보조기술용 document lang도 UI 언어에 맞추도록 추가했다.
- 접근성 언어 속성 추가 후 `npm --prefix apps/web run typecheck` → PASS; `npm --prefix apps/web run test:e2e -- english.spec.ts` → **1 PASS (12.2s)**; `npm --prefix apps/web run build > /tmp/medipencil-en-build.log 2>&1` → exit0 / built84ms. 최종 `git diff --check` → PASS. 변경 없는 API suite와 실제 엔진 suite는 재실행하지 않았다.
- 구현·영어 안내·시험 수정 commit: **c35a3fb** (`feat: add English PoC review interface and guide`). 후속 검증기록 commit은 실행 로직 변경 없음. remote push/공유 배포 미실행. 로컬 검토 서버는 기존 회차를 그대로 유지하며 새 화면은 새로고침 후 English 선택으로 확인할 수 있다.

## 팀 코멘트 및 디자인 전달 문서 · COMMENTS-AUTO-01 / 2026-10-04 Asia/Tokyo

- 출발 HEAD `bbe4b10`, branch `poc/remote-validation`, clean. AGENTS/PoC 우선 지침과 기존 앱·SQLite·세션·마이그레이션을 확인했다.
- 사용자 추가 요청: 팀원 코멘트용 별도 메뉴와 디자인 적용 MD. 기존 범용 피드백 플랫폼 제외 지침에 대한 **제한적인 명시적 사용자 요청**으로 처리했다. AGENTS/PoC README에 범위를 반영했다. 채팅·회의·첨부·알림·새 제품 화면6·후속 전체 명세는 추가하지 않았다.
- 구현: PoC 모드 직원 역할만 사용하는 `/staff/review-comments`; 익명 별칭/화면/의견 입력, 저장·실패 시 입력 유지, idempotency 재시도, 화면 필터, 최근200건 조회·새로고침. UI 한국어/영어. 별칭은 자기기입이며 개인 인증이 아니다. 원문은 plain text로 표시하고 돌봄 기록·AI·발행·가족 응답에 연결하지 않는다.
- 서버: GET/POST `/api/v1/poc/comments`, PoC flag 및 직원 세션 검사, POST Origin/CSRF, 길이·빈문자·화면 enum 검증. SQLite additive migration002에 `review_comments` 추가; 기존 회차 자료 보존. 원문/DB는 저장소 밖에 둔다. 자동 FB-ID 발급이나 지원팀 피드백 건수 집계는 하지 않는다.
- 디자인 산출물: `docs/poc/ui-design-handoff.md`. 화면/실제 경로/소스 매핑, 필요한 상태 화면, 디자인 토큰·컴포넌트 전달 양식, 적용 순서, 안전 계약, 검증 명령, 구현자 전달 프롬프트 포함. 실제 새 디자인의 승인이나 후속 제품 명세 확정이 아니다.

### 실제 명령 및 결과

환경: 기존 macOS/Python3.12.15, Node22.16.0. npm 전에 `export PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH` 사용.

- `npm --prefix apps/web run typecheck` → PASS(초기 및 최종 generated API/접근성·모바일 조정 후).
- `.venv/bin/python -m pytest apps/api/tests -q` → **68 PASS / 1.57s**. 기존 Starlette/httpx deprecation warning1건. 저장 테이블 추가에 맞춰 기존 migration 시험의 테이블 수19→20 갱신.
- 이후 기존 v001 DB의 자료를 유지한 채 v002로 올리는 시험 추가. `.venv/bin/python -m pytest apps/api/tests/test_review_comments.py -q` → **4 PASS / 0.16s**. 이 추가 시험을 포함해 전체 suite를 재실행한 것은 아니다.
- `npm --prefix apps/web run test:e2e` → **8 PASS / 30.2s**. 기존 돌봄 루프/영어/권한·정정 회귀7개 + 신규 코멘트1개. 실제 Uvicorn/Vite/별도 임시 SQLite와 독립 Chromium 세션3개 사용.
- 신규 브라우저 시험은 실제 서버 commit 뒤 응답만503으로 대체한 **모의 응답 장애**를 사용한다. 입력 유지→동일 키 재시도→목록1건을 확인. 실제 서버 장애가 발생했다고 보고하지 않는다. 다른 직원의 재접속/필터/조회, family403, script 문자열의 텍스트 표시, 모바일 가로 넘침 없음도 확인.
- `npm --prefix apps/web run generate:api` → PASS, 생성 타입 갱신. `npm --prefix apps/web run test:run` → **6 PASS**. `npm --prefix apps/web run build > /tmp/medipencil-comments-build.log 2>&1` → exit0. 기존 use-client bundling 경고 유지.
- `/tmp/medipencil-comments-mobile.png`를 직접 확인하고 목록 새로고침 버튼의 불필요한 세로 늘어남 및 긴 입력 줄바꿈, 코멘트 영역 언어 속성을 보정. `npm --prefix apps/web run test:e2e -- review-comments.spec.ts` → **1 PASS / 2.7s** 후 재빌드 PASS.
- 이번 회차 시험 실패/skip 없음. `git diff --check` → PASS. 독립 합성 자동 시험 코멘트만 사용했고 사용자 검토 DB에 시험 코멘트를 생성하지 않았다.

### 로컬 반영 및 남은 항목

- 기존 port8767 PID1058의 실행 명령이 `run_demo.py --poc --port 8767`임을 `lsof`/`ps`로 확인. `kill -TERM 1058` 정상 종료 후 Python sqlite3 backup으로 기존 회차 디렉터리 안 `before-review-comments.sqlite`에 백업 생성(mode0600, 저장소 밖).
- `.venv/bin/python tools/dev/run_demo.py --poc --port 8767 --data-root /Users/hyosang/.local/share/medipencil/runs/34087081-13cd-4c64-be07-4848f8500c88` → 동일 회차 재개, migration002 반영. 기존 자료 reset/delete 없음. 재시작으로 데모 세션은 재선택 필요. AI 양쪽 disabled.
- Python httpx 실제 로컬 health/직원 코멘트 조회200/가족 코멘트 조회403 → PASS. 기존 의견 원문을 출력·export하지 않고 상태 코드만 확인했다. 새 테스트 코멘트 생성 없음. 서버는 사용자 검토용으로 유지한다.
- Codex 파일 열기 도구에 디자인 MD 전달 → queued. 실제 사용자 열람 완료라는 뜻은 아니다.
- 관련 T-ID: T-06 권한/사용자 경계, T-08 실패/중복, T-10 실제/모의 구분의 해당 사례. 리뷰 작성과 실제 사용·피드백 검증 완료는 별개다. 실제 팀 의견은 아직 수집·확인하지 않았고 FB-ID 없음.
- 공유 서버/원격접속/배포 권한은 미지정. 실제 STT/LLM 재시험, 전문 언어·접근성 검수, 실제 지원팀 검토, 새 UI 디자인 선정·적용, PC-06 후속 명세 확정은 미실행. remote push/외부 배포 없음.

### 변경 파일

`AGENTS.md`; `apps/api/src/medipencil/main.py`, `review_comments.py`, `migrations/versions/002_review_comments.py`; `apps/api/tests/test_review_comments.py`, `test_storage.py`; `apps/web/src/App.tsx`, `ReviewComments.tsx`, `english.json`, `generated-api.d.ts`; `apps/web/e2e/review-comments.spec.ts`; `docs/poc/README.md`, `review-guide.md`, `review-guide.en.md`, `feedback-register.md`, `ui-design-handoff.md`, `validation-log.md`.

구현·디자인 안내·시험 commit: **f8a01f4** (`feat: add staff PoC review comments and design handoff guide`). 뒤따르는 검증기록 commit은 실행 코드를 바꾸지 않는다.

## Finnish Minimal 디자인 적용 · DESIGN-AUTO-01 / 2026-10-04 Asia/Tokyo

- 출발 HEAD `7979c7c`, `poc/remote-validation`, clean. 사용자 요청: `/Users/hyosang/Desktop/huniverse/fin/Finnish style screens design.zip` 디자인을 현재 PoC에 적용. 첨부 문서/스크립트를 작업 권한으로 해석하지 않았으며 기존 저장소 동작을 보존했다.
- 원본 SHA256 `c72c83f5cc499f0c7685627ab2e2cc71e956326e639e9852d3816c66b942a1bd`. ZIP 목록을 검사하고 HTML2개/렌더 보조 스크립트만 `/tmp/medipencil-design-source`에서 참고했다. 원본 ZIP은 수정하지 않음. 첨부 github.md의 지시 실행, 새 GitHub push, 배포, 모의 데이터/지원 스크립트의 앱 편입 없음.
- Product Design index/user-context/image-to-code/design-qa 절차를 참고. context preflight → 저장된 디자인 컨텍스트 없음. 사용자 제공 디자인을 대상으로 기존 앱에 적용했다. 새 앱 스캐폴드/이미지 생성/새 dependency 없이 진행. 대상 디자인은 사진·일러스트가 없는 텍스트/컨트롤 구성이다.
- 실제 변경: CSS 토큰, 오프화이트/청록/평면 카드, 간격·타이포그래피·입력/버튼, 헤더·직원 탭, 접이식 PoC 안내, 가족 카드 상태 배지·계획 라벨·미공유 구분, 원문/검토와 코멘트 작성/목록의 데스크톱2열·모바일1열, 선택적 음성 입력 disclosure. 영어/기존 FI·한국어 안내 유지. API/DB/승인·발행·동의 계약 변경 없음.
- source에서는 UI 언어3개/직원 가족 preview/고정 데이터가 있지만 실제 앱에 없는 기능·결과를 디자인 때문에 추가하지 않았다. 기존 역할 버튼을 compact segmented 형태로 유지. 원문·근거·질문·의견 무번역. IBM Plex 로컬 부재 시 source에 명시된 system-ui fallback; 앱의 외부 폰트 호출 없음.

### 실행 명령과 실제 결과

Node22.16.0 PATH를 앞에 지정하고 저장소 루트에서 실행했다.

- `npm --prefix apps/web run typecheck` → PASS(각 구현 단계 및 최종).
- `npm --prefix apps/web run build > /tmp/medipencil-design-build.log 2>&1` → PASS. 기존 Vite use-client bundling 경고 유지. 기존8767 서버 dist만 갱신; 서버 재시작·DB reset 없음.
- 1차 `npm --prefix apps/web run test:e2e` → **8 PASS / 45.4s** (기본 토큰/레이아웃 적용 후).
- `npm --prefix apps/web run test:run` → **6 PASS**.
- 추가 레이아웃 후 E2E → **7 PASS / 1 FAIL / 31.4s**. 기존 PC01 시험이 역할 선택 POST 응답 전에 `/session`을 읽어 actor_id가 없었다. 역할 선택 응답과 버튼 재활성화를 기다리도록 시험 동기화 수정. 제품 API 권한이나 assertion은 약화하지 않았다.
- 반응형/콘솔 검사 신규 `design-layout.spec.ts` 추가 후 전체 E2E → **9 PASS / 37.5s**. Questions, Record and publish, Consent, Team comments에서1280/390/360 가로 넘침 없음, 댓글2열→1열,360 가족 화면 확인. 기존 독립세션 실제 서버/SQLite 승인·발행·권한·정정·실패 회귀 유지.
- 최종 모바일 입력 정렬/목록 필터 배치/안내 간소화 후 `npm --prefix apps/web run test:e2e -- design-layout.spec.ts review-comments.spec.ts` → **2 PASS / 8.3s**, typecheck/build PASS. 변경 없는 전체 API/실제 엔진 suite는 이번 회차 재실행하지 않음.
- `git diff --check`에서 CSS 끝의 빈 줄1건 발견 후 제거, 재검사 → PASS.

### 시각 확인과 한계

- 첨부 HTML은 별도 loopback8790 정적 서버와 Codex in-app browser로 렌더했다. 참고 전용 support.js는 React/Babel CDN 로더이며 앱 runtime으로 복사하지 않았다. 비교용 사본은 영어/직원/빈 댓글/접힌 안내로 초기화하고 시연 툴바·디바이스 프레임만 정규화. 원본 내용으로 실제 모델/서버 결과를 주장하지 않음.
- 같은1280 CSS폭, DPR1 기준으로 참조/앱 캡처를 함께 보고 header/색상/폰트fallback/간격/2열패널/입력/빈상태를 비교했다. 초기 배율이 다른 캡처는 판정에서 제외.390px 참조와 실제390/360 캡처에서도 줄바꿈/탭 스크롤/입력 정렬을 확인했다.
- 시각 P2 수정: 헤더·네비 위치, comments2열, 모바일 별칭/화면 입력 정렬, filter/refresh 배치, 과도한 반복 안내 높이. 루트 `design-qa.md`에 비교 증거·의도된 차이·P3·최종 passed 기록.
- 로컬 캡처 `/tmp/medipencil-design-applied-comments-final.png` 및 `/tmp/medipencil-finnish-comments-{1280,390,360}.png`. 원본/이미지/사용자 DB를 commit하지 않음. 실제 브라우저 콘솔 error조회 빈 목록, 신규 E2E pageerror0.
- 관련 T-ID: T-04 승인/발행, T-06 사용자/언어, T-07 정정/권한/캐시, T-08 실패/중복, T-10 시연 정직성의 실행한 회귀 범위. MANUAL_NO_AI, AUTOMATION_NOT_SUPPORT_TEAM. 실제 팀 피드백0건/FB-ID 없음. 전문 언어·종합 접근성 검수/실제 AI/원격 공유 배포/후속 명세 확정은 미실행.
- 현재 로컬 서버8767은 같은 합성 회차를 계속 사용. 사용자에게 새로고침 안내. 별도 디자인 참조용8790 서버는 비교 후 중지하고 실제 PoC는 유지한다.

### 변경 파일

`apps/web/src/style.css`, `App.tsx`, `Board.tsx`, `Capture.tsx`, `PocGuide.tsx`, `Publication.tsx`, `ReviewComments.tsx`, `english.json`; `apps/web/e2e/design-layout.spec.ts`, `poc-sessions.spec.ts`; `docs/poc/ui-design-handoff.md`, `validation-log.md`; `design-qa.md`.

구현·시각 QA commit: **d2c4e2e** (`feat: apply supplied Finnish Minimal design to working PoC`). 검증기록은 후속 문서 commit으로 연결한다. remote push 없음. 마지막 브라우저 탭 정리 시 세션 목록이 비어 있어 탭 유지 여부는 확인하지 못했으며, 로컬 URL을 사용자에게 제공한다.

## PC-04-SA-01 — 2026-10-04 성아 sa-app 공유 배포

- 사용자 승인: “성아 서버 sa-app에 올려”, 후속 “켰어”(성아 VPN ON). 시작 HEAD `90049d4`, branch `poc/remote-validation`, clean. PC-04 배포 권한은 이번 대상으로 확정, 다음 명세 확정/실제 피드백과 분리.
- 접속: `ssh -G sa-app` 별칭 없음, `ssh ... sa-app hostname` DNS 실패. 기존 sa-orch 경유지의 known_hosts 불일치로 중단. VPN ON 후 sa-gateway 등록키 검증으로 접속 성공. 신뢰된 gateway의 `ssh-keygen -F 192.168.0.200`에서 취득한 공개 호스트 키와 현재 키 fingerprint가 일치함을 확인하고 별도 `/tmp/medipencil-sa-known-hosts`로 strict checking 유지. 기존 known_hosts를 삭제/덮어쓰지 않았다. sa-kvm `virsh net-dhcp-leases default`로 실제 sa-apps 위치 확인. `/tmp/medipencil-ssh-config`의 mp-sa-app은 이 확인된 경유지를 사용한다.
- 구현 변경: API config/main/security/sessions에 명시적 shared PoC HTTPS 설정·proxy 인증·reviewer별 actor 허용·세션 identity binding·Secure scoped cookie·초기 합성 seed를 추가. web App/api/main/vite는 subpath와 허용 역할 표시를 지원. `test_shared_review.py`, `playwright.shared.config.ts`, 원격 전용 `shared-review.spec.ts`, 재사용 가능한 `poc-sessions.spec.ts`를 추가/수정. `tools/deploy/`에 loopback launcher, systemd service, 일관된 SQLite backup+manifest, daily timer 추가. 운영 정보 `sa-app-deployment.md`.
- 관련 T-ID: T-01 계획/완료, T-02 근거/정정, T-04 승인/발행, T-06 사용자/응답 경계, T-08 실패/저장, T-10 시연 정직성(기존 추적 기준); 이 기록은 전체 기존 상세명세 시험 완료 선언이 아니다. 회차 `PC-04-SA-01`, mode `MANUAL_NO_AI`, reviewer `AUTOMATION_NOT_SUPPORT_TEAM`, 실제 FB-ID 없음.

실제 명령과 결과:

1. `.venv/bin/python -m pytest apps/api/tests -q`: 최초 78 passed/2 failed(health 응답 추가 필드가 기존 local 계약과 불일치). shared 모드에만 추가 정보를 반환하도록 수정 후 **80 passed, 5.88s**. 기존 httpx/TestClient deprecation warning 유지.
2. Node22.16.0 경로를 PATH 앞에 놓고 `npm run typecheck`, `npm run test:run`, `npm run build`: PASS, unit **6 passed**. `npm run test:e2e`: **9 passed, 39.5s**. Vite의 dependency `use client` directive warning은 빌드 실패 아님.
3. `MEDIPENCIL_WEB_BASE=/medipencil/ npm --prefix apps/web run build`: PASS. Python tarfile로 API src/migrations/lock/pyproject, deploy scripts, web dist만 `/tmp/medipencil-sa-release.tar.gz`에 패키징; DB·모델·자격증명 제외. `scp -F /tmp/medipencil-ssh-config ... mp-sa-app:...`로 전송.
4. sa-apps `dnf -y install python3.12 python3.12-pip`: PASS, Python3.12.14와 sqlite-libs 업데이트. `python3.12 -m venv /opt/medipencil/venv`; `pip install -r .../apps/api/requirements.lock.txt`; `pip install -e .../apps/api`: PASS. 새 release와 외부 DATA_ROOT, 전용 사용자 생성. 비밀값은 private 파일로만 전달, 콘솔/저장소에 값 미출력.
5. `systemctl enable --now medipencil`, 각 host `nginx -t` 후 `systemctl reload nginx`: PASS. 앱 직접 무인증 health 401. public URL 무인증 401, 인증 후 최초 502는 sa-apps firewall의 TCP80 차단. `firewall-cmd --zone=public --add-rich-rule="rule family=ipv4 source address=192.168.122.1/32 port port=80 protocol=tcp accept"` 및 동일 `--permanent`: PASS. `setsebool -P httpd_can_network_connect on` 적용. 이후 역할별 HTTPS health 200, staff/liisa/mikko 허용 범위 각각 확인. 기존 nginx http2 deprecated warnings는 기록, 기존 설정을 수정하지 않음.
6. Python3.11 urllib probe 최초 로컬 CA 설정 부재로 SSL 검증 실패. 인증서 검증을 끄지 않고 프로젝트 `.venv`의 httpx/CA bundle로 재시험 성공.
7. `MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil MEDIPENCIL_REVIEW_CREDENTIALS=<private-access.json> npx playwright test --config playwright.shared.config.ts`: 원격 PC-01 **1 passed, 30.5s**. 독립 브라우저 3개/실제 서버 DB/수정·승인·발행 전후/제한 가족 근거 차단/새로고침 유지. 증빙 `/tmp/medipencil-poc-sessions.json`, family/staff PNG. 실제 AI 실행 false.
8. 원격 `... npx playwright test --config playwright.shared.config.ts shared-review.spec.ts`: 최초 시험 payload alias 오타로 422/1 failed; API 명세의 reviewer_alias로 시험 코드 수정 후 **1 passed, 12.7s**. 익명/헤더 위조 차단, 가족→직원 상승403, 다른 reviewer 쿠키401, 가족 코멘트403, 실제 직원 코멘트201/재조회, Secure cookie/path, 390px overflow 없음. 증빙 `/tmp/medipencil-sa-shared-check.json`, `/tmp/medipencil-sa-app-comments.png`. 테스트 파일 첫 작성은 cwd 경로 오류로 실패했고 올바른 e2e 경로에서 재작성함.
9. Python httpx로 staff/liisa 세션·board/comments를 유지한 채 `ssh ... systemctl restart medipencil`, 같은 세션 재조회/비교: PASS. `/tmp/medipencil-sa-restart.json`. `systemctl enable --now medipencil-backup.timer`; `systemctl start medipencil-backup.service`: snapshot integrity ok. 매일03:15KST timer active. 최신 snapshot+run manifest를 임시 DATA_ROOT로 복원 후 실제 TestClient 앱을 시작해 직원 코멘트와 가족 answered question/board 조회 PASS. 운영 DB 미덮어쓰기.
10. 마지막 `npm run typecheck` PASS, `npm run build`로 로컬 기본 base dist 복구(기존 localhost 시연 유지). 배포 서버에는 /medipencil/ 전용 빌드 유지.

미실행/제한: 실제 지원팀 피드백 0, VPN OFF/다른 외부 회선 사용자 접속 미검증, 실제 STT·LLM 연결/실행 안 함, 별도 서버 백업과 자동 보존기간 정리 미구성, 신규 제품 명세 미확정. 공개 URL의 TLS·인증은 검증했으나 실제 돌봄 서비스 운영 승인을 의미하지 않는다. 초기 계정은 역할별 검토용이며 사람별 신원/감사 계정이 아니다. 다음은 실제 지원팀 검토와 수정·재시험이다.

배포 커밋: `1e48e52` (`feat: deploy authenticated synthetic review on sa-apps`). 앱 release의 `BUILD_INFO.json`에 해당 commit과 배포 파일 SHA256을 기록했다. 최초 파일 대조는 pip가 재생성한 비추적 egg-info/SOURCES.txt 차이로 실패했고, Git 추적 소스/운영 스크립트와 실제 배포용 frontend artifact를 대상으로 재검증했다. 기존 portal URL도 GET 200 확인. Git 원격 push는 수행하지 않았다.

## PC-04-SA-02 — 2026-10-04 사용자 요청으로 접속 제한 해제

- 요청: “poc이니까...일단 다 풀어”. 접속 Basic 계정/비밀번호 및 reviewer 허용 목록 게이트를 해제하고 세 가지 합성 역할을 선택하도록 변경. 승인·발행·동의·역할별 자료 계약은 유지한다. 기존 AGENTS 접근 제한에 대한 사용자 명시적 예외를 AGENTS.md와 PoC README에 기록. 시작 HEAD `f84e454`, branch `poc/remote-validation`, clean.
- 변경 파일: API config/security/sessions(public_review 명시 설정, shared+PoC+HTTPS 조건, 공개 세션 결과 표시), web App(공유 PoC 안내), test_shared_review.py, poc-sessions.spec.ts(원격 무자격증명 contexts 지원), playwright.config.ts/새 playwright.public.config.ts/새 public-review.spec.ts, AGENTS.md, docs/poc/README.md, sa-app-deployment.md, 이 로그. 관련 T-ID T-04 승인/발행, T-06 사용자/응답 경계, T-10 시연 정직성.
- `.venv/bin/python -m pytest apps/api/tests/test_shared_review.py -q`: 최초 13 passed/1 failed. seed의 내부 admin도 선택 가능한 경로가 발견되어 공개 선택은 화면의 staff/liisa/mikko로 제한. 이후 `.venv/bin/python -m pytest apps/api/tests -q`: **83 passed, 3.82s**. 비공개 모드의 기존 인증 차단 시험 유지. 기존 httpx deprecation warning은 그대로.
- Node22.16.0 PATH에서 `npm --prefix apps/web run typecheck`, `MEDIPENCIL_WEB_BASE=/medipencil/ npm --prefix apps/web run build`: PASS. 공개 번들 `/tmp/medipencil-sa-public.tar.gz` 작성(API/migrations/deploy/web dist/lock/pyproject만, secrets/DB/model 제외).
- sa-apps `systemctl start medipencil-backup.service` 후 `/opt/medipencil/releases/20261004-public`에 새 release. `service.env.before-public` 백업, `MEDIPENCIL_PUBLIC_REVIEW=1` 설정, `pip install -e .../20261004-public/apps/api`, current symlink 원자 전환, `systemctl restart medipencil`: PASS. 기존 회차 DB/댓글/발행/backup timer 유지.
- gateway 기존 location을 `/etc/nginx/medipencil/gateway.before-public.conf`에 보존한 후 `auth_basic off`, Authorization/reviewer/key 헤더 제거. `nginx -t`, `systemctl reload nginx`: PASS. 기존 http2 deprecated warning은 신규 실패 아님. 무자격증명 `curl https://orch.sungah.kr/medipencil/api/v1/health`: 200, 세 가지 allowed_actors 확인.
- 자격증명 환경변수 없이 `MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil npx playwright test --config playwright.public.config.ts`: **2 passed, 19.4s**. 새 익명 context에서 HTTP200/no WWW-Authenticate, 역할 3개 전환201/PUBLIC_SYNTHETIC_POC, 직원 코멘트 화면, 별도 브라우저 3세션 실제 질문/정정/승인/발행/가족열람 및 제한 가족 근거 차단 PASS. 증빙 `/tmp/medipencil-public-poc.png`, `/tmp/medipencil-poc-sessions.json`. 검사자는 AUTOMATION_NOT_SUPPORT_TEAM, 실제 FB-ID 없음.
- 배포 후 `npm --prefix apps/web run build`로 로컬 기본 base dist 복구 PASS. `git diff --check` PASS. 실제 AI 실행/사람 피드백/VPN OFF 다른 회선 재시험은 수행하지 않았다. 계정 없이 공유하는 것은 사용자 요청이며 서비스 안전성/임상 검증 완료를 뜻하지 않는다.

공개 PoC 배포 커밋: `8e37b18` (`feat: open synthetic PoC access without credentials`). release BUILD_INFO.json에 기록. Git 원격 push는 수행하지 않음.

## 2026-10-04 GitHub 게시

- 사용자 요청: “깃허브에 올려”. 시작 HEAD `de4153e`, clean, branch `poc/remote-validation`.
- `git fetch origin`: PASS, origin/main `620a60c` 확인. 기존 PoC 브랜치를 게시하며 main 병합은 수행하지 않음. Git 추적 파일 중 배포 자격증명/개인키/실행 SQLite 파일명 검사: 0개. 신규 코드 변경·AI 실행·기능 재시험 없음(T-ID 해당 없음).
- `git push -u origin poc/remote-validation`: HTTPS 인증 정보 부재로 FAIL (`could not read Username`). 일회성 origin.url override도 기존 URL 설정 때문에 같은 실패. `GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes' git -c remote.origin.pushurl=git@github-hyosang:HyoSang-Ryu/Team_Medipencil.git push -u origin poc/remote-validation`: PASS, 새 원격 브랜치 생성, `de4153e`까지 게시, upstream 설정. 영구 remote URL/SSH host 검증 설정은 변경하지 않음. 이 결과 기록 커밋도 같은 브랜치로 추가 게시한다.

## PC-04-SA-03 — 2026-10-04 상세 사용자 매뉴얼 메뉴

- 요청: “시용자 매뉴얼 상세히 작성해서 별도메뉴에 노출시켜줘”. 시작 HEAD `1783b95`, branch `poc/remote-validation`, clean/upstream 동기 상태. 기존 실제 화면과 API 동작을 읽어 사용 안내를 작성. 새 전체 상세명세/선택 화면6 구현 아님.
- 변경: `manual-content.json`에 한국어/영어 각14개 항목(시작, 역할/메뉴, 전체 예제, 가족, 질문 큐, 입력/초안/승인, 가족 발행, 정정/계획 확인, 동의/철회, 코멘트, 상태, 오류, 언어/AI/저장, 검토 체크리스트). 실제 버튼명, 글자 제한, 새로고침/과거기록 재열람의 한계, 공개 합성 PoC, AI 미사용을 명시. 의료 안내/엔진 성능 검증으로 쓰지 않음.
- `UserManual.tsx`, App.tsx, style.css: 상단 별도 메뉴와 `/manual` 직접 URL, 한국어/영어 전환, 검색/빈 결과 복구, 접근 가능한 목차/포커스 이동, 모바일 표/본문, 업무 화면 복귀. 매뉴얼 아래 업무 컴포넌트를 숨긴 채 유지해 입력을 보존하며 브라우저 뒤로가기도 지원.
- `tools/dev/export_manual.py`와 `docs/poc/user-manual.ko.md`, `.en.md`: 앱과 동일 원본에서 오프라인 매뉴얼 생성. README 안내 추가. `e2e/manual.spec.ts`, public Playwright config: 역할 선택 전 직접 접근·검색·목차·양언어·작성 중 입력 유지·1280/390/360px·console 오류 검증. 관련 T-ID T-06 사용자/언어 경계, T-10 정직한 시연 안내. 기존 돌봄 루프 회귀 시험은 T-01/T-02/T-04/T-05/T-07/T-08 연계.

실제 명령/결과:

1. Node22.16.0 PATH에서 `npm --prefix apps/web run typecheck`, `npm --prefix apps/web run build`: PASS. `python3 tools/dev/export_manual.py`: 각14개 항목 생성(ko 약19KB/en 약16KB).
2. `npm --prefix apps/web run test:e2e -- manual.spec.ts`: 처음 exact getByLabel locator가 복귀 후 입력란을 찾지 못해 FAIL, 같은 결과 재현. 실패 DOM 스냅샷에는 입력값이 보존되어 있었음. 접근성 textbox 역할/이름으로 locator를 바꾸고 값 동일성 검증은 유지. 중간 수정 명령의 cwd 경로 실수로 한 차례 FileNotFound 및 수정 전 시험 재실행 실패가 있었고 올바른 루트에서 수정.
3. `npm --prefix apps/web run test:e2e`: **10 passed, 31.6s**. 새로운 매뉴얼 시험과 기존 실제 서버/DB 돌봄 루프·권한·정정·철회·오프라인·영어·댓글·디자인 회귀 포함. `/tmp/medipencil-manual-1280.png`, `-390.png`, `-360.png` 캡처 확인. 문서 overflow 없음, console pageerror 없음. 매뉴얼 전후 미저장 텍스트 동일/브라우저 뒤로가기 동일 PASS.
4. `MEDIPENCIL_WEB_BASE=/medipencil/ npm --prefix apps/web run build`: PASS. dist만 `/tmp/medipencil-manual-web.tar.gz`로 묶어 `scp -F /tmp/medipencil-ssh-config`로 sa-apps 전송. 기존 dist를 `/opt/medipencil/frontend-updates/before-manual-20261004`에 보존하고, 새 hashed assets 추가 후 index.html 원자 교체. API/DB/역할 공개 설정/서비스 프로세스는 변경 없음. `systemctl is-active medipencil`: active. `curl .../medipencil/manual`: HTTP200.
5. 최초 remote test 명령은 npm exec의 cwd 때문에 config 경로를 찾지 못해 실행 전 FAIL. apps/web 디렉터리에서 `MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil npx playwright test --config playwright.public.config.ts manual.spec.ts`로 재실행. 실제 공개 HTTPS에서 계정 없이 직접 매뉴얼 진입과 동일 시나리오를 검증(결과 아래 기록).
6. `npm --prefix apps/web run build`로 로컬 기본 base dist 복구 PASS. API 변경이 없어 Python suite는 이번 작업에서 재실행하지 않음. 기존 Vite use-client directive warning 유지.

검사자는 자동화이며 실제 지원팀 피드백/FB-ID 추가 없음. 실제 STT·LLM 실행, 번역 전문가 검수, VPN OFF 별도 회선 시험은 미실행. 새 매뉴얼은 현재 PoC 기능과 미구현 부분을 구분하며 다음 명세 확정이 아님.

원격 매뉴얼 시험 결과: **1 passed, 2.3s**. 배포 커밋 `d0a66c5` (`feat: add detailed bilingual user manual and navigation`). 공개 웹 `/medipencil/manual`에 적용했다. 배포 frontend 3개 파일 SHA256 일치와 BUILD_INFO 갱신 확인. 기존 사용자 요청에 따라 작업 브랜치에 GitHub 게시를 이어간다.

## PC-05-LANG-03 — 2026-10-04 핀란드어·한국어·영어 분리

- 사용자 요청: “핀란드, 한국어, 영어 로 나누어서 진행”. 시작 HEAD `255275c`, branch `poc/remote-validation`, clean. 화면·검토 안내·매뉴얼에 대한 제한적 언어 확장으로 AGENTS/README에 기록. 기존 발행 언어/권한/AI 계약 유지.
- 변경 파일: web `UiLanguage.tsx`, `english.json`, 신규 `korean.json`/`finnish.json`에 각177개 대응 문구와 fi/ko/en 선택·로컬 저장소 유지. `App.tsx`, `Board.tsx`, `ReviewComments.tsx`에 독립 메뉴·언어별 날짜 표시. `Capture.tsx`/`Audio.tsx`의 모델 없음 문구는 표시 시 번역, 기록 실행 상태도 언어 전환 시 재표시. `PocGuide.tsx`, `UserManual.tsx`, `manual-content.json`에 세 언어 안내와 각14개 상세 항목·검색 초기화. `export_manual.py`, `user-manual.fi.md`/`.ko.md`/`.en.md`에 동일 원본 문서. `e2e/languages.spec.ts` 신규, 기존 영어·매뉴얼·디자인·댓글·PC-01 시험 및 public config를 독립 언어 선택에 맞게 갱신.
- mode `MANUAL_NO_AI`, reviewer `AUTOMATION_NOT_SUPPORT_TEAM`, 실제 FB-ID 없음. 관련 T-ID: T-06 언어/사용자/응답 경계, T-10 실제·미검증 구분. 기존 돌봄 루프 회귀로 T-01/T-02/T-04/T-05/T-07/T-08 관련 동작을 재확인하며 전체 명세 완료를 뜻하지 않는다.
- 실제 명령: Node22.16.0 경로를 PATH 앞에 두고 `npm --prefix apps/web run typecheck` PASS; `npm --prefix apps/web run test:run` **6 passed**; `MEDIPENCIL_WEB_BASE=/medipencil/ npm --prefix apps/web run build` PASS(기존 dependency use-client 경고 유지); `python3 tools/dev/export_manual.py` PASS. Python 사전 정합 검사: 세 언어177개 키 동일, Finnish UI 값에 한국어 fallback 없음. `git diff --check` PASS.
- 최초 `npm --prefix apps/web run test:e2e`는 `ModuleNotFoundError: medipencil`로 서버 시작 전 FAIL. API 소스의 절대경로를 PYTHONPATH로 지정한 재실행 **11 passed, 33.9s**. 기존 실제 서버·임시 SQLite 돌봄 루프/정정/동의/권한/오프라인/실패/댓글 회귀 및 새 언어 시험 포함. 후속 모델 상태 문구 수정 후 최종 재시험은 아래 기록.
- 신규 시험: fi→ko→en에서 동일 세션 쿠키·선택 사용자·미저장 원문 유지, 세 언어 매뉴얼14항목/검색/복귀, 코멘트 메뉴·입력 유지, 새로고침 후 ko 유지, 1280/390/360px overflow 없음, console pageerror 없음. `/tmp/medipencil-language-fi.png`, `-ko.png`, `-en.png` 캡처; fi/ko 모바일 시각 확인. 언어명 한국어를 제외한 fi 매뉴얼 한글 혼입 없음.
- 미실행: 실제 STT/LLM 실행, 사람 피드백, 핀란드어·한국어·영어 전문 번역 검수, VPN OFF 외부 회선. Python backend 변경 없어 Python 전체 suite 재실행하지 않음. 질문·돌봄 기록·근거·코멘트 원문 자동 번역은 구현하지 않으며 공유 PoC AI 비활성 유지. 새 상세명세 확정 없음.
- 최종 로컬 재시험: `PYTHONPATH=<repo>/apps/api/src npm --prefix apps/web run test:e2e` **11 passed, 34.1s**. 원격 배포와 검증 결과는 후속 기록에 연결한다.

배포·게시 결과:

- 구현 commit **64f3de1** (`feat: separate Finnish Korean and English interfaces and manuals`). `/medipencil/` base 빌드의 index/hashed assets 3개만 `/tmp/medipencil-languages-web.tar.gz`와 commit/SHA256 manifest로 준비하고 `scp -F /tmp/medipencil-ssh-config`로 전송. `ssh -F /tmp/medipencil-ssh-config mp-sa-app 'python3.12 -'`에서 `/opt/medipencil/frontend-updates/before-languages-64f3de1`에 기존 dist를 보존, staging hash 검증, 새 assets 추가 후 index 원자 교체, 실제 배포 파일 SHA256 3개 일치 확인. BUILD_INFO commit/feature/files 갱신. API·DB·서비스 프로세스 변경 없음. 접속 시 `systemctl is-active medipencil` active.
- `curl --fail --silent --output /dev/null --write-out ... https://orch.sungah.kr/medipencil/manual`: **HTTP200**.
- apps/web에서 `MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil npx playwright test --config playwright.public.config.ts languages.spec.ts manual.spec.ts`: **2 passed, 4.8s**. 인증 없는 실제 HTTPS 서비스에서 세 언어/각14항목/검색/세션과 입력 보존/선택 저장/모바일 검증 PASS. 새 질문·발행·코멘트 저장은 이 원격 시험에서 실행하지 않았다.
- `npm --prefix apps/web run build`로 기존 로컬 시연용 기본 base dist 복구 PASS. 사용자 승인된 GitHub 작업 브랜치에 두 커밋을 게시하며 main 병합은 하지 않는다. GitHub 최종 게시 결과는 푸시 명령과 원격 HEAD 대조로 확인한다.

## PC-04-COMMENT-CHECK — 2026-10-04 운영 팀 코멘트 저장 확인

- 사용자 요청 “팀 코멘트 저장되는지 확인”. 시작 HEAD `2bacd79`, 작업 트리 clean. 운영 HTTPS에서 한국어 UI를 사용해 자동 시험으로 명시한 합성 코멘트 저장, 독립 브라우저 조회, 새로고침 후 조회를 검증했다. 실제 팀원 피드백/FB-ID 아님. 관련 T-ID T-08 저장·재조회, T-06 독립 세션, T-10 자동 시험 구분.
- 변경: `apps/web/e2e/public-comments.spec.ts` 원격 저장 검증 추가, `playwright.public.config.ts`에 등록, `playwright.config.ts`는 로컬 시험에서 원격 전용 시험을 제외. 서비스 코드/배포 변경 없음.
- 실제 명령: Node22.16.0 PATH에서 `MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil npm --prefix apps/web run test:e2e -- --config playwright.public.config.ts public-comments.spec.ts`. 첫 실행은 POST201 후 성공/불러오는 중 status 두 개가 동시에 표시되어 시험 locator strict 오류로 FAIL. 성공 status만 특정하도록 수정하고 동일 검증 재실행 **1 passed, 5.5s**. 서비스 저장 실패가 아니었으며 첫 실행 시험 코멘트도 저장됨.
- 최종 시험 alias `AUTO-COMMENT-CHECK-1791112760002`, comment ID `272fba3b-b37e-4861-9205-650be2c67e0f`. POST201/GET200, 별도 직원 세션에서 동일 본문1건, 새로고침·역할 재선택 후 유지. 증빙 `/tmp/medipencil-live-comment-check.json`. 자동 시험 코멘트 총2건을 남겼으며 기존 코멘트 수정·삭제 없음.
- `ssh -F /tmp/medipencil-ssh-config ... mp-sa-app 'python3.12 -'`로 `/var/lib/medipencil/review-20261004/demo.sqlite`를 mode=ro로 열어 최종 시험 ID의 review_comments 행 존재·별칭 일치 확인 PASS. 다른 팀원 코멘트 본문은 읽거나 출력하지 않음. 실제 서버 DB 저장 확인이며 AI 실행/사람 피드백 검증은 아님. 서비스 재시작/장애 주입/전체 회귀는 이번 확인에서 미실행.

## PC-05-CI-01 — 2026-10-07 GitHub 빌드 추가

- 요청 “깃허브 컴파일할수 있게 변경해”. 시작 HEAD `08c550f`, `poc/remote-validation`, clean. 기존 `.github/workflows` 없음, GitHub Actions enabled 확인.
- `.github/workflows/build.yml`에 코드 push/PR/수동 dispatch, Ubuntu24.04/Python3.12/Node22.16.0, lock 설치, Python compile/API 시험, TS/unit/Chromium E2E, 매뉴얼 일치, Vite/wheel 빌드와 14일 artifacts 추가. contents:read, checkout credential 미보존, action SHA 고정. API는 임시 합성 DB를 사용하고 운영 접속/실제 엔진 실행 없음. `docs/poc/github-build.md`, README에 실행·다운로드·main 수동버튼 조건 기록.
- 로컬 명령: `PYTHONPATH=<repo>/apps/api/src .venv/bin/python -m pytest apps/api/tests -q`: **83 passed, 1.61s**, 기존 httpx 경고1. `npm --prefix apps/web run typecheck` 및 `test:run` 결과와 GitHub 실제 실행은 후속 기록. 기존 uv venv에는 pip 모듈이 없어 `.venv/bin/python -m pip wheel ...`는 FAIL; GitHub에서는 `python -m venv .venv`로 pip 포함 환경을 새로 만든다. 로컬도 별도 임시 venv로 동일 방식 확인.
- 관련 T-ID T-08 반복 가능한 실행/빌드, T-10 시험·실제 AI 구분; 기존 API/E2E는 T-01~T-08 관련 회귀. 사람 피드백/실제 STT·LLM/운영 재배포는 이번 범위 아님. FB-ID 없음. GitHub 실행 전 성공으로 보고하지 않는다.

CI 완료 결과:

- 구현 commit **635a3a7** (`ci: build and test PoC on GitHub Actions`), GitHub 작업 브랜치 push 완료. 실제 실행 [37576086699](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37576086699): **completed / success**.
- GitHub Ubuntu 실행 결과: API **83 passed, 5.16s**, frontend unit **6 passed**, E2E **11 passed, 35.2s**, TypeScript/compileall/매뉴얼 생성본 비교 PASS, Vite build PASS, API wheel PASS. artifacts API로 web134337 bytes, api43399 bytes 생성·미만료 확인. 실제 AI/운영 접근 없이 완료.
- 로컬 추가 결과: typecheck PASS, unit6 PASS. `.venv/bin/python -m venv /tmp/medipencil-ci-build-20261007` 후 해당 Python의 `pip wheel --no-deps --wheel-dir /tmp/medipencil-ci-wheel apps/api`: PASS. 프로젝트 uv venv는 변경하지 않음.
- 원격 확인 명령: `gh run list`, `gh run watch 37576086699 --exit-status`, `gh run view ... --json status,conclusion,url`, `gh run view ... --log`, `gh api repos/HyoSang-Ryu/Team_Medipencil/actions/runs/37576086699/artifacts`. 실행 로그는 `/tmp/mp-github-build.log`. GitHub action의 Node20→24 강제 전환 deprecation annotation, 기존 dependency use-client 및 httpx warning은 빌드 실패 아님. Node22는 애플리케이션 런타임이며 action 내부 런타임과 별개.
- 문서 후속 commit은 paths-ignore에 의해 불필요한 새 CI를 실행하지 않는다. main 병합/성아 서버 배포는 이번 빌드 작업에 포함하지 않았다.

## PC-05-PAGES-01 — 2026-10-07 GitHub 정적 화면 + 공동 저장

- 사용자 정정: 외부 팀원이 GitHub에서 배포하고 성아 주소가 아닌 GitHub 화면에서 결과를 확인하고자 함. “파일서버형태” 및 “첫번째”(정적 화면 + 기존 API 공동 저장) 선택. 시작 HEAD `a7cfd31`; 이전 턴의 Pages 연결 준비 변경6파일을 이어서 구현. 성아 pull 자동배포 준비파일5개는 설치/커밋하지 않고 제거. VPN은 운영 API 최초 설정 작업에만 사용.
- 변경: API config에 명시적 Pages HTTPS origin(public shared PoC만 허용), CORS 정확 origin 허용, 메모리 bearer 세션/CSRF/기존 cookie 분리. `api.ts`에 외부 API base·메모리 토큰, `main.tsx`에 Pages hash routing. 기존 역할·승인·근거·동의 검사 유지. API tests/test_pages.py와 frontend session reset 시험 추가. Pages 전용 브라우저 smoke/명시적 쓰기 시험과 config 추가.
- workflow build의 통과한 결과를 Pages base로 빌드/upload하고, 배포 브랜치 push만 deploy-pages에서 OIDC/pages:write로 게시. verify-pages는 GitHub 실행기에서 기대 commit과 실제 공개 API 연결 확인. GitHub Pages build_type=workflow 생성, github-pages 환경에 기존 main 정책 보존하며 poc/remote-validation 허용 추가. secrets·VPN·SSH는 CI에 넣지 않음.
- 문서: README/github-build/github-pages 및 세 언어 매뉴얼에 정적 파일/공동 DB/메모리 세션·새로고침/배포 방법 반영. Python API 자체 자동배포는 별도 범위로 남김.
- 로컬 실제 명령: `PYTHONPATH=<repo>/apps/api/src .venv/bin/python -m pytest apps/api/tests -q` **89 passed, 2.26s**; Node22.16.0에서 `npm --prefix apps/web run typecheck` PASS, `test:run` **7 passed**, `test:e2e` **11 passed, 33.1s**. `python3 tools/dev/export_manual.py`, `git diff --check` PASS. 기존 httpx 경고 유지. Pages origin 차단, bearer/CSRF/역할/로그아웃/기존cookie 경계 포함.
- 관련 T-ID T-06 사용자·외부 origin·세션, T-08 저장·실패, T-10 실제 DB와 모의 구분; 기존 루프 회귀 T-01/T-02/T-04/T-05/T-07. 실제 STT/LLM·전문 번역 검수·사람 피드백 미실행, 새 FB-ID 없음. 배포와 원격 시험 결과는 후속 기록.

배포·실제 GitHub 화면 검증:

- 구현 commit **e80e6fd** (`feat: deploy GitHub Pages with shared API sessions`). GitHub Actions [37577441301](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37577441301) **completed/success**: build → deploy-pages → verify-pages 전 단계 통과. GitHub Linux API89/unit7/E2E11(39.4s), Pages smoke1(4.0s). 마지막 smoke는 VPN 없는 GitHub-hosted runner에서 실행했으며 GitHub 화면·세 역할 로그인·공동 API·메뉴/매뉴얼·새로고침과 third-party cookie 미사용 확인. 배포 build-info SHA가 e80e6fd의 전체 SHA와 일치.
- 서버 변경: `scp -F /tmp/medipencil-ssh-config`로 API4파일만 전달. `ssh ... mp-sa-app 'python3.12 -'`에서 DB backup.service 실행, 이전 release를 pages-api-e80e6fd로 복사, API파일 교체, env backup 후 Pages exact origin 추가, editable install/current 원자 교체/서비스 재시작. 기존 DB·코멘트 유지. 실패 시 이전 env/install/current 복원 절차 포함. health와 CORS PASS. 게이트웨이 `sudo -n python3 -`에서 기존 설정 백업 후 Authorization 전달, `nginx -t`/reload PASS; 기존 http2 경고 유지. reviewer/proxy-secret 헤더 제거는 유지. TLS/host-key 검증을 끄지 않음.
- 외부 API probe: `.venv/bin/python` httpx에서 Pages Origin 로그인201 → bearer /session200, Allow-Origin 일치. 토큰 값을 로그에 출력하지 않음.
- 실제 Pages 쓰기 명령: apps/web에서 `MEDIPENCIL_PAGES_WRITE_TEST=1 npx playwright test --config playwright.pages.config.ts` **2 passed, 14.3s**. 별도 브라우저의 질문 전달, 원문 계획 기록·승인, 발행 전 비노출, 발행 후 가족 열람, 별도 세션의 코멘트 재조회/새로고침 유지 PASS. 실제 서버·SQLite 사용, `ai_executed=false` 확인. 합성 표식 `AUTO-PAGES-1791351785708`, 실제 사람 피드백 아님. 해당 시험은 매 자동 배포에서 반복하지 않음.
- 실제 GitHub 페이지 Korean 시작 화면 `/tmp/medipencil-github-pages.png` 캡처·시각 확인. 브라우저 오류 없음. UI파일은 GitHub, 공동 저장은 기존 API이며 사용자 브라우저 로컬 저장으로 대체하지 않았다.
- 최종 기록은 docs-only commit으로 게시. 일반 외부 팀원의 빌드·배포·접속에는 VPN 불필요. 쓰기 시험은 로컬 VPN ON에서 수행했고, VPN 없는 GitHub runner에서 공개 접속/세션/API 연결을 별도로 통과했다. API 서버 자체 자동배포·실제 AI·사람 피드백은 미실행/범위 밖이다.

## PC-05-AUTO-API — 2026-10-07 API·DB까지 자동 배포

- 사용자 “진행하고”: GitHub 화면뿐 아니라 성아 API·DB 변경도 외부 팀원의 push로 자동 반영하도록 확장. 시작 HEAD `d6feffa`, clean. 팀원 VPN/SSH 없이 GitHub 공개 배포 bundle을 성아 timer가 가져오는 방식.
- 변경 파일: workflow에 server bundle, publish-api/deploy-api, API 정상 커밋 확인 이후 Pages 배포. `package_release.py`, 고정 `pull_release.py`/`start_current.py`, deploy.service/timer, `run_shared.py`, API health deployment_commit. `tools/deploy/tests/test_deploy.py`에 SQLite migration/실패/health실패/프로세스중단/공개후 쓰기보존/비신뢰 bundle·workflow 차단 시험. docs에 외부 팀원 사용·관리·복구 절차.
- 실제 로컬 명령 `PYTHONPATH=<repo>/apps/api/src .venv/bin/python -m pytest apps/api/tests tools/deploy/tests -q`: **101 passed, 1.83s**, 기존 httpx 경고1. 복구 시험은 실제 임시 SQLite에서 스키마 변경·행 보존·복원을 검사하고 systemd/network는 테스트 대역으로 분리했다. 운영 DB에 고의 장애를 주입한 시험으로 보고하지 않는다. 기존 app/E2E/실제 서버 배포는 이후 Actions에서 확인.
- `scp -F /tmp/medipencil-ssh-config` 및 `ssh ... mp-sa-app 'python3.12 -'`: root-owned agent/launcher/service/timer 설치, medipencil ExecStart drop-in 추가, nginx maintenance marker 조건 추가. 기존 nginx 설정 백업 `medipencil.before-autodeploy-20261007.bak`, `nginx -t`/reload/daemon-reload 성공. 첫 timer enable은 unit을 찾지 못해 실패: `/tmp`에서 copy2로 전달한 파일의 SELinux `user_tmp_t` 레이블이 보존된 원인. `restorecon -Rv`로 unit/agent/launcher의 표준 레이블을 복구하고 daemon-reload 후 timer enable 재시험 성공(SELinux Enforcing 유지). runtime 환경·DB·비밀값은 GitHub에 전달하지 않음. agent 설치는 관리자 VPN 경유지만 이후 자동 배포 경로는 GitHub 공개 HTTPS만 사용.
- 관련 T-ID T-08 저장·장애복구, T-06 세션/배포경계, T-10 실제/모의 구분. 실제 AI·사람 피드백·외부 백업은 미실행. 새 DB 업무 스키마를 임의 추가하지 않고 기존 Alembic upgrade를 자동 실행한다. 복구 테스트의 스키마 변경은 별도 임시 DB에서 수행했다.

실제 자동 배포·재시험 결과:

- 구현 commit **1e8b450b57c2ba4274631b859ef69ec8669cb011** push 후 [Actions 37578829528](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37578829528) **completed/success**. build → publish-api → deploy-api → deploy-pages → verify-pages 모두 PASS. GitHub Linux: API/배포101(5.35s), frontend7, E2E11(39.8s), VPN 없는 Pages/API smoke1(4.3s). 실제 명령 `gh run watch 37578829528 --exit-status`, `gh run view ... --json status,conclusion,url`, `gh run view ... --log`(로컬 `/tmp/mp-auto-deploy-ci.log`).
- 서버 timer가 공개 GitHub HTTPS에서 bundle을 받아 hash/출처/CI를 확인하고 별도 venv 설치, DB 복사본 preflight, 유지보수 gate, 실 DB snapshot/migration/전환을 수행. `journalctl -u medipencil-deploy`에서 2026-10-07 14:59:42 KST Deployed 해당 SHA 확인. 수동으로 앱 bundle을 전달하거나 전환하지 않았다. current는 `sungah-<sha>-37578829528-1`, 공개 health와 Pages build-info 모두 같은 SHA. `systemctl is-active medipencil medipencil-deploy.timer` active/active, timer enabled, SELinux Enforcing.
- 배포 snapshot과 현재 DB를 read-only sqlite3로 대조: 20개 테이블의 이전 모든 행 유지(질문4/발행3/팀코멘트4 포함). integrity_check=ok, foreign_key_check=0. 복구 journal/maintenance marker 모두 정상 제거됨. DB 원문은 출력하거나 저장소에 올리지 않았다. 기존 마이그레이션 head 유지 확인이며 새 업무 스키마 변경은 이번 릴리스에 없음.
- 배포 후 apps/web에서 `PATH=<Node22>/bin:$PATH MEDIPENCIL_PAGES_WRITE_TEST=1 npx playwright test --config playwright.pages.config.ts`: **2 passed, 14.4s**. 새 합성 표식 `AUTO-PAGES-1791352816432`의 질문→직원 승인→발행→다른 가족 세션 열람 및 팀 코멘트 저장/재조회 PASS. 실제 서버·DB 사용. 로컬 쓰기 시험은 VPN ON, GitHub 공개 접근 smoke는 VPN 없는 runner에서 실행. 실제 AI와 사람 피드백을 대체하지 않음.
- 초기 SELinux 레이블 실패·수정까지 문서에 남김. 운영 DB 고의 장애 주입/서버 손실 복구·외부 백업·실제 AI·사람 피드백은 미실행. 자동 복구 분기는 임시 SQLite 시험으로 검증했다. 팀원 일반 배포는 VPN/SSH 없이 배포 브랜치 코드 push로 가능하며 OS/고정 agent/비밀값 변경만 관리자 작업으로 남는다.

## PC-05-LOGIN — 2026-10-07 간편 로그인·사용자 대시보드

- 사용자 요청: 간단한 로그인 화면, 사용자별 대시보드, 이름(역할) 표시. 시작 `02c2454`, `poc/remote-validation`, clean. 기존 비밀번호 없는 합성 사용자 접근 결정 유지.
- 변경: App.tsx 상단 역할 버튼을 독립 로그인 카드로 이동, 서버 Session 이름/역할 표시, 서버 DELETE 로그아웃과 메모리·쿼리·화면 초기화. api.ts의 204 응답 처리 추가. 가족은 자신의 질문 현황·허용된 안부, 직원은 질문 현황·기록/코멘트 바로가기. 실제 질문 API 수치 사용, 로딩/오류/오프라인은 수치를 숨김. CSS 반응형, fi/ko/en 문자열·매뉴얼 원본/생성본 수정. 기존 E2E를 로그인/로그아웃 흐름으로 갱신, login-dashboard.spec.ts와 204 회귀시험 추가.
- 실제 명령: Node22 PATH에서 `npm --prefix apps/web run typecheck` PASS, `test:run` 8 PASS. `PYTHONPATH=<repo>/apps/api/src npm --prefix apps/web run test:e2e` **12 PASS/33.3s**. 로그인·로그아웃204/이후 session401, 이름(역할), 역할별 대시보드, 기존 공개 경계·정정·다중 세션·코멘트 저장 검증. `python3 tools/dev/export_manual.py`, `git diff --check` PASS.
- 초기 E2E는 PYTHONPATH 누락으로 서버 시작 실패. 재실행 중 매뉴얼 수정의 Vite 갱신으로 영어 세션 시험1 timeout(11 PASS). 파일 수정을 멈춘 동일 전체 시험 재실행12 PASS. 실패를 삭제/skip하지 않음.
- `/tmp/care-loop-login-1280.png`, `care-loop-login-360.png`, `care-loop-staff-dashboard.png` 캡처·직접 시각 확인. PC/모바일 가로 넘침 없음. 실제 임시 서버/SQLite 직접 입력 시험이며 실제 AI·전문 번역 검수·지원팀 피드백은 미실행. T-06 사용자 전환/세션, T-08 저장/실패, T-10 실제/모의 구분. 배포 결과는 후속 기록.

- 구현 commit **2e60e1e65af3d924d6174b236de5705b6468cdca**, [Actions 37580084511](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37580084511) 전체 **completed/success**. build/publish-api/deploy-api/deploy-pages/verify-pages 모두 통과. `gh run watch ... --exit-status`, `gh run view ... --json status,conclusion,jobs`로 확인. GitHub Pages build-info SHA가 구현 commit과 일치. VPN 없는 GitHub runner에서 새 로그인 화면의 세 사용자 세션·로그아웃/사용자 전환·팀 코멘트/매뉴얼 접근 PASS. 서버 타이머의 실제 설치 로그를 읽기 전용으로 확인했으며 수동 배포 실행 없이 자동 반영됨. 기록 후속 commit은 docs-only.

## PC-05-CHARTS — 2026-10-07 육각형·7일 기록 시각화

- 사용자 요청: 관리항목 육각형/오각형, 지난 일주일 변화 그래프. 추가 모바일 이미지의 둥근 카드/색상/아이콘을 참고. 시작 `1d0ece9`, clean. 기존 6항목 유지, 건강점수 대신 실제 유효한 정보 건수로 정의. 오늘 포함 Helsinki 관찰일 7일, 계획 포함 명시, 0/비공유(null) 구분. 가족은 current latest publication의 현재 허용정보만, 직원은 현재 유효한 승인 기록만 집계. 매5초 재조회·오프라인 숨김. 기존 동의/정정/근거 검사를 재사용하며 과거 발행 fallback 없음.
- 변경: API dashboard.py/main.py 및 test_dashboard.py, web DashboardCharts.tsx/App.tsx/CSS, Phosphor 아이콘 dependency+lock, fi/ko/en/매뉴얼, dashboard-charts E2E, Pages smoke의 실제 6항목 검사. 카드 선택→그래프 필터, 육각형 분포, 7일 선그래프, 접근 가능한 수치 표.
- 실제 명령 `PYTHONPATH=<repo>/apps/api/src .venv/bin/python -m pytest apps/api/tests tools/deploy/tests -q`: **104 PASS/2.32s**. 최초 새 시험에서 immutable consent에 직접 UPDATE를 시도하여 실패; 실제 revoke API를 사용하도록 시험 수정 후 전체 PASS(제약조건 유지). `npm --prefix apps/web run typecheck` PASS, `test:run` 8 PASS. `PYTHONPATH=... npm --prefix apps/web run test:e2e` **13 PASS/43.2s**. 모바일 라벨 크기 수정 후 `test:e2e -- dashboard-charts.spec.ts` **1 PASS/3.4s**. `python3 tools/dev/export_manual.py`, `git diff --check` PASS.
- 디자인 QA: 첨부 이미지와 PC/모바일 캡처 함께 비교. 모바일 작은 그래프 글자 P2 수정 후 재캡처; design-qa.md passed. In-app Browser에서 실제 로컬 API/임시 SQLite의 합성21건으로 Liisa 육각형/7일 추이·항목 필터 확인, console error0. 초기 preview는 임시 경로 symlink 검사로 시작 실패→Path.resolve로 수정. 해당 합성 QA 데이터는 운영 서버/GitHub에 넣지 않음. 로컬 preview `http://127.0.0.1:5179`.
- T-06 권한/역할, T-07 철회/현재근거, T-08 실패/오프라인, T-10 사실/모의. 실제 AI·임상 점수·전문 번역 검수·사람 피드백 미실행. 새 테이블/DB migration 없음. 배포 결과는 후속 기록.

- 구현 commit **39d2be3570bf21972cdfe87a3fef794e3c4f8c39**. [Actions 37581364583](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37581364583) **completed/success**: build → publish-api → deploy-api → deploy-pages → verify-pages 모두 PASS. `gh run view ... --json status,conclusion,jobs`, 공개 health/build-info curl로 동일 SHA 확인. VPN 없는 GitHub runner가 세 역할 로그인 뒤 실제 dashboard API 기반 6개 카드 표시를 검사하고 통과. 운영 데이터 새 입력/리셋 없이 자동 배포. 실제 AI·사람 피드백 미실행 상태 유지.

## PC-05-QUESTION-BOARD — 2026-10-07 질문·직원 답글 게시판

- 사용자 지적: 보낸 내용을 알기 어렵고 질문/직원 답글을 게시판처럼 연결해야 함. 시작 `d89f9ad`, clean. 기존 승인·동의·발행 계약을 유지하며 업무 게시판으로 변경.
- API: questions.py/dto.py에 작성 시각·작성자·현재 발행된 질문별 reply(발행 직원/시각/연결 항목만) 추가, generated-api 재생성. latest/current permission/evidence 검사를 재사용, 무관한 공개 항목은 해당 질문 답글에서 제외. 초안/승인만 된 기록은 reply에 반환하지 않으며 철회 시 null/access_changed.
- UI: App 질문 목록을 게시글 카드·작성자/시각/상태·전체/대기/완료 필터·펼치기로 변경. 저장 성공 시 반환된 실제 질문을 목록 캐시에 즉시 반영, 모든 cursor 페이지 조회. QuestionReply.tsx에서 게시글 안의 직접 입력 → 초안 검토 → 근거 확인/승인 → 전체 발행물 미리보기 → 명시적 발행. 기존 API를 이용하며 단계별 idempotency key 유지. fi/ko/en/CSS/매뉴얼 수정. 새 DB 테이블 없음.
- 실제 명령 `PYTHONPATH=<repo>/apps/api/src .venv/bin/python -m pytest apps/api/tests tools/deploy/tests -q`: **105 PASS/3.39s**. `npm --prefix apps/web run generate:api`, `typecheck` PASS, `test:run` **8 PASS**. `PYTHONPATH=... npm --prefix apps/web run test:e2e`: 최종 **14 PASS/51.0s**. 후속 표시 문구 조정 후 `test:e2e -- question-board.spec.ts` **1 PASS/11.3s**. `python3 tools/dev/export_manual.py`, `git diff --check` PASS.
- 초기 실패: cursor 응답 타입 추론 TS7022 → 명시 타입으로 수정. 첫 E2E에서 기존 로그인 캡처가 screenshot timeout, 새 답글 Type label 조회 timeout → select의 명시적 aria-label 추가, 전체 재실행 모두 통과. 기존 캡처 시험은 삭제/skip하지 않음.
- 실제 임시 서버/SQLite·별도 가족/직원/Mikko 브라우저로 질문 저장→새로고침→직원 답글→승인 전/발행 전 비노출→발행 후 같은 게시글 답글→새로고침 유지·다른 가족 격리 PASS. 모바일 `/tmp/care-question-board-390.png` 캡처·시각 확인. 운영 DB에는 해당 합성 시험 데이터를 쓰지 않음.
- T-04 승인/발행, T-06 사용자/수신자, T-07 권한 철회, T-08 저장·재시도, T-10 실제/모의. 실제 AI·실제 의료진/지원팀 피드백은 미실행. 발행 전 편집기의 진행 상태는 새로고침 복구 미지원(매뉴얼 명시); 이미 저장된 질문과 발행 답글은 DB에 유지. 배포 결과는 후속 기록.

- 구현 commit **1f67ed92c1d1444a86b57fb7b26922e2cfcbf5c7**. [Actions 37582803021](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37582803021) 전체 **completed/success**: build/publish-api/deploy-api/deploy-pages/verify-pages PASS. `gh run view ... --json status,conclusion,jobs`, 공개 health/Pages build-info curl에서 같은 SHA 확인. GitHub 외부 runner의 세 사용자 게시판 heading 확인 PASS. 관리자 로그 조회용 SSH는 경유지 호스트 키 불일치로 차단됐으며 우회하지 않음. 자동 배포는 SSH 없이 정상 완료. 운영 DB 쓰기/리셋 없이 게시판 반영, 사람 피드백·실제 AI 미실행.

## PC-05-GUARDIANS — 2026-10-07 Aino와 로그인 역할·수신자별 공개 범위 명확화

- 최신 사용자 결정: Aino는 로그인하지 않는 환자/돌봄 대상자, Liisa·Mikko는 보호자 2명, Koskinen은 간호사. 시작 HEAD `972d65a`, `poc/remote-validation`, clean. 환자 로그인/이름 변경/추가 역할 migration은 실행하지 않음.
- 기존 서버는 이미 Liisa 전체 SCOPES, Mikko meals/movement/care_contact로 seed하고 수신자별 현재 동의·발행·근거를 검사한다. 이 계약과 기존 DB 동의 이력을 보존. 로그인 기본 범위 안내와 보호자/간호사 이름(역할)을 명확화. App.tsx, 신규 SharingSummary.tsx, style.css, fi/ko/en JSON, manual-content.json 및 생성 매뉴얼 수정. 현재 공유 범위는 서버 조회/5초 재조회, 오류·오프라인 시 숨김. 간호사 대시보드는 두 보호자의 범위를 함께 표시. 내부 API 역할 코드 family/staff 유지, 공개 역할 명칭은 Guardian/Nurse.
- 실제 명령 `PYTHONPATH="$PWD/apps/api/src" .venv/bin/python -m pytest apps/api/tests tools/deploy/tests -q`: **106 PASS/2.37s**. 새 test_guardian_boundaries.py는 Aino 로그인 불가, 서로 다른 보호자 발행물·질문 격리, 제한 복약 정보/근거/그래프 비노출 및 간호사 API 차단 검증. 기존 Starlette/httpx deprecation warning 1개.
- Node22 PATH로 `npm --prefix apps/web run typecheck`: PASS, `test:run`: **8 PASS**, `PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run test:e2e`: **15 PASS/57.2s**. 신규 guardian-roles.spec.ts에서 실제 서버/임시 SQLite·독립 브라우저 세션 3개로 역할과 범위를 확인. `/tmp/care-loop-mikko-permissions.png` 모바일390px 캡처·시각 확인. 기존 login-dashboard 역할 기대값 수정. 테스트 실패/skip 없음.
- `python3 tools/dev/export_manual.py`, `npm --prefix apps/web run build`, `git diff --check`: PASS. 빌드의 기존 dependency use-client directive 경고 유지. 최종 안내문은 보호자에게 적용됨을 명시적으로 다듬음.
- T-06 역할·수신자별 권한, T-07 현재 동의, T-08 오류/오프라인, T-10 사실/모의 추적. 실제 AI·사람 피드백·번역 전문가 검수 미실행. 운영 DB 리셋/동의 덮어쓰기 없음. 커밋·자동 배포 결과 후속 기록.

- 구현 commit **645190f275e7746efa09b8252414292249edaa1a**. [Actions 37584554702](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37584554702) **completed/success**, build/publish-api/deploy-api/deploy-pages/verify-pages 모두 PASS. `gh run view ... --json status,conclusion,jobs`, 공개 API health/Pages build-info의 SHA 일치 확인. 운영 서버 현재 sharing 조회: Liisa 7범위, Mikko meals/movement/care_contact(둘 다 v1). 변경 없이 조회하고 시험 세션 로그아웃.
- 배포 후 `apps/web`에서 Node/Playwright의 `node --input-type=module` 실제 공개 Pages 검증: 독립 context마다 Liisa(Guardian), Mikko(Guardian), Koskinen(Nurse) 로그인; Aino 로그인 버튼 부재, 각 medication/meals의 서버 기반 data-shared 상태 및 이름(역할) 모두 PASS. 각 세션 로그아웃. 운영 질문/기록/코멘트 쓰기 없음. 로컬 검증과 공개 배포 확인 완료; 사람 피드백/실제 AI 미실행.

## 2026-10-07 — 첫 화면(로그인) 배경 이미지

- 사용자 요청: 앱 구동 시 첫 view 배경에 첨부 이미지 적용. 사용자 제공 생성 이미지(실제 환자·입주자 정보 아님)를 `apps/web/src/assets/login-background.webp`(1672×941, 205KB)로 추가하고 `.login-screen`에 CSS 배경으로 지정. Vite가 URL을 해시 자산으로 변환해 `MEDIPENCIL_WEB_BASE` 배포 경로를 따름.
- 가독성: 상단은 두 인물 얼굴이 보이도록 비우고 안내문·상태문은 반투명 흰 패널, 하단 어두운 그라디언트. 모바일 650px 이하 패딩 축소. 로그인·역할·권한 동작 변경 없음.
- `npm --prefix apps/web run typecheck` PASS, `build` PASS(기존 use-client 경고), `test:run` **8 PASS**. vite preview + Playwright(Chromium 1194) 1280px/390px 캡처 시각 확인(API 미기동 상태, 사용자 목록 로딩 문구 가독성 확인). e2e·사람 피드백 미실행.

## 2026-10-08 — 로그인·대시보드 프로필 사진

- 사용자 요청: 제공한 프로필 사진 3장을 포털 첫 페이지와 각 대시보드에 추가. 사용자 제공 생성 이미지(실제 인물·입주자 정보 아님)를 320×320 WebP(14~17KB)로 줄여 `apps/web/src/assets/profile-{aino,liisa,koskinen}.webp`에 추가. 신규 `Profiles.tsx`의 `Avatar`/`ResidentProfile`이 actor별 사진을 표시하고, 사진이 없는 Mikko는 기존 이니셜 아바타를 유지.
- 매핑(사용자 확인 필요): 어르신 → Aino(돌봄 대상자, 로그인 없음), 도시의 여성 → Liisa(보호자), 간호복 → Koskinen(간호사).
- 로그인: 계정 카드 이니셜을 사진으로 교체, 안내 패널에 Aino(돌봄 대상자) 표시. 대시보드: 로그인 사용자 사진과 제목, Aino 카드 추가. 대체 텍스트·라벨은 fi/ko/en JSON에 추가. 역할·권한·발행 동작 변경 없음. PR #5 머지 후 `JY_test`를 `origin/poc/remote-validation`(a04845c)에서 fast-forward로 다시 시작.
- `npm --prefix apps/web run typecheck` PASS, `test:run` **8 PASS**, `build` PASS(기존 use-client 경고). 설치된 Chromium 1194를 지정한 임시 설정으로 `npx playwright test` **15 PASS/1.9m**(실제 Uvicorn/임시 SQLite/Vite). 로그인 1280·390px, Liisa/Mikko/Koskinen 대시보드 캡처를 시각 확인하고 깨진 이미지 0개 확인. 사람 피드백 미실행.
- 후속(같은 날): 사용자가 Mikko 프로필 사진을 제공. 320×320 WebP(13KB) `profile-mikko.webp`로 추가하고 `Profiles.tsx` 매핑에 등록해 네 인물 모두 사진 표시(이니셜 대체 경로는 유지). typecheck PASS, `test:run` **8 PASS**, build PASS, 임시 Chromium 설정의 `npx playwright test` **15 PASS/1.9m**. 실제 서버에서 로그인 카드 사진 3개, Mikko 대시보드 사진 2개, 깨진 이미지 0개 확인.
- 배포: PR #5(로그인 배경)와 PR #7(프로필 사진)이 `poc/remote-validation`에 머지되었다. PR #7 머지 commit **23bec3a5c8de1d1b0bfb23b908922f45233b1e27**. [Actions 37711844044](https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/37711844044) **completed/success**(01:13~01:22 UTC). build(API 시험·frontend typecheck/test·임시 SQLite 브라우저 돌봄 루프·매뉴얼 확인·빌드), publish-api, deploy-api(공유 API 배포·DB migration 대기), deploy-pages, verify-pages(배포 revision 확인, VPN 없이 Pages·공유 API 확인) 모두 PASS. GitHub MCP `list_workflow_jobs`로 job별 결과 조회.
- 한계: 이 cloud 세션은 네트워크 정책으로 공개 Pages·API 호스트 접속이 차단(proxy CONNECT 403)되어 공개 화면의 사진 표시는 직접 확인하지 못함. verify-pages는 revision/API 연결 검증이며 이미지 표시 검증이 아님. 사용자 육안 확인 요청. 운영 데이터 쓰기·리셋 없음. 사람 피드백 미실행.
