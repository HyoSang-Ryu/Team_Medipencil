# 로컬 독립 합성 데모 실행

이 구현은 FastAPI + SQLite + React/TypeScript/Vite의 **직접 입력 돌봄 루프**다. 로컬 Whisper STT와 Ollama LLM을 설정으로 선택할 수 있으며, Veil 반입·외부 AI·운영 인증·공개 배포·화면6은 포함하지 않는다. FI 문구의 전문 검수는 미완료다. 사용자 구현 착수 지시와 주최 측 확인을 구분한 기록은 [progress.md](progress.md)에 있다.

## 검증 환경

macOS arm64, Python 3.12.15, Node 22.16.0/npm 10.9.2. Python·Node 의존성은 apps/api/requirements.lock.txt와 apps/web/package-lock.json에 고정했다. 파일 잠금은 fcntl 기반이므로 현재 패키지는 macOS/Linux 대상으로 작성했으며 Windows 검증은 하지 않았다.

## 설치

저장소 루트에서 Python 3.12와 Node 22.12 이상 22.x를 사용한다.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r apps/api/requirements.lock.txt
.venv/bin/python -m pip install --no-deps -e apps/api
npm --prefix apps/web ci
npm --prefix apps/web run build
```

이 장비의 격리 준비 런타임은 `~/.local/share/medipencil-preparation`에 있다. 기존 `.venv`가 준비되어 있다. Node가 기본25인 경우 다음을 현재 shell에만 설정한다.

```bash
export PATH="$HOME/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH"
```

## 바로 실행

```bash
.venv/bin/python tools/dev/run_demo.py --port 8767
```

브라우저에서 `http://127.0.0.1:8767`을 연다. 이 명령은 저장소 밖 `~/.local/share/medipencil/runs/<run-id>`에 새 합성 DB를 만들고 위치를 출력한다. 이미 사용 중인 포트를 빼앗지 않는다. 기본 외부 AI off, 단일 API 프로세스, 빌드된 프론트를 같은 출처에서 제공한다. 이 명령은 포트 연결을 유지하므로 Ctrl+C로 종료한다. 실제 데이터·음성을 입력하지 않는다.

동일 DB 재개:

```bash
.venv/bin/python tools/dev/run_demo.py --port 8767 --data-root /absolute/outside/repository/run-directory
```

재시작 시 세션 secret은 새로 만들어져 다시 데모 사용자를 선택해야 한다. 업무 DB는 유지된다. 시작 시 미완료 음성 job은 실패로 표시하고 로컬 audio artifact 정리를 재시도한다. 실제 엔진 내부 삭제 확인을 했다고 표시하지 않는다.

## 환경변수와 개발 모드

명세의 개별 CLI/uvicorn 실행도 지원한다. `MEDIPENCIL_DATA_ROOT`는 저장소 밖 절대경로·비symlink 전용 폴더, `MEDIPENCIL_SESSION_SECRET`은 32자 이상이다. secret은 출력·커밋하지 않는다. `MEDIPENCIL_ORIGIN`은 UI의 정확한 loopback 출처다.

```bash
export MEDIPENCIL_DATA_ROOT="$HOME/.local/share/medipencil/manual-demo"
export MEDIPENCIL_SESSION_SECRET="$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export MEDIPENCIL_ORIGIN=http://127.0.0.1:5173
.venv/bin/python -m medipencil.cli check-environment
.venv/bin/python -m medipencil.cli migrate
.venv/bin/python -m medipencil.cli seed-demo --dry-run
.venv/bin/python -m medipencil.cli seed-demo --confirm TEAM_SYNTHETIC
.venv/bin/python -m uvicorn medipencil.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
# 별도 터미널
npm --prefix apps/web run dev -- --port 5173 --strictPort
```

기존 DB를 seed로 초기화하지 않는다. 이미 seed된 DB는 명시적으로 거절한다. 8000이 사용 중이면 run_demo의8767 경로를 쓰거나 양쪽 API proxy 포트를 함께 설정한다. `MEDIPENCIL_API_PORT`는 Vite 개발 proxy의 loopback API 포트다. 빌드된 앱을 8000에서 직접 제공하려면 UI origin도8000으로 맞춘다.

## 수동 돌봄 루프

1. Liisa 선택 → 가족 상황판에서 질문 작성. AI 즉답 없이 접수된다.
2. Koskinen 선택 → 질문 큐에서 확인 예정 지정 또는 미답변 유지.
3. “Kirjaa ja julkaise” → 질문 선택, 독립 합성 텍스트·화자·진술/관측/계획·공개 분류를 입력한다.
4. 초안의 원문·화자·부정·숫자·계획·scope·답변 충분성을 실제로 검토하고 체크한 후 승인한다. 승인만으로 가족 질문이 완료되거나 동의가 바뀌지 않는다.
5. Liisa 대상으로 발행 미리보기 생성 → 문장/근거/언어 검토 → 별도로 발행한다. 그때 유효한 해당 질문만 answered가 된다.
6. Liisa로 돌아가 질문의 답변 완료, 문장과 근거를 확인한다. Mikko로 바꾸면 허용되지 않은 건강정보가 응답에서도 빠진다. 언어만 SV로 바꾸면 같은 사용자이며 미준비 안내가 표시된다.
7. “Suostumukset”에서 후보 출처를 선택하고 Mikko의 outdoors만 확인한다. 후보 생성 자체로는 grant가 바뀌지 않는다. 철회할 항목과 대상은 별도 확인한다.
8. 승인 기록에서 정정을 시작하면 옛 답을 즉시 보류한다. 정정된 새 원문을 저장하고 재검토·승인·발행한다. 새 승인 전에는 대체 사실을 공개하지 않는다.

문구는 **manual 원문 문장**만 사용한다. 기존 source의 사실을 바꾸는 임의 생성·요약·번역은 하지 않는다. 초안 문구는 source의 전체 문장과 일치해야 한다. 부정어를 잘라내는 위험을 막기 위해 부분문자열 발췌를 허용하지 않는다. 문구 변경은 직원이 새 근거를 명시적으로 확인하고 별도 source로 저장해야 한다. 원문에 계획만 있으면 완료로 바꾸지 않는다. 후속 승인 관측으로만 별도 행동 확인을 수행한다.

음성 시험은 별도 녹음 허용 source reference와 고지가 필요하다. WAV 업로드의 크기/형식/길이 및 실제 로컬 삭제 경로는 동작하지만 로컬 Whisper가 설정된 경우 실제 전사 후 검토 가능한 source로 저장한다. 미설정이면 PROVIDER_NOT_CONFIGURED로 실패하며 직접 입력으로 이어간다. 에러가 난 STT를 LIVE AI 성공으로 표시하지 않는다.

## 검증

```bash
.venv/bin/python -m pytest apps/api/tests -m 'not real_provider'
npm --prefix apps/web run lint
npm --prefix apps/web run typecheck
npm --prefix apps/web run test:run
npm --prefix apps/web run build
# 최초 한번 Chromium 설치
(cd apps/web && npx playwright install chromium)
npm --prefix apps/web run test:e2e
```

`lint`는 현재 TypeScript 엄격 검사와 동일한 명령이며 별도 스타일 lint 엔진은 아니다. E2E는8765/5179와 새 임시 합성 DB를 사용하고 종료한다. 기존 서버를 재사용하지 않아 기존 데이터 초기화를 막는다. 브라우저 trace는 off이며 합성 화면 screenshot만 `/tmp` 또는 ignored test-results에 남는다. 일반 테스트는 모델을 호출하지 않는다. 아래 opt-in 로컬 모델 검증 명령의 실제 실행 증거는 별도로 보관한다.

## 정리

먼저 서버를 중지하고 해당 run의 DATA_ROOT·secret을 설정한다.

```bash
.venv/bin/python -m medipencil.cli clean-run --dry-run
.venv/bin/python -m medipencil.cli clean-run --confirm <위에 표시된 정확한 run_id>
```

기본값은 dry-run이다. 실제 삭제는 run ID가 일치할 때만 DB/WAL/SHM/알려진 audio artifact와 run manifest를 대상으로 수행한다. 실행 중 잠금·symlink·알 수 없는 파일이 있으면 거절한다. 재귀 삭제는 없으며 SSD 물리적 완전 소거를 보증하지 않는다. `.run.lock` 및 빈 audio 디렉터리는 남을 수 있다.

Veil 명령은 `python -m medipencil.cli veil-plan`에서 BLOCKED_VEIL을 출력할 뿐 파일을 읽지 않는다. 실제 schema·이용조건을 확인한 제한 로컬 환경의 별도 구현은 남아 있다.

## 알려진 제한

- 운영 인증·임상/법률 적합성·FI 전문 검수·실제 AI 성능은 검증하지 않았다.
- manual 작업은 즉시 처리하고 로컬 모델은 durable job + background task로 실행한다. 단일 실행 슬롯이며 모델 오류 시 명시적 실패 후 직원이 manual 경로를 선택한다.
- 전체 SV/EN 번역, 임의 자연어 생성, 마이크 스트리밍, 화면6은 구현하지 않았다.
- 테스트용 초기 grant·합성 사용자는 seed에 명시되어 있으며 현장 권한 사실이 아니다.
- 설계 예시 F-01~F-08의 모든 문장/2주 센서 이력을 대량 seed하지 않았다. 핵심 상태·권한은 독립 합성 테스트로 검증한다.

## 로컬 STT·LLM 설정과 교체 (2026-10-03 추가)

이 장비는 `~/.config/medipencil/local-models.json`에 아래 설정을 저장했다. 파일은 저장소 밖에 있으며 모델 가중치를 복사하거나 다운로드하지 않았다. `run_demo.py`와 환경 기반 CLI는 이 설정을 읽는다. 서버를 재시작하면 변경이 적용된다. `MEDIPENCIL_MODEL_CONFIG`로 다른 JSON 파일을 지정할 수 있고, 환경변수가 JSON 값보다 우선한다. 파일이 없으면 모델은 disabled다. 테스트에서 직접 만드는 Settings의 기본값도 disabled다.

```json
{
  "stt_backend": "whisper",
  "stt_python": "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
  "stt_model": "/Users/hyosang/.cache/whisper/medium.pt",
  "llm_backend": "ollama",
  "llm_model": "llama3.1:8b",
  "llm_url": "http://127.0.0.1:11434",
  "timeout": 180
}
```

다른 장비에서는 절대경로를 그 장비의 설치 위치로 변경한다. `stt_python`은 whisper/torch와 ffmpeg가 준비된 기존 Python이며 API의 Python3.12와 분리했다. Whisper worker는 CPU·4스레드, checkpoint 절대경로만 읽고 네트워크 연결을 차단한다. 모델을 자동 다운로드하지 않는다. runtime을 교체할 때 해당 Python의 whisper·torch 호환을 다시 검증해야 한다.

| 교체 대상 | 환경변수 | 예 |
|---|---|---|
| STT 방식 | MEDIPENCIL_STT_BACKEND | whisper 또는 disabled |
| STT 런타임 | MEDIPENCIL_STT_PYTHON | 설치된 Python 절대경로 |
| STT 가중치 | MEDIPENCIL_STT_MODEL | 기존 medium.pt 또는 large-v3.pt 절대경로 |
| LLM 방식 | MEDIPENCIL_LLM_BACKEND | ollama 또는 disabled |
| LLM 모델 | MEDIPENCIL_LLM_MODEL | ollama list에 존재하는 모델명 |
| LLM 주소 | MEDIPENCIL_LLM_URL | 명시적 http://127.0.0.1:포트 |
| 제한 시간 | MEDIPENCIL_AI_TIMEOUT | 5~600초 |

같은 adapter의 모델 교체는 설정만 바꾸면 된다. 다른 엔진 방식은 `WhisperSpeech`/`OllamaExtraction` 구현과 factory 분기를 추가하되 승인·DB·권한 계층은 재사용한다. 현재 임의 외부 API/클라우드 모델/redirect는 허용하지 않는다. Ollama의 설치 목록과 remote_model/remote_host를 확인하며 자동 pull·fallback을 하지 않는다.

### 화면과 처리 범위

화면3에 로컬 LLM/수동 선택과 STT 업로드가 연결되어 있다. provider 설정이 있는 로컬 데모는 LLM 선택이 기본이며, 일반 회귀 테스트 서버는 manual 기본이다. STT는 언어 선택, 별도 녹음 허용, 업로드, 취소, 전사 확인을 거친다. 인식된 화자는 unknown으로 두고 health_context를 기본 적용한다. 가족 화면에서도 미확인 화자를 직원 관찰로 표시하지 않는다.

현재 LLM의 역할은 **전사에서 기록할 근거 선택**이다. 전체 출처 문구·화자·유형·scope는 서버가 보존한다. 자유 요약·번역·자동 동의 후보 추출은 아직 지원하지 않는다. 질문 연결은 직원이 선택하고 검토하며, 가족 발행 문구는 승인된 문장 그대로다. 가족용 문구 재작성 LLM은 연결하지 않았다. 이는 현재의 원자료 충실성 제약을 유지하는 보수적인 첫 adapter다.

job에는 backend/model/hash 또는 digest/input_mode/STT 수행 여부/실행 모드를 남긴다. 정상 모델 실행만 LIVE + ai_executed=true, 재조회는 저장 결과이며 idempotency 재요청은 REPLAY다. 승인·동의·발행은 기존 직원 검토와 별도 transaction을 유지한다. 오디오는 worker 종료 후 로컬 업로드 파일을 삭제한다. 물리적 메모리/SSD 소거를 보증하지 않는다. 저장 완료 전사와 초안은 재시작 때 보존한다.

### 실제 모델 검증

```bash
.venv/bin/python tools/dev/verify_local_models.py
```

이 장비의 macOS `say` 핀란드어 음성과 ffmpeg를 사용해 독립 합성 WAV를 만들고 Whisper→Ollama→DB 초안→테스트 승인·발행을 실제 실행한다. 음성·DB는 저장소 밖 임시 디렉터리에서 정리한다. 다른 OS의 TTS 경로는 별도 조정이 필요하다. 일반 pytest와 분리한 opt-in 명령이다.

[실행 결과](../evidence/local-model-smoke.json): Whisper medium7.93초, Ollama1.21초(해당 1회). 첫 단어 Tämä를 sama로 인식한 오류를 보존했다. 연결·저장 검증 성공이지 FI 품질·임상 적합성·전문가 승인 성공이 아니다. large-v3와 다른 Ollama 모델은 설치 확인만 했고 추론 검증하지 않았다.

Adapter 참고: [Ollama chat API](https://docs.ollama.com/api/chat), [Whisper 로컬 모델 로딩](https://github.com/openai/whisper). Whisper 설치 소스의 load_model signature와 로컬 checkpoint 분기도 직접 확인했다.
