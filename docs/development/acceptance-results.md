# 독립 합성 구현 수용 검증 결과

최신 추가 결과는 아래 로컬 모델 추가 검증을 따른다. 기존 표는 최초 구현 시점의 결과를 보존한다.

검증일: 2026-10-03 KST. 기준: 확정 설계 v1.1, 상세 명세01~03. 구현 branch: `codex/care-loop-mvp`; 작업별 commit·명령은 [progress.md](progress.md). 검토 주체는 개발 에이전트의 코드/자동 검증이며 FI 전문가·임상 검토자가 아니다. 원본 명세의 역사적 NOT_RUN 표시는 변경하지 않았다.

51개 pytest, 3개 Vitest, 4개 Playwright가 통과했다. 아래 55개 명세 하위 항목의 전체 통과를 뜻하지 않는다. **PASS는 기재된 독립 합성 자동 경로**, PARTIAL은 일부 경계만 검증, NOT_RUN/BLOCKED는 미실행이다. 테스트 데이터는 저장소의 tests/e2e 코드로 버전 관리되는 TEAM_SYNTHETIC이며 실자료·실제 AI 결과가 없다. 체크박스를 누르는 브라우저 자동화는 사람 의미 검수 증빙이 아니다.

## 실행 증거

- `.venv/bin/python -m pytest apps/api/tests -q`: 51 passed, Starlette/httpx deprecation 경고1개.
- Node22 `npm --prefix apps/web run lint`, `run typecheck`: exit0. lint는 현재 타입 검사 alias다.
- `npm --prefix apps/web run test:run`: 3 passed. `run build`: exit0, 의존성 use-client directive 경고 있음.
- `npm --prefix apps/web run test:e2e`: 4 passed (4.7초), 새 파일 SQLite + 실제 Uvicorn/Vite/Chromium. API 응답 전체 mock 없음. 늦은 응답 테스트는 실제 route.fetch 응답의 지연 주입.
- wheel의 새 가상환경 설치, CLI, TCP 시작/중지/재시작, 실행 중 삭제 거절, dry-run/정리: 별도 패키지 검증 명령을 progress에 기록.
- [성능 측정](../evidence/local-performance.json): 합성 최소 DB, API1프로세스, 동시 세션5, 경로별50회 TCP 요청. 가족 board p95 11.25ms, 직원 queue p95 10.06ms. 실제 현장·대규모 자료·AI 지연·업무 절감 수치가 아니다.

## 명세 항목별 결과

테스트 경로의 기준은 `apps/api/tests/`이다. `acceptance`는 test_acceptance.py, `E2E`는 apps/web/e2e/care-loop.spec.ts, `UI unit`은 apps/web/src/api.test.ts다.

| T-ID | 상태 | 실제 확인 범위 / 남은 사항 |
|---|---|---|
| T01-A | PASS | records/publications: plan 승인·발행 뒤 planned 유지, 임의 완료 생성 없음 |
| T01-B | PASS | acceptance: 미승인 후속 기록으로 confirm422, 승인 후 명시적 확인 가능 |
| T01-C | PASS | publications: plan을 완료 근거로 사용 거절 |
| T01-D | PASS | acceptance: 사건시각 역순 입력에도 자동 완료 없음, 후속 승인 근거로 확인 |
| T02-A | PASS | acceptance: 계획/완료의 서로 다른 실제 record/version/segment 연결 확인; 원본 예시 ID 대신 독립 합성 ID |
| T02-B | PASS | acceptance: 타 resident source409, 잘못된 ref 검증 |
| T02-C | PASS | corrections_failures/acceptance/E2E: 불변 원문, 새 버전, 즉시 옛 발행 차단, 새 source 재승인·재발행 |
| T02-D | PARTIAL | records/acceptance: source 전체 문구 일치·부정어 잘라내기 거절. 자연어 의미/화자 판단의 사람 검수 NOT_VERIFIED |
| T03-A | PASS | acceptance: 무릎 통증 문장 그대로, 좌우/기간/점수 추가 없음 |
| T03-B | PASS | acceptance: 약 목록 원문 유지, 복용 완료 생성 없음 |
| T03-C | PASS | sensors: 문 센서 관측, 동행/통증 의미 생성 및 행동 확인 금지 |
| T03-D | PARTIAL | sensors/acceptance: 침대·문 집계와 냉장고 문장 원문 유지. 냉장고 시계열 전용 import는 미구현 |
| T03-E | PASS | aggregation/sensors: 야간·중복·누락 coverage 구별, 임의 부재 확정 없음 |
| T03-F | PASS | acceptance: 외부 전송 지시 문장을 자료로 보존, 네트워크 생성 감시. 실제 LLM prompt injection 시험은 미실행 |
| T04-A | PASS | records/publications/E2E: 초안 가족 미노출 |
| T04-B | PASS | records: 승인과 질문 answered·동의 변경 분리 |
| T04-C | PASS | publications: preview 비공개, 별도 publish 필요 |
| T04-D | PASS | corrections_failures: 실제 SQLite 실패 trigger로 publication·질문 원자 rollback |
| T04-E | PASS | records/acceptance: stale revision412, snapshot 재검사 |
| T05-A | PARTIAL | consents: 후보 생성은 grant 불변. 이름 모호성/긍정 발언 LLM 해석은 미실행 |
| T05-B | PASS | consents/E2E: outdoors만 추가, 다른 건강 scope 미허용 |
| T05-C | PASS | consents: 후보 밖 scope422 |
| T05-D | PASS | consents: stale consent409 |
| T06-A | PASS | E2E/acceptance: FI→SV actor 유지, SV unavailable |
| T06-B | PASS | E2E/sessions: 세션 교체, 허용하지 않은 건강정보 raw JSON/DOM 미노출 |
| T06-C | PASS | acceptance/sessions: recipient 위조 추가 필드422, 세션 기준 판단 |
| T06-D | PASS | publications/consents: 숨긴 evidence404, 전체 source ID/본문 미노출 |
| T06-E | PASS | UI unit/E2E: 응답 지연 및 JSON decode 중 사용자 전환 시 옛 결과 폐기 |
| T06-F | PASS | questions/acceptance: 다른 가족 질문·타 resident 근거 차단 |
| T07-A | PASS | consents/E2E: 철회 후 기존 URL 재접근 거절 |
| T07-B | PASS | corrections_failures: idempotency replay 전에 현재 권한 검사 |
| T07-C | PARTIAL | acceptance: prepare→권한변경→publish412. 실제 LLM 실행 중 변경은 BLOCKED_PROVIDER |
| T07-D | PASS | consents: 최신 revoked 뒤 과거 grant fallback 없음 |
| T07-E | PASS | corrections_failures: 최신 invalidated 뒤 과거 발행 fallback 없음 |
| T08-A | PASS | questions: 미답변·예정 경과 유지, AI 보충 없음 |
| T08-B | PARTIAL | audio/acceptance: 미설정 provider 실패 및 timeout 주입, 질문·직접 입력 유지. 실제 STT timeout 미실행 |
| T08-C | PARTIAL | questions: 병렬 동일 key 한 질문; 공통 transaction idempotency 적용. 모든 record/job 조합 병렬 수용시험은 미실행 |
| T08-D | PASS | questions: 동일 key 다른 payload409 |
| T08-E | PARTIAL | acceptance: 취소/기한 경과 후 늦은 결과 거절, 실제 로컬 파일 정리. 실제 provider 응답 없음 |
| T08-F | PARTIAL | acceptance: record 저장 실패503·질문 미완료·capture 유지. 모든 source 실패 UI 조합은 미실행 |
| T09-A | PARTIAL | audio: 실제 합성 WAV 파일 삭제 후 local receipt. 정상 실제 STT 승인·엔진 receipt 미검증 |
| T09-B | PARTIAL | audio/acceptance: 취소·실패·주입 timeout에서 로컬 artifact 삭제. 엔진 내부 artifact 미검증 |
| T09-C | PARTIAL | audio: PermissionError 주입 시 failed/deleted_at=null, 재시도 복구. 엔진 receipt 실패 미실행 |
| T09-D | PARTIAL | audio: durable manifest 복구 경로 테스트; 패키지 실제 정상 중지/재시작. STT 실행 중 OS 강제종료 시험 미실행 |
| T09-E | PASS | audio/providers: VEIL/혼합/미상 계보·외부 endpoint 네트워크 전 차단; 실제 Veil 파일 읽지 않음 |
| T09-F | PARTIAL | providers: 모든 외부 endpoint 차단, fallback 없음. 연결된 provider의 redirect 체인 시험 미실행 |
| T09-G | PASS | lifecycle/foundation/acceptance: dry-run삭제0, exact run ID, 실행 중 잠금, 미상 파일 보존, symlink 거절 |
| T09-H | PASS | acceptance/audio: 크기413, 형식415, chunked body 제한, 오류에 입력명 미반영 |
| T09-I | PARTIAL | acceptance: validation 오류에 입력 미반영, audit 본문 컬럼 없음. Git 산출물 경로 검사 수행; 외부 CI/실데이터가 없어 그 검사 미실행 |
| T10-A | NOT_RUN | fixture provider를 구현·사용하지 않음. 실제 수동 처리와 idempotency REPLAY는 구분 |
| T10-B | BLOCKED | 실제 LLM 모델/endpoint/권리 미확인. manual 경로 ai_executed=false, STT skipped; AI LIVE 성공으로 보고하지 않음 |
| T10-C | PASS | acceptance: 저장 board CACHED·최초 manual provenance, idempotency job REPLAY 메타 |
| T10-D | NOT_RUN | 사람의 확인·수정·발행·동의 포함 90초 시연 미측정. E2E 시간/HTTP latency로 대체하지 않음 |
| T10-E | PARTIAL | 업무 효과 수치 UI 자체를 만들지 않았으며 전화0건·절감률을 표시하지 않음. 현장 효과 자료 없음 |
| T10-F | PASS | E2E/UI unit: offline 민감내용 마스킹, 미준비 언어 unavailable |

## 인수인계 상태

C-01~C-08의 직접 입력 핵심, C-10 화면1~5, C-11 위 자동 검증, C-12 독립 합성 패키징을 구현했다. C-09는 실제 로컬 오디오 수명주기와 provider 차단 경계까지 구현했으며 실제 STT/LLM 연결은 BLOCKED_PROVIDER다. C-12의 Veil adapter 매핑·반입은 BLOCKED_VEIL이다. 위 PARTIAL/NOT_RUN 항목 때문에 전체 명세 완료로 선언하지 않는다.

FI/selkokieli 전문 검수, 실제 모델 품질·엔진 내부 삭제, 주최 측 이용조건/Q-01~Q-03 확인, 사람 시연시간·현장 업무효과는 남아 있다. 선택 화면6·전체 다국어·스트리밍은 범위 밖이다. 실행은 [runbook.md](runbook.md)를 따른다.

## 로컬 모델 추가 검증 (2026-10-03, 사용자 후속 지시)

STT/LLM 연결 BLOCKED_PROVIDER는 설치된 Whisper medium + Ollama llama3.1:8b의 독립 합성 범위에서 해소했다. [실제 모델 증거](../evidence/local-model-smoke.json), 설정·범위는 [runbook](runbook.md#로컬-sttllm-설정과-교체-2026-10-03-추가)에 있다. Veil 차단과 FI 사람 검수 미완료는 유지한다.

- API62 PASS, UI unit3 PASS, 실제 서버 브라우저5 PASS. 추가 단위 테스트의 adapter double은 REPLAY/ai_executed=false이며 실제 모델 증거와 분리한다.
- T10-B: 직접 입력 + 실제 Ollama 경로에서 STT skipped, AI LIVE, 검토 전 draft 확인. 실제 음성 Whisper + Ollama 경로도 DB와 명시적 테스트 승인/발행까지 실행했다.
- T09-A/B: 실제 Whisper 자식 프로세스 종료와 로컬 업로드 파일 삭제 확인. worker는 별도 출력 파일을 만들지 않는다. 프로세스 내부 메모리·SSD 물리 소거 검증은 아니다.
- T09-F: HTTP adapter의 redirect와 cloud metadata 거절을 transport double로 확인했다. 실제 외부 요청은 하지 않았다.
- T08-B/E, T07 계열: 주입 timeout 뒤 manual 재시도, 취소 후 지연 LLM 결과 미저장, 같은 key 모델 재호출 방지, 완료 STT source의 restart 보존을 추가했다. 실제 장시간 모델 timeout/강제종료 품질시험은 아직 미실행이다.
- 의미·FI 품질은 NOT_VERIFIED. 실제 합성 STT의 첫 단어 인식 오류를 확인했다. LLM은 근거 선택만 수행하며 자유 문구 생성·가족용 재작성·동의 자동 추출은 미구현이다.

## 실제 모델 브라우저·취소·편집 후속 검증

- 일반 자동 테스트: API64 PASS, UI unit6 PASS, 일반 브라우저5 PASS.
- 별도 `npm --prefix apps/web run test:e2e:local`: 실제 설치 모델 + 실제 API/SQLite + Chromium1 PASS. 직원 UI의 합성 녹음 허용·업로드·Whisper·Ollama·명시적 자동 검토/승인/발행·가족 evidence 확인. 추가 running STT 취소 후 source0/파일삭제 확인. [실행 증거](../evidence/local-browser-models.json).
- T06-E: job polling 대기 중 사용자 전환 시 새 세션으로 옛 작업을 조회하지 않도록 중단 검증.
- T08-E/T09-B: 실제 STT running 취소 검증. 취소했지만 아직 반환하지 않은 모델 호출과 다음 모델 호출의 겹침은 adapter double로 별도 재현·차단 검증.
- T06/T07: 추론 중 요청 직원의 권한 철회 시 결과 저장 거절(주입 검증). 실제 업무 권한 운영 검증으로 확대하지 않는다.
- T02-C/D: 다중 문장 편집 시 다른 문장/근거/scope를 덮어쓰지 않는 회귀 검증. 문장별 의미 검수는 여전히 사람의 책임이다.
- T10-B/C: 실제 STT 기반 근거를 직접 입력이라고 표시하던 고정 label 제거. 실제 모델 실행과 사람 FI/의료 품질 검수는 계속 분리한다.
