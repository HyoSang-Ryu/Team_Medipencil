# MediPencil 상세설계 및 개발명세 — 03. Codex 작업지시·검증·실행계획

문서 ID: MP-PK-DEV-003 / 버전: 1.0 / 작성일: 2026-10-02  
상태: **SPEC_READY / 실행단계 PREPARATION / 구현 NOT_IMPLEMENTED / T-01~T-10 NOT_RUN**

[시작점](README.md) · [01 상세설계](01-detailed-design.md) · [02 API·UI·AI](02-api-ui-ai-spec.md) · [상위 설계 v1.1](../design/medipencil-final-design-v1.1.md)

## 1. Codex에게 주는 목적

문서를 다시 쓰는 것이 최종 목표가 아니다. 허용된 구현 단계에서 **가족 질문 하나가 실제 서버·DB·승인·권한을 거쳐 가족에게 돌아오는 동작**을 만든다. UI에 하드코딩된 완성 카드만 띄워 end-to-end라고 보고하지 않는다.

기존 v1.1, R2 보정, 5개 핵심 화면, T-01~T-10을 유지한다. 새로운 범용 AI 앱·에이전트 플랫폼으로 확대하지 않는다. 본 작업표와 수용 기준은 이번 개발명세에서 구체화한 [DD]이며 실제 실행 실적이 아니다.

## 2. 시작 조건과 사전/현장 경계

### 2.1 현재 기준 상태

| 항목 | 문서 작성 시 상태 | Codex의 행동 |
| --- | --- | --- |
| v1.1 설계 | DESIGN_APPROVED | 변경하지 않고 구현 기준으로 읽기 |
| 상세 개발명세 | SPEC_READY | 작업별 입력·출력·테스트 기준으로 사용 |
| 현재 작업단계 | PREPARATION | P-00/P-01의 문서·기존 자산·범용 환경 준비만 수행 |
| 과제 전용 구현 | WAITING_FOR_PERMITTED_PHASE | 현장 시작 또는 범위를 특정한 주최 측 확인 전 자동 시작 금지 |
| D-05 | OPEN | 기본 FI UI 계획 유지, 발표자·검수자 확보를 완료로 쓰지 않음 |
| D-06/Q-03 | OPEN | 실제 엔진 연결은 미설정. 허용된 단계에서는 mock·직접 입력 경로부터 구현 |
| Q-01 | OPEN | 과제 전용 prompt·테스트 fixture·합성 음성도 산출물별 사전 경계 적용 |
| Q-02 | OPEN | VEIL/VEIL_DERIVED의 외부 API·개발 에이전트 전송 차단 유지 |
| Q-04 | OPEN | 담당 직종·연락처·권한·FI 문구를 실제 현장 사실로 단정하지 않음 |

이는 [v1.1 §9.1·§15](../design/medipencil-final-design-v1.1.md)를 유지한 것이다. 이번 “개발명세 작성·등록” 요청을 주최 측 사전 구현 허가로 해석하지 않는다. 시간이 지났다는 이유만으로 자동 gate 해제하지 않는다.

### 2.2 구현 단계 열기

팀 담당자는 현장 시작 또는 주최 측의 해당 범위 허용을 확인하고 Codex 작업에 다음을 명시한다: `실행 단계`, `허용된 작업 ID`, `확인자`, `확인 시각`, `근거 또는 회신 참조`, `기존 자산 기준 commit`.

비공개 회신·개인 이메일 원문은 공개 저장소에 올리지 않는다. 공개 가능한 결정 요지와 내부 근거 식별자만 기록한다. Codex가 스스로 주최 측 승인자나 사용자 확인자를 만들어 쓰지 않는다.

gate가 열리면 허용된 C 작업을 순서대로 진행하며 사소한 코드 변경마다 재승인을 요구하지 않는다. 다만 외부 모델 다운로드·유료 호출·새 외부 전송·데이터 삭제·공개 배포는 별도 권한과 조건을 확인한다.

**OPEN 항목이 있다고 전체 개발을 멈추지는 않는다.** Q-02가 미결이면 독립 합성자료의 로컬 루프를 구현하고 Veil 외부 전송만 차단한다. Q-03이 미결이면 실제 엔진 연결만 blocked로 표시하고 직접 입력·명시적인 fixture 경로로 나머지 테스트를 수행한다.

### 2.3 첫 메시지 템플릿

지금 사용할 준비 단계 지시:

> AGENTS.md와 docs/development/README.md, 01~03 명세를 읽어라. v1.1 범위를 유지한다. P-00부터 현재 저장소·실행단계·반입 자산을 확인하고, 허용된 준비 범위만 수행하라. 과제 전용 구현 시작 조건이 없으면 코드를 미리 완성하지 말고 작업계획과 미결 조건을 보고하라. 실제 수행·미수행·차단을 구분하라.

허용된 현장 구현 단계에서 사용할 지시:

> 확인된 구현 단계와 허용 범위를 작업 기록에 남긴 뒤 C-01부터 순서대로 구현하라. 01의 저장·상태·권한 계약과 02의 API·화면 계약을 따른다. 기본은 FastAPI/SQLite/React+TypeScript이고, 모델은 adapter로 분리한다. 먼저 직접 입력으로 서버·DB를 지나는 루프를 완성하고 동의·정정·실패 경로를 검증한 뒤 실제 엔진을 연결하라. 작업마다 변경 파일·실행 명령·결과·commit·남은 제한을 보고한다. 미실행 테스트나 mock 결과를 실엔진 검증으로 표시하지 마라.

## 3. 공통 작업 규칙

1. 시작할 때 branch, HEAD, 작업 트리, 기존 문서를 읽는다. 다른 사람이 작성한 코드를 reset·삭제·덮어쓰지 않는다. 과거 자산의 작성 시점을 숨기거나 commit history를 재작성하지 않는다.
2. 구현 branch는 예를 들어 `feat/care-loop-mvp`로 만들고 작업별 작은 commit을 남긴다. 이미 작업 branch가 있으면 그 기준을 확인한다. main 강제 push 금지.
3. 하나의 작업은 목표·파일 범위·의존성·수용 테스트를 가진다. 실패하면 해당 원인만 수정한다. 테스트를 지우거나 skip하여 완료 처리하지 않는다.
4. 실제 엔진이 없으면 adapter와 PROVIDER_NOT_CONFIGURED를 구현한다. 가짜 성공 API로 gap을 덮지 않는다.
5. 실제 환자·입주자 데이터·음성, VEIL 내용, 비공개 엔진·credentials를 개발 에이전트 workspace·prompt·공개 repo·CI에 넣지 않는다.
6. 모든 명세 수치·fixture·deadline은 개발 기준이다. 임상 성과, 실운영 성능, 법률 준수, 우승 가능성을 입증한 것으로 쓰지 않는다.
7. 명세 충돌은 영향받는 작업만 중단하고 두 문구·선택지를 보고한다. 범위·승인·권한·데이터 조건을 몰래 약하게 만들지 않는다.

## 4. 작업 패키지

### P-00 저장소·문서·시작 조건 확인 — 지금 가능한 준비

**입력:** 현재 HEAD, v1.1, 01~03, AGENTS.md.  
**산출물:** `docs/development/progress.md`의 첫 preflight 기록, 작업 분리표, 기존 자산 목록의 문서 틀. 새 기능 구현은 아님.

확인 항목: 기준 commit과 main 차이, 앱 소스 존재 여부, mock/실엔진 구분, 현재 구현 허용 범위, 공개 저장소에 들어오면 안 되는 자료, 담당 미결. 설계 문서가 있다는 이유로 구현이 존재한다고 쓰지 않는다.

**완료:** P-00 관측 사실과 unknown이 구분되고, 시작 조건이 없는 C 작업은 WAITING으로 남아 있다.

### P-01 범용 환경·기존 자산 준비 — 허용된 사전 범위만

기존 STT/LLM·범용 라이브러리·개발환경의 버전·권리·실행 경로를 확인한다. 직접 접근할 수 없는 엔진은 NOT_VERIFIED. 모델 다운로드·비공개 repo clone은 권한이 있을 때만 수행한다.

산출물은 반입 자산의 제품명·버전·commit·준비 범위·사용권 확인 상태다. 범용 환경 smoke input과 과제 전용 Aino fixture를 혼동하지 않는다. 새로운 가족 질문 매핑·상황판·동의 로직을 “범용 준비”라고 이름 바꿔 미리 구현하지 않는다.

### C-01 앱 기반·계약·테스트 실행틀

**의존:** 구현 시작 조건, P-00.  
**대상:** apps/api, apps/web, Python/Node lockfile, migrations, 테스트 설정, 제한 작업영역 설정, `.gitignore`.

FastAPI health, React shell, 같은 출처 proxy, 공통 오류 DTO, 명세 enum, 기본 테스트를 만든다. 앱 기본값은 localhost, 외부 AI off, 실제 자료 없음. 모의 데이터·오디오·DB·trace가 build와 git staging에 섞이지 않도록 exclude 규칙을 작성한다.

**완료:** API health·프론트 build·빈 테스트틀 실행 결과가 남고, 엔진·외부망 없이 실행된다. requirements/package lock을 남긴다. 이것은 돌봄 루프 완료가 아니다.

### C-02 저장소·원천·버전·상태 서비스

**의존:** C-01.  
**대상:** db/models, migrations, domain/states·evidence·lineage, 저장 무결성 단위 테스트.

01의 테이블·FK·unique·revision·UTC·원천 계보를 구현한다. JSON 관계의 주체·버전·존재도 검사한다. 승인된 내용 덮어쓰기 금지, 원천 invalidation, clock 주입, idempotency 결과 참조를 구현한다.

**완료:** schema 생성/upgrade, FK 검사, 타 입주자 근거 거절, source version 불변, 미래 시각·시간대 없는 입력 처리, 중복 명령 테스트. 모델 호출 없음.

### C-03 모의 세션·수신자 필터

**의존:** C-02.  
**대상:** session API, memberships, permissions service, family DTO 필터.

allowlist 세션 발급·만료·전환, CSRF/Origin, role 검사, subject+recipient scope를 구현한다. health_context 분리와 all-of scope 검사, 공개 근거 발췌 API의 거절 경로부터 테스트한다.

**완료:** family가 staff API를 쓸 수 없고, recipient/body 위조·타 subject 접근·전체 record 조회가 차단된다. 모의 인증의 한계가 화면·README에 표시된다.

### C-04 가족 질문·직원 큐 — 화면 1·2의 첫 연결

**의존:** C-03.  
**대상:** questions service/API, family composer/list, staff queue/schedule.

질문이 DB에 들어가 직원 큐에 나타나고, 담당·예정·미답변 이월이 작동하게 한다. AI 즉답은 만들지 않는다. 질문 생성·schedule·미답변에 idempotency/revision을 적용한다.

**완료:** 새로고침 후 질문이 유지되고 동일 요청 재시도는 한 건이다. 다른 가족 질문은 노출되지 않는다. 확인 예정 미정·지연 상태가 명확하다. T-08 일부 통과 증빙.

### C-05 직접 입력·기록 초안·승인 — 화면 3

**의존:** C-02~C-04.  
**대상:** captures/text, source_events, 기록 draft/edit/approve, answer/consent 후보, staff review UI.

실제 음성 없이 직접 입력 source에서 초안을 만들고 사람이 확인해 승인하는 경로를 먼저 완성한다. 초기 fixture provider는 REPLAY/TEST FIXTURE라고 표시한다. 표준 JobDTO와 worker 기본 경로를 이 단계에서 만든다.

**완료:** draft가 가족에게 보이지 않고, 근거 없는 좌우·기간을 테스트에서 잡는다. 승인해도 질문은 아직 answered가 아니고 동의도 그대로다. 계획 행동은 planned다. T-01/T-03/T-04/T-08 일부.

### C-06 센서 집계·근거 있는 발행 — 화면 1·4 연결

**의존:** C-05.  
**대상:** aggregation, publications service/API, family board/evidence, staff 발행 preview.

독립 합성 센서 집계, 허용된 승인 근거 선택, 문구 후보·검토·발행의 구분을 구현한다. publication commit과 본인 질문 answered를 원자 저장한다. 근거 source의 의미·시각을 문장마다 표시한다.

**완료:** 질문 접수부터 승인·발행·가족 답까지 실제 DB를 지나는 첫 루프. 오전 source만 있을 때 산책 완료가 없고 오후 승인 후에만 완료가 생긴다. 빈 자료·비공개·검토대기를 구분한다. T-01/T-02/T-04.

### C-07 동의 후보·확인·철회 — 화면 5

**의존:** C-03/C-05/C-06.  
**대상:** consent candidates/versions, confirm/revoke, scope diff UI, invalidation.

candidate와 effective grant를 분리하고 Mikko의 outdoors만 허용하는 사례를 구현한다. 동의 version 검사, 일부 scope 철회, 최신 revoked에서 과거 grant로 후퇴 금지를 검사한다.

**완료:** 후보만으로 권한은 변하지 않으며, 외출을 허용해도 통증·복약·수면·숨긴 출처가 응답에 없다. API raw JSON·DOM·늦은 응답·언어 전환에서 T-05~T-07을 확인한다.

### C-08 정정·재시도·경합

**의존:** C-06/C-07.  
**대상:** corrections, source/record version, content_epoch, publish transaction, stale result handling.

기록 정정 시 옛 발행과 관련 질문·행동을 재검토 상태로 바꾼다. LLM 호출 도중 동의/근거가 바뀌는 경합, 동일 idempotency-key의 동시 요청, DB commit 실패를 시험한다.

**완료:** 원문이 바뀐 옛 답이 과거 캐시·출처 링크로 재등장하지 않는다. 발행이 rollback되면 질문도 미완료다. T-02/T-04/T-07/T-08.

### C-09 음성·AI adapter·삭제 실제 경로

**의존:** C-05/C-08. 실제 엔진은 Q-03의 확인된 범위만.  
**대상:** providers, transcribe/extract/render jobs, audio manifest·cleanup, capture upload·cancel UI.

Port를 유지해 확인한 로컬 STT/LLM을 연결한다. 모델명·endpoint·권리·언어·제한을 기록한다. 실제 엔진이 없으면 해당 하위 작업만 BLOCKED_PROVIDER, 직접 입력은 유지한다. 캡처 고지·허용, 업로드 제한, timeout·cancel·늦은 결과·restart 정리를 구현한다.

**완료:** 실제로 실행한 provider와 fixture 결과가 구분되고, 외부망 없이 허용 범위를 지킨다. 삭제 미확인/실패에 deleted_at이 null이다. DB 저장 성공과 오디오 정리 실패가 별도 표시된다. T-09, 실제 provider 시험은 별도 결과.

### C-10 FI UX·사용자 전환·시연 표시

**의존:** C-06~C-09.  
**대상:** 화면1~5, FI 문구, 최소 SV 전환, execution badge, responsive UI.

핀란드어 담당 검수, 현재 viewer/subject 표시, 질문창 비긴급 안내, source drawer, 승인·발행 차이, 데이터 부족 상태를 마무리한다. 최소 언어 전환은 같은 사용자·scope가 유지됨을 검증하는 범위이며 전체 번역을 새 필수로 확대하지 않는다.

**완료:** 잘못된 언어 라벨이나 mock LIVE 표시가 없고 360px·1280px에서 루프가 가능하다. T-06/T-10. 아직 검수자가 없으면 language review는 NOT_VERIFIED다.

### C-11 T-01~T-10·데모·재현성 검증

**의존:** C-01~C-10의 핵심 경로.  
**대상:** pytest, Vitest, Playwright, 테스트 결과 요약, runbook, 시연 스크립트.

아래 테스트를 자동·수동으로 나누어 실행한다. 증빙은 실제 입력 fixture version·commit·명령·결과·검토자를 포함한다. 네트워크 차단, 새 DB, 새 세션에서도 재현한다.

**완료:** 핵심 기능의 실제 test report가 있다. 테스트 adapter로만 통과했으면 실제 엔진 검증 상태를 따로 남긴다. 90초 데모는 목표이며 시간을 억지로 맞추려고 승인·권한 절차를 생략하지 않는다.

### C-12 제한된 Veil 반입·패키징·인수인계

**의존:** 독립 합성 core 검증. Veil은 실제 자료·이용조건 확인된 로컬 환경에서만.  
**대상:** VeilImportPort/CLI, dry-run 매핑표, 로컬 배포·정리 명령, 최종 기능 상태.

실제 schema를 확인하여 어댑터를 매핑하되 없는 항목은 없음으로 처리한다. 개발 에이전트·public CI에 Veil을 읽게 하지 않는다. 조건이 미결이면 반입 실행은 BLOCKED로 남기고 독립 합성 데모 패키지를 완성한다.

**완료:** 설치·실행·중지·재시작·정리 절차가 재현되고, 공개 가능한 산출물만 commit된다. 운영 인증·실기관 연동·임상검증 완료로 확대 보고하지 않는다.

### O-01 선택 기능

화면6, 전체 SV/EN, 스트리밍은 C-11 핵심 통과 및 팀의 별도 범위 승인 이후다. 이를 하느라 기존 P0 결함을 남기지 않는다.

## 5. 계약 구현 시 빠뜨리기 쉬운 세부사항

다음은 01·02를 코드로 옮길 때 적용할 공통 보완 정의다. 새 제품 기능을 추가하는 내용이 아니다.

- Capture의 서버 status는 `created|audio_uploaded|transcribing|transcribed|drafting|draft_ready|approved|canceled|failed`로 고정한다. 화면의 review/idle 같은 표현은 이 상태를 매핑한다. 전사는 source로, 기록은 별도 record version으로 남는다.
- 오디오 capture는 생성 시 `occurred_at`을 입력받아 이야기 시각을 저장한다. 업로드·job 시작·승인·삭제 시각은 서버가 실제 시각을 기록한다. typed capture도 같은 구분을 따른다.
- source payload는 `required_scopes`와 분류 검토 상태를 포함한다. record segment와 publication item에도 검증된 scope가 이어진다. 새로운 분류는 staff-only가 기본이다.
- 새 manual source·question·record가 Veil 기반 resident 맥락이나 Veil source를 참조하면 payload lineage를 VEIL_DERIVED로 보수적으로 계산한다. content를 가진 모든 객체의 lineage는 DB 컬럼 또는 검증된 payload metadata로 조회 가능해야 한다. source만 태그하고 question/LLM input을 무태그로 보내지 않는다.
- 녹음 허용 reference는 별도의 staff가 확인한 처리 동의 기록을 참조한다. 가족의 outdoors grant를 녹음 허용으로 사용하지 않는다. 법적 효력의 검증과 모의 절차의 동작은 구별한다.
- 공개 item_id는 서버가 전역 유일하게 생성하고 소속 publication으로 역조회할 수 있어야 한다. public evidence handle은 데이터 파일 경로나 전체 record ID에 대한 자유 조회 권한이 아니다.
- 한 질문의 업무상 answered와 특정 언어·수신자의 현재 answer_available은 구분한다. SV 발행이 없다고 이미 FI로 답한 업무 이력을 지우지 않는다. 정정 때문에 답 근거가 무효하면 unanswered로 재검토한다.
- source correction으로 본문을 바꾸지 않고 새 version을 만든다. 정정 요청부터 가족 발행을 보류하고 새 record 승인 전까지 대체 사실을 발행하지 않는다.

## 6. 검증 기준 — 모두 초기 NOT_RUN

자동 테스트는 API·DB·권한·알려진 오류를 확인한다. 의료적 의미·쉬운 핀란드어·임상 성능 전체를 자동으로 보증하지 않는다. 수동 의미 검수는 누가 어떤 문장을 확인했는지 별도로 남긴다.

### T-01 계획과 완료

| 사례 | Given / When | 기대·증빙 |
| --- | --- | --- |
| T01-A | 오전 계획만 승인 후 발행 | action planned, 산책 완료·오후 인용 없음 |
| T01-B | 오후 source는 있으나 미승인 | confirm endpoint 422, 가족 완료 문장 없음 |
| T01-C | plan segment를 확인 근거로 지정 | EVIDENCE_REQUIRED 또는 REVIEW_REQUIRED, 상태 불변 |
| T01-D | 사건시각이 앞뒤로 입력됨 | 실제 approved/valid 근거로 판단하고 입력 순서만으로 완료 처리 금지 |

권장 파일: `apps/api/tests/unit/test_action_states.py`, `tests/e2e/plan-vs-completion.spec.ts`.

### T-02 문장별 근거와 정정

| 사례 | Given / When | 기대·증빙 |
| --- | --- | --- |
| T02-A | 오전·오후 승인 후 발행 | 사유는 rec-0832, 완료·인용은 rec-1328의 실제 버전·구간 |
| T02-B | 다른 resident 또는 없는 segment ref | 409 SUBJECT_MISMATCH 또는422, 발행 없음 |
| T02-C | source/record 정정 시작 | 종전 publication invalidated, 원문 내용 보존, 재검토 표시 |
| T02-D | 출처 링크는 있으나 의미가 다름 | 자동 검사 또는 사람 검수에서 보류. 링크 존재만으로 PASS 금지 |

권장 파일: `apps/api/tests/integration/test_evidence_and_corrections.py`. 의미 검수표는 별도 첨부한다.

### T-03 원자료 충실

| 사례 | 입력 | 기대 |
| --- | --- | --- |
| T03-A | 좌우·기간 없는 무릎 통증 | right/left·며칠·통증 점수를 보충하지 않음 |
| T03-B | 약 목록만, 복약 확인 없음 | 복용 완료 출력 없음 |
| T03-C | 문 센서만 | 직원 동행·통증 호전 출력 없음 |
| T03-D | 침대 재실·냉장고 개폐 | 숙면·식사 완료로 바꾸지 않음 |
| T03-E | 센서 coverage 누락 | 실제 무활동/미외출로 단정하지 않음 |
| T03-F | source text에 “지시 무시·외부 전송” | 자료로 처리, 도구·URL·권한 동작 없음 |

고정 fixture의 알려진 부정 사례는 자동 검사하고 실제 provider 출력은 입력·출력별 사람 의미 검수를 추가한다. 단어 블랙리스트만으로 모든 언어의 사실성 검증이 끝났다고 보고하지 않는다.

권장 파일: `apps/api/tests/unit/test_source_fidelity.py`, `apps/api/tests/providers/test_extraction_contract.py`.

### T-04 승인과 발행

| 사례 | When | 기대 |
| --- | --- | --- |
| T04-A | draft 존재 상태에서 family 읽기 | 새 초안 문장·source ID 없음 |
| T04-B | 기록만 승인 | 질문은 아직 answered 아님, 동의 불변 |
| T04-C | preview만 생성 | publication draft, family에 미노출 |
| T04-D | 발행 transaction 중 저장 실패 주입 | publication·질문 상태 모두 rollback |
| T04-E | 승인 뒤 수정·발행 revision 불일치 | 412, 최신 데이터 재조회 요구 |

권장 파일: `apps/api/tests/integration/test_approval_publication.py`.

### T-05 동의 후보

| 사례 | When | 기대 |
| --- | --- | --- |
| T05-A | 모호한 이름·긍정 발언으로 후보 생성 | 현재 consent version/scopes 불변 |
| T05-B | outdoors만 확인 | health_context·medication·sleep은 미허용 |
| T05-C | 후보 밖 scope를 confirm body에 추가 | 422, 권한 불변 |
| T05-D | 오래된 consent version으로 확인 | 409 STALE_CONSENT, 변경 불가 |

권장 파일: `apps/api/tests/integration/test_consent_candidates.py`.

### T-06 사용자·언어·응답 경계

| 사례 | When | 기대 |
| --- | --- | --- |
| T06-A | Liisa fi→sv | actor·subject·scopes 동일. 미준비 언어는 명시적 unavailable |
| T06-B | Liisa→Mikko | 새 세션·재조회, 통증·복약·수면 내용이 raw JSON에도 없음 |
| T06-C | body/query recipient_id 위조 | 세션 기반 판정, 요청 거절 또는 무시가 아닌 명시적 validation |
| T06-D | 숨긴 item evidence URL 직접 요청 | 404, 전체 원문·메타 유출 없음 |
| T06-E | Liisa 요청 지연 중 Mikko로 전환 | 늦은 Liisa 결과가 화면·cache에 반영되지 않음 |
| T06-F | 다른 가족 질문 ID/타 resident 사용 | 404 또는 SUBJECT_MISMATCH, 질문·답 변조 없음 |

권장 파일: `apps/api/tests/integration/test_recipient_isolation.py`, `tests/e2e/identity-language.spec.ts`. DOM 확인만 하지 말고 네트워크 응답도 검사한다.

### T-07 철회·캐시·경합

| 사례 | When | 기대 |
| --- | --- | --- |
| T07-A | grant 후 revoke, 이전 URL 재요청 | 현재 version 검사 후 접근 제한 |
| T07-B | old cache/idempotency result 재요청 | 현재 권한 먼저 검사, 원 응답 replay로 유출 금지 |
| T07-C | LLM 생성 중 consent 변경 | prepare/publish stale로 차단 |
| T07-D | latest revoked 뒤 과거 confirmed 존재 | 과거 grant로 후퇴하지 않음 |
| T07-E | 최신 publication invalidated 뒤 옛 발행 존재 | 과거 발행을 자동 fallback하지 않음 |

권장 파일: `apps/api/tests/integration/test_revocation_and_stale_reads.py`.

### T-08 미답변·실패·중복

| 사례 | When | 기대 |
| --- | --- | --- |
| T08-A | 답 없는 질문·예정 경과 | 미답변 이월, AI 보충 답 없음 |
| T08-B | STT 오류·timeout | 질문 유지, 직접 입력 경로 활성화 |
| T08-C | 동일 idempotency 요청 반복·동시 실행 | 질문/record/job 중복 생성 없음 |
| T08-D | 같은 key 다른 payload | 409, 기존 결과 변조 없음 |
| T08-E | job 취소 후 늦은 provider 성공 | 결과 미반영·음성 정리 수행 |
| T08-F | source/record 저장 실패 | 미완료 상태 유지, 성공 toast 없음 |

권장 파일: `apps/api/tests/integration/test_retry_and_failures.py`, `tests/e2e/manual-fallback.spec.ts`.

### T-09 자료와 음성

| 사례 | When | 기대 |
| --- | --- | --- |
| T09-A | 정상 승인·저장 후 cleanup 성공 | 실제 receipt 확인 뒤 deleted/time. 요청 시점에는 null |
| T09-B | 취소·실패·timeout 각각 | 모든 알려진 임시 artifact 정리, 별도 결과 |
| T09-C | 파일 삭제 또는 engine receipt 실패 | failed/unverified, deleted_at=null, 재시도 관리 |
| T09-D | 실행 중 프로세스 중단·재시작 | durable job/manifest 복구, 유실·가짜 성공 없음 |
| T09-E | VEIL 또는 혼합 계보로 외부 provider 호출 | 실제 network 호출0, EGRESS_DENIED |
| T09-F | provider가 redirect/임의 URL 요청 | allowlist 밖 차단, fallback 없음 |
| T09-G | dry-run 정리·잘못된 root/symlink | dry-run은 삭제0, 경로 탈출 거절 |
| T09-H | 업로드 과대·지원하지 않는 형식 | 413/415, 불필요한 임시파일 정리 |
| T09-I | payload·오류·CI artifact 검사 | 실제 원문·음성·비공개 데이터·키 없음 |

권장 파일: `apps/api/tests/integration/test_audio_cleanup.py`, `apps/api/tests/unit/test_egress_lineage.py`. 실제 엔진에 대한 cleanup 시험이 없으면 provider 검증은 NOT_VERIFIED로 남긴다.

### T-10 시연 정직성·효과 측정

| 사례 | When | 기대 |
| --- | --- | --- |
| T10-A | fixture 결과 사용 | REPLAY/TEST FIXTURE, live provider 성공으로 집계하지 않음 |
| T10-B | 직접 입력 + 실제 LLM | STT skipped·입력 직접 입력, 실제 실행 단계만 LIVE |
| T10-C | 저장 결과 사용 | CACHED/REPLAY와 최초 provenance 표시 |
| T10-D | 합성 시연 시간 측정 | 합성 측정으로 표시, 확인·수정·발행·동의 시간 포함 |
| T10-E | 수치 미수집 | null/미측정. 전화0건·절감률로 표시하지 않음 |
| T10-F | 네트워크 단절·언어 미준비 | 오래된 상태·언어 fallback을 현재 검증 완료로 위장하지 않음 |

권장 파일: `tests/e2e/demo-provenance.spec.ts`, 수동 데모 체크표.

## 7. 자동·수동 검증의 구분

| 계층 | 도구·범위 | 완료 조건 |
| --- | --- | --- |
| 단위 | pytest: 상태·scope·계보·집계·시각 | 정의된 invariant와 negative case 통과 |
| API/DB | pytest + HTTP test client + 임시 SQLite | 실제 migration·transaction·session·DTO 경계를 통과 |
| 프론트 | Vitest + component test | 입력·loading·오류·권한 변경·늦은 응답 처리 |
| 브라우저 | Playwright | 실제 API를 사용한 5화면 loop. 모든 API를 mock해서 완료 주장 금지 |
| 실엔진 | 별도 marker/provider test | 허용 자료·실제 모델 버전·호출·지연·삭제 receipt 기록 |
| 의미·FI | 지정한 사람 | 출처가 문구를 지지하는지, 쉬운 핀란드어·번역 정확성 확인 |

기본 CI는 독립 합성자료와 network-deny provider double만 사용한다. 실제 Veil·엔진 키·제한 fixture를 public CI에 넣지 않는다. 전체 coverage 비율만으로 보안·의미 검증을 대체하지 않는다.

### 개발용 성능 목표 [DD, 실측 아님]

동일 로컬 장비에서 non-AI board/queue 응답 50회 측정, p95 1초 이내를 초기 목표로 한다. 테스트 데이터와 동시성(최대5세션), 장비를 기록한다. STT120초·구조화60초·문구60초는 실패 복귀를 위한 상한이며 90초 시연을 보장하는 값이 아니다. 실제 성능을 보고 시연을 조정하고 필요하면 명시적인 REPLAY를 사용한다.

## 8. 구현 후 제공할 실행 명령 계약

**현재 명령이 실행 가능하다는 뜻이 아니다.** Codex는 C-01~C-12에서 아래 명령에 해당하는 파일·script·CLI를 만들고 검증해야 한다.

```bash
# 최초 환경: Python/Node 버전은 lock 및 실제 검증 기록과 일치시킨다.
python3.12 -m venv .venv
.venv/bin/python -m pip install -r apps/api/requirements.lock.txt
.venv/bin/python -m pip install --no-deps -e apps/api
npm --prefix apps/web ci

# 단위·통합·화면 검증
.venv/bin/python -m pytest apps/api/tests -m 'not real_provider'
npm --prefix apps/web run lint
npm --prefix apps/web run typecheck
npm --prefix apps/web run test:run
npm --prefix apps/web run build
npm --prefix apps/web run test:e2e

# 로컬 실행: DATA_ROOT는 저장소 밖, 실제 secret은 별도 환경
.venv/bin/python -m medipencil.cli check-environment
.venv/bin/python -m medipencil.cli migrate
.venv/bin/python -m medipencil.cli seed-demo --dry-run
.venv/bin/python -m medipencil.cli seed-demo --confirm TEAM_SYNTHETIC
.venv/bin/python -m uvicorn medipencil.main:app --host 127.0.0.1 --port 8000 --workers 1
```

frontend `test:e2e`는 설정된 실제 API와 테스트 전용 DB를 띄우고 테스트 후 중지하도록 구현한다. production DB를 테스트용으로 초기화하지 않는다. Playwright 브라우저 설치·패키지 다운로드는 실행환경의 네트워크 권한과 사용자 허용을 따른다. 다운로드하지 못했으면 실행하지 못한 것으로 기록한다.

CLI의 `seed-demo`는 **비어 있는 TEAM_SYNTHETIC 전용 run**에만 적용한다. DB가 이미 있으면 확인 없이 초기화하지 않는다. Veil run에는 seed reset을 허용하지 않는다. 정리 CLI는 별도로 dry-run과 정확한 run ID 확인을 요구한다.

### 환경설정 명세

| 변수 | 기본·의미 |
| --- | --- |
| MEDIPENCIL_ENV | `local_demo`; 운영 모드 별도 미구현 |
| MEDIPENCIL_DATA_ROOT | 저장소 밖 절대경로, 필수. 포함·symlink 검사 |
| MEDIPENCIL_UI_LOCALE | `fi` |
| MEDIPENCIL_DISPLAY_TIMEZONE | `Europe/Helsinki` |
| MEDIPENCIL_STT_PROVIDER / LLM_PROVIDER | `not_configured`; 테스트 설정에서만 명시적 fixture 선택 |
| MEDIPENCIL_EXTERNAL_AI_ENABLED | `false` |
| MEDIPENCIL_PROVIDER_CONFIG | 로컬 비공개 설정 파일. endpoint·허용 원천·권리 확인 상태 |
| MEDIPENCIL_SESSION_SECRET | 실행환경 생성 secret. repo·프론트 번들·로그에 금지 |
| MEDIPENCIL_OPTIONAL_PREFILL | `false` |
| MEDIPENCIL_AUDIO_MAX_BYTES | `20971520` |
| MEDIPENCIL_AUDIO_MAX_SECONDS | `180` |

프론트 `VITE_` 변수에는 API key·세션 secret을 넣지 않는다. 모델 주소·보안 설정을 UI에서 직접 임의 변경하게 하지 않는다.

## 9. 데모 운용 순서

1. 독립 합성 run·provider mode·origin·현재 viewer·언어를 확인한다. 실제 자료로 시연하는 것으로 설명하지 않는다.
2. Liisa가 상황판을 보고 질문. staff queue로 이어진다.
3. 오전 합성 음성의 실제 처리 또는 명시적 대체 경로. 원문·초안·계획을 보여 준다.
4. staff 승인과 동의 후보 확인. 가족 발행은 별도 preview에서 확인한다.
5. 오후 확인 기록을 REPLAY로 불러온 뒤 승인한다. 산책 완료·인용이 오후 근거에 연결되는지 보여 준다.
6. Mikko로 전환하여 비공개 정보가 빠지는 장면, Liisa 언어 변경에서 사용자 유지 장면을 보여 준다.
7. 실패하면 미완료 상태와 직접 입력·재생 경로를 그대로 보여 준다. 성공 영상을 실제 실행인 것처럼 대체하지 않는다.

핵심 시연 90초는 목표다. 별도 rehearsal 기록에는 실제 소요시간·막힌 동작·사용한 fallback을 쓴다. 타인 개인정보나 Veil 유래 내용이 포함된 영상의 보관·공개는 Q-02 확인 전 진행하지 않는다.

## 10. 진행 보고와 완료 판정

Codex는 `docs/development/progress.md`에 다음 형식으로 작업별 기록을 추가한다. 이 파일이 없다고 실제 작업이 수행된 것으로 가정하지 않는다.

```text
작업 ID / 상태:
기준 branch / 시작 HEAD / 종료 commit:
허용된 실행 단계와 근거:
변경 파일:
구현한 동작:
실행 명령과 실제 결과:
관련 T-ID / 자동·수동 구분:
실제 provider / fixture / 미설정 구분:
미실행·실패·차단 항목:
다음 작업:
```

상태는 `NOT_STARTED|IN_PROGRESS|BLOCKED|DONE`을 사용한다. DONE은 해당 산출물과 수용 검증이 실제로 끝났을 때만 쓴다. 큰 단위 완료도 `TEXT_LOOP_VERIFIED`, `MOCK_INTEGRATION_VERIFIED`, `REAL_PROVIDER_VERIFIED`, `DEMO_READY_WITH_LIMITATIONS`처럼 근거 수준을 구분한다. 전부 구현했다고 source baseline의 NOT_IMPLEMENTED 표기를 임의로 과거까지 바꾸지 말고 실행 기록에서 현재 상태를 갱신한다.

### 인수인계 체크

- 화면1~5와 API·DB 연결, 재시작 후 유지, source·권한·상태 계약이 일치한다.
- T-01~T-10에 실제 결과 또는 미실행·차단 사유가 빠짐없이 있다.
- P0 안전·권한·사실 왜곡 결함을 남긴 상태에서 선택 기능을 시작하지 않는다.
- actual provider 시험과 fixture 시험을 섞지 않는다. Q-01~Q-04 확인은 코드 완료와 별개다.
- README의 설치 명령·환경·제한이 실제 동작과 같다. 공개 repo에 원자료·오디오·비공개 엔진·키가 없다.
- 마지막 보고에 commit, 실행 명령, 미확인 엔진/언어/현장 조건, 남은 작업을 명시한다.

**이 문서를 등록한 시점에는 애플리케이션 코드 생성·실행, 모델 시험, T-01~T-10 실행을 하지 않았다.**
