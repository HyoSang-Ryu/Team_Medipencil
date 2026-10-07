# GitHub 빌드 사용법

구현 브랜치: `poc/remote-validation`. Workflow: `.github/workflows/build.yml` · **Build and test PoC**.

## 실행과 결과 확인

1. `main`, `poc/**`, `codex/**` 브랜치에 코드를 push하면 자동 실행된다. Pull request에서도 실행된다. Markdown/docs만 변경하면 자동 실행하지 않는다.
2. 저장소의 **Actions → Build and test PoC**에서 해당 커밋의 실행을 연다.
3. 성공한 실행 하단 **Artifacts**에서 `medipencil-web-<commit>`과 `medipencil-api-<commit>`을 다운로드한다. 보관 기간은 14일이다.
4. 같은 커밋을 다시 빌드하려면 해당 실행의 **Re-run all jobs**를 사용한다. 실행/재실행에는 저장소 쓰기 권한이 필요하다.

`workflow_dispatch`도 정의되어 있다. GitHub의 **Run workflow** 버튼을 사용하려면 워크플로가 기본 브랜치 main에도 있어야 한다. 현재 PoC 브랜치에만 있는 동안에는 코드 push 또는 기존 실행 재실행을 사용한다. 이 변경은 PoC 전체를 main에 자동 병합하지 않는다.

## 수행 내용

Ubuntu 24.04, Python 3.12, Node 22.16.0 환경에서 다음을 순서대로 실행한다.

- 해시를 검사하는 Python lock 설치와 npm ci
- Python 문법 컴파일, API 시험, TypeScript 검사, 프런트엔드 단위 시험
- Chromium 및 임시 FastAPI/SQLite를 사용한 직접 입력 브라우저 시험
- 한국어·핀란드어·영어 매뉴얼 생성본 일치 검사
- Vite 웹 빌드와 Python wheel 패키징

실제 AI 모델을 다운로드하거나 실행하지 않는다. 운영 서버/VPN/SSH/운영 DB·팀 코멘트에는 접근하지 않으며, 별도 secrets 없이 실행한다. 서버·DB는 시험마다 생성한 독립 합성자료를 사용한다. 원격 서비스용 시험과 실제 엔진 시험은 이 CI에 포함하지 않는다.

## 빌드 파일의 용도

웹 artifact의 `index.html`, `assets/`, `build-info.json`은 `/medipencil/` 경로에 맞춰 빌드된다. 기본 경로 `/`용 파일이 필요하면 워크플로의 `MEDIPENCIL_WEB_BASE`를 `/`로 바꾸어 빌드한다. API wheel에는 Python 애플리케이션이 들어 있으며 실행 시 Python 3.12와 `apps/api/requirements.lock.txt` 의존성 설치가 필요하다.

이 workflow는 빌드·시험·artifact 저장까지만 수행한다. 운영 배포는 별도 절차다. 웹 artifact만 GitHub Pages에 올려도 FastAPI/SQLite 서버 기능이 실행되지는 않는다.
