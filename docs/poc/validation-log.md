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
