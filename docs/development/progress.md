# 개발 진행 기록

기록일: 2026-10-02 (Asia/Seoul). source 문서의 역사적 상태는 변경하지 않는다.
현재: **PREPARATION / NOT_IMPLEMENTED / T-01~T-10 NOT_RUN**.

## P-00 / DONE — 저장소·기준·허용 단계 확인

- 시작 branch / HEAD: `main` / `9c64133960f8305c0dab9e3713009bbb39e46e1c`.
- 작업 branch: `codex/preparation-preflight`. 종료 commit: 이 절을 추가한 `docs: record P-00 repository and phase preflight` 커밋(해시는 후속 기록 참조).
- 허용 근거: 사용자 지시 1~2 및 AGENTS.md 실행 단계, 03 §2·P-00. **P-00/P-01만 허용 확인**. 사용자도 “구현 시작 조건이 열리면” C 작업을 수행하도록 지시했다.
- 현재 폴더는 대상 저장소가 아니며, 원격 이름·기본 branch 확인 후 `work/Team_Medipencil`에 별도 clone했다. 상위 폴더의 기존 미추적 자산은 수정·staging하지 않았다.
- clone 직후 dirty tree 없음, HEAD와 origin/main 차이 없음. 추적 자산 17개: Markdown 8개와 SVG 9개. 앱 소스·실행 fixture·DB·음성·lockfile 없음.
- 기준 `9437e5cead05663bc575739301997a75750fef80` 대비 AGENTS.md·개발명세 4개 추가 및 루트 README 변경뿐. 설계 v1.1 blob은 명세의 `f13a3b9732c1490cdff7f3c9b52dbc474538a03a`와 동일.
- AGENTS.md, 개발 README, v1.1 전체, 01~03 전체, 확정 기록 읽음. 출력이 잘린 부분은 범위를 나누어 다시 읽음.
- 변경 파일: `docs/development/progress.md`.
- 실제 명령·결과: `gh repo view HyoSang-Ryu/Team_Medipencil --json nameWithOwner,defaultBranchRef,url` → 대상 일치/main; `git clone https://github.com/HyoSang-Ryu/Team_Medipencil.git work/Team_Medipencil` → 성공; `git rev-parse HEAD`, `git status --short --branch`, `git ls-files`, `git log -4 --oneline` → 위 관측; `git diff --stat origin/main HEAD` → 출력 없음; `git diff --name-status 9437e5cead05663bc575739301997a75750fef80 HEAD` → 위 6파일; `git rev-parse HEAD:docs/design/medipencil-final-design-v1.1.md` → 위 blob; `git switch -c codex/preparation-preflight` → 성공.
- 관련 T-ID: T-01~T-10 모두 NOT_RUN. 문서 읽기·Git 비교는 기능 테스트가 아니다.
- provider / fixture: 모두 미실행·미설정. 설계 내 합성 예시를 실행 fixture로 바꾸지 않았다.
- 차단: 실행 단계, 허용 작업 ID, 확인자, 확인 시각, 근거/회신 참조가 제공되지 않아 C 작업은 WAITING_FOR_PERMITTED_PHASE. 날짜 경과로 해제하지 않는다.
- 미결: D-05/D-06/Q-01~Q-04 유지. 원격 push·PR·배포 미실행.

## 작업 분리 및 다음 순서

모든 C 작업은 현재 NOT_STARTED이며 공통 사유는 WAITING_FOR_PERMITTED_PHASE다. 표의 T-ID는 계획상 연결이며 통과 표시가 아니다.

| 작업 | 허용 후 수행 순서·산출물 | 관련 검증 |
| --- | --- | --- |
| P-00 | 현재 기준·자산·단계 기록 | 문서/Git 관측 |
| P-01 | 범용 환경·권리·기존 자산 조사 | 범용 smoke, 앱 테스트와 분리 |
| C-01 | FastAPI/SQLite/React·TS·Vite 기반, lockfile | health/build/실행틀 |
| C-02 | DB·근거·버전·상태 | T-01/02/08/09 관련 무결성 |
| C-03 | 모의 세션·수신자 필터 | T-05/06/07 |
| C-04 | 가족 질문→DB→직원 큐 | T-08 |
| C-05 | 직접 입력→초안→사람 승인 | T-01/03/04/08 |
| C-06 | 근거·권한 검토→발행→가족 답 | T-01/02/04 |
| C-07 | 동의 후보·확인·철회 | T-05/06/07 |
| C-08 | 정정·실패·재시도·경합 | T-02/04/07/08 |
| C-09 | 검증된 실제 STT/LLM adapter·음성 정리 | T-09, 실provider 별도 |
| C-10 | 화면1~5 FI UX·전환·실행 표시 | T-06/10, 사람 FI 검수 |
| C-11 | 실제 API/DB 브라우저 루프·재현성 | T-01~T-10 |
| C-12 | 로컬 패키징·인계, 조건 충족 시 Veil 반입 | 핵심 재현, Veil 별도 차단 가능 |
| O-01 | NOT_STARTED, 핵심 통과 및 별도 승인 필요 | 화면6·전체 번역·스트리밍 |

구현 단계가 확인되면 C-01부터 순차 실행한다. C-08까지 직접 입력 루프·승인·권한·정정·실패를 검증한 후 C-09 실제 엔진 연결로 간다. Q-02/Q-03 미결은 그 시점에 외부 연동만 차단하며 독립 합성·직접 입력 루프 전체를 막는 이유로 쓰지 않는다.

### 구현 시작 확인 기록 — 현재 미제공

- 실행 단계: PREPARATION (구현 허용 단계 미확인)
- 허용 작업 ID: P-00/P-01
- 구현 허용 확인자 / 확인 시각 / 근거 또는 회신 참조: 미제공
- 기존 자산 기준 commit: `9c64133960f8305c0dab9e3713009bbb39e46e1c`

03 §2.2의 공개 가능한 확인 요지·근거 식별자가 필요하다. 비공개 회신 원문은 저장하지 않는다.

## P-01 / DONE — 범용 환경·자산 조사 (환경 구성 완료 아님)

- 시작 HEAD: `81a3cf0` (P-00 종료 commit), branch: `codex/preparation-preflight`.
- 종료 commit: 이 절과 자산 목록을 추가한 `docs: record P-01 generic environment smoke and asset gaps` 커밋. 자체 해시의 순환 기재 대신 고유 제목으로 식별하며 `git log -1 --format='%H %s' -- docs/development/preparation-assets.md`로 조회한다.
- 허용 범위: 03 P-01의 기존 설치 metadata·일반 입력 smoke·반입 자산 문서 조사. 기능·스키마·과제별 fixture·prompt 작성 없음.
- 변경 파일: `docs/development/progress.md`, `docs/development/preparation-assets.md`.
- 구현한 앱 동작: 없음. 임시 메모리에서만 범용 도구 확인; socket·DB 파일·AI 호출 없음.
- 결과: 범용 FastAPI TestClient 200, SQLite 없는 부모 FK 거절, Node JSON roundtrip PASS. 상세 버전·권리 확인 수준은 [자산 목록](preparation-assets.md).
- 관련 T-ID: T-01~T-10 모두 NOT_RUN. 위 smoke는 C-01 health 또는 앱 통합검증이 아니다.
- provider/fixture: 실제 provider NOT_VERIFIED, 실행 fixture 없음. 모델 다운로드·유료 호출·외부 AI·비공개 엔진 clone 없음.
- 실패·제한: `python3.12`, `uv`는 command not found. 목표 Python 3.12·Node 22.x 환경 및 앱 의존성 lock 설치/호환성 시험은 미실행. 기존 전역 환경은 변경하지 않음. 실제 엔진 버전/commit/권리/endpoint/FI/삭제 receipt 미제공으로 엔진 검증은 BLOCKED_PROVIDER.
- 다음 작업: 확인된 구현 단계에서 격리된 목표 런타임과 lockfile로 C-01 시작; 엔진 담당자의 공개 가능한 metadata로 자산 목록 보완. P-01 DONE은 조사 산출물 완료이며 ENVIRONMENT_READY 또는 REAL_PROVIDER_VERIFIED가 아니다.

### 실제 실행 명령 및 결과

아래 smoke는 저장소에 실행 코드로 추가하지 않고 shell에서 실행했다.

```bash
command -v python3 python3.12 node npm uv sqlite3 git gh
python3 --version
python3.12 --version
node --version
npm --version
uv --version
sqlite3 --version
git --version
gh --version
```

결과: Python 3.11.2, Node v25.2.1, npm 11.6.2, SQLite CLI 3.51.0, Git 2.49.0, gh 2.96.0. python3.12/uv 조회는 실패. 복수 명령 shell의 최종 exit=0은 중간 명령 성공을 뜻하지 않는다.

```bash
python3 - <<'PY'
import sys, sqlite3, importlib.metadata as m
print('python_executable=',sys.executable)
print('sqlite_runtime=',sqlite3.sqlite_version)
for name in ['fastapi','pydantic','sqlalchemy','alembic','pytest','httpx']:
    try:
        d=m.distribution(name)
        print(name, d.version, 'license=',d.metadata.get('License-Expression') or d.metadata.get('License') or 'NOT_DECLARED')
    except m.PackageNotFoundError:
        print(name, 'NOT_INSTALLED')
c=sqlite3.connect(':memory:')
c.execute('pragma foreign_keys=on')
c.execute('create table parent(id integer primary key)')
c.execute('create table child(id integer primary key, parent_id integer references parent(id))')
try:
    c.execute('insert into child values (1,99)')
except sqlite3.IntegrityError:
    print('generic_sqlite_fk_smoke=PASS')
else:
    raise AssertionError('FK not enforced')
c.close()
PY
node --input-type=module -e 'import assert from "node:assert/strict"; assert.equal(JSON.parse(JSON.stringify({value: 1})).value, 1); console.log("generic_node_json_smoke=PASS", process.version)'
```

결과: exit=0, generic_sqlite_fk_smoke=PASS, generic_node_json_smoke=PASS. 패키지별 버전·license metadata는 자산 목록에 기재.

```bash
python3 - <<'PY'
from fastapi import FastAPI
from fastapi.testclient import TestClient
app=FastAPI()
@app.get('/health')
def health(): return {'status':'ok'}
with TestClient(app) as client:
    r=client.get('/health')
    assert r.status_code == 200 and r.json() == {'status':'ok'}
print('generic_fastapi_in_process_smoke=PASS; socket=none; AI=none')
PY
```

결과: exit=0, generic_fastapi_in_process_smoke=PASS; socket=none; AI=none.

환경 위치 보조 조회:

```bash
ls -d /opt/homebrew/opt/python* /opt/homebrew/opt/node* /Library/Frameworks/Python.framework/Versions/* /Users/hyosang/.nvm/versions/node/* 2>/dev/null
find /opt/homebrew/opt /Library/Frameworks/Python.framework/Versions -maxdepth 1 \( -name 'python*' -o -name 'node*' -o -name '3.*' \) -print
```

첫 명령: exit=1, zsh unmatched glob으로 실패. 후속 find: exit=0, Python 3.11/3.14와 Node 25 계열 위치 확인. 해당 조회에서 목표 버전은 발견되지 않음.

### 문서 변경 검증

`git diff --cached --check`로 각 커밋의 공백 오류를 검사한다. 앱 테스트·빌드는 실행 파일이 없고 구현 단계가 미확인되어 실행하지 않는다. 원격 push와 공개 배포는 수행하지 않았다.

## P-01 추가 준비 / DONE — 2026-10-03 격리 런타임 및 범용 호환 확인

- 시작 HEAD: `870acaa`, branch `codex/preparation-preflight`. 종료 commit: `build: prepare isolated generic Python and React smoke tooling` (해시는 후속 최종 기록 참조).
- 허용 근거: 사용자 “알아서 진행해봐”에 따라 P-01 내 환경 설치·범용 테스트 준비를 계속 수행. 현장 시작 또는 주최 측 허용 사실은 제공되지 않아 C-01~C-12의 WAITING_FOR_PERMITTED_PHASE를 유지한다. 확인자·근거를 만들어 기입하지 않았다.
- 변경 파일: 루트 .gitignore(macOS metadata 제외), 본 progress.md, preparation-assets.md, tools/preparation/README.md, requirements.in, requirements.lock.txt, smoke.py, web/{.gitignore,package.json,package-lock.json,tsconfig.json,index.html,main.tsx}.
- 준비 결과: 저장소 밖 Python 3.12.15 venv와 Node 22.16.0/npm 10.9.2 설치. Python 패키지 26개 의존성 일치. 비의료적 echo API·금지 필드 거절·메모리 DB rollback PASS. React 19.3.0/TS 7.0.2/Vite 8.3.2 일반 샘플 typecheck/build PASS. 제품 구현 없음.
- 관련 T-ID: T-01~T-10 전부 NOT_RUN. 실provider 0회, 제품 fixture 없음, AI 미설정. 브라우저 검증·앱 테스트·migration·FI/엔진 검증 미실행.
- 실패: Homebrew 설치 exit=1, ca-certificates가 이미 연결되어 link 불가. brew 경로의 Python/Node 설치 실패. 캐시와 ca-certificates 설치 상태는 남아 있으며 전역 링크를 강제 변경하거나 기존 패키지를 삭제하지 않음. Microsoft tap 경고의 trust를 변경하지 않음.
- 경고: Starlette TestClient httpx deprecation warning. 테스트 통과와 별도로 유지하며 후속 앱 의존성 선택 시 재검토.
- 작업 트리: 준비 중 추적하지 않는 루트 `.DS_Store`가 관측되어 그대로 보존·커밋 제외. node_modules/dist도 커밋 제외.
- 다음: 확인된 구현 단계에서 C-01부터 시작. 현재 저장소 밖 준비 환경을 재사용할 수 있으나 앱 의존성·테스트 계약을 별도로 검증한다. 실제 provider/Q-02 조건은 계속 별도 확인 대상.

### 실제 실행 명령·결과 (이번 추가 준비)

명령의 작업 디렉터리는 별도 표기 없으면 저장소 루트다. 긴 lock 출력은 요약했으며 lock 본문은 파일에 보존했다.

```bash
brew list --versions python@3.12 node@22
HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew install python@3.12 node@22
```

첫 조회 exit=1(목표 버전 미설치). 설치 exit=1(위 인증서 링크 충돌). 이후 `brew list --versions ca-certificates python@3.12 node@22`에는 ca-certificates 2026-09-25 및 2026-05-14만 표시, 목표 런타임 없음.

```bash
mkdir -p /Users/hyosang/.local/share/medipencil-preparation
python3 -m venv /Users/hyosang/.local/share/medipencil-preparation/bootstrap
/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/python -m pip install uv
UV_PYTHON_INSTALL_DIR=/Users/hyosang/.local/share/medipencil-preparation/python /Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv python install 3.12 --no-bin
UV_PYTHON_INSTALL_DIR=/Users/hyosang/.local/share/medipencil-preparation/python /Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv venv --python 3.12 /Users/hyosang/.local/share/medipencil-preparation/venv
/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv pip compile --python /Users/hyosang/.local/share/medipencil-preparation/venv/bin/python --generate-hashes tools/preparation/requirements.in -o tools/preparation/requirements.lock.txt
/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv pip sync --python /Users/hyosang/.local/share/medipencil-preparation/venv/bin/python tools/preparation/requirements.lock.txt
```

모두 성공, uv 0.12.22 및 Python 3.12.15, 26개 패키지 설치. 라이브러리 해시는 lock에 기록.

준비 폴더를 cwd로 하여 실행:

```bash
curl --fail --location --output node-v22.16.0-darwin-arm64.tar.gz https://nodejs.org/dist/v22.16.0/node-v22.16.0-darwin-arm64.tar.gz
curl --fail --location --output SHASUMS256.txt https://nodejs.org/dist/v22.16.0/SHASUMS256.txt
rg ' node-v22.16.0-darwin-arm64.tar.gz$' SHASUMS256.txt | shasum -a 256 -c -
tar -xzf node-v22.16.0-darwin-arm64.tar.gz
```

exit=0, archive SHA-256 OK. 배포 checksum과의 일치 확인이며 별도 서명 검증은 수행하지 않음.

저장소 루트에서 실행:

```bash
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web install --save-exact react react-dom
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web install --save-dev --save-exact typescript vite @types/react @types/react-dom
/Users/hyosang/.local/share/medipencil-preparation/venv/bin/python tools/preparation/smoke.py
/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv pip check --python /Users/hyosang/.local/share/medipencil-preparation/venv/bin/python
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web ci
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web run typecheck
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web run build
PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH npm --prefix tools/preparation/web ls --depth=0
```

모두 exit=0. Python 3가지 검사 PASS, uv 26개 compatible. npm ci 성공 및 해당 시점 audit 0 vulnerabilities(전체 보안검증 아님). tsc 성공, Vite 14모듈 build 성공(65ms). 직접 의존성 목록은 preparation-assets.md에 기록.

최종 staging 검사에서 하위 `.DS_Store`도 발견하여 `git restore --staged`로 제외하고 루트 `.gitignore`에 등록했다. 파일은 삭제하지 않았다. `git diff --cached --check`는 exit=0. 준비 자산 외 앱·데이터·node_modules·dist가 staging에 없음을 확인했다.

### 종료 확인

P-01 추가 준비 종료 commit: `eb1b574` (`build: prepare isolated generic Python and React smoke tooling`). `git status --short --branch` 결과는 branch 한 줄만으로 clean. 이 후속 문서 커밋은 종료 해시 기록만 추가하며 테스트 결과를 변경하지 않는다. 원격 push·PR·배포는 미실행이다.

## 실행 범위 변경 — 2026-10-03T01:05:23+09:00

사용자의 후속 명시 지시 “멈추지말고 계속 구현해”를 기존 준비 단계 대기를 해제하는 사용자 범위 변경으로 적용한다. 확인자는 이 대화의 사용자이며 별도 실명은 제공되지 않았다. 허용 작업은 C-01~C-12의 로컬 독립 합성·직접 입력 구현과 검증이다. 이것은 현장 시작 또는 주최 측 승인 확인이 아니며 Q-01은 OPEN으로 유지한다. 외부 AI·Veil·비공개 엔진·공개 배포·O-01은 허용 사실을 추가로 만들어내지 않는다. 기존 자산 기준은 `cd6e721`. 구현 branch `codex/care-loop-mvp`.

## C-01 / DONE — 앱 기반

- 시작 HEAD `cd6e721`. 변경: .gitignore, apps/api/{pyproject.toml,requirements.in,requirements.lock.txt,src/medipencil/*,tests/test_foundation.py}, apps/web/{package*.json,tsconfig.json,vite.config.ts,index.html,src/main.tsx}.
- 동작: 설정 경계, 정제 오류 DTO, no-store/Host 검사, 실제 FastAPI health, React shell 및 Vite 동일 출처 proxy. 앱의 데이터 root는 저장소 밖·비symlink만 허용.
- 실제 명령: `uv venv --python 3.12 .venv`, `uv pip sync --python .venv/bin/python apps/api/requirements.lock.txt`, `uv pip install --python .venv/bin/python --no-deps -e apps/api` 성공. uv는 준비 폴더 bootstrap/bin, UV_PYTHON_INSTALL_DIR은 이전 준비 경로 사용.
- `.venv/bin/python -m pytest apps/api/tests -q` → 2 PASS, 기존 Starlette/httpx deprecation warning 1. Node 22 PATH로 `npm --prefix apps/web install --package-lock-only`, `npm --prefix apps/web ci`, `npm --prefix apps/web run build` → 성공.
- T-ID: 기반 점검만, T-01~T-10 기능 검증 미실행. provider 미설정, fixture 미사용. 실제 루프 미구현.
- 종료 commit: `feat: C-01 local API and web foundation` (다음 작업에서 해시 기록).

## C-02 / IN_PROGRESS — 저장 기반 (C-01 종료 d9dfa83)

- 변경: schema_v1.py, db.py, domain.py, migrations/{env.py,versions/001_initial.py}, tests/test_storage.py.
- Alembic revision 001로 18개 도메인 테이블·FK·인덱스·불변 trigger 생성. write transaction은 BEGIN IMMEDIATE. source/record 근거 버전·입주자·유효성 검사, UTC 시각 검증 추가.
- `.venv/bin/python -m pytest apps/api/tests -q` → 6 PASS. migration 2회, FK 거절·rollback, 무시간대/미래 시각 거절 실행. T-02/08/09의 기반 일부이며 전체 수용 통과 아님.
- idempotency와 공개 권한을 포함하는 서비스 검증은 다음 작업에서 연결한다. provider/fixture 없음.
- 종료 commit 제목: `feat: C-02 versioned storage and evidence foundations`.

## C-03 / IN_PROGRESS — 세션·권한 기반 (C-02 commit fef7df6)

- 변경: security.py, sessions.py, seed.py, main.py, tests/{conftest.py,test_sessions.py}.
- 로컬 allowlist 세션 회전·만료·해시 저장·CSRF/Origin·역할·membership·최신 all-of grant 구현. C-02 idempotency는 본문 대신 객체 참조만 저장하도록 공통 실행 함수 추가.
- `.venv/bin/python -m pytest apps/api/tests -q` → 8 PASS. T06-C/F 및 역할·Origin·구 세션 차단 확인. 가족 evidence 필터는 C-06 연결 후 검증 예정. 세션은 운영 인증이 아니다.
- TEAM_SYNTHETIC 초기 grant만 사용. 실제 provider 없음. 종료 commit 제목 `feat: C-03 isolated demo sessions and recipient authorization`.

## C-04 / IN_PROGRESS — 질문→직원 큐 (C-03 commit 97f75a5)

- 변경: questions.py, main.py, tests/test_questions.py, web/src/{api.ts,main.tsx,style.css}.
- 질문 DB 저장·본인 질문만 조회·직원 큐·예정/미답변 API와 화면1/2 초기 연결. 병렬 동일 키는 한 객체, 다른 payload 동일 키는409. 사용자 전환 시 요청 취소·세대 검사와 화면 비우기.
- `.venv/bin/python -m pytest apps/api/tests -q` → 10 PASS. T08-A/C/D 및 질문 격리 확인. Node22 PATH `npm --prefix apps/web run typecheck` 성공. 브라우저 검증은 C-11 예정, 담당·예정 UI는 후속 완성.
- provider 호출 없음, TEAM_SYNTHETIC만. 종료 commit 제목 `feat: C-04 durable questions and staff queue`.

C-04 검증 정정: 위 최초 typecheck는 실제로 TS2882(CSS side-effect import 타입 선언 누락)로 실패했다. 같은 shell의 후속 commit 성공을 typecheck 성공으로 잘못 기재했다. `src/vite-env.d.ts`에 Vite client 타입을 추가한 뒤 동일 typecheck를 재실행하여 exit=0을 확인했다. C-04 본체 commit `d256bee`; 실패를 숨기거나 테스트를 제거하지 않았다.

## C-05 / IN_PROGRESS — 직접 입력·초안·승인 (이전 commit 4eb09aa)

- 변경: records.py, db.py, main.py, tests/{helpers.py,test_records.py}, web/src/{Capture.tsx,main.tsx}.
- Manual 처리기는 원문을 그대로 구조화하며 AI 실행으로 표시하지 않는다. 직원이 입력 시 화자·유형·scope를 지정하고 기본은 health_context. 이 입력 분류 필드는 직접 입력 계약의 명시적 보완이며 LLM 분류가 아니다. JobDTO와 단계 메타, 답변 후보, 필수 사람 검토, 불변 승인·계획 행동 생성.
- 최초 pytest 1 FAIL/11 PASS: nullable confirmed_in_json을 json.loads(None)한 오류. decode 수정 후 `.venv/bin/python -m pytest apps/api/tests -q` →12 PASS. Node22 typecheck 성공.
- T01-A, T03-A, T04-A/B/E 일부 실행: 출처 없는 문구·stale revision·미검토 승인 거절, 승인 후 질문 미완료·동의 불변·계획 유지. 실provider·fixture 없음. 직접 입력에 음성 삭제 결과를 만들지 않음.
- 초안 편집 API는 출처에 있는 발췌만 허용하며 새 사실은 새 source가 필요. UI 편집/후속 수용검증은 계속 진행. 종료 commit 제목 `feat: C-05 manual capture and explicit record approval`.

## C-06 / IN_PROGRESS — 승인 근거 발행·가족 열람 (C-05 commit 15e9945)

- 변경: publications.py, aggregation.py, questions.py/main.py, tests/{helpers.py,test_publications.py,test_aggregation.py}, web/src/{Publication.tsx,Board.tsx,main.tsx}.
- 실제 DB 발행과 질문 answered를 한 transaction으로 저장. prepare/preview는 비공개. 현재 grant·epoch·근거를 발행/열람마다 재검사하고 가족 evidence는 현재 item의 발췌만 응답. FI만 발행 가능, SV는 명시적 unavailable. 계획과 확인을 별도 표시.
- `.venv/bin/python -m pytest apps/api/tests -q` →15 PASS. Node22 typecheck 성공. T01-A/C, T04-A/B/C, T06-D 일부 및 실제 직접 입력 API 루프 확인. interval 집계의 야간/중복/누락 테스트 통과; 센서 반입·발행 연결은 아직 미구현이며 전체 C-06 DONE으로 표시하지 않는다.
- 실제 LLM/STT 없음, manual 처리만. 브라우저 E2E·센서 연결은 후속 검증 대상. 종료 commit 제목 `feat: C-06 reviewed publications and restricted family evidence`.

## C-07 / IN_PROGRESS — 동의 후보·확인·철회 (C-06 commit b6bcc87)

- 변경: consents.py/main.py, test_consents.py, web/src/{Consent.tsx,main.tsx}. 후보·불변 effective version 분리, 후보 밖 scope 거절, 최신 version 확인, 철회 즉시 관련 발행 무효화. 화면5는 대상·출처 발언·추가/제거 scope를 별도로 확인.
- `.venv/bin/python -m pytest apps/api/tests -q` →16 PASS. typecheck 성공. T05-A/B/C/D, T06-D 및 T07-A/D 일부: outdoors만 추가 후 health_context 문구는 raw JSON에서 제외, 전체 철회 후 기존 근거 URL404. DOM·늦은 응답 검증은 C-11에서 수행.
- 실제 동의 법적 검증·FI 검수·실provider 미실행. 종료 commit 제목 `feat: C-07 versioned consent review and revocation`.

## C-08 / IN_PROGRESS — 정정·경합·저장 실패 (C-07 commit e5ae478)

- 변경: corrections.py, main.py, tests/test_corrections_failures.py. 승인 원문을 보존한 새 정정 버전, 옛 source 무효화, 관련 질문 재검토·행동 재확인·발행 차단. 새 버전의 답변 후보도 pending으로 복제. 저장 오류는 원문 없이503.
- `.venv/bin/python -m pytest apps/api/tests -q` →19 PASS. T02-C, T04-D, T07-B/E 확인: SQLite 실패 trigger로 발행·질문 transaction rollback, 철회 후 같은 idempotency 응답도 현재 grant 재검사, 최신 무효화 후 옛 발행 fallback 없음. C-04 병렬 중복 검사 포함.
- 실제 LLM 호출 중 변경 시험은 provider 미설정으로 미실행; snapshot stale 검증은 후속 테스트 확장. 정정 UI는 C-10에서 연결. 종료 commit 제목 `feat: C-08 immutable corrections and transactional failure handling`.

## C-09 / IN_PROGRESS, 실제 provider BLOCKED_PROVIDER (C-08 commit ccd4d27)

- 변경: providers.py, audio.py, records.py/main.py, requirements*, tests/test_audio.py.
- STT/extract/render/cleanup Port 경계, 미설정 provider의 명시적 실패. 혼합/미상/Veil 계보·외부 endpoint는 네트워크 이전 거절. 실제 모델·endpoint·권리 미제공으로 AI 연결은 수행하지 않음.
- 별도 녹음 허용 근거, WAV 형식·크기·길이 검사, opaque artifact, durable cleanup manifest, 실제 파일 삭제 후 receipt/시각 기록. 실패는 deleted_at=null. startup recovery, 취소, 늦은 성공 무시. 실제 엔진 artifact는 생성되지 않아 local-only receipt라고 명시.
- `uv pip compile --quiet --python .venv/bin/python --generate-hashes apps/api/requirements.in -o apps/api/requirements.lock.txt`, sync 및 editable install 성공(python-multipart 추가). `.venv/bin/python -m pytest apps/api/tests -q` →25 PASS. T09-A/C/D/E 일부: 테스트 생성 무음 WAV의 실제 파일 제거, PermissionError 실패 주입·재시도, restart 정리, 별도 녹음 허용 요구. T08-E 미설정/종결 job 늦은 결과 무시 확인.
- 실제 STT/LLM·FI 성능·엔진 내부 삭제 receipt는 NOT_VERIFIED. 업로드 UI·크기/형식/경로 negative 확장은 후속 작업. 종료 commit 제목 `feat: C-09 honest provider failures and durable local audio cleanup`.

## C-10 / IN_PROGRESS — 화면1~5·전환·실행 표시 (C-09 commit dfcc28d)

- 변경: web/src/{App.tsx,Audio.tsx,Capture.tsx,Board.tsx,main.tsx,api.ts,api.test.ts,style.css}, web/{package*.json,vitest.config.ts}; API sensors.py 및 publication/main 보완, test_sensors.py.
- React Router의 가족/직원큐/기록/동의 경로, TanStack Query 세션별 메모리 조회, 전환 시 cancel·cache 제거, 네트워크 단절 시 민감 화면 마스킹. 승인/발행 분리, 담당 예정·미답변, 기록 편집·정정·행동 확인·음성 실패 UI. 최소 SV 전환은 사용자 유지와 unavailable 표시만.
- C-06 보완: 독립 합성 door/bed 집계를 승인 초안으로 저장하는 sensor-observations API 추가. UTC 집계·coverage·귀속 확인, sensor_observation 표기. 센서 근거로 행동 confirm 거절.
- 실제 `npm install --save-exact react-router-dom @tanstack/react-query`, dev install vitest/Playwright/testing-library/jsdom 성공. Node22 `npm --prefix apps/web run typecheck`, `run build` 성공. build에 dependency의 use-client directive 경고 있음(클라이언트 SPA, 숨기지 않음). `run test:run` →2 PASS(늦은 이전 사용자 응답 폐기·네트워크 실패). `.venv/bin/python -m pytest apps/api/tests -q` →27 PASS.
- T06-E/T10-F 일부 확인. UI FI 문구는 작성본이며 사람 FI/selkokieli 검수 NOT_VERIFIED. 브라우저360/1280 및 전체 동작 검증은 다음 작업. 종료 commit 제목 `feat: C-10 focused care screens and session-safe UI`.

## C-11 / IN_PROGRESS — 실제 API/DB/브라우저 검증 (C-10 commit 002e2ca)

- 변경: API cli.py/main.py/audio.py/config.py, test_acceptance.py; web e2e/care-loop.spec.ts 및 playwright.config.ts/vite.config.ts, App 언어 접근성 라벨, tools/dev/e2e_api.py.
- `.venv/bin/python -m pytest apps/api/tests -q` →40 PASS. 추가: 타입·원문 불변, 타 입주자 근거409, 미승인 완료 거절→승인 후 확인, 직접 입력 원문 보존, snapshot stale, DB 저장 실패, timeout/cancel/실제 파일 정리, symlink 거절, 세션 만료·CSRF, 새 app 인스턴스의 파일 DB 유지.
- Node22 `playwright install chromium` 성공(153.0.8010.12). E2E 최초 실패:8000 포트가 기존 서비스에서 사용 중 → 해당 서비스를 건드리지 않고 전용8765/5179 분리. 다음 실패: macOS 임시 디렉터리 `/var` symlink → 테스트 root를 resolve, 경계검사 유지. 첫 실행 1 FAIL/1 PASS: 언어 select의 접근성 이름이 모호 → aria-label 지정. 재실행2 PASS 후 화면5·offline·지연 실제 응답 테스트 추가.
- 최종 해당 실행 `npm --prefix apps/web run test:e2e` →4 PASS (5.1초). 새 임시 TEAM_SYNTHETIC DB·실제 Uvicorn/Vite 사용. 모든 API를 mock하지 않음. 지연 응답 사례는 실제 서버 응답을 route.fetch로 받아 지연시키는 장애 주입이다. test server는 종료됨.
- `/tmp/medipencil-staff-1280.png`, `/tmp/medipencil-family-360.png` 실제 캡처 시각 검사: 필드/텍스트/버튼 잘림 없음, 360px 수평 overflow 검사 통과. 저장소에는 이미지·trace를 포함하지 않음.
- 실제 AI/자연어 의미/전문 FI 검수는 NOT_VERIFIED. 자동 test의 사람이 누른 체크는 브라우저 자동화이며 실제 언어 전문가 검토 증거가 아니다. 종료 commit 제목 `test: C-11 verify care loop against real API and browser`.

## C-12 / 독립 합성 패키징 완료, Veil BLOCKED (C-11 commit f6d99d5)

- C-09 실제 provider 연결은 BLOCKED_PROVIDER 유지. VeilImportPort와 반입 차단 CLI만 추가했고 실제 schema·원천 자료를 읽거나 반입하지 않았다. 원본 설계·AGENTS의 역사적 상태는 보존했다.
- 설치·마이그레이션·합성 seed·단일 프로세스 loopback 실행·중지·재시작·정리 runbook, 실행 도구, wheel 검증 도구를 추가했다. run.json과 프로세스 잠금으로 실행 중 정리 차단; dry-run 기본·정확한 run ID 확인·미상 파일 보존·비재귀 삭제.
- C-02~C-11 최종 보완: 수신자별 signed cursor, chunked 포함 body 크기 제한, family/질문/job Pydantic 응답 DTO 및 OpenAPI 생성 TypeScript, 저장 board CACHED·최초 provenance, 사용자 전환 후 JSON decode 응답도 폐기. 동시 login 버튼 잠금. 원문 일부 잘라내어 부정을 뒤집는 편집은 거절하며 문구 변경에는 명시적 새 source 확인을 요구한다. UI 상태 enum을 FI 문구로 매핑했지만 전문 검수 완료로 표시하지 않는다.
- 실패/수정: openapi-typescript 설치 최초 ERESOLVE(TypeScript7과 peer ^5 불일치). --force/legacy-peer-deps를 사용하지 않고 TypeScript5.9.3 + openapi-typescript7.13.0으로 고정해 설치·생성·typecheck 통과. 패키지 검증 최초 구 wheel의 고정 origin 때문에 임시 포트 거절; 명시적 loopback 포트 설정을 허용하고 wheel 재빌드 후 성공.

### 실제 최종 명령·결과 (2026-10-03 KST)

Node 명령에는 `PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin:$PATH`를 적용했다.

| 명령 | 결과 |
|---|---|
| `.venv/bin/python -m pytest apps/api/tests -q` | 51 PASS, 1.57초; Starlette TestClient/httpx deprecation 경고1 |
| `npm --prefix apps/web run generate:api` | OpenAPI→src/generated-api.d.ts 생성 성공 |
| `npm --prefix apps/web run lint` | exit0; 현재 tsc 엄격 검사 alias |
| `npm --prefix apps/web run typecheck` | exit0 |
| `npm --prefix apps/web run test:run` | 3 PASS, 이전 응답·네트워크 실패·JSON decode 중 전환 |
| `npm --prefix apps/web run build` | exit0; use-client dependency directive 경고 있음 |
| `npm --prefix apps/web run test:e2e` | 4 PASS, 4.7초; 실제 API/SQLite/브라우저, 서버 종료 확인 |
| `/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv build apps/api --wheel --quiet --out-dir /Users/hyosang/.local/share/medipencil-preparation/package-check` | exit0, 저장소 밖 wheel 생성 |
| `.venv/bin/python tools/dev/verify_package.py --uv /Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv --wheel /Users/hyosang/.local/share/medipencil-preparation/package-check/medipencil-0.1.0-py3-none-any.whl` | 새 venv wheel 설치·CLI·두 번 실제 TCP 시작/중지·실행 중 정리 거절·dry-run/실제 정리 PASS |
| `.venv/bin/python tools/dev/benchmark.py > docs/evidence/local-performance.json` | exit0; 합성 최소 DB, AI0, 5세션/각50회. board p95 11.25ms, queue10.06ms |
| `git diff --check` | exit0 |
| Python inline Git 후보 경로 검사 및 T-ID 행 검사 | 103개 후보 경로에 DB/audio/.env/venv/node_modules/dist/trace artifact 없음; 결과표55행 |

- T-ID: T01~T10의 55개 세부 항목을 acceptance-results.md에 PASS/PARTIAL/NOT_RUN/BLOCKED로 구분했다. pytest51개를 T-ID55개 전체 통과로 간주하지 않는다. 40개 명세 endpoint가 OpenAPI에 존재하는 검사도 통과했으나 모든 DTO/행위의 완전 검증을 뜻하지 않는다.
- 테스트 자료는 버전 관리되는 TEAM_SYNTHETIC 테스트 입력과 생성 무음 WAV뿐이다. 자동 체크는 실제 FI 전문가 검수가 아니다. 실제 provider·Veil·현장 자료/효과·사람90초 시연·운영 인증은 미검증/미실행. 전체 SV/EN·화면6·스트리밍은 만들지 않았다.
- 성능은 로컬 최소자료 HTTP baseline일 뿐 임상·업무 절감 효과가 아니다. 실제 데이터·음성·키·wheel·DB·trace를 commit하지 않는다. 외부 CI·remote push·배포는 실행하지 않았다.
- 종료 commit 제목: `feat: C-12 package local synthetic demo and verification evidence`.

### C-12 변경 파일

- `.gitignore`
- `README.md`
- `apps/api/src/medipencil/body_limit.py`
- `apps/api/src/medipencil/cli.py`
- `apps/api/src/medipencil/common.py`
- `apps/api/src/medipencil/config.py`
- `apps/api/src/medipencil/db.py`
- `apps/api/src/medipencil/domain.py`
- `apps/api/src/medipencil/dto.py`
- `apps/api/src/medipencil/lifecycle.py`
- `apps/api/src/medipencil/main.py`
- `apps/api/src/medipencil/pagination.py`
- `apps/api/src/medipencil/providers.py`
- `apps/api/src/medipencil/publications.py`
- `apps/api/src/medipencil/questions.py`
- `apps/api/src/medipencil/records.py`
- `apps/api/src/medipencil/security.py`
- `apps/api/tests/helpers.py`
- `apps/api/tests/test_acceptance.py`
- `apps/api/tests/test_lifecycle.py`
- `apps/web/e2e/care-loop.spec.ts`
- `apps/web/package-lock.json`
- `apps/web/package.json`
- `apps/web/src/App.tsx`
- `apps/web/src/Board.tsx`
- `apps/web/src/Capture.tsx`
- `apps/web/src/Publication.tsx`
- `apps/web/src/api.test.ts`
- `apps/web/src/api.ts`
- `apps/web/src/generated-api.d.ts`
- `apps/web/src/labels.ts`
- `docs/development/acceptance-results.md`
- `docs/development/progress.md`
- `docs/development/runbook.md`
- `docs/evidence/local-performance.json`
- `tools/dev/benchmark.py`
- `tools/dev/export_openapi.py`
- `tools/dev/run_demo.py`
- `tools/dev/verify_package.py`

## 최종 인수인계 — 구현 commit 확인

C-12 구현·검증·패키징 commit은 **222a570**이다. 이 아래 기록은 그 결과를 연결하는 문서 변경이며 새 기능 변경이 아니다.

| 작업 | commit | 현재 결과 |
|---|---|---|
| C-01 | d9dfa83 | 로컬 기반 구현·검증 |
| C-02 | fef7df6 | 저장소·불변 version·근거 기반 구현, C-12 DTO/manifest 보완 |
| C-03 | 97f75a5 | 데모 세션·권한 구현; 운영 인증 범위 밖 |
| C-04 | d256bee, 4eb09aa | 질문·큐 구현, C-12 cursor 보완 |
| C-05 | 15e9945 | 직접 입력·검토·승인 구현, C-12 원문 충실성 보완 |
| C-06 | b6bcc87 | 발행·가족 근거 구현, C-10 센서 집계 연결 |
| C-07 | e5ae478 | 동의 후보·확인·철회 구현 |
| C-08 | ccd4d27 | 정정·무효화·rollback 구현 |
| C-09 | dfcc28d | 실제 로컬 audio cleanup·차단 경계 구현; 실제 AI BLOCKED_PROVIDER |
| C-10 | 002e2ca | 화면1~5 구현·360/1280 확인; FI 전문가 검수 NOT_VERIFIED |
| C-11 | f6d99d5, 222a570 | 51 API + 3 UI unit + 4 실제 브라우저 PASS; 상세55항목은 결과표대로 일부 미검증 |
| C-12 | 222a570 | 합성 패키지 재현 검증 완료; Veil 반입 BLOCKED_VEIL |

다음 실제 연동에 필요한 외부 정보는 허용된 로컬 STT/LLM의 모델·endpoint·재사용 조건과 FI 검토자, Veil의 제한 환경·schema·이용조건이다. 임의 외부 provider나 가짜 AI adapter를 붙여 완료 처리하지 않았다. [실행 안내](runbook.md)와 [항목별 수용 결과](acceptance-results.md)를 기준으로 이어간다.

## C-09/C-10 후속 — 설치된 로컬 STT·LLM 연결, 교체 설정 (시작 HEAD 55c2228)

- 사용자 지시: “stt와 llm은 로컬에 설치된 모델로 하고 나중에 변경할수 있도록 하자”. clean `codex/care-loop-mvp`에서 시작. 로컬 합성 추론을 허용한 지시이며 Veil/실자료/외부 AI 허가를 추정하지 않았다.
- 설치 확인: `ollama list` → llama3.1:8b, gpt-oss:20b, gemma4:26b/e2b, nomic embed. `ls -lh ~/.cache/whisper` → medium.pt, large-v3.pt. `python3` import로 Whisper20250625/Torch2.12.1 및 Python3.11 runtime 확인. 기존 Ollama 프로세스/모델을 사용하고 다운로드·설치·서비스 종료는 하지 않았다.
- 기본 선택: Whisper medium CPU4스레드 + Ollama llama3.1:8b. 저장소 밖 `~/.config/medipencil/local-models.json` 생성(0600). 모델·runtime·loopback 주소·timeout은 JSON/환경변수로 교체, 재시작 시 반영. 다른 backend는 adapter 확장으로 교체하며 도메인/승인 계층을 재사용.
- STT worker는 기존 checkpoint 절대경로만 로드, 네트워크 연결 차단, stdout으로만 전사를 반환. 실제 자식 종료 후 local upload cleanup. 타임아웃/취소 시 프로세스 종료와 늦은 결과 미저장. STT 전사는 unknown/health_context로 저장, 가족 화면의 미확인 화자를 직원 관찰로 잘못 표시하지 않도록 unattributed_statement DTO 추가.
- Ollama는 로컬 설치 모델·remote metadata 검사, proxy/redirect off, cloud fallback 없음. 현재 LLM 역할은 허용된 근거 키 선택이며 원문/화자/분류/scope를 서버가 보존. 자유 요약/번역/가족 문구 생성/자동 동의 추출을 구현했다고 보고하지 않는다. 모델이 승인·권한·질문 완료를 결정하지 않는다.
- 모델 호출은 SQLite transaction 밖 background job, 서버 revision/근거 재확인 뒤 draft/source 저장. queued/running/result/error·model hash/digest·LIVE/REPLAY·입력/STT 단계 기록. LLM 실패 시 전사 보존, manual 재시도 가능. 재시작 시 이미 완료한 STT source 보존.
- 화면3 모델 선택·실제 STT 업로드/언어/취소/전사→초안 검토 연결. 실행 모드·모델 표시. 별도 동의·승인·발행 절차 유지. 일반 테스트 서버는 disabled, 사용자의 run_demo는 로컬 설정을 읽는다.

### 실제 명령·결과와 실패 수정

1. 최초 `.venv/bin/python -m pytest apps/api/tests -q`는 editable 모듈 미등록으로 ModuleNotFoundError. `/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv pip install --python .venv/bin/python --no-deps -e apps/api` 실행 후 기존51 PASS.
2. 실제 OllamaExtraction 단일 핀란드어 근거 호출 최초 EVIDENCE_REQUIRED: 모델이 허용 목록 밖 key 반환, 저장 거절. JSON schema의 key enum도 요청의 허용 key로 제한 후 실제 재실행 PASS. 검증을 제거하지 않았다.
3. `.venv/bin/python tools/dev/verify_local_models.py > /tmp/medipencil-local-model-result.json` 두 번 실제 실행. 마지막 결과: 직접 입력+실제LLM(STT skipped), macOS say로 만든 합성 FI 음성→실제Whisper→실제Ollama→SQLite draft→명시적 테스트 승인/발행 PASS. STT7.93초/LLM1.21초. 음성 원문과 전사의 첫 단어 오류(Tämä→sama)를 숨기지 않고 docs/evidence/local-model-smoke.json에 기록. 처음 실행8.46초/1.26초와 구분. 사람 FI 검수·임상 품질 PASS 아님.
4. `.venv/bin/python -m pytest apps/api/tests -q` 최종 **62 PASS**,1.48초, Starlette/httpx deprecation 경고1. 새 adapter double은 REPLAY/ai_executed=false. 실제 모델 시험과 분리.
5. Node22 PATH 적용 `npm --prefix apps/web run generate:api`, `run typecheck`, `run test:run` → 생성/타입검사 성공,3 PASS.
6. `npm --prefix apps/web run test:e2e` 최초2 FAIL/2 PASS: 새 실행 status와 발행 status가 같은 role로 중복되어 기존 locator 모호. 발행 status에 접근성 이름을 추가하고 locator를 명확히 함. 실패·manual 전환 시험 추가 후 **5 PASS**,6.9초. 실제 API/DB/브라우저이며 실제 모델 호출은 별도 Python API smoke로 검증.
7. `npm --prefix apps/web run build > /tmp/medipencil-web-build.log 2>&1` → exit0, 기존 use-client dependency 경고 있음. 1280px 직원 화면 캡처 직접 확인, 360px 가족 화면 E2E 유지.
8. `/Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv build apps/api --wheel --quiet --out-dir /Users/hyosang/.local/share/medipencil-preparation/package-check` 성공. `.venv/bin/python tools/dev/verify_package.py --uv /Users/hyosang/.local/share/medipencil-preparation/bootstrap/bin/uv --wheel /Users/hyosang/.local/share/medipencil-preparation/package-check/medipencil-0.1.0-py3-none-any.whl` → 새 venv 설치/CLI(whisper/ollama 설정 확인)/2회 TCP 재시작/정리 PASS.
9. `git diff --check` → exit0. 생성 음성·DB·모델 가중치·설정 파일은 저장소 밖에만 존재. 증거 JSON에는 공개 가능한 독립 합성 문장·모델 식별 정보만 포함.

관련 T-ID: T02-D/T03(원문 충실·unknown 화자), T04(승인 분리), T08-B/C/E(실패/재요청/늦은 결과), T09-A/B/F(실제 로컬 삭제/redirect 거절), T10-B/C(실제 로컬 실행·STT skipped·replay). 실제 provider 미설정 blocker는 위 두 로컬 adapter의 합성 경로에서 해소했다. large-v3/다른 LLM, 실제 강제종료/장시간 timeout, FI 전문가·의료 의미 품질, 사람 시연 효과, Veil은 여전히 미검증 또는 차단. 기존55항목 전체 완료로 확대하지 않는다.

종료 commit 제목: `feat: connect configurable local Whisper and Ollama providers`.

변경 파일:
- `README.md`
- `apps/api/src/medipencil/audio.py`
- `apps/api/src/medipencil/cli.py`
- `apps/api/src/medipencil/config.py`
- `apps/api/src/medipencil/dto.py`
- `apps/api/src/medipencil/local_jobs.py`
- `apps/api/src/medipencil/local_providers.py`
- `apps/api/src/medipencil/providers.py`
- `apps/api/src/medipencil/publications.py`
- `apps/api/src/medipencil/records.py`
- `apps/api/src/medipencil/whisper_worker.py`
- `apps/api/tests/test_local_models.py`
- `apps/web/e2e/care-loop.spec.ts`
- `apps/web/src/App.tsx`
- `apps/web/src/Audio.tsx`
- `apps/web/src/Board.tsx`
- `apps/web/src/Capture.tsx`
- `apps/web/src/Publication.tsx`
- `apps/web/src/generated-api.d.ts`
- `apps/web/src/jobs.ts`
- `apps/web/src/labels.ts`
- `docs/development/acceptance-results.md`
- `docs/development/progress.md`
- `docs/development/runbook.md`
- `docs/evidence/local-model-smoke.json`
- `tools/dev/run_demo.py`
- `tools/dev/verify_local_models.py`

로컬 모델 연결 구현 commit: **a604a36**. 이 기록은 실제 커밋을 연결하는 문서 변경이다. `codex/care-loop-mvp`에 보관했으며 remote push·외부 배포는 실행하지 않았다.

## C-09~C-11 후속 — 실제 모델 브라우저 경로·취소·편집 회귀 (시작 HEAD f5f21e9)

사용자 “다음 진행” 지시에 따라 clean codex/care-loop-mvp에서 기존 승인 범위의 로컬 독립 합성 검증을 이어갔다. 새 선택 화면/외부 provider/Veil은 추가하지 않았다.

### 변경 및 발견 사항

- job polling은 이전 사용자 요청 사이의 sleep 후 새 세션으로 옛 job을 조회할 수 있었다. 세션 AbortSignal로 대기 자체를 중단하고 Audio finally의 후속 조회도 막았다.
- durable job을 canceled로 바꾸면 엔진 호출이 반환하기 전에도 다음 job이 시작될 수 있었다. 모델 실행 슬롯은 실제 호출/cleanup 종료까지 유지하고 충돌 작업은 PROVIDER_BUSY로 처리. 단일 프로세스 전제를 유지한다.
- 모델 완료 후 요청 직원의 현재 활성 상태·membership/can_review를 재검사. capture 작성자와 요청자가 다를 수 있어 requested_by 메타에 실제 요청자를 기록한다. 추론 중 권한 철회 결과는 저장하지 않는다.
- Capture의 기존 단일 editing 문자열을 모든 segment에 적용하던 문제 발견. 문장별 편집값과 출처를 분리하고 미변경 문장·scope·근거는 유지한다. correction은 무효화된 출처를 각각 새 source로 교체한다.
- 실제 모델 브라우저 화면 검사에서 evidence 고정 label이 STT도 “suora syöttö”(직접 입력)로 표시함을 발견. 사실에 맞는 “승인된 기록” label로 수정하고 실제 브라우저 회귀 assertion 추가.
- 로컬 모델 전용 Playwright config/suite 추가. 일반 suite는 disabled, 전용 suite만 LocalModels.env를 사용. 실제 모델이 없으면 실패하며 fixture로 대체하지 않는다. API 응답 mock 없이 actual Uvicorn/SQLite/Chromium/Whisper/Ollama 사용.

### 실행 명령·결과

- `.venv/bin/python -m pytest apps/api/tests -q`: 최초64 PASS/1.42초, 요청자 메타와 회귀 assertion 보완 후 **64 PASS/1.34초**. Starlette/httpx 경고1 유지. 모델 슬롯/권한 철회는 REPLAY adapter double 시험으로 표시.
- Node22 PATH에서 `npm --prefix apps/web run typecheck`: exit0.
- `npm --prefix apps/web run test:run`: **6 PASS**, 544ms(기존3 + 세션대기1 + 문장별 편집2).
- `npm --prefix apps/web run test:e2e`: **5 PASS**,6.9초. 실제 API/DB, 모델 호출 없는 회귀.
- `npm --prefix apps/web run test:e2e:local`: 최초1 PASS/17.7초, 편집 개선 후1 PASS/14.9초. 실제 녹음 허용 UI→업로드→STT→LLM→명시적 테스트 승인·발행→가족 근거 확인. 두 번째 실제 STT가 running인 동안 취소→canceled/source0/삭제 확인. 마지막 label 수정 후의 실행 결과는 아래 보완 기록.
- `npm --prefix apps/web run build > /tmp/medipencil-web-build-next.log 2>&1`: exit0/94ms, 기존 dependency use-client 경고 유지.
- `/tmp/medipencil-local-family.png` 실제 시각 검사: 가족 카드·unknown 화자·근거 표시 확인. 전사의 기존 첫 단어 인식 오류도 그대로 보존했으며 품질 PASS로 해석하지 않는다.
- `git diff --check`: exit0. 실제 음성/DB는 임시 디렉터리에서 정리, 모델은 기존 설치 사용. 증거 JSON은 TEAM_SYNTHETIC 문장·실행 식별 메타만 포함.

T-ID: T02-C/D, T06-E, T07, T08-E, T09-B, T10-B/C. 실제 모델 브라우저 경로의 미실행 항목을 해소했으나 FI 전문가/임상 품질·장시간 timeout/OS 강제종료·다른 모델·Veil·현장 효과는 여전히 미검증/차단이다. LLM 범위는 기존 근거 선택이며 가족 자유 문구 생성·자동 동의 추출은 추가하지 않았다.

종료 commit 제목: `fix: verify real model browser flow and isolate async reviews`.

변경 파일:
- `apps/api/src/medipencil/local_jobs.py`
- `apps/api/src/medipencil/publications.py`
- `apps/api/tests/test_local_models.py`
- `apps/web/e2e-local/models.spec.ts`
- `apps/web/package.json`
- `apps/web/playwright.local.config.ts`
- `apps/web/src/Audio.tsx`
- `apps/web/src/Capture.tsx`
- `apps/web/src/api.test.ts`
- `apps/web/src/api.ts`
- `apps/web/src/jobs.ts`
- `apps/web/src/segmentEdits.test.ts`
- `apps/web/src/segmentEdits.ts`
- `docs/development/acceptance-results.md`
- `docs/development/progress.md`
- `docs/development/runbook.md`
- `docs/evidence/local-browser-models.json`
- `tools/dev/e2e_api.py`

마지막 evidence label 수정 후 `npm --prefix apps/web run test:e2e:local` → **1 PASS/15.5초**. API/브라우저 서버 정상 종료 확인. 이 실행의 메타 요약을 `docs/evidence/local-browser-models.json`에 저장했다.

이번 후속 구현·검증 commit: **2a2e71a**. 아래 문서 커밋은 이 해시를 기록하며 기능 변경은 없다. remote push·공개 배포 미실행.

## 2026-10-07 PC-05 API·DB·GitHub 화면 자동 배포

현재 우선 범위는 내부 PoC다. 구현 commit `1e8b450`, 관련 T-06/T-08/T-10. workflow·API health·서버 배포 agent/launcher·package·systemd timer·SQLite 복구시험 및 배포 문서 변경. 실제 명령/파일/초기 SELinux 실패와 수정/CI 결과/실서버 DB 보존 증빙은 [PoC 검증 로그 PC-05-AUTO-API](../poc/validation-log.md#pc-05-auto-api--2026-10-07-apidb까지-자동-배포)에 기록했다.

로컬 API/배포101 PASS, GitHub101 + frontend7 + E2E11 + Pages1 PASS, 배포 후 실제 공유 DB 브라우저 시험2 PASS. Actions `37578829528` 전체 성공, 서버/API·Pages SHA 일치. 기존 20테이블의 이전 행 보존 및 DB 무결성 확인. 운영 장애 주입·외부 백업·실제 AI·사람 피드백은 미실행. 상세명세 재확정 없음.

## 2026-10-07 간편 로그인·대시보드

App.tsx/api.ts/CSS·세 언어/매뉴얼·E2E 수정. T-06/T-08/T-10. typecheck PASS, unit8 PASS, 실제 임시 API/SQLite E2E12 PASS(33.3초). 명령·초기 실패·재시험·변경 상세는 docs/poc/validation-log.md의 PC-05-LOGIN에 기록. 실제 AI·사람 피드백 미실행. 기존 비밀번호 없는 합성 PoC 접근 유지.

구현 commit `2e60e1e`, Actions `37580084511` 전체 PASS. API 자동 배포 및 GitHub Pages 새 로그인/사용자 대시보드 반영 완료, 공개 접속 검증 PASS. 상세 증빙은 PoC 로그 참조.

## 2026-10-07 6항목 시각화와 7일 추이

API dashboard/main/tests, web 차트/필터/CSS/아이콘/언어/매뉴얼/E2E 수정. 관련 T-06/T-07/T-08/T-10. API104 PASS, web unit8 PASS, E2E13 PASS 및 모바일 수정 후 대상1 PASS. 명령·실패·수정·디자인 QA 상세는 PoC 로그 PC-05-CHARTS. 실제 기록 건수만 집계하며 건강점수·AI실행·사람 피드백으로 보고하지 않음.

시각화 구현 commit `39d2be3`, Actions `37581364583` 전체 PASS. 실제 API·GitHub Pages 동일 SHA 반영 및 공개 세 역할 차트 로딩 확인.

## 2026-10-07 질문·답글 게시판

questions/DTO/read contract, App/QuestionReply/CSS/세 언어/매뉴얼/API 타입/E2E 변경. T-04/T-06/T-07/T-08/T-10. API105 PASS, unit8 PASS, E2E14 PASS, 후속 대상1 PASS. 실제 명령·초기 실패/수정/재시험 및 파일은 PoC 로그 PC-05-QUESTION-BOARD 참조. 질문 저장/재조회, 게시글 내 답글 작성·승인·발행·가족 열람, 다른 가족 격리 검증. AI·사람 피드백 미실행. 발행 전 진행 상태 새로고침 복원 미지원.

질문 게시판 구현 `1f67ed9`, Actions `37582803021` 전체 PASS. API/Pages 동일 SHA 반영 및 외부 세 사용자 게시판 표시 확인. SSH 조회 차단은 우회하지 않았으며 자동 배포 완료.

### 2026-10-07 PoC 보호자·간호사 역할 정리
- Aino는 비로그인 돌봄 대상자, Liisa/Mikko 보호자·Koskinen 간호사로 명확화. 수신자별 현재 공유 범위를 대시보드에 표시하고 서버 격리 재검증. API106/unit8/실제 서버 E2E15 PASS. 변경 파일·명령·미실행·배포 추적: `docs/poc/validation-log.md` PC-05-GUARDIANS. 기존 동의/질문 보존, 실제 AI/사람 피드백 아님.

### 2026-10-08 핵심 가치 중심 로컬 수정
- 사용자 PPT의 핵심 가치에 맞춰 보호자 안부 우선/간호사 질문 우선, 날짜별 공개 기록 탐색, 7일 그래프 보조 정보화를 구현. 로컬 브랜치 `codex/local-daily-update`; GitHub push/운영 배포 미실행(사용자 지시). 상세 변경 파일·명령·시험 실패/재시험·로컬 시연·커밋: `docs/poc/validation-log.md` PC-05-DAILY-VALUE.

### 2026-10-08 상세조회 기간 선택
- 안부 상세/그래프의 최근3·7·30일 및 사용자 지정기간(하루~90일) 구현. API 현재권한 기반 기간 집계 및 입력검증 추가. 로컬-only, GitHub/운영 미반영. 파일·명령·실패/재시험·커밋은 `docs/poc/validation-log.md` PC-05-PERIOD 참조.

### 2026-10-08 사람 중심 안부 프로세스
- PPT의 Aino/Liisa 시연 사진·이름, 어제/오늘 공개 원문 비교 및 항목 질문 초안→기존 간호사 답글 흐름 연결. 효과측정 이전 프로세스 개선을 우선. 로컬-only. 변경/명령/실패재시험/커밋 추적: `docs/poc/validation-log.md` PC-05-PERSON-PROCESS.

- 2026-10-08 PC-05-MIKKO-PHOTO: 사용자 요청으로 Mikko 웹 사진 적용 및 로컬 안부/기간 개선 GitHub 반영 진행. 실제 검사/통합/배포 결과는 `docs/poc/validation-log.md` 참조.

- 2026-10-08 PC-05-FAMILY-EVENTS: 미반영 원격 브랜치 문서를 먼저 병합하고 가족확인사항/합성 병원 일정 알림·수신 확인 구현. 실제 EMR 연결 없이 컨셉만 구현하라는 사용자 지시 적용. 변경 파일·명령·실패/재시험·배포는 `docs/poc/validation-log.md`, 사용 안내는 `docs/poc/family-events.md`.

- 2026-10-08 PC-05-ROLE-LOGIN: 보호자/직원 별도 로그인 화면, 계정 선택+로그인, fi/ko/en 및 모바일 적용. 비밀번호 없는 합성 PoC 정책 유지. 명령/실패수정/커밋·배포는 `docs/poc/validation-log.md`.

- 2026-10-08 PC-05-RETIRE-GUARDIAN: Mikko 계정·세션·접근 비활성화(이력 보존), 보호자 비공개 카드/공유배지/그래프/선택/표 숨김, 활성 계정 기반 수신자 UI. 명령·시험·커밋·배포는 `docs/poc/validation-log.md`.

### 2026-10-08 보호자 첫 화면 → 시각 대시보드

로그인 후 요약 카드·7일 그래프를 먼저 보여주고 기존 긴 안부 화면을 상세보기로 분리. 실제 API의 현재 공개 정보만 표시. 타입/빌드, 단위 11, API 113, E2E 22 및 최종 수정 회귀 4 PASS. 파일·명령·T-ID·미실행 항목은 `docs/poc/validation-log.md`의 같은 날짜 항목 참조. 구현 커밋 제목: `Add guardian overview dashboard and separate care details`.

- 공개 배포 완료: 구현 `2911e9f`, Actions `37787357358` 전체 SUCCESS. GitHub Pages와 Sungah API 버전 일치, 공개 로그인→대시보드→상세보기 자동 확인 PASS.
