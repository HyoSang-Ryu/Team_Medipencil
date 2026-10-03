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
