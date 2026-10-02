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
