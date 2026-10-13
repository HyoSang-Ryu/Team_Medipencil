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

### 2026-10-08 카드 중심 요약 개선

사용자 모바일 참고 이미지의 정보 계층을 반영하여 최근 원문과 공유 관리 항목을 그래프보다 먼저 표시. 타입/빌드·단위11·관련 E2E2 PASS. 변경 파일·명령·T-ID·검증 한계는 PoC validation-log와 design-qa.md 참조.

### 2026-10-08 직원 EMR 검토 흐름

직원 로그인→가족 안내 검토함→합성 EMR→초안 저장/재개→원문 대조·승인→별도 가족 발행 구현. API114/단위11 PASS, 기존 E2E22 및 새 흐름 수정 후 개별1 PASS; 최종 CI는 후속 확인. 로컬 llama3.1:8b 실제 근거 선별 1회 성공(3문장 중2개), 공유 서버는 AI 미실행 시연. 관련 파일·실행 명령·실패/수정·T-ID·한계는 PoC 검증 로그 참조. 구현 커밋 제목 `Center staff workflow on synthetic EMR draft review`.

- 배포 완료: `7417b4f`, Actions `37795683992` 전체 SUCCESS(E2E23 포함). Pages/API 버전 일치, 직원 로그인 검토함 첫 화면 공개 검증 PASS.

### 2026-10-09 보호자 일괄 발송

4단계 보호자 체크박스·전체 선택·개별 공개 범위 미리보기·일괄 발송·개별 결과/중복 방지 구현. 타입/빌드·단위11·전체 E2E24 PASS. 파일·실행 명령·실패 수정·T-ID·제한은 docs/poc/validation-log.md 참조. 커밋 제목 `Support guardian checkboxes and bulk publication`.

- 배포 완료: `2444e80`, Actions `37817752065` 전체 SUCCESS. 공개 Pages/API SHA 일치 및 정상 응답 확인.

- 2026-10-09: 요양원 4개 대안 시나리오·180건/30일 합성자료를 로컬 HTML/Excel/CSV/JSON으로 작성. 서비스 반영 없음, 커밋 없음. 상세 검증은 PoC validation-log 참조.

- 2026-10-10: 동의 검토 보호자 목록 자동 조회·선택별 범위/후보/철회 필터·확인 초기화 수정. 타입/빌드·단위11·동의 브라우저 회귀1 PASS. 명령·실패·재시험·T-ID는 PoC 검증 로그 참조.

- 동의 검토 수정 공개 반영 완료: c139199, Actions 37961183694 전체 SUCCESS, Pages/API 버전 일치.

- 2026-10-10 동의 간소화: 보호자별 체크박스·변경 요약·동의 확인 기록·원자적 저장, 기존 이력 보존. API115/단위11 PASS, 브라우저23 및 매뉴얼 수정 재시험1 PASS. 실제 파일·명령·실패·T-ID는 PoC validation-log 참조.

- 간소화 공개 배포 완료: d67936f, Actions 37968136287 전부 SUCCESS. 공개 직원 동의 설정 화면/7항목 직접 확인, 운영 동의 변경 없음.

### 2026-10-11 GitHub 이슈 프로그램 반영

GitHub #8~11의 동의 스위치·전체 이름·보호자 세로 카드·4개 상세 패널·쉬운 막대그래프 수정, #12 담당 권한 목록/병동·질문 수·바로 답글 입력 부분 반영. 기존 최초 설정 후 매일18시 합성 일상 자동 전달 작업도 통합한다. 실제 교대 편성·복수 환자 작업공간, 일반 AI 무검토 발행은 완료 아님. API120/프런트 단위12 PASS, 브라우저25 PASS/1 FAIL에서 표시명/actor_id 혼용을 수정하고 최종 회귀 중. 파일·실제 명령·실패 및 미실행·T-ID는 docs/poc/validation-log.md, 이슈별 범위는 docs/poc/github-issue-review.md 참조. 구현 커밋·공개 배포 결과 후속 기록.
- 최종 전체 브라우저26 PASS/1.8m, 타입·빌드·OpenAPI·매뉴얼 생성 PASS. 구현 커밋 제목 `Apply care dashboard feedback and enable scheduled synthetic updates`.
- 공개 배포 완료: 구현 bf4c0e8, Actions38125591968 전 단계 SUCCESS. API/Pages SHA 일치, 공개 브라우저에서 전체 이름·상세4탭·동의7스위치·모바일 표시 확인 PASS. 관련 실행 명령·초기 검사 스크립트 타이밍 실패/재시험·미완료 범위는 PoC 검증 로그 참조.

## 2026-10-11 PC-05 현재 시간 기준 안부 문구 (FB-TIME-01)

- 출발: `90e8824`, `codex/family-events`; 기존 .venv/node_modules 링크 및 primary의 중복 이름 untracked 파일 보존.
- 변경: GuardianDashboard/Board 공통 useCareMessage·careMessage, fi/ko/en 문구. 핀란드 현지 18시 전/후와 오늘 관찰 기록 여부를 구분; 서버가 확인한 활성 미래 일정만 다음 전달로 표시. 10초/탭 복귀 시 시계 갱신. 이전 기록 날짜 유지, 언어 미제공과 항목 미전달 구분. 정기 전달 설정 자체는 변경하지 않음.
- 실행: Node22 PATH에서 `npm --prefix apps/web run typecheck`, `npm --prefix apps/web run test:run`, `npm --prefix apps/web run build` PASS (단위 15건; 기존 번들크기/use-client 경고).
- 실행: `NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run test:e2e -- care-message.spec.ts issue-feedback.spec.ts recurring.spec.ts` 3 PASS/17.2s. `git diff --check` PASS.
- 시험: 여름/겨울 Helsinki 18시·자정·중지/다음날/기한 지난 일정·오늘 기록. 브라우저 시간 이동 시험은 합성 API 응답 fixture이며 실제 정기 작업 실행 검증으로 주장하지 않음. 기존 브라우저 공유설정/정기설정 흐름도 회귀 실행.
- T-ID: T-05/T-06 공개 범위·가족 표시 회귀. 실제 AI/EMR/핀란드어 전문가 검수/현지 효과 검증 미실행. 서버 코드 변경 없음으로 전체 API 시험은 이번 회차 미실행.
- 커밋: 이 항목을 포함한 `Adapt family update messages to Helsinki time and delivery schedule` 커밋. 배포 확인은 후속 기록.

## 2026-10-11 PC-05 항목별 상황 안내·표시 예시 (FB-TOPIC-01)

- 출발 `9bb95d7`, codex/family-events, 기존 untracked 링크 보존. 변경: careTopicMessages/TopicMessage, GuardianDashboard/Board, style.css, fi/ko/en 및 회귀 시험.
- 일곱 허용 관리 항목의 빈 상태에 핀란드 18시 전후의 서로 다른 합성 예시를 표시. 각 예시에 “표시 예시 · 실제 돌봄 기록 아님” 명시. 실제 공개 기록이 있으면 예시를 대체하지 않고 원문·이전 날짜·계획 설명 유지. 비공개 항목 및 언어 미제공에는 예시를 노출하지 않음. 서버 저장/AI 생성/정기 전달 데이터는 변경하지 않음.
- 명령: Node22 PATH, `npm --prefix apps/web run typecheck`, `npm --prefix apps/web run test:run`, `npm --prefix apps/web run build`; 최종 PASS/17 단위시험. 기존 번들크기/use-client 경고 유지.
- 명령: `NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run test:e2e -- care-message.spec.ts issue-feedback.spec.ts`; 최종 2 PASS. 시간 이동·일곱 예시는 합성 API fixture UI 시험, 실제 AI/EMR 검증 아님. 공유 설정/역할/탭 회귀는 로컬 API·DB 사용.
- 최초 typecheck 및 브라우저 2건 실패: macOS 대소문자 비구분 파일 해석에서 TopicMessage.tsx/topicMessage.ts 충돌. 도우미를 careTopicMessages.ts로 변경하고 서버를 재시작하여 재시험 통과. 실패 증빙 /tmp/topic-e2e.log, 재시험 /tmp/topic-e2e2.log. `git diff --check` PASS.
- T-ID: T-05/T-06 공개범위·가족 표시 회귀. 핀란드어 전문가 검수·현지 효과 검증 미실행. 프런트엔드만 변경하여 전체 API 시험 미실행.
- 커밋: 이 로그를 포함한 `Show topic-specific contextual examples for empty care updates`. GitHub 자동 배포 완료 여부는 별도 확인 필요.

## 2026-10-11 PC-05 실제 로컬 AI 가족 안부 생성 (FB-AI-SUMMARY-01)

- 출발: d1632fb / codex/family-events. 기존 .venv/node_modules 링크 및 primary의 중복 이름 untracked 파일 보존.
- 변경 파일: synthetic_emr.py(1~30일 독립 합성 식사/이동/수면·미확인 산책 계획), ai_wording.py(교체 가능한 로컬 Ollama 안부 종합), ai_summary.py(비동기 영속 작업·결과 재열람), main.py 라우팅, publications.py 근거 재검사·가족 원문 반환; Publication/StaffReview/Board/GuardianDashboard/dailyUpdate, fi/ko/en, OpenAPI·매뉴얼·ai-family-summary.md 및 API/브라우저 시험.
- 입력 전 보호자 권한·출처 검사, 추론은 DB 쓰기 트랜잭션 밖, 결과 저장 전 동의/자료/접근 재검사. 새 숫자·잘못된 구조·계획 완료 오인 일부 기계검사. 자유 생성은 직원 검토 후 발행. 현재 18시 확정 원문 자동 전달은 그대로이며 자유 생성 AI 자동발행은 미구현. 공유 PoC 모델 비활성 정책 유지, 화면에 비활성 안내.
- 실제 실행 명령: `PYTHONPATH=apps/api/src .venv/bin/pytest -q` 최종 134 PASS (/tmp/ai-api-last.log). Node22 PATH에서 `npm --prefix apps/web run typecheck`, `npm --prefix apps/web run test:run` 17 PASS, `npm --prefix apps/web run build` PASS(기존 번들/use-client 경고). `PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run generate:api`, `python3 tools/dev/export_manual.py`, `git diff --check` PASS.
- 일반 브라우저: `NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run test:e2e` 27 PASS/1.9m; 이후 추가된 `-- ai-summary-disabled.spec.ts` 1 PASS/3.3s. 이 시험은 실제 AI 호출 없음.
- 실제 AI 브라우저: `MEDIPENCIL_LLM_BACKEND=ollama MEDIPENCIL_LLM_MODEL=gpt-oss:20b MEDIPENCIL_AI_TIMEOUT=240 NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 PYTHONPATH="$PWD/apps/api/src" npm --prefix apps/web run test:e2e:local -- ai-summary.spec.ts` 최종 1 PASS/14.9s (/tmp/ai-real-browser-verified.log). 별도 직원/가족 브라우저, 실제 임시 서버·DB·모델, 재로그인 후 저장 결과 복원, 공개 AI 표기·원문 조회 확인. 테스트의 검토 체크는 자동 전달경로 시험이며 사람의 핀란드어 검수 아님.
- 실제 추론: llama3.1:8b 3일 18.98초, gpt-oss:20b 3일 16.19초의 API 시험 및 gpt-oss:20b 최종 브라우저 실행. gpt-oss:20b 30일 24.69초는 생성·DB·발행·근거 전달경로 통과이나 긴 날짜 목록의 월 표현이 모호해 언어/의미 품질 PASS로 간주하지 않음. 3일 기본 시연 권장, 전문가 검수 미완료.
- 실패/수정: 최초 실험 임시 DATA_ROOT symlink 거부→resolve 수정. 모델의 개별 원문 나열/근거 누락·Gemma 출력 형식 오류·30일 JSON 복사 및 미확인 계획을 미실행으로 서술하는 품질 문제 확인. 그룹별 문장 계약·원문/날짜 보존 압축·JSON 복사 차단·계획 확인 문구 검사 추가. 숫자/형식 검사가 의미 완전성을 보장하지 않아 사람 검토 유지. 초기 immutable consent 시험 fixture UPDATE 실패→새 동의 버전 INSERT로 수정. 입력 압축 편집 중 Python 구문 오류→수정 후 전체 재시험. 중간 실브라우저는 HMR 영향 및 새로고침 뒤 로그인 누락으로 실패/중단→재로그인 절차로 최종 재시험 통과. 실제 추론 실패 시에도 완료 응답을 받은 경우 ai_executed=true와 실패코드를 보존.
- 관련 T-ID: T-01~T-06 입력·AI 실패·근거·발행·권한 경계; 실제 병원 EMR/STT/의료 효과·현지 피드백은 미실행. 기존 네 가지 30일 가족 시나리오 전체 연결은 미구현. 실제 모델 설치/다운로드나 외부 cloud 호출 없음.
- 커밋: 이 로그를 포함한 `Add evidence-linked local AI family summaries from synthetic EMR`. GitHub push/자동 배포 여부는 별도 확인. 공유 서버에서는 실제 AI 실행을 주장하지 않음.

## 2026-10-12 PC-05: unavailable model in EMR draft selector
- FB: screenshot shows local LLM/no model with enabled generation; T-05/T-10 provider failure and honest execution labels.
- Start HEAD 30430f7, codex/family-events; only untracked .venv and node_modules symlinks, preserved.
- Files: apps/web/src/Capture.tsx (loading/configured state, disabled local option, guarded generation, fi/ko/en existing notice); Audio.tsx (handle shared provider lookup rejection); e2e/ai-summary-disabled.spec.ts (model absent/fetch failure, keyboard selection block, real manual draft creation).
- Commands: Node22 PATH npm --prefix apps/web run typecheck PASS; npm --prefix apps/web run build PASS (existing directive warnings); PYTHONPATH=$PWD/apps/api/src npm --prefix apps/web run test:e2e -- ai-summary-disabled.spec.ts final 3 PASS / 4.2s, temporary API/SQLite.
- Intermediate test failures: wrong translated button name; Playwright option disabled matcher required DOM disabled property plus keyboard check; reused daily EMR bundle already drafted; ambiguous supplementary link. Corrected test targeting and used separate direct-input captures. Provider failure also exposed Audio unhandled rejection; caught and retested cleanly. No tests skipped.
- Actual AI NOT_RUN; shared-server model still unconfigured. No server model connection or AI deployment claimed. Commit: this change's commit (fix unavailable local model selection); GitHub deployment status reported separately.

## 2026-10-12 PC-05: Korean synthetic EMR content review
- User feedback: menus alone do not allow Korean reviewers to check Finnish EMR content. Start d17dbb7 / codex/family-events, only existing untracked dependency symlinks preserved.
- Changes: ReviewText.tsx and reviewTranslation.ts display Korean explanations beside unchanged Finnish originals in Capture, StaffReview inbox and Publication statements/evidence. Includes three screenshot fixture sentences and 30-day meals/movement/sleep/plan vocabulary, retaining quantities and dated evidence. style.css adds readable bilingual layout. Editing and stored evidence remain original.
- Explicit scope: curated synthetic-example display translation, NOT AI translation or Finnish expert verification. Unknown/free-form AI output says Korean review text unavailable; never guessed or silently substituted. Actual AI and shared-server model connection NOT_RUN.
- T-02/T-03 meaning, plan/confirmation and evidence preservation; T-10 honest processing labels.
- Actual commands (Node22 PATH): npm --prefix apps/web run typecheck PASS; npm --prefix apps/web run test:run 19 PASS; PYTHONPATH=$PWD/apps/api/src npm --prefix apps/web run test:e2e -- korean-review.spec.ts 1 PASS / 2.9s, real temporary API/SQLite manual draft; npm --prefix apps/web run build PASS (existing bundler warnings); git diff --check PASS. No failed/ skipped cases in this change.
- Commit: this change (Add Korean review text beside synthetic EMR originals). Push/deployment tracked separately; no live deployment claim from local tests.

## 2026-10-12 PC-05: CI deployment gate regression repair
- Actual GitHub run 38237943509 FAILED: old local-AI failure test selected a now-disabled option; Korean EMR test consumed the same daily synthetic bundle as staff-review. Live Pages remained 30430f7; previous push was not deployment completion.
- Files: e2e/care-loop.spec.ts now simulates stale provider configuration only, exercising real API PROVIDER_NOT_CONFIGURED then manual recovery; e2e/korean-review.spec.ts uses independent supplementary capture for draft translation and leaves daily EMR fixture available. No skips or weakened production checks.
- Node22 PATH + PYTHONPATH=$PWD/apps/api/src npm --prefix apps/web run test:e2e: 31 PASS / 1.9m. Evidence /tmp/medipencil-full-ci-fix.log. T-05/T-10 failure and recovery; T-02/T-03 bilingual evidence; no real AI executed.
- Commit: this change, Fix browser test isolation and stale provider failure coverage. New CI/deployment outcome must be checked separately.

## 2026-10-12 PC-05: deployment verified
- GitHub Actions run 38239400470 SUCCESS: build, publish-api, deploy-api, deploy-pages, verify-pages all completed. https://github.com/HyoSang-Ryu/Team_Medipencil/actions/runs/38239400470
- Commands: gh run view 38239400470 --json status,conclusion,jobs; curl -fsS https://hyosang-ryu.github.io/Team_Medipencil/build-info.json; curl -fsS https://orch.sungah.kr/medipencil/api/v1/health. Both live revisions match 392c09378865da837220325855cec07e60a3a5f4, API status ok, checked 2026-10-12 14:10 Europe/Helsinki.
- Actual hosted browser: Korean language → staff login → synthetic EMR view. Confirmed Korean meal/movement/unconfirmed outdoor-plan explanations with Finnish originals; unavailable local model option disabled. Did not generate/approve/publish new production care records during this check.
- Local-model server connection remains unavailable; not represented as actual AI verification. Translation covers independent synthetic fixture vocabulary, free-form AI translation remains unimplemented. T-02/T-03/T-10, deployment smoke verification PASS.
- Docs-only evidence commit follows deployed code and is ignored by workflow paths-ignore; deployed application revision remains 392c093.

## 2026-10-12 PC-05: Adobe XD design — LOCAL ONLY
- User supplied XD 286725f5-3afb-4089-b35c-8e906ed53f58-7d34 and explicitly requested local-only application. HEAD 981f8d3 on codex/family-events; existing dependency symlinks left untracked. No push, merge into primary, GitHub Actions trigger or production deployment for this change.
- Files: Login.tsx (photo/resident card/role panels), App.tsx (role-specific shell), GuardianDashboard.tsx (compact counts), Board.tsx (native evidence dialog and history ordering), main.tsx + xd-theme.css (blue/charcoal XD theme, responsive), assets/xd-care-hero.png (generated photo, original XD photo unavailable), design-qa.md.
- Reference: all 7 XD screens inspected in in-app browser. Local visual comparisons and 390px/1280px/1920px checks completed; see design-qa.md. Retained existing routes, roles, source evidence, consent and synthetic labels.
- Commands: Node22 PATH npm --prefix apps/web run typecheck PASS; npm --prefix apps/web run test:run 19 PASS; npm --prefix apps/web run build PASS (existing warnings, /tmp/xd-build.log); git diff --check PASS. PYTHONPATH=apps/api/src .venv/bin/python tools/dev/run_demo.py --poc --port 8778 --data-root /private/tmp/medipencil-xd-preview-data starts local-only persistent synthetic preview.
- Browser: direct synthetic import→manual draft→simulated review→approval→publication→guardian retrieval, period 7-day switch, family-confirmation tab, evidence modal/Escape, mobile overflow checks PASS; console errors none. T-01/T-02/T-03/T-10 relevant smoke checks, not exhaustive regression or actual AI/Finnish expert validation.
- Build initially had portrait crop, low-contrast staff subtitle, squeezed tabs and excessive comparison whitespace; fixed and recaptured. CLI E2E suite NOT_RUN this iteration; GitHub/production deployment intentionally NOT_RUN per user instruction. Local commit contains these changes; remote remains unchanged.

## 2026-10-12 PC-05: two-host design comparison
- User now authorizes deploying the XD version to Sungah while retaining the previous design on GitHub Pages. This supersedes local-only delivery for the XD design; historical entries remain unchanged.
- Files: designVariant.ts, LegacyLogin.tsx, Login/App/Board/GuardianDashboard/main, build.yml, design-variant.spec.ts. Explicit xd build uses new styling/dialog; default and Pages legacy builds retain previous styling/login/evidence panel. Both keep the shared API/DB and permission checks.
- Commands: Node22 npm --prefix apps/web run typecheck PASS; npm --prefix apps/web run test:run 19 PASS; VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build PASS; default npm --prefix apps/web run build PASS. Existing bundler warnings remain. CI adds XD login/navigation smoke checks alongside full legacy regression.
- T-01/T-02/T-10: role navigation, source UI, truthful synthetic/AI labels. Actual AI and Finnish expert review NOT_RUN. Deployment pending verification after push; commit: this change, Split Sungah XD and GitHub Pages legacy designs for comparison.

- Comparison CI 38244375585 FAILED only new smoke selector: two date-presets exist (board and chart). Existing 31 browser tests PASS. Scoped selector to .daily-board .date-presets; no checks skipped. Commit: Scope design comparison test to board date controls. Deployment blocked by CI until rerun passes.

## 2026-10-12 PC-05: comparison deployment verified
- Deployed code 33196b0e1517477ff8901c7baa36623eba665d90. Actions 38244906092 SUCCESS: build, publish-api, deploy-api, deploy-pages, verify-pages. API 134 PASS (one warning); frontend 19 PASS; legacy browser 32 PASS; XD browser 3 PASS; public no-VPN smoke 1 PASS.
- Actual commands: gh run view 38244906092 --json status,conclusion,jobs; gh run view 38244906092 --log; curl -fsS https://orch.sungah.kr/medipencil/api/v1/health; curl -fsS https://hyosang-ryu.github.io/Team_Medipencil/build-info.json. Both live revisions match; Pages design=legacy; API status=ok.
- In-app browser opened both public URLs and logged in as the same synthetic guardian Liisa in separate origin sessions. Sungah blue XD dashboard and Pages green previous dashboard visibly confirmed with matching published source statements/date and recurring schedule. No care records changed in production verification. Screenshot evidence captured inline; no local screenshot artifact exported.
- Compare https://orch.sungah.kr/medipencil/ (XD) and https://hyosang-ryu.github.io/Team_Medipencil/ (previous). Shared API/DB; login independently. T-01/T-02/T-10 relevant automated and hosted smoke PASS; actual AI/Finnish expert validation NOT_RUN. Generated hero is a substitute, not the original XD photograph.
- Documentation evidence commit follows deployment; docs-only commit does not trigger another deployment.

## 2026-10-12 PC-05: XD guardian landing graphs
- User asks for visualization on first guardian page in new design. GuardianDashboard.tsx now mounts existing DashboardCharts family/compact immediately below profile; xd-theme.css adds blue/white responsive chart styling. Pages legacy is unchanged.
- Existing server-filtered dashboard API supplies visible topic counts and seven-day daily counts; no invented health score, no hidden topics. Existing offline/error masking preserved. design-variant.spec.ts verifies XD-only chart, visible topics, item filter, 390px overflow, offline masking and reconnect.
- Commands: Node22 npm --prefix apps/web run typecheck PASS; npm --prefix apps/web run test:run 19 PASS; VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build PASS. In-app browser local guardian login confirms chart/real local synthetic SQLite data and desktop layout. T-01/T-03/T-10. Actual AI/Finnish expert review NOT_RUN. Commit: Show seven-day care charts on XD guardian dashboard. Deployment results follow CI.

- Deployment verification: Actions 38248844160 SUCCESS (all jobs). Deployed commit 9862ba054f7f44607f30a6ef8a9daebacf5c87cf matches Sungah health and Pages build-info (legacy). Commands: gh run view 38248844160 --json status,conclusion,jobs; curl both health/build-info endpoints. Hosted Sungah guardian login shows seven-day topic distribution/trend from shared DB, visual screenshot captured inline. Local mobile 390px document width=390 PASS. No production care data mutated; actual AI NOT_RUN. Documentation-only evidence commit follows deployment.

## 2026-10-13 PC-06 candidate: mobile voice charting design record
- User requests saving discussed design and local dataset analysis. Added docs/poc/mobile-voice-charting-design.md: mobile staff/family UX, four charting domains, conditional missing questions, provenance, one-review/two-output direction, existing vs proposed capabilities and test scope. Not final product specification or implemented feature.
- HEAD 7d0419a; primary poc/remote-validation. Existing unrelated untracked files preserved. Previous /tmp worktree lost Git metadata; read-only discovery reported not-a-repository, continued in primary checkout. No reset/prune.
- Dataset analysis artifacts kept exclusively outside repository; no dataset content/derived results included here. Commands: git status/log; local directory/README/schema inventory; local Python JSONL profiling script. No app tests needed for documentation-only change. No external AI, training, service import or deployment. T-01/T-02/T-03/T-05/T-10 planning links only. Commit: Document mobile voice charting and guardian workflow proposal.

## 2026-10-13: data source versus voice capture mapping
- User requested Markdown of the preceding classification. Added docs/poc/data-source-and-voice-capture-mapping.md: existing background/history vs new observations across ①–④, separate consent/account settings, provenance, conditional missing questions and guardian display rules.
- HEAD 0ab54cc; existing untracked files preserved. No raw dataset/derived statistics added. No application changes, data import, AI execution, push or deployment.
- Validation: git diff --check PASS; checked document headings and related local design link. Application tests NOT_RUN (documentation only). T-02/T-03/T-10 planning references, not new test completion. Commit: Document existing data and voice capture responsibilities.

## 2026-10-13: task 2.2 core scope, voice phase two
User explicitly prioritizes consent-based family daily-life information and moves voice charting to phase two. Added family-daily-life-core-scope.md, linked README, and marked both previous voice documents as secondary references. Preserved historical design and existing features. git diff --check PASS; documentation only, no application tests/AI/data import/deployment. T-02/T-03/T-10 planning references only. Commit: Prioritize family daily-life overview and defer voice charting. No push.

## 2026-10-13: implementation summary and online-team data planning
- User requested two Markdown documents. Added task-2-2-implementation-summary.md (data usability, missing data, existing PoC vs remaining phase-one/phase-two work) and online-team-data-planning.md (P0/P1 inventory, proposed exchange fields, independent synthetic scenarios, role discussion, acceptance checklist and decision log).
- HEAD 366c164; unrelated untracked files preserved. No dataset rows/derived statistics copied. Proposed owners/size/deadlines distinguished from actual agreement; no messages sent to team.
- Validation: git diff --check and relative-link existence checks PASS. Documentation only; application tests/AI/import/deployment NOT_RUN. T-02/T-03/T-05/T-10 planning references only. Commit: Document task summary and online-team data acquisition discussion. Local only, no push.

## 2026-10-13: apply Sungah XD design to GitHub Pages
User now requests the Sungah design on Pages, superseding previous two-design comparison. HEAD 3a8da89; existing untracked files preserved. Changed build.yml Pages VITE_MEDIPENCIL_DESIGN and build-info design to xd; same shared API/DB and hash routes. Existing XD guardian graphs included. T-01/T-03/T-10 deployment smoke scope. No dataset content included; no actual AI execution. Local build and CI/deployment evidence follows. Commit: Apply Sungah XD design to GitHub Pages.

- Verified deployment: 26f8afba44a17f40ba0867fbbe1b7e6278e4a368; Actions 38367146680 SUCCESS, all jobs. Exact Pages env local npm build PASS; gh run view and live build-info/health confirm same revision, Pages design=xd. In-app browser confirms XD login and Liisa guardian landing with seven-day charts on GitHub Pages. No production care records changed. No actual AI executed. Documentation-only verification commit follows deployment.

## 2026-10-13: local voice recording and four-domain charting
- User requested voice processing, then explicitly local-only and a separate recording screen. Start HEAD 689fe0d, branch poc/remote-validation; unrelated `* 2.*` files preserved. No push or deployment.
- Changes: API voice_charting.py, migration 007 and main router; API test_voice_charting plus migration fixture/table-count updates; web VoiceCharting, Microphone, PCM worklet/wav encoder and tests, Audio integration, App staff-only /staff/voice, three UI dictionaries, style.css, generated-api.d.ts; docs/poc/voice-charting-local.md and validation log. StaffReview returned to its prior source: voice editor moved to dedicated route.
- Function: microphone start/stop/local preview, max 180s/20MiB, explicit submit to existing STT upload; selected 14-field checklist, exact keyword evidence candidates, explicit unanswered/confirmed/unknown/not-applicable/follow-up, persisted resume/revision, staff evidence and existing draft review/approval. No automatic diagnosis, completion or family publication. Existing source scopes plus health_context preserved.
- Commands: `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q` → 127 PASS (one existing Starlette deprecation warning). Node PATH=/Users/hyosang/.local/share/medipencil-preparation/node-v22.16.0-darwin-arm64/bin: `npm --prefix apps/web run typecheck` PASS; `npm --prefix apps/web run test:run` → 23 PASS / 8 files; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS (existing directive/chunk warnings); `PYTHONPATH=../../apps/api/src npm --prefix apps/web run generate:api` PASS; `git diff --check` PASS.
- Initial failures fixed: TS closing-tag/duplicate-property errors; migration simulation still contained the new table and expected old count (fixture reconstruction updated); OpenAPI generation lacked PYTHONPATH (rerun with correct path); new microphone mock test type syntax/cast (fixed). Tests were not skipped. UI date field automation did not populate a value; server rejected EVIDENCE_REQUIRED, then explicit current-observation-time control and completion guard verified. No clinical timestamp was inferred silently.
- Local run: `PYTHONPATH=apps/api/src .venv/bin/python tools/dev/run_demo.py --poc --port 8780 --data-root /private/tmp/medipencil-voice-20261013`; restarted this exact loopback process after final backend edit. Separate DB, STT/LLM disabled.
- Browser: staff login, synthetic transcript, selected food/mobility/medication, no auto-confirmation, follow-up reason, save → review draft visible in inbox; final separate /staff/voice with microphone controls, saved chart resume after login, 390px layout no horizontal overflow. Screenshot outside repo /private/tmp/medipencil-voice-screen.png.
- Related T-01/T-02/T-03/T-04/T-06/T-07/T-08/T-09/T-10 cases only. Actual microphone hardware, real STT/LLM, handset, Finnish expert review and human workflow feedback NOT_RUN; mocked microphone unit cases are not real audio validation. Follow-up audio merging, conversational AI, actual EMR writing remain unimplemented.
- Local implementation commit: `Add local voice recording screen and reviewed charting workflow` (commit subject; hash recorded by Git). No GitHub/sa-app changes.

## 2026-10-13 — local STT configuration correction
User asked why STT was disabled. Confirmed existing ~/.config/medipencil/local-models.json points to installed Whisper medium.pt and Python 3.11 runtime; imports report Whisper 20250625 / Torch 2.12.1. `--poc` forces disabled twice (launcher and Settings). Removed that flag when restarting only our 127.0.0.1:8780 server with the same synthetic DB. A tentative --local-models launcher edit was ineffective due to Settings and fully reverted; no application source change retained. Final command: `PYTHONPATH=apps/api/src .venv/bin/python tools/dev/run_demo.py --port 8780 --data-root /private/tmp/medipencil-voice-20261013`. Authenticated GET /api/v1/staff/providers confirms whisper/medium.pt, ollama/llama3.1:8b, external_ai=false. Initial verification assumed bearer token; local mode uses cookie, corrected HTTP client verification PASS. Real transcription/model inference NOT_RUN. T-09 configuration only; docs updated, diff check PASS; local commit subject Clarify and enable existing local STT configuration; no push/deployment.

## 2026-10-13 — local incremental STT, referencing existing MediPencil
- User requests live STT and says to reference the prior MediPencil implementation. Start acf9f51, poc/remote-validation. Local-only remains in force. Read standalone app.jsp PCM/VAD/chunk/polling code; reused the approach with 6-second minimum + 0.6-second silence / 12-second forced split, not its external service configuration or failure-as-completed behavior.
- Changed main.py + new live_speech.py/whisper_live_worker.py; Audio.tsx queue/provisional display/explicit synthetic test permission; Microphone.tsx boundary/final-tail callback; new audioChunking.ts and tests; wav downsampling/tests; Audio/Microphone tests; regenerated API and verify_live_stt.py; voice documentation and logs. Temporary/unrelated `* 2.*` files preserved.
- Backend preview validates staff/current recording permission/capture before and after inference. Offline persistent model worker, memory-only PCM/text transport, timeout/cancel, global inference lock. Preview never writes a source or approves/publishes. Existing whole-recording STT produces durable final evidence. No live-preview result is treated as reviewed data.
- Commands (Node22 PATH as prior entry): `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q` 130 PASS; `npm --prefix apps/web run typecheck` PASS; `npm --prefix apps/web run test:run` 28 PASS / 10 files; `PYTHONPATH=../../apps/api/src npm --prefix apps/web run generate:api` PASS; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS with existing bundle/directive warnings; `git diff --check` PASS.
- Actual AI: `PYTHONPATH=apps/api/src .venv/bin/python tools/dev/verify_live_stt.py` PASS with TWO actual API/Whisper calls on generated Finnish TTS, 3.67 seconds input: cold 7.26s, warm 2.45s. Earlier worker-only measurements 7.79/2.58 and 7.80/2.71 seconds. Provider whisper/medium.pt, LIVE/ai_executed true; no LLM call. Error observed: source initial word Tämä became sama; negative statement Ulkoilu ei toteutunut. retained. Not an accuracy or clinical validation claim.
- Initial failures fixed: pending-microphone test unmounted before new pre-start await reached getUserMedia; now waits for permission request to exercise intended case. Actual API verification script secret too short, extended test-only string and rerun. No skipped/deleted tests.
- Browser local /staff/voice confirms whisper medium, live toggle, synthetic permission creation via actual server and enabled recording button; selected Korean voice input. Did NOT open physical microphone. Audio pipeline/chunk ordering/tail/wait and stale unmount verified with mocked devices, not real microphone. Screenshot /private/tmp/medipencil-live-stt-screen.png. Loopback server restarted with same isolated DB, no --poc flag.
- Related T-02/T-03/T-04/T-06/T-07/T-08/T-09/T-10 subsets. Phone hardware, long recordings, real speech, language review and care-workflow human validation NOT_RUN. Local commit subject: Add incremental local STT using MediPencil silence-aware recording. No push or deployment.

## 2026-10-13 — 제공 합성자료 로컬 적용

- 시작: `poc/remote-validation`, HEAD `0bc64c4`. 기존 untracked `* 2.*` 자산 보존. 사용자 out.zip/PERSONAS 로컬 적용 지시를 반영. GitHub/성아 배포 없음.
- 변경: API `provided_data.py`, `main.py`; CLI `tools/dev/import_provided_data.py`; 웹 `ProvidedData.tsx`, `provided-data.css`, `App.tsx`, 생성 API 타입; `test_provided_data.py`; 적용 문서와 검증 로그.
- 구현: 저장소 밖 별도 SQLite, 2026년 필터, 출처 해시·원래 식별자 유지, 직원 전용 조회, 3/7/30일 및 직접 기간·그래프·원문 기록·보호자 프로필. 기존 동의/자동 전달/AI에는 연결하지 않음. 공유 환경 차단.
- 실행: `PYTHONPATH=apps/api/src .venv/bin/python tools/dev/import_provided_data.py --archive '/Users/hyosang/Desktop/2026 SOTE/out.zip' --personas '/Users/hyosang/Desktop/2026 SOTE/PERSONAS.md' --data-root /private/tmp/medipencil-voice-20261013` → 생활730/진료7/사회63, 대상2/보호자8. 내용 원문은 로그·저장소에 미포함.
- 검증: `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q` → 최종134 PASS. 처음 신규 시험은 Fault의 기본422를400으로 잘못 기대하여1 FAIL(기대값 수정); 전체 첫 회는 health에 false 속성 추가로2 FAIL(데이터 없는 환경은 기존 응답 유지하도록 수정) 후 재시험 통과.
- Node22 PATH 사용: `npm --prefix apps/web run typecheck` PASS; `npm --prefix apps/web run test:run` 10파일/28 PASS; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS(기존 directive/chunk 경고). `npm --prefix apps/web run generate:api` 최초 PYTHONPATH 누락 FAIL; `PYTHONPATH=../../apps/api/src`로 재실행 PASS.
- 실행 서버: 기존 이 작업의 PID85363 종료 후 같은 데이터 루트/포트8780으로 `run_demo.py` 재시작(PID61157). 실제 HTTP 별도 직원/가족 세션에서200/403, A/B 각각365일·4가족 조회. CUA 직원 로그인→제공 자료→A/B 전환·30/7일 조회·3그래프 확인. exact label 선택 첫 시도 실패 후 실제 label로 선택 성공.
- 관련 추적: T-01 출처/의미 보존, T-04 공개·역할 경계의 관련 회귀. 전체 기존 상세명세 완료를 뜻하지 않음.
- 미실행: 제공 자료 AI/STT 처리, 가족 발행, 실제 현장/모바일 기기 검수, 외부 배포. 모의AI 결과 없음.
- 커밋: 본 항목을 포함하는 `Integrate supplied 2026 scenarios into local staff data viewer` 로컬 커밋. 해시는 `git log`로 확인.

## 2026-10-13 — 제공자료 화면 디자인 정리

- 시작 HEAD ad5efc3, poc/remote-validation. 이전 untracked 복제 자산 보존. 사용자 디자인 훼손 수정 요청, 로컬만 반영.
- 변경: App.tsx, StaffReview.tsx, ProvidedData.tsx, provided-data.css, 제공자료 안내 및 진행/검증 로그. 상단 독립 메뉴 제거, 직원 검토함의 업무/2026자료 선택으로 통합. 요약·상세·가족 탭으로 분리, 출처/원본 JSON 접기, 기존 XD 색상 토큰/카드/버튼 재사용. 모바일 1열 그래프. 신규 대상자에 기존 Aino 세션 문구가 붙지 않도록 검토함 컨텍스트를 일반 합성자료 문구로 수정.
- 실제 명령(Node22 PATH): `npm --prefix apps/web run typecheck` PASS; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS(기존 번들 경고); `git diff --check` PASS.
- CUA: 직원 로그인→검토함→2026 생활 기록, 그래프3개/독립메뉴0개 확인. 상세30일/보호자탭 전환 PASS. 390x844 뷰포트에서 문서너비390, 그래프1열358px, 가로넘침 없음. 뷰포트 복원. 원본 레코드/스크린샷은 모델·저장소 증빙에 포함하지 않음.
- 관련 T-04 역할·공개 경계 유지(서버/권한 변경 없음); UI 동작 확인을 AI/임상 검증으로 보고하지 않음. 서버 재시험·실기기 검수·GitHub/성아 배포 NOT_RUN. 로컬 commit `Restore design consistency for staff data review`에 기록.

## 2026-10-13 — 보호자 상세 언어 선택 제거

사용자 첨부의 Kieli/Suomi 선택 UI를 App.tsx에서 제거. 핀란드어 기록 조회와 상단 화면 언어 설정은 유지. 기준 db69bd2, 기존 untracked 파일 보존. Node22 PATH로 `npm --prefix apps/web run typecheck`, `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS. 로컬 번들 반영, 서버/AI/권한 변경 없음. 관련 T-04 공개 경계 변경 없음. 브라우저 재시험 및 외부 배포 미실행. 커밋: Remove redundant family detail language selector.

## 2026-10-13 — 제공 대상자·보호자별 로그인 및 업무 연결

- 기준 d5f6c03 / poc/remote-validation. 기존 untracked 복제 파일 보존. 사용자 “일단 다 통합…첫 로그인도 보호자별” 지시. 로컬만 적용.
- 변경: API provided_workflow.py(신규), main.py, security.py; 웹 ProvidedWorkspace.tsx(신규), App.tsx, Login.tsx, ProvidedData.tsx, provided-data.css, generated-api.d.ts; test_provided_workflow.py(신규); 적용 안내/진행/검증 로그.
- 직원 공통 대상자 선택, 보호자8계정/대상자 연결, 서버 측 공유 필터·미래 제외, 가족별 질문·직원답변, 확인한 핀란드어 메모의 수신자별 공유, revision 기반 PoC공유 설정, 선택 대상자 음성 STT 경로. 기존 독립 시연과 제공자료 구분/격리. 로그인명은 로컬파일에서만 읽음.
- 실제 명령: `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q` 최종138 PASS(추가4시험, 음성 provider는 명시적 test mock); Node22 PATH `npm --prefix apps/web run test:run` 28 PASS/10파일; `npm --prefix apps/web run typecheck` PASS; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS; `PYTHONPATH=../../apps/api/src npm --prefix apps/web run generate:api` PASS. 기존 번들/directive 및 Starlette 경고 유지.
- 실제 HTTP: 제공 보호자8명 개별 쿠키 세션 로그인, 자기 대상자 조회8/8 200, 타 대상자8/8 403. 기록 원문 출력 없음. 독립시험 DB에서 같은 대상자 두 보호자의 건강 범위·질문 격리, 공유철회 후메모/답변숨김, 중복방지, 역할/공유환경/음성형식 차단 확인.
- CUA: 직원 로그인→B 선택→음성(마이크 패널 존재)→공유설정(4명×3체크) 대상자 유지. 보호자 로그인 계정9개(제공8+기존1), 제공 보호자 로그인 후 그래프3개/직원메뉴0개/질문탭 확인. 390px 모바일 문서너비390 확인, 뷰포트 복원.
- 서버: 이 작업 PID61157 종료 후 동일8780·데이터루트로 run_demo.py 재시작 PID52849, 최종 backend 수정 후 PID52849를 종료하고 PID67723으로 재시작 완료. 모델/자료 원본/공개 전송 없음.
- 관련 T-01 근거·출처/미래 구분, T-04 수신자·대상자·공유범위 관련 회귀. 실제 STT 신규 경로·실제 마이크는 NOT_RUN(기존 STT 구현 재사용). KIDE·자동 번역·자동차팅·제공대상자 정기 발행은 미구현. 사람/현장 검증·GitHub/성아 배포 미실행.
- 커밋: `Unify local supplied resident and family workflows` 로컬 커밋.

## 2026-10-13 — 보호자 로그인 간소화

기준5c624de. 8명 전체 카드 나열 대신 대상자→연결된 보호자 두 선택란으로 Login.tsx 정리. 대상자 변경 시 계정 선택 초기화, 기존 시연계정은 별도 그룹으로 유지. provided-data.css에 기존 테마를 사용하는 데스크톱2열/모바일1열 스타일 추가. 데이터/권한/계정 삭제 없음. Node22 PATH `npm --prefix apps/web run typecheck`, `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS. 브라우저 재시험/서버변경/외부배포 미실행. 관련 T-04 접근범위 계약 변경 없음. 커밋 Simplify family login by resident.

## 2026-10-13 — 환자별 대표 보호자 한 명

사용자 지시로 제공 대상자당 primary_contact 보호자1명(복수/미지정은 family_id 순으로 결정)만 활성화. 원본 가족자료/기존 업무 이력은 보존. people/상세프로필/로그인/공유대상에 동일 선택 적용, 기존 제외 계정 세션도 매 요청 차단. 로그인은 환자 선택 후 연결 보호자 자동표시. 기존시연1+제공2=환자3/보호자3. 수정 provided_data.py/provided_workflow.py/security.py/Login.tsx/provided-data.css, 회귀시험 및 로그. Node22 typecheck/build PASS, pytest test_provided_workflow.py test_provided_data.py 8 PASS(대표자교체·기존세션차단·제외수신자차단·원본보존 포함). 실제health 활성3가족/제공대상각1 확인. 로컬 PID67723→89865 재시작. 관련 T-04 권한·수신자 경계. 외부배포/실마이크/브라우저 재시험 미실행. 커밋 Limit each resident to one representative guardian.

## 2026-10-13 — 기존 시연 대상자 Helmi Nieminen으로 구분

사용자 승인으로 기존 독립 시연 이름 Aino→Helmi Nieminen 변경. subject_id aino 및 원본/승인/발행 이력은 유지, 제공 Aino/Eetu는 수정하지 않음. migration008로 기존 DB 표시명 변경, seed와 신규 합성EMR/정기전달 예문, 프로필/로그인/대시보드/동의/공유/매뉴얼/3언어 문구 갱신. 과거 원문 번역사전은 보존하고 Helmi 예문 별도 추가. 수정 파일은 본 커밋 diff 참조(기존 untracked 복제 자산 제외).
실행: API전체 pytest 첫137 PASS/1 FAIL(종전 이름 기대). 해당 test_issue_feedback.py 기대명을 사용자 요청에 맞춰 변경 후2 PASS. 웹 test:run 28 PASS, typecheck/build PASS(Node22). 실제 기존런타임 DB 마이그레이션 후 HTTP 직원대상목록 Helmi 확인, 제공대상Aino/Eetu 불변 확인. 로컬 PID89865→3671 재시작. 관련 T-01 과거근거보존/T-04 ID·권한유지. 브라우저 재시험/외부배포 미실행. 커밋 Rename original demo resident to Helmi Nieminen.

## 2026-10-13 — 보호자 기준 관계(이름,나이)

기준2f1a48e. provided_workflow.py에서 guardian relation_fi를 환자 관계로 역변환, 원본 대상자 label의 나이 사용. 딸→엄마/아빠, 부모→아들/딸(대상자 성별 근거), 불명은 가족/나이미등록. familyIdentity.ts 공통3언어 형식, ProvidedWorkspace/GuardianDashboard/Board/Profiles/App의 보호자 제목에 적용. 기존Helmi는 확정설계v1.1 §4의 Liisa의 어머니·84세 페르소나를 유지. 제공자료·권한 변경 없음.
명령: pytest apps/api/tests/test_provided_workflow.py -q 5 PASS(PYTHONPATH=apps/api/src, .venv/bin/python); Node22 typecheck/build PASS. 실제2보호자 HTTP board 응답 엄마75/아들25 확인. 로컬서버 PID3671→12922. 재시작 중 `.venipencil --help` 명령 오타 exit127, 정상 run_demo.py로 즉시 재실행 성공. 브라우저재시험/외부배포 미실행. T-01 관계방향·나이추론 방지. 커밋 Show resident relationship name and age for guardians.

## 2026-10-13 — Round Loop 외부 실시간 STT 로컬 연결

기준 HEAD 9a5d9bd, branch poc/remote-validation. 기존 untracked 복제 자산 보존. 사용자 제공 ZIP의 API 문서를 참고했고 포함 JS/HTML은 실행하지 않았다. 변경: roundloop.py 신규 staff 세션/일회용 WS 티켓·권한·Origin·크기제한·오류 정제; main.py router; requirements.in/lock의 websockets15.0.1; RoundLoopVoice.tsx/PCM worklet; ProvidedWorkspace/App 연결; generated-api 및 3언어 footer의 로컬 전용 오표기 수정; test_roundloop.py; verify_roundloop_stt.py; 사용/시험 문서 roundloop-live-stt.md. API 키는 저장소 밖0600 서버 설정 파일, 번들/추적파일 미포함 확인.

실행 명령/결과:
- uv pip compile apps/api/requirements.in --generate-hashes -o apps/api/requirements.lock.txt 및 uv pip install --python .venv/bin/python websockets==15.0.1 완료(준비 uv 경로 사용). venv pip 미설치 확인 후 uv 사용.
- PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q: 141 PASS. 최종 언어 매개변수 제거 후 test_roundloop.py 2 PASS 재시험. mock provider 권한·Origin·재사용·전사 스냅숏·크기·오류 비밀정보 차단 시험이며 실제 AI 시험과 별개.
- Node22 PATH npm --prefix apps/web run test:run: 28 PASS/10파일. typecheck, VITE_MEDIPENCIL_DESIGN=xd build, PYTHONPATH=../../apps/api/src generate:api PASS. 최종 수정 후 typecheck/build/generate:api 재실행 PASS. 기존 번들 크기/use client/Starlette 경고 유지.
- 실제 health 200. ko/en/fi 초기 빈음성 ready→done 확인, 이어 새 비임상 합성 음성의 실제 로컬 relay 시험. 초기 문서에 없는 language query와 최종 query 제거 모두 영어 일치·한국어/핀란드어 오인식. 최종 .venv/bin/python tools/dev/verify_roundloop_stt.py --send-synthetic-audio: 3회 ready→여러 transcript→done, 6.96/6.15/5.51초. 원문/출력은 독립 합성 시험 문서 참조. 외부 /openapi.json은 unauth401/auth404로 규격 조회 불가. 다국어 정확도 완료 아님.
- CUA 직원 로그인→음성→KaiLab 엔진선택→준비/전송확인/오인식 안내/확인 전 시작 비활성 검증. getByLabel 선택은 no_matches로 실패, AX setValue로 성공. 실제 물리 마이크 NOT_RUN.
- localhost8780 동일 데이터루트 재시작 PID12922→55997→69230. 제공 EMR/페르소나/음성 원본 업로드 없음. 현재 엔진은 전사 전용; /record 생성·자동 번역·승인/발행 미연결. GitHub/성아 배포 미실행. 언어 지정 API 규격 질문 응답 대기.
- 관련 T-03 원자료 충실(잠정·확정 구분), T-06 사용자·응답 경계, T-08 실패 경로, T-09 자료와 음성, T-10 실제/모의 시험 구분의 부분 검증. 사람/모바일/장시간/음성 품질 검증은 미완료.
- 커밋: Add optional server-proxied Round Loop live transcription (로컬).

## 2026-10-13 — KIDE 자동 초안 저장·확인 발송

기준723a1d7, poc/remote-validation, 기존 untracked 복제 자산 보존. 최신 사용자 진행 지시: 대화 전사→KIDE종료 신호→핀란드어 초안 자동저장→직원 확인발송. 변경 파일: apps/api/src/medipencil/kide.py/main.py, test_kide.py; web KideWorkflow.tsx/.test.tsx, kideCommand.ts/.test.ts, RoundLoopVoice/App/ProvidedWorkspace/GuardianDashboard/generated-api.d.ts, docs/poc/kide-auto-record.md 및 이 로그. 새 SQLite에 생성·실패·초안·확정·철회/검토자 저장. API키·제공자료 외부입력 없음. 독립 합성 발화만 외부 /record로 전송.

실제 실행:
- PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests -q:144 PASS; 최종 수정 뒤 test_kide.py test_roundloop.py 5 PASS. provider 호출은 단위시험에서 mock이며 권한·근거·중복·실패/재시도·현재 범위·revision 변경·철회 검증.
- Node22 PATH npm --prefix apps/web run test:run:30 PASS/12파일. 종료명령 파싱 및 mock 전사완료→자동생성/확인 전발송 차단 포함. typecheck, VITE_MEDIPENCIL_DESIGN=xd build, PYTHONPATH=../../apps/api/src generate:api PASS. 최종 typecheck/build 재실행PASS. 기존경고 유지.
- 실제 새 독립 합성 한국어 대화 POST /api/v1/kide/aino/drafts → 외부 /v1/record:HTTP200/5.6초/DB초안. 종료명령 제외, 핀란드어 본문 확인. 원문에 없는 평온 표현·식사량 활력징후 오분류·불일치 인용 발견. 부정확한 결과를 정확한 완료로 보고하지 않음.
- 별도 staff/liisa HTTP 세션: 초안 가족 미노출, 원본 생성결과 발송422(인용 불일치), 독립 합성 시험 내용 수정 후발송200/가족4카드조회/전체간호기록·전사미반환/중복발송200. 첫 검증 스크립트에서 이미 요청한 httpx.Client를 with로 재진입하여 RuntimeError 발생, 명시적 finally close로 수정 재실행PASS. 이는 임상 승인시험이 아님.
- CUA 직원 로그인→Helmi선택→음성→KIDE패널·저장기록조회·published 표시 확인. 마이크는 실행하지 않았음. 로컬PID77869/8780으로 재시작 완료(이전69230→71681→77869).
- 관련T-02 근거/철회, T-03 원자료 충실, T-04 승인·발행, T-06 대상자·사용자경계, T-07 권한변경, T-08 실패/중복, T-09 음성/자료, T-10 실제모의구분의 부분시험. 미실행: 실제음성종료명령·모바일·전체음성E2E·사람검수. 기존STT한국어/핀란드어오인식 미해결. 다국어본문/실EMR/외부알림/정기발행연계/외부배포 미구현 또는 미실행. 문서에 구분.
- 커밋: Automate KIDE Finnish drafts and reviewed family sharing (로컬).

### 2026-10-13 · KIDE 직접 호출 및 공개 화면 준비 (PC-03/05)
- 시작 HEAD f4402a1 / poc/remote-validation. origin main/JY_test/support/hyunah-test는 모두 HEAD에 포함되어 추가 병합 불필요. 기존 이름 중복 파일(`* 2.*`)은 보존·제외.
- 사용자 결정: GitHub Pages/성아는 배포 환경, KaiLab AI는 브라우저가 직접 호출. 서버 중계가 기본이라는 설명을 정정.
- 변경: roundloopDirect, RoundLoopVoice, KideWorkflow, 독립 KideDirectPage, App/main 메뉴·경로, api 세션 키 삭제, kide.py 직접 결과 저장·출처 표시. 이전 이름/언어 메뉴 변경에 따른 E2E와 3개 매뉴얼 동기화.
- 관련 T-ID: T-01 직접입력/초안, T-03 승인, T-04 권한, T-07 실패·재시도, T-09 실제/모의 구분.
- 실제 실행: `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests tools/deploy/tests -q` →157 passed. Node22 PATH로 `npm --prefix apps/web run typecheck` 통과, `npm --prefix apps/web run test:run` →32 passed. 직접 API 테스트는 mock이며 실제 음성 인식 검증으로 보고하지 않음.
- 앞선 E2E: 19/32 통과 후 이름/삭제된 언어 메뉴 단언 갱신; 재시험30/32, 오프라인 문구와 세션 실패 조사. 전체 재시험 진행 중.
- 기존 가족 공유는 서비스 DB가 필요하며, 독립 화면은 전사/초안 확인·다운로드만 제공. 카이랩 저장/공유 API는 확인되지 않아 구현 완료로 주장하지 않음.
- 커밋/배포: 후속 결과에 기록. 실제 마이크·모바일·한국어/핀란드어 품질은 미검증/기존 오인식 미해결.

- 후속 검증: 전체 브라우저 시험33/33 PASS (실제 임시 서버·SQLite), 정정 후 사용자 전환 단독5회 PASS. 앞선1회 실패는 재현되지 않아 해결됐다고 단정하지 않음. GitHub Pages origin의 KaiLab OPTIONS 실제 응답204, Allow-Origin `*`, Content-Type/X-API-Key 허용 확인. 시스템 python3 urllib는 인증서 trust 설정 오류로 실패했고 .venv httpx의 정상 인증서 검증으로 재확인했다.
- `npm --prefix apps/web run generate:api` 최초 PYTHONPATH 누락으로 실패, 절대경로 PYTHONPATH 지정 후 PASS. Pages base/hash/XD 설정 빌드 PASS (기존 번들 크기/라이브러리 directive 경고), compileall PASS.

- XD 디자인 E2E4/4 PASS. 커밋 예정: `Connect KIDE directly to KaiLab from both hosting environments`; 배포 후 해시와 실행 결과를 추가 기록한다.

### 2026-10-13 · 직접 호출 커밋/실제 API 확인
- 커밋 `cfb6cd9` / 원격 poc/remote-validation push 완료. 기본git credential helper 부재로 첫push 실패; `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin poc/remote-validation`으로 기존 GitHub 인증을 사용해 성공. 키를 원격 URL/소스에 기록하지 않음.
- 실제 GitHub Pages 출처 Chromium에서 카이랩 `/v1/record` 직접 POST: HTTP200, nursing_note9필드, laheiskortti8필드. 독립 합성 핀란드어 텍스트만 사용. 서비스 API/성아를 중계하지 않았으며 STT/마이크 시험으로 보고하지 않음. 결과는 보호자에게 발행하지 않음.
- 로컬 XD 빌드 및8780서비스 재시작(기존data-root유지), CUA `/kide-direct`에서 연결URL·키입력·전사버튼·초안의 임시보관 설명 확인.
- GitHub Actions run38392990990 배포 결과 확인 중.

- 배포 완료: Actions38392990990의 build / publish-api / deploy-api / deploy-pages / verify-pages 모두 SUCCESS. 실제 Pages build-info와 성아 health가 `cfb6cd9f16b70198d42ff6512cb6234c5d1fc490` 일치. 서버 적용 대기 중 VPN 관리 경로(sa-gateway/sa-kvm)를 읽기 확인했으며, 수동 서버 변경 없이 자동 배포가 완료됐다. 등록 호스트 키 검증 유지.
- 공개 CUA 확인: `https://hyosang-ryu.github.io/Team_Medipencil/#/kide-direct` 에서 로그인 없이 API URL/키 입력/받아쓰기/종료 버튼과 임시 초안 안내 표시 PASS. 서비스 API가 없는 경우의 동작은 로컬 E2E에서 요청차단으로 확인했고, 실제 Pages origin→KaiLab POST200은 별도 실제 엔진 시험이다. 물리 마이크·실제 음성 종료명령·핀란드어 품질 미검증은 유지한다.

### 2026-10-13 · KIDE 화면 문구 정리 (PC-05, T-ID: UI 회귀)
- 시작 HEAD f01c791, poc/remote-validation. 기존 미추적 중복파일 보존. 사용자 요청에 따라 화면 제목/메뉴를 KIDE로, 연결영역 제목을 연결 설정으로 변경. KaiLab Round Loop 전사 제목과 외부 처리 안내의 업체명 제거, 브라우저·성아·로그인 설명 문단 삭제(ko/en/fi). 연결 기능과 키 취급 방식은 변경하지 않음.
- 변경파일: App.tsx, KideDirectPage.tsx, RoundLoopVoice.tsx, kide-direct.spec.ts.
- 실행: Node22 PATH에서 `npm --prefix apps/web run typecheck` PASS, 절대 PYTHONPATH 및 VITE_MEDIPENCIL_DESIGN=xd로 `npm --prefix apps/web run test:e2e -- kide-direct.spec.ts` 1 PASS, `npm --prefix apps/web run build` PASS(기존 번들 경고). 실제 AI 재호출은 불필요하여 미실행.
- 커밋: `Simplify KIDE screen wording`; 배포 결과는 후속 기록.

- 로컬 CUA로 KIDE/연결 설정/실시간 전사 제목과 상단 설명 삭제 확인. 대체 문구의 한국어 조사도 교정.

- 후속 사용자 결정: 테스트용 KIDE 메뉴·독립 화면은 유지. 메뉴 삭제 없이 표시명/안내 문구만 변경한 현재 구현과 일치. 커밋 c3a88a9 및 조사 교정 b0410fa 원격 반영, Actions38396050243 검증·배포 진행 중.

- 최종 배포: Actions38396050243 모든 job SUCCESS. Pages build-info b0410fa 일치. 공개 CUA에서 제목 KIDE/연결 설정/실시간 전사, 업체명 및 브라우저 설명 제거 확인. 홈 상단 KIDE 메뉴가 `/kide-direct`로 연결되는 것도 확인. 이전 c3a88a9 빌드는 조사 교정 후 최신 빌드로 대체됨.

### 2026-10-13 · 보호자 전용 모바일 디자인 (PC-05, T-ID: T-02/T-03/T-07 연관 UI·권한 회귀)
- 시작 HEAD bd8e1c4, poc/remote-validation. 기존 미추적 `* 2.*` 파일 보존.
- Adobe XD main_m 보호자 화면 참고. 430px 모바일 캔버스, 햄버거/파란 메뉴, 최근 안부/관리항목, 상세/기간/가족확인/공유범위 이동. 의료진 레이아웃·API·DB 변경 없음. KIDE 테스트 메뉴 유지.
- 변경: App.tsx, GuardianMenu.tsx, guardian-mobile.css, GuardianDashboard.tsx, ProvidedWorkspace.tsx, main.tsx; e2e/login.ts, english, guardian-home, issue-feedback, login-dashboard 시험; design-qa.md.
- 실행 환경 Node22.16.0 PATH 및 절대 PYTHONPATH=apps/api/src. `npm --prefix apps/web run typecheck` PASS. `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS(기존 라이브러리 directive/번들 경고).
- `npm --prefix apps/web run test:e2e -- guardian-home.spec.ts login-dashboard.spec.ts english.spec.ts` 5 PASS. git ls-files로 추적된 spec만 지정한 전체 E2E 32 PASS/1 FAIL: issue-feedback의 구형 한열 레이아웃 기대. 새 세열 명세로 갱신 후 `test:e2e -- issue-feedback.spec.ts guardian-home.spec.ts login-dashboard.spec.ts` 5 PASS.
- `VITE_MEDIPENCIL_DESIGN=xd ... test:e2e -- design-variant.spec.ts login-dashboard.spec.ts english.spec.ts` 4 PASS. 별도 세션 API/SQLite 발행·권한 검사 포함, 임의 skip 없음.
- CUA 로컬8780: 보호자 메뉴/기간 상세/로그아웃/추가 대상자 가족확인사항 연결, 직원 넓은 화면 유지 확인. 320/390px 가로 넘침 없음. 원안과 실제 렌더 동시 비교 및 간격/로그인 배경 수정. QA 문서 참조.
- 미실행: 실제 AI/STT·물리 모바일 기기·핀란드어 전문가 검수. 제공 합성자료 원본·키·스크린샷은 Git에 추가하지 않음.
- 커밋 예정: `Apply guardian-only mobile layout from XD`; 배포 결과는 후속 기록.

- 후속 QA: 데스크톱에서도 추가 대상자 보호자 그래프를 단일 열로 유지하도록 `.provided-charts/.provided-family-grid`와 로그인 선택기를 보완. CUA 실제 1280px 화면에서 그래프 398px 단일 열 확인. XD build PASS. 본 변경 커밋 c1fad0f 이후 보완 커밋으로 배포한다.

- 배포 완료: c1fad0f + 보완 37e8073 원격 반영. 이전 중복 run38399842460 취소, 최신 Actions38399988095 build/publish-api/deploy-api/deploy-pages/verify-pages 전부 SUCCESS. 실제 Pages build-info 및 성아 health의 revision은 37e807317cf101e357cf443e058846c508c5cc98로 일치(HTTP200). 공개 CUA 보호자 로그인→430px 대시보드·현재 발행 데이터·햄버거 확인. 공개 화면 증빙 /private/tmp/guardian-mobile-published.jpg, 저장소에는 추가하지 않음.

### 2026-10-13 · A/B 두 환자 자료 공유 배포 (PC-05, T-ID T-06/T-07/T-08)
- 사용자 명시 배포 요청, 시작 3dd413a/poc/remote-validation. 기존 중복 미추적 파일 보존.
- 변경: config.py, provided_data.py, security.py, test_provided_data.py, App.tsx. 로컬 기본 차단은 유지하고 공개 PoC+정확한 런타임 DB SHA256 일치 시에만 제공 자료 활성화. 검증된 provided 계정에 한해 공개 로그인 허용. 화면의 로컬 전용 표현 교정.
- 데이터: 기존 로컬 DB를 SQLite backup으로 별도 /private/tmp 파일에 복사, A/B만 확인, 대표 보호자 각각1명만 보존, 2026년 외 기록0 확인. A 일상365/진료4/사회25, B 일상365/진료3/사회38, 합계800. integrity_check ok. 원본DB·진행중 질문·직원 작성자료는 변경/복사하지 않음. 기존 SUPPLIED_VEIL_DERIVED 메타데이터 유지, 외부 AI 실행/전송 없음.
- 전송: 등록키 검증 sa-gateway→mp-kvm→sa-apps. 신뢰된 KVM known_hosts의 앱키를 별도 임시 known_hosts로 사용. scp로 sa-apps 별도 staged 파일 전송; 서버에서 SHA256·2환자·각1보호자·2026 범위 확인 후 런타임 경로 설치. 환경파일을 백업하고 MEDIPENCIL_SHARED_SUPPLIED_SHA256만 추가. 기존 demo DB 유지. 원본/SQLite/계정키는 Git에 추가하지 않음.
- 검증: `PYTHONPATH=$PWD/apps/api/src .venv/bin/python -m pytest apps/api/tests/test_provided_data.py apps/api/tests/test_provided_workflow.py -q` 10 PASS. 신규 시험 최초2회는 중복seed/잘못된 TestClient host 설정 실패였으며 fixture 설정 수정 후 통과. 정확한 파일허용·변조차단·Pages 로그인·다른환자403 검증.
- `... pytest apps/api/tests tools/deploy/tests -q` 158 PASS. Node22 `npm --prefix apps/web run typecheck` PASS. 실제 배포/API/브라우저 결과는 후속 기록.

- 배포 코드 54b8ddc, Actions38403667662의 build/publish-api/deploy-api/deploy-pages SUCCESS. 서버의 기존 medipencil-deploy.service를 --no-block으로 즉시 실행하여 적용. 실제 health/Pages build-info 모두54b8ddc, provided=true/계정2 확인.
- 원격 HTTPS 실제 API: Pages Origin bearer 및 성아 Origin cookie 각각 A/B 독립 세션 로그인201→자기환자 최근7일200/7행→다른환자403→로그아웃204. 직원 catalogue2명/800건 확인. 데이터 수정·질문 작성·AI 실행은 하지 않음.
- 공개 CUA: 대상자 선택 Aino→Marjut / Eetu→Hanna, 각 보호자 화면의 엄마(Aino,75세)/아들(Eetu,25세)와 그래프 확인. 기존 Helmi 시연 선택은 보존.
- 배포 후 verify-pages만 기존 라디오형 로그인 가정으로 FAIL. e2e/login.ts를 compact 대상자 선택과 비동기 목록 대기에 대응, 직원 기존 시연 선택 명시. e2e-pages/pages.spec.ts에 두 제공 보호자의 별도 컨텍스트 로그인/그래프/서드파티쿠키 미사용 검증 추가. skip/권한 검사 제거 없음.
- 실행: 최초 npm --prefix exec는 cwd의 config 경로 오류, apps/web cwd에서 `PATH=<Node22> npx playwright test --config playwright.pages.config.ts --grep 'loads and reaches'` 수행. 첫1FAIL/1PASS는 목록 로딩 대기 누락; 대기 보완 후 2 PASS(12.9s). 두 시험은 실제 공개 Pages/API 읽기 검증이며 AI 시험 아님.


## 2026-10-13 · PC-05 KIDE 연결 입력 영역 간소화
- 요청: 키 적용 후 URL/API key 입력 영역 제거. KIDE 테스트 메뉴 유지.
- 변경: `apps/web/src/RoundLoopVoice.tsx`는 미설정 때 접힌 연결 설정만 표시하고 적용 후 전체 설정 폼을 제거한다. 메모리 키의 새로고침/로그아웃 초기화 정책은 그대로다. 전역 키가 배포됐다고 표시하지 않는다.
- 검증: Node v22.16.0 PATH, apps/web에서 `npm run typecheck` PASS. 첫 `npx playwright test e2e/kide-direct.spec.ts`는 PYTHONPATH 미지정으로 API startup 실패. `PYTHONPATH=<repo>/apps/api/src`로 재실행: 1 PASS (4.3s). 미설정 접힘→테스트 키 적용→폼 제거/녹음 준비→reload 후 미설정 복귀 및 서비스 API 무호출 검증. `VITE_MEDIPENCIL_DESIGN=xd npm run build` PASS (기존 chunk/use-client 경고).
- 관련: PC-05, T-08 세션 경계; `apps/web/e2e/kide-direct.spec.ts` UI 회귀. 실제 마이크/STT/LLM 호출 미실행. 테스트 키는 가상 문자열만 사용.
- 커밋: 이 항목을 포함한 `fix: hide KIDE connection form after configuration` 커밋. 배포 상태는 후속 확인으로 구분한다.


## 2026-10-13 · PC-05 첫 로그인 공통 소개 문구
- 사용자 요청: 대상자 2명이므로 로그인 중앙에 특정 환자 사진/이름을 표시하지 않는다.
- `apps/web/src/Login.tsx`: XD 중앙 카드를 공통 제목/서비스 설명(ko/en/fi)으로 교체. 보호자/직원 진입 카드도 이름 대신 역할 안내. 계정 선택과 대상자 연결은 유지.
- `apps/web/src/App.tsx`: 로그인 전 상단 PoC 안내에서 특정 대상자 이름 제거.
- 실행: Node22 PATH로 `npm --prefix apps/web run typecheck` PASS; `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS (기존 번들 경고). CUA로 localhost8780 첫 화면 열어 공통 제목/설명, 역할별 링크와 비로그인 안내 확인.
- T-ID: PC-05 UI 문구 보완; 권한/API 변경 없음. 실제 AI 실행 없음. 운영 배포 완료는 미확인.
- 커밋: 본 항목을 포함한 `fix: make login introduction resident-neutral`.


## 2026-10-13 · PC-05 KIDE 새로고침 후 녹음 비활성 수정
- 원인: 키가 메모리에서 소실되어 configured=false인데 설정창이 접혀 있었음. KideDirectPage unmount도 키를 지웠음.
- 변경: roundloopDirect.ts에 탭 한정 sessionStorage 복원 추가 (빌드/Git/API에는 키 미포함). 로그아웃/session reset에서는 삭제 유지. KideDirectPage 화면 이동은 진행 요청만 취소. RoundLoopVoice 미설정 시 설정을 열고 키 입력 안내, 적용 후 폼 제거.
- 검증: Node22/PYTHONPATH=<repo>/apps/api/src, apps/web에서 `npm run typecheck`, `npx vitest run src/roundloopDirect.test.ts` 3 PASS, `npx playwright test e2e/kide-direct.spec.ts` 1 PASS (3.9s), `VITE_MEDIPENCIL_DESIGN=xd npm run build` PASS. 가상 키로 새로고침 후 복원/폼 숨김/시작 활성화, 세션 해제 시 삭제 검증.
- 초기 편집 명령 cwd 오류(FileNotFoundError) 후 repo root에서 재실행. 오류 직후 시험은 기존 코드 시험이므로 변경 검증에서 제외.
- 실제 외부 URL HEAD는 401 및 CORS 응답 확인 (인증 없는 도달성만 확인). 실제 키 인증·마이크·STT·LLM 호출은 미실행. 이전에 소실된 키는 복원 불가하여 최초 1회 재입력 필요.
- 관련 T-ID: PC-05/T-08 세션 경계. 커밋: 본 항목을 포함한 `fix: retain KIDE connection across tab reloads`. 배포 성공 여부는 별도 확인.


## 2026-10-13 · PC-05 초기 Helmi/Liisa 시연 퇴역
- 요청: 초기 시연 대상 Helmi/Liisa 삭제. 두 대상자 자료가 있는 환경에서 초기 계정 비활성화, 기존 가족 세션 제거, 접근 membership 비활성화, Helmi 정기 발송 중지. FK로 연결된 과거 기록/감사 이력은 보존하며 물리 삭제로 보고하지 않는다. 자료 없는 독립 회귀시험 환경은 유지.
- 변경: `provided_workflow.sync_accounts`, `Login.tsx`/`App.tsx` 초기 시연 선택 제거, `test_provided_data.py` Liisa 로그인 거부/비활성 검증. Pages smoke를 현행 직원 2대상자 선택 검증으로 변경. 제공자료 원본/DB는 Git 미포함.
- 실행: `PYTHONPATH=apps/api/src .venv/bin/python -m pytest apps/api/tests/test_provided_data.py -q` 5 PASS; 전체 `... pytest apps/api/tests -q` 146 PASS; Node22 `npm --prefix apps/web run typecheck`, `VITE_MEDIPENCIL_DESIGN=xd npm --prefix apps/web run build` PASS.
- 로컬: 기존 /private/tmp/medipencil-voice-20261013에 sync_accounts 실행. 실제 localhost8780 health: staff+보호자2명, 대상 Aino/Eetu 확인. AI 미실행. Pages 수정 시험은 배포 후 실행 대상, 아직 미실행.
- 관련 T-ID: PC-05/T-08 계정 접근. 커밋: 본 항목 포함 `fix: retire initial Helmi and Liisa demo accounts`. 운영 배포 완료 별도 확인.


## 2026-10-13 · PC-03/05 녹음 재시험 및 두 호스팅 배포 완료
- 앱 배포 SHA: 007e86dc8225d96d337a4c63b7057477be474dcf. Actions 38407159141 build/publish-api/deploy-api/deploy-pages/verify-pages 모두 SUCCESS. 이전 ff49c75 실행 38406708736은 최신 배포를 위해 취소.
- `npm run test:e2e` (Node22, PYTHONPATH 지정): 로컬 전체 화면 33 PASS (2.2m).
- `.venv/bin/python /private/tmp/test_kide_direct.py`: 로컬 비공개 설정에서 키를 읽어 독립 합성 TTS만 외부 직접 전송. 한국어/영어/핀란드어 모두 WS ready→transcript→done. 영어 정확; 한국어는 핀란드어 유사 문장, 핀란드어는 다른 언어로 오인식. 다국어 품질 검증 완료 아님. `/v1/record` 실제 HTTP200, nursing_note/charting/family_notices 등 반환, CORS=* 확인.
- `node /private/tmp/kide-browser-test.cjs`, KIDE_TEST_URL을 로컬8780, 성아 /medipencil/kide-direct, Pages /#/kide-direct로 각각 실행: 모두 PASS. Chromium 합성 WAV 마이크→getUserMedia→AudioWorklet→실제 외부 WS→종료→실제 record HTTP200→초안 화면 표시. reload 후 키 유지 확인. 음원 반복은 Chromium fake audio loop에 의한 것. 사람의 실제 마이크/현장 음성 시험 아님. 제공 환자 자료/EMR 외부 전송 없음, DB/가족 발송 없음.
- `ssh -F /private/tmp/medipencil-direct-ssh mp-app 'systemctl start --no-block medipencil-deploy.service'`: 기존 updater 실행, journal 배포007e86d 완료. 공개 health SHA 일치, liisa 없음, Aino/Eetu만 제공. Pages build-info SHA 일치.
- `npx playwright test --config playwright.pages.config.ts --grep 'GitHub Pages'`: 최초 직원 검사만 .provided-data 다중 일치로 실패, guardian PASS. `apps/web/e2e-pages/pages.spec.ts`를 최상위 workspace 및 선택값 확인으로 수정 후 2 PASS (10.0s). 앱 변경 없음.
- 관련 T-ID: PC-03 실제 엔진/PC-05 UI/T-08 계정 경계. 세 언어 전문가 검수 및 실제 장치 마이크 시험 미실행. 키는 탭별 첫 입력 필요, 전역 내장 키 없음.
- 이 기록/테스트 선택자 수정 커밋은 앱 배포 SHA와 별개이며 실행 코드 변경 없음.
