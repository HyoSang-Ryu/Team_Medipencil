# MediPencil 상세설계 및 개발명세 — 01. 아키텍처·도메인·저장 계약

문서 ID: MP-PK-DEV-001 / 개발명세 버전: 1.0 / 작성일: 2026-10-02  
제품 설계 기준: **Päivän kuulumiset 최종 설계안 v1.1**  
상태: **SPEC_READY / 애플리케이션 NOT_IMPLEMENTED / 통합검증 NOT_RUN**

[개발명세 시작점](README.md) · [API·화면·AI](02-api-ui-ai-spec.md) · [Codex 작업·검증](03-codex-tasks-and-tests.md)

## 1. 기준과 해석

### 1.1 직접 대조한 기준본

- [최종 설계안 v1.1](../design/medipencil-final-design-v1.1.md): §3~9, §12, §15, 별첨 D.
- [v1.1 확정 기록](../design/finalization-v1.1.md).
- 대조 시 저장소 HEAD: `9437e5cead05663bc575739301997a75750fef80`.
- v1.1 Markdown blob: `f13a3b9732c1490cdff7f3c9b52dbc474538a03a`.

이 문서는 v1.1을 대체하지 않고 구현 수준으로 구체화한다. 문서에서 **[B]는 기준본에서 계승한 요구**, **[DD]는 이번 명세에서 정한 개발 선택**, **[OPEN]은 외부·팀 확인이 필요한 사항**이다. API, DB 필드, 시간제한, 라이브러리 조합은 [DD]이며 기존 시스템의 검증된 사실이나 주최 측의 추가 요구가 아니다. 공식 규정과 엔진은 이번 명세 작성에서 재검증하지 않았다.

충돌 우선순위는 사용자 승인된 범위·안전 경계 → v1.1의 수정된 계약 → 본 개발명세 → 예시·목업이다. v1.0에 있던 `answered: true`, `deleted_at: on_approve_or_cancel`, 근거 없는 좌우·기간 표현으로 되돌리지 않는다. 해결되지 않는 충돌은 해당 작업만 `BLOCKED_SPEC_CONFLICT`로 남긴다.

### 1.2 범위 고정 [B]

핵심은 **가족 질문 → 직원 질문 큐 → 돌봄 대화 → 수정·승인 기록 → 근거·권한을 적용한 가족 답변**이다. 화면 1~5, 6칸 상황판, 기본 쉬운 핀란드어, 권한 보존을 확인하는 최소 언어 전환을 구현한다.

화면 6 사전문진, 전체 SV/EN 번역, 실시간 스트리밍 전사는 핵심 통과 후 선택이다. 병동 회진·퇴원 서비스, 자율 의료 판단, 자동 긴급도 분류, 범용 챗봇, 실 EMR 쓰기, 상용 인증·예약·푸시, 벡터DB·모델 학습·다중 에이전트는 필수 범위가 아니다.

### 1.3 개발 선택 기록 [DD]

| ID | 이번 명세의 선택 | 이유·경계 |
| --- | --- | --- |
| DD-01 | Python 3.12 + FastAPI + Pydantic 2 + SQLAlchemy 2 + Alembic | 기준본의 FastAPI/Node 후보 중 기본 구현 경로를 하나로 정함. 기존 음성 엔진의 기술 스택을 확정하는 것은 아님 |
| DD-02 | SQLite 파일 1개, API 프로세스 1개, 프로세스 내 작업 실행기 1개 | 짧은 현장 개발·로컬 실행 우선. Redis/Celery/분산 DB 불필요 |
| DD-03 | React + TypeScript + Vite, npm, React Router, TanStack Query | 기준본 React SPA 유지. Node 22.12 이상 22.x를 초기 재현성 목표로 하되 실제 선택 패키지와 호환 시험 후 lockfile 고정 |
| DD-04 | 동일 출처 UI/API, HTTP JSON, 작업상태 polling | WebSocket 없이도 MVP 구현. 개발 중 Vite proxy, 배포형 시연에서는 빌드된 UI를 API에서 제공 |
| DD-05 | 모의 엔진·직접 입력과 실제 엔진을 동일 포트로 분리 | 실제 엔진 API·권리·핀란드어 성능은 Q-03. 모의 성공을 실제 AI 성공으로 보고하지 않음 |
| DD-06 | 기록 승인과 가족 문구 발행을 별도 명령·트랜잭션으로 분리 | 승인된 기록도 자동 공개하지 않음. 직원은 같은 화면에서 연속 처리 가능 |
| DD-07 | DB에 원천·승인 버전, JSON payload, 역참조 가능한 근거 목록 저장 | 과도한 테이블 분할을 피하면서 불변 버전·권한 검증 유지 |
| DD-08 | 내용 변경 epoch와 동의 version을 이용한 보수적 결과 무효화 | 의미가 바뀐 옛 답을 재사용하지 않음. 무효화 후 이전 답으로 자동 후퇴 금지 |
| DD-09 | 로컬 모의 세션으로 역할·입주자 접근 검사 | 상용 인증 아님. 기본 loopback 전용, 외부 공개 배포 금지 |
| DD-10 | 모델명·상용 서비스·비공개 엔진 endpoint는 설정 전까지 미정 | D-06·Q-02·Q-03은 닫지 않음. API 실패 시 임의의 외부 서비스로 우회 금지 |

라이브러리의 정확한 패치 버전은 Codex가 설치 단계에서 호환 시험 후 lockfile에 기록한다. `latest`만 적고 재현 가능한 버전을 남기지 않는 설치는 완료로 보지 않는다. 기존 구현이 추후 생겼다면 삭제·재생성하지 말고 차이를 먼저 보고한다.

## 2. 실행 구조

```text
브라우저: 가족 / 직원 / 모의 동의 관리
  └─ 같은 출처 /api/v1
       ├─ 세션·입주자 접근 검사
       ├─ 질문·기록·행동·동의 명령 서비스
       ├─ 발행 서비스: 권한 선택 → 문구 후보 → 사람 확인 → 저장
       ├─ 가족 읽기 서비스: 현재 권한·근거 재검사 → 제한 DTO
       ├─ 작업 실행기: 전사 / 구조화 / 문구 생성 / 음성 정리
       └─ SQLite + 저장소 밖 제한 작업영역
             └─ ProviderPort → 모의 / 직접 입력 / 검증한 로컬 엔진
```

### 2.1 개발 대상 디렉터리 [DD]

아래는 **Codex가 허용된 구현 단계에서 만들어야 할 구조**다. 현재 실행 파일이 존재한다는 뜻이 아니다.

```text
apps/api/
  pyproject.toml
  migrations/
  src/medipencil/
    main.py
    config.py
    api/{session,family,staff,captures,records,consents,publications,jobs}.py
    schemas/{common,question,record,consent,publication,provider}.py
    domain/{states,evidence,permissions,lineage}.py
    services/{questions,records,actions,consents,publishing,board,audio}.py
    db/{models,session,repositories}.py
    providers/{base,fixture,manual,local_stt,local_llm}.py
    workers/{jobs,cleanup}.py
    cli.py
  tests/{unit,integration,providers}/
apps/web/
  package.json
  src/
    app/{router,session,query-client}.tsx
    features/{family,staff,capture,consent,publication}/
    components/{Tile,EvidenceDrawer,StatusBadge,ExecutionBadge}.tsx
    api/{client,types}.ts
    i18n/{fi,sv,en}.json
  tests/
tests/e2e/
docs/development/
docs/evidence/           # 실행 후 승인된 독립 합성 테스트 요약만
```

환경, 실제 데이터, 오디오, DB, 브라우저 trace, 모델 파일은 저장소 밖 `MEDIPENCIL_DATA_ROOT`에 둔다. 프론트 빌드에 테스트 fixture 전체를 포함하지 않는다. 세부 파일명 변경은 기능과 테스트 대응을 유지하는 범위에서 작업 보고에 기록한다.

### 2.2 모듈 책임

| 모듈 | 책임 | 금지 |
| --- | --- | --- |
| API route | 인증 맥락, DTO 검사, 명령 호출, 오류 변환 | route 안에서 원문 임의 조합·권한 우회 |
| domain | 상태 전이, 근거 유효성, 공개 범위, 계보 규칙 | HTTP 호출·LLM 호출·전역 DB 접근 |
| service | 트랜잭션·권한·revision·감사·중복 요청 관리 | LLM 결과를 곧바로 승인·발행 상태로 저장 |
| provider | 전사·구조화·표현 후보 생성 | 동의 변경, 임의 URL 접근, shell/SQL 실행 |
| worker | 작업 상태·취소·기한·재시도·정리 | 취소된 작업의 늦은 결과 반영 |
| family DTO | 수신자에게 허용된 현재 결과만 직렬화 | 원시 record JSON, 숨긴 문장, 내부 오류 포함 |

LLM을 기다리는 동안 DB 쓰기 트랜잭션을 잡지 않는다. 입력 snapshot을 저장하고 외부 작업 후 다시 revision·동의·근거를 검사한다.

## 3. 공통 타입과 불변 조건

### 3.1 타입

- ID: 서버가 생성하는 불투명 문자열. 실제 객체는 UUID 기반을 기본으로 하고 `rec-0832` 같은 이름은 문서용 fixture alias로 쓴다. 이름·방 번호는 식별키나 권한이 아니다.
- 시각: RFC 3339로 offset 포함. DB에는 UTC로 정규화한 TEXT, API는 `Z` 또는 명시적 offset. UI는 `Europe/Helsinki`로 변환한다.
- `occurred_at`: 이야기 속 관찰 시각. `recorded_at`, `created_at`, `approved_at`, 감사시각: 해당 행위를 실제 서버가 저장한 시각. 합성 데모 재생은 `scenario_at`으로 별도 표시하고 감사시각을 과거로 조작하지 않는다.
- `version`: 불변 원자료·기록의 내용 버전. `revision`: 편집·상태 동시성 제어용 양의 정수. `content_epoch`: 입주자에게 발행 가능한 근거 묶음의 변경 번호.
- `lang`: `fi|sv|en`. 언어와 actor는 별개다.
- `data_origin`: `VEIL|VEIL_DERIVED|TEAM_SYNTHETIC`. 분류가 불명확하면 세 값 중 임의로 고르지 말고 반입을 거절한다.
- `integration_mode`: `MOCK_INTEGRATION|FILE_IMPORT|ENGINE_INPUT|MANUAL_INPUT`. 이는 [DD] 처리 방식 열거이며 원천의 이용 제한을 바꾸지 않는다.
- JSON 컬럼은 Pydantic으로 검증한다. 외부·LLM 입력은 알려지지 않은 필드를 거절한다. 읽기 DTO는 저장 객체와 별도로 정의한다.

### 3.2 반드시 유지할 불변 조건

| ID | 계약 |
| --- | --- |
| INV-01 | 모든 질문·근거·행동·동의·발행은 동일한 `subject_id` 범위 안에서만 연결한다 |
| INV-02 | 원자료와 승인 기록은 버전 고정. 수정은 새 버전이며 옛 출처를 새 내용으로 덮어쓰지 않는다 |
| INV-03 | 승인 전 초안은 가족에게 내려가지 않는다. 승인과 발행은 다르다 |
| INV-04 | 질문 `answered`는 유효한 승인·권한·발행·저장이 모두 성립한 서버 명령의 결과다 |
| INV-05 | `planned`만 있는 행동에서 완료 문장·완료 후 인용을 만들지 않는다 |
| INV-06 | 문구의 모든 사실·인용은 허용된 현재 근거로 설명 가능해야 한다. 링크 존재만으로 통과하지 않는다 |
| INV-07 | 공개 문장에 필요한 모든 scope가 현재 수신자에게 있어야 한다. 일부 scope만 있으면 문장 전체를 제외한다 |
| INV-08 | 동의 후보, LLM 판단, 언어 변경은 공개 권한을 변경하지 않는다 |
| INV-09 | 삭제 요청·실패·미확인 상태에서 `deleted_at`을 채우지 않는다 |
| INV-10 | 원천에 VEIL 내용이 섞인 파생 결과는 VEIL_DERIVED로 추적한다 |
| INV-11 | LIVE/REPLAY/CACHED와 단계별 실제 처리방식을 서버가 기록하며 클라이언트가 성공 이력을 꾸미지 않는다 |
| INV-12 | 정정·철회 후 유효하지 않은 결과를 옛 캐시·출처 링크·지연 응답으로 재노출하지 않는다 |

## 4. 데이터베이스 명세 [DD]

### 4.1 공통 저장 규칙

SQLite 연결마다 `PRAGMA foreign_keys=ON`을 확인한다. 로컬 파일에서 WAL을 사용할 수 있지만 DB·`-wal`·`-shm`은 모두 동일 제한 작업영역에 둔다. schema migration은 Alembic으로 관리한다. `create_all()`만으로 운영 스키마 변경을 대신하지 않는다.

아래 `id`는 TEXT, `n`은 INTEGER, `ts`는 UTC TEXT, `json`은 검증된 JSON TEXT다. `?`는 nullable이다. 별도 표시 없는 필수 컬럼은 NOT NULL이다. `created_at`·`updated_at`·`revision>=1`은 변경 가능한 업무 행에 공통으로 포함한다. JSON 내부 관계도 service에서 존재·버전·주체를 검사한다.

### 4.2 테이블 계약

| 테이블 | 필수 컬럼 | PK·관계·추가 제약 |
| --- | --- | --- |
| units | unit_id, name, contact_config_json, contact_verified_by?, contact_verified_at? | PK unit_id. 검증되지 않은 연락처를 실제 시설 연락처로 표시 금지 |
| actors | actor_id, role, display_name, active | PK actor_id. role=`family|staff|demo_admin`. demo_admin은 운영 권한이 아닌 시연 관리자 |
| residents | subject_id, unit_id, display_name, room_label?, care_order, content_epoch, data_origin | PK subject_id, FK unit_id. room_label은 UNIQUE 식별키가 아님 |
| access_memberships | subject_id, actor_id, can_ask, can_review, can_manage_consent, active | PK(subject_id,actor_id), 양쪽 FK. 가족 관계와 내용 scope는 별도 검사 |
| demo_sessions | session_hash, actor_id, csrf_hash, expires_at | PK session_hash. 원 token은 DB에 저장하지 않음 |
| source_events | source_id, version, subject_id, source_type, occurred_at, recorded_at, data_origin, integration_mode, payload_json, source_refs_json, valid, invalidated_at? | PK(source_id,version), FK subject_id. content는 불변, valid만 통제된 무효화에서 변경 |
| captures | capture_id, subject_id, actor_id, input_mode, status, source_refs_json, audio_ref?, disclosure_ack_at?, recording_permission_ref?, error_code? | PK capture_id. audio_ref는 불투명 파일 참조이며 URL·원경로가 아님 |
| processing_jobs | job_id, subject_id, job_type, status, target_id, expected_revision, input_refs_json, result_ref?, provider_id?, execution_meta_json, deadline_at, canceled_at?, error_code? | PK job_id. 재시작 시 실행 중이던 작업을 무작정 성공 처리하지 않음 |
| record_versions | record_id, version, subject_id, capture_id?, status, segments_json, reviewed_by?, approved_at?, supersedes_version?, correction_reason? | PK(record_id,version), FK subject_id. status=`draft|approved|superseded|withdrawn`. approved에는 검토자·승인시각 필수 |
| family_questions | question_id, subject_id, recipient_id, text, assigned_to?, status, review_due?, active_publication_id?, status_reason? | PK question_id, FK subject_id·recipient_id·assigned_to. recipient_id는 로그인한 가족 actor |
| answer_candidates | candidate_id, question_id, record_id, record_version, answer_segment_ids_json, review_status, reviewed_by?, reviewed_at? | PK candidate_id, FK question 및 복합 FK record. 답변 본문은 근거와 버전으로 추적 |
| care_actions | action_id, subject_id, description, status, planned_in_json, confirmed_in_json?, review_required | PK action_id. confirmed에는 유효한 승인 근거 필수. planned와 confirmed 참조의 subject 일치 |
| consent_candidates | candidate_id, subject_id, recipient_id?, proposed_scopes_json, utterance_ref_json, disposition, reviewed_by?, reviewed_at? | PK candidate_id. disposition=`pending|accepted|rejected`. 수신자가 불명확하면 recipient_id=null, 확인 전 해소 |
| consent_versions | consent_id, version, subject_id, recipient_id, status, scopes_json, confirmed_by, confirmed_at, revoked_at?, evidence_ref_json, derived_from_candidate_id? | PK(consent_id,version), UNIQUE(subject_id,recipient_id,version). effective status=`confirmed|revoked`. 최신 버전 하나만 현재 권한 |
| publications | publication_id, subject_id, recipient_id, lang, revision, status, consent_version, content_epoch, items_json, answer_bindings_json, input_refs_json, generation_meta_json, reviewed_by?, published_at?, invalidated_at?, invalidation_reason? | PK publication_id. status=`draft|published|invalidated`. 읽을 때 현재 권한·epoch·근거 재검사 |
| audio_cleanup_jobs | cleanup_id, capture_id, artifact_refs_json, deletion_status, deleted_at?, trigger, attempts, next_retry_at?, receipts_json | PK cleanup_id, FK capture. trigger=`saved|cancel|failure|timeout|startup_recovery`. 결과는 서버·엔진 기록 |
| audit_events | audit_id, actor_id?, action, subject_id?, object_id, object_version?, timestamp, outcome, request_id, reason_code? | PK audit_id. payload·전사·음성·질문·LLM prompt·토큰 저장 금지 |
| idempotency_keys | actor_id, route_key, request_key, request_digest, object_ref_json?, result_status?, state, expires_at | PK(actor_id,route_key,request_key). 원 요청·원 응답 본문은 저장하지 않음 |

SourceEvent·ApprovedRecord·FamilyQuestion·CareAction·CardItem·Consent·AuditEvent의 이름과 의미는 v1.1을 계승한다. `CardItem`은 MVP에서 `publications.items_json` 안의 DTO로 저장한다. v1.1의 Consent 후보는 후보 테이블로, 확인·철회는 버전 테이블로 나눈 **물리 저장 선택**이며 동의 절차의 의미 변경이 아니다.

### 4.3 인덱스와 무결성

- `family_questions(subject_id,status,review_due,created_at)` 및 `(recipient_id,subject_id,created_at)`.
- `source_events(subject_id,occurred_at)`; `record_versions(subject_id,status,approved_at)`.
- `publications(subject_id,recipient_id,lang,status,published_at)`; `consent_versions(subject_id,recipient_id,version)`.
- `processing_jobs(status,deadline_at)`; `audio_cleanup_jobs(deletion_status,next_retry_at)`.
- 질문·기록·행동 삭제는 일반 API에 제공하지 않는다. 정정·철회는 버전·감사로 처리한다. 행사 후 제한 데이터 정리는 별도 승인된 도구다.
- `record_versions.status='approved'`이면 `reviewed_by`·`approved_at`이 null일 수 없다.
- `audio_cleanup_jobs.deletion_status='deleted'`와 `deleted_at IS NOT NULL`은 함께 성립한다. 미확인·실패는 null이다.
- `consent_versions`에서 최신 revoked를 발견하면 이전 confirmed로 되돌아가 조회하지 않는다.
- 가족 질문과 답변 후보의 record.subject_id가 다르면 transaction 전체를 거절한다. JSON 참조여서 FK만으로 보장되지 않는 부분은 별도 검증한다.
- source_refs의 순환, 없는 버전, 타 입주자 근거, invalid 근거를 거절한다. 소규모 MVP에서는 근거 JSON을 조회해 역의존성을 찾는 방식으로 충분하다. 별도 그래프 DB는 도입하지 않는다.

## 5. 상태 전이 명세

### 5.1 가족 질문 [B + DD 전이 조건]

| 현재 → 다음 | 수행 주체·조건 |
| --- | --- |
| 없음 → received | 허용된 가족이 질문 저장. AI 답변 호출 없음 |
| received/unanswered → scheduled | 직원이 담당자·실제 확인 예정 시각을 저장 |
| received/scheduled → unanswered | 직원이 답 없음 표시, 또는 확인 예정이 지났음을 서비스가 평가. 행은 남김 |
| received/scheduled/unanswered → answered | 승인된 답변 후보가 포함된 해당 가족의 문구를 사람이 발행하고 DB commit 성공 |
| answered → unanswered | 정정으로 답의 근거가 무효화된 경우. `status_reason=evidence_invalidated`, 과거 감사는 유지 |

동의 철회는 과거에 답했다는 행위를 지우지 않는다. `status=answered`의 업무 이력은 유지하되 가족 DTO의 `answer_available=false`, `display_state=access_changed`로 내용 접근을 막는다. 근거 정정으로 답 자체가 무효인 경우와 구분한다. 일반 PATCH로 answered를 지정할 수 없다.

답변 완료는 메시지를 실제로 읽었다는 뜻이 아니다. READ receipt는 MVP 범위 밖이다. 부분 문구만 허용되어 질문에 대한 본질적 답이 빠지면 그 후보를 완료로 처리하지 않는다.

### 5.2 기록·행동

`draft`는 수정 가능하지만 revision을 증가시킨다. 승인 명령은 명시적 검토 결과와 expected revision을 요구한다. 승인 버전은 내용 불변이다. 정정 요청은 새 draft version을 만들고 옛 승인 버전에 연결된 결과를 즉시 보류한다. 승인하기 전의 새 draft로 옛 문장을 대체하지 않는다.

행동은 승인된 계획 근거가 있어야 planned로 등록된다. 확인 명령은 후속 승인 기록의 observation/statement 등 실제 수행을 지지하는 구간과 직원의 의미 확인을 요구한다. 단순 plan 구간이나 센서 신호만으로 confirmed가 될 수 없다.

확인 근거가 정정·철회되면 `review_required=true`, 현재 실행확인 표시를 중단한다. 현재 유효한 확인이 없으면 planned로 되돌리되 화면은 “실행 확인 근거 재검토”라고 표시한다. 이는 과거 행동이 일어나지 않았다는 판단이 아니다. 원 상태 변화는 audit에 남긴다.

### 5.3 동의

후보는 `pending → accepted/rejected`. 후보 추가는 기존 유효 consent version을 바꾸지 않는다. 직원이 입주자·수신자·항목·발언을 확인한 뒤에만 새 effective version을 만든다.

허용 추가는 기존 scopes와 확인한 항목의 합집합이다. 제거는 별도 revoke 명령으로 명시한다. 확인 화면이 보이지 않은 항목을 암묵적으로 추가·제거하지 않는다. 전부 제거되면 revoked, 일부가 남으면 새 confirmed version에 남은 scopes를 저장한다.

녹음 허용은 가족 공개 동의와 별도다. `recording_permission_ref`와 고지 확인은 capture에 연결하고 family scopes를 녹음 허용으로 사용하지 않는다. 법적 효력은 Q-03·Q-04 및 파일럿 검토 대상이다.

### 5.4 발행·작업·삭제

- publication: `draft → published → invalidated`. 무효화된 발행을 되살리지 않고 새 발행을 만든다.
- job: `queued → running → succeeded|failed|canceled`. deadline 이후 늦게 도착한 결과는 버리고 필요한 음성 정리를 수행한다.
- audio deletion: `unverified → deleted|failed`; `failed → deleted`는 재시도 성공 근거가 있을 때만.
- 직접 입력 경로에는 오디오 삭제 객체가 없을 수 있다. 이때 `audio_applicable=false`로 표시하고 가짜 deleted 행을 만들지 않는다.

## 6. 트랜잭션·동시성·재시도

### 6.1 공통 명령 계약

상태 변경 요청에는 `Idempotency-Key`를 요구한다. 128자 이하 불투명 키, 동일 actor·route에서 동일 payload 재시도는 하나의 작업만 만든다. 다른 payload로 같은 키를 쓰면 409이다. digest는 정규화 payload의 서버 keyed digest로 저장하고 원문을 복제하지 않는다.

기존 객체 변경에는 `If-Match: "<revision>"`를 요구한다. 없으면 428, 다르면 412. 사용자는 최신 상태를 다시 읽고 판단한다. Codex는 충돌을 무한 retry 또는 마지막 쓰기 승리로 숨기지 않는다.

동일 요청의 과거 결과를 돌려줄 때도 **현재 actor·입주자 접근권한을 먼저 검사**한다. 과거 응답 본문을 그대로 재생하지 않고 object ref로 현재 허용 DTO를 만든다. idempotency는 권한 검사를 우회하는 캐시가 아니다.

### 6.2 기록 승인 트랜잭션

1. 직원의 can_review, subject 일치, draft revision·source 유효성 검사.
2. 각 구간 화자·유형·근거와 답변 후보의 의미 검토 결과 확인. 모호한 scope는 발행 대상으로 제외.
3. record를 approved로 저장하고 검토자·시각 기록. 수용된 후보를 accepted로 변경. 계획 행동 등록은 승인된 plan 근거만 사용.
4. `resident.content_epoch` 증가, 영향을 받는 기존 publication 무효화, 관련 감사·정리 작업 행 생성.
5. DB commit 성공 후 음성 정리 실행. **삭제 실패가 승인 저장 성공을 거짓 실패로 바꾸거나, 승인 실패가 삭제 성공처럼 표시되지 않게 한다.**
6. 질문은 아직 answered가 아니다. 동의 후보도 자동 적용하지 않는다.

외부 음성 삭제와 DB commit은 하나의 원자 트랜잭션이 아니다. durable cleanup job을 두어 재시작 후 회복한다. 승인 저장 자체가 실패하면 rollback하고 별도의 failure cleanup 경로를 실행한다. 저장 실패를 숨기고 가족 발행으로 진행하지 않는다.

### 6.3 문구 준비·발행 트랜잭션

문구 준비는 직원에게만 허용한다. 대상 recipient를 한 명 정하고 현재 consent·epoch를 읽는다. 허용된 근거만 선택하여 provider에 전달한다. 결과는 draft publication으로 저장한다. LLM 호출 중 변경이 있었으면 새 snapshot으로 다시 준비한다.

발행은 다음을 **하나의 짧은 DB 쓰기 트랜잭션**으로 처리한다.

1. 직원 역할, revision, consent version, content epoch, 모든 근거의 현재 유효성을 재검사.
2. 문구별 source 지지·scope·언어·계획/완료 검토표 확인. 수정된 문장은 다시 검토.
3. publication을 published로 저장. 이전 동일 recipient/lang snapshot은 최신 조회 대상에서 제외.
4. 포함된 accepted 답변 후보 중 **그 수신자 본인의 질문이며 답의 근거가 충분한 것만** answered로 갱신.
5. audit와 idempotency result ref를 저장하고 commit. 중간 오류 시 모두 rollback.

미발행 draft가 생긴 것은 이전의 유효한 published 결과를 자동 삭제하지 않는다. 다만 근거·epoch·동의가 변한 이전 결과는 읽을 수 없다. 발행 실패 시 성공 toast나 answered를 먼저 표시하지 않는다.

### 6.4 철회·정정과 읽기의 경합

동의 변경은 해당 pair의 최신 version 증가와 관련 publication 무효화를 같은 트랜잭션에서 수행한다. 승인된 source 변경은 해당 resident content_epoch를 증가시키고 의존 발행을 무효화한다. MVP는 영향을 세밀하게 계산하지 못하면 그 입주자의 발행 전체를 보류하는 보수적 방법을 허용한다.

가족 읽기는 같은 DB 읽기 snapshot에서 membership, 최신 consent, epoch, publication, 근거 유효성을 검사한다. 이미 commit된 철회보다 먼저 생성한 스냅샷을 나중 요청에 재사용하지 않는다. 취소할 수 없는 이미 전송된 정보는 회수했다고 주장하지 않는다.

기존 최신 발행이 invalidated면 더 오래된 발행으로 자동 후퇴하지 않는다. 고정 6개 항목의 제목과 “새 확인을 기다리는 중” 같은 중립 상태만 반환한다. 출처 ID·숨겨진 내용·개수는 제외한다.

## 7. 권한 상세

### 7.1 scope 계약 [DD]

고정 UI 항목은 `meals, medication, movement, outdoors, sleep, care_contact`다. 공개 판단을 위해 **내부 scope `health_context`**를 추가한다. 이는 일곱 번째 UI 기능이 아니라 무릎 통증 등이 외출 항목을 통해 새는 것을 막는 분류키다.

- 문장 `required_scopes`는 의미와 모든 근거의 scope 합집합이다. 직원이 확인한 source/segment의 태그를 기반으로 서버가 계산한다.
- “무릎이 아파 밖에 나가지 않았다”는 최소 `health_context + outdoors`를 요구한다.
- “출입문 기록 13:05–13:25”는 `outdoors`만 요구한다.
- LLM이 `required_scopes=[outdoors]`라고 출력해도 서버의 원천 태그를 낮출 수 없다.
- 하나의 source 구간이 복합 민감정보이면 구간 전체를 제외하거나 검토된 하위 구간으로 분리한다. 단순 단어 가리기를 안전한 익명화로 취급하지 않는다.
- 분류가 미확정된 근거는 staff-only로 두고 발행을 차단한다.

### 7.2 역할 매트릭스

| 기능 | family | staff | demo_admin |
| --- | --- | --- | --- |
| 가족 상황판·본인 질문 | 자기 pair만 | 별도 staff preview로만 | 시연 세션을 family로 전환 후 사용 |
| 질문 등록 | membership.can_ask + 자기 actor | 대신 질문 생성은 MVP 제외 | 기본 불가 |
| 직원 큐·원문·초안 | 불가 | 해당 resident can_review | 기본 불가 |
| 기록 승인·행동 확인·발행 | 불가 | can_review | 기본 불가 |
| 동의 후보 확인·철회 | 불가 | can_manage_consent | 기본 불가 |
| 시연 fixture 초기화 | 불가 | 불가 | 독립 합성 DB, 명시적 확인 때만 |

가족이 자신의 질문을 볼 수 있다는 이유로 다른 가족의 질문·답을 볼 수는 없다. 직원 preview는 대상 recipient·scope를 표시하고 실제 family endpoint와 동일한 필터 함수를 호출한다.

### 7.3 모의 세션의 한계와 경계

로컬 시연에서만 allowlist actor를 골라 서버가 임시 불투명 세션을 발급한다. 이후 가족 요청의 recipient는 세션에서 가져오며 body/query의 actor ID를 신뢰하지 않는다. 쿠키 HttpOnly·SameSite, 상태 변경 CSRF token·Origin 검사, 세션 만료·사용자 전환 시 토큰 회전을 적용한다.

모의 세션 발급이 존재하므로 이것은 실제 인증이 아니다. 기본 API/UI bind는 `127.0.0.1`, CORS wildcard 금지, Host allowlist, 공개 터널 금지다. LAN·실운영 공개가 필요하면 별도 접근통제 설계와 사용자 승인을 받는다. 사용자 전환 테스트용 기능을 숨기는 것만으로 운영 보안이 완성됐다고 주장하지 않는다.

### 7.4 출처와 캐시

가족은 전체 전사나 record API에 접근하지 못한다. `/family/items/{item_id}/evidence`는 해당 item이 포함된 현재 발행을 찾고, **허용된 발행용 근거 발췌문만** 제공한다. 같은 record의 다른 segment·질문·화자 개인정보는 제외한다.

가족 응답은 `Cache-Control: no-store`를 기본으로 한다. service worker/IndexedDB/localStorage에 내용을 보관하지 않는다. 서버 내부 캐시를 추가할 때 키는 subject+recipient+consent version+content epoch+근거 버전+lang이며 hit에서도 현재 권한을 재검사한다. MVP는 서버 내용 캐시 없이 시작한다.

## 8. 데이터 계보·반입·삭제

### 8.1 Veil 어댑터

실제 파일 schema는 미확인이다. `VeilImportPort`는 제공 파일을 읽고 컬럼·형식·결측·식별 연결을 점검하는 반입 계획을 먼저 만든다. 매핑 승인 전에는 clinical object를 생성하지 않는다. 필드가 없으면 없음으로 남기고 일상 센서·돌봄 대화를 임의로 만들어 Veil 사실로 표시하지 않는다.

원천파일 hash·반입시각·매핑버전·행 위치를 제한 영역에 저장하고 lineage refs로 연결한다. public GitHub에는 원자료·값이 포함된 schema 샘플·error trace·스크린샷을 올리지 않는다. 코드 공개와 데이터 공개를 분리한다.

### 8.2 AI·개발 도구의 외부 전송

[B]의 팀 운영 기준을 유지하여 VEIL·VEIL_DERIVED의 외부 전송은 서면 확인 전 차단한다. **Codex·Claude 등의 개발 에이전트 대화, 클라우드 실행기, 오류 추적, CI artifact, MCP 호출도 외부 전송 경로에 포함**한다. `.gitignore`만으로 모델 컨텍스트 노출을 막았다고 보지 않는다.

개발 에이전트의 workspace에는 설계와 권리 확인된 TEAM_SYNTHETIC만 둔다. Veil 실제 반입·시험은 제한된 로컬 작업 경로와 승인된 로컬 처리기로 수행한다. 실패 조사도 원문 대신 정제한 독립 재현 예제를 사용한다.

전송 정책은 모든 provider 호출 직전에 입력 전체 계보와 실제 endpoint를 검사한다. `local`이라는 이름만 믿지 않는다. 서버 관리 allowlist의 loopback 또는 확인된 팀 통제 endpoint만 허용하고 redirect는 기본 금지한다. 클라이언트가 URL·API key를 지정할 수 없다. 허용하지 않은 호출은 `EGRESS_DENIED`로 끝내며 자동 외부 fallback은 없다.

### 8.3 정리 도구

명령 도구는 dry-run으로 대상 run ID·root·파일 수·예상 작업을 먼저 보여 준다. 실제 정리는 담당자의 명시적 확인을 요구한다. repo 밖의 허용 root인지 검증하고 symlink·상위 경로 탈출을 거절한다.

원자료·복제본은 기준본 정책대로 정리한다. 파생물 보관·공개 범위는 Q-02를 닫지 않고, 별도 승인 보관 예외가 없다면 팀의 보수적 정리 대상으로 함께 관리한다. 이 선택을 공식 규정이 파생물 전부를 명시적으로 삭제하라고 했다는 뜻으로 쓰지 않는다.

SQLite row 삭제만으로 내용이 물리적으로 지워졌다고 주장하지 않는다. run 전용 DB, WAL/SHM, 임시파일, export, 음성, 캐시, 브라우저 trace까지 목록을 관리하여 닫힌 DB의 파일 단위 정리를 수행한다. 검증 로그에는 내용 대신 대상 종류·개수·결과만 남긴다. SSD의 물리적 완전 소거는 보증하지 않는다.

## 9. 음성 작업과 장애

[DD] 초기 제한은 합성 오디오 180초, 업로드 20MiB, 전사 deadline 120초, 구조화/렌더링 각각 60초다. 실제 엔진 검증 후 제한 변경은 설정과 시험 결과에 남긴다. 목표 성능이나 기존 엔진 실측이 아니다.

업로드는 서버가 할당한 무작위 파일 참조를 사용한다. MIME·실제 형식·용량 검사, 상한을 넘기면 413, 지원 불가면 415. 파일명·경로를 shell 문자열에 삽입하지 않는다. 파일을 웹 정적 경로로 제공하지 않는다.

작업 성공·취소·실패·timeout·프로세스 재시작마다 정리 대상 manifest를 확인한다. 브라우저는 사용 종료 시 microphone track·object URL·메모리 참조를 해제한다. 서버는 파일 제거와 engine receipt를 별개로 확인한다. 전체 알려진 처리 영역이 확인되기 전에는 aggregate deletion_status가 deleted가 될 수 없다. 확인 불가능한 외부 engine 영역이 있으면 unverified/failed와 사유를 남긴다.

텍스트는 저장되었는데 음성 삭제만 실패한 경우 UI에 두 결과를 따로 표시한다. 원음 복구를 위해 비밀 백업을 만들지 않는다. 정리 재시도 횟수·오류코드는 기록하되 원문·파일 내용은 audit에 넣지 않는다.

## 10. 미결 과제와 종료 기준

D-05 발표 담당, D-06 실제 모델·실행 조합, Q-01 사전 제작물, Q-02 전송·파생물, Q-03 엔진·권리·삭제, Q-04 현장 업무·핀란드어는 **OPEN**이다. DD-01의 FastAPI 선택이나 본 명세 발행으로 이 항목이 해결된 것으로 표시하지 않는다.

구현은 [Codex 작업·검증](03-codex-tasks-and-tests.md)의 시작 조건과 작업 단위에 따른다. 개발 완료는 파일 생성이 아니라 실제 명령·결과·commit·T-01~T-10 증빙으로 판정한다. 이 문서 자체는 실행 결과가 아니다.

### 기술 참고

이하 공식 문서는 구현 방식 참고이며 제품 요구의 출처가 아니다. 확인일 2026-10-02.

- SQLite 외래키: https://www.sqlite.org/foreignkeys.html
- FastAPI 테스트: https://fastapi.tiangolo.com/tutorial/testing/
