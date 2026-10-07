# 돌봄루프 — GitHub 화면과 공동 데이터 저장

팀 이름은 MediPencil(메디펜슬). 외부 팀원용 화면 주소:

**https://hyosang-ryu.github.io/Team_Medipencil/**

## 팀원의 사용·배포

1. 위 주소에서 Suomi / 한국어 / English를 선택한다.
2. Liisa/Mikko는 가족, Koskinen은 직원 역할이다. 질문·코멘트는 공동 서버에 실제 저장된다.
3. 저장소 쓰기 권한이 있는 팀원이 `poc/remote-validation`에 코드 변경을 push하면 **Build and test PoC → deploy-pages → verify-pages**가 실행된다.
4. 검증에 성공한 정적 웹 파일이 GitHub Pages에 자동 배포된다. **verify-pages**는 VPN 없는 GitHub 실행기에서 실제 공개 화면과 API 연결을 확인한다.
5. 같은 화면 주소를 새로 열면 결과를 확인할 수 있다. 업데이트 직후에는 GitHub CDN 반영 시간이 조금 필요할 수 있다.

팀원의 빌드·배포·화면 접속에는 VPN이나 서버 SSH 계정이 필요하지 않다. 저장소 쓰기 권한이 없는 팀원은 PR을 보내고 권한 있는 팀원이 배포 브랜치에 병합한다. PR 자체에서는 운영 Pages를 교체하지 않는다. 문서만 변경한 push는 기존 paths-ignore에 따라 빌드하지 않는다. main에 앱을 자동 병합하지 않으며 배포 브랜치는 현재 `poc/remote-validation`이다.

## 구조와 범위

GitHub Pages는 HTML/CSS/JavaScript 파일을 제공한다. FastAPI·SQLite는 기존 성아 서버에서 실행한다. 사용자는 GitHub 주소에 머무르며 HTTPS API로 질문·기록·코멘트를 공동 저장한다. 순수 브라우저 저장이나 모의 저장으로 대체하지 않는다. API 서비스가 중지되면 공동 저장 기능은 사용할 수 없다.

Pages 빌드: `MEDIPENCIL_WEB_BASE=/Team_Medipencil/`, `VITE_MEDIPENCIL_HASH_ROUTER=1`, `VITE_MEDIPENCIL_API_BASE=https://orch.sungah.kr/medipencil/api/v1`. URL의 `#/...`는 GitHub 정적 파일 서버에서도 새로고침과 직접 링크가 동작하기 위한 경로다. 매뉴얼 직접 주소는 `https://hyosang-ryu.github.io/Team_Medipencil/#/manual`이다.

API는 `MEDIPENCIL_PAGES_ORIGIN=https://hyosang-ryu.github.io`만 허용한다. 공개 합성 PoC 모드에서만 활성화된다. Pages 세션 토큰은 탭 메모리에만 보관하며 localStorage/URL에 저장하지 않는다. 새로고침 후 역할 재선택이 필요하지만 DB 데이터는 유지된다. 기존 성아 화면은 HttpOnly 쿠키 방식을 계속 사용한다. 역할·CSRF·근거·승인·발행·동의 검사는 두 방식에서 동일하다.

이번 자동 배포 대상은 **GitHub 화면 파일**이다. Python API 변경의 서버 배포는 별도 운영 작업이다. GitHub Pages에서는 Python/DB를 실행할 수 없다. 별도 성아 서버 자동배포 타이머를 설치하지 않았다.

## 검증

- 기본 CI: 기존 API, 프런트엔드, 독립 임시 DB 브라우저 회귀 시험.
- 자동 배포 검증: `playwright.pages.config.ts`의 읽기 중심 smoke test. 공개 GitHub 주소에서 세 역할, 메뉴·매뉴얼, API 연결, 제3자 쿠키 없는 세션을 점검한다.
- 명시적 합성 쓰기 검증: `MEDIPENCIL_PAGES_WRITE_TEST=1 npx playwright test --config playwright.pages.config.ts`. 실제 공유 DB에 AUTO-PAGES 표식의 질문·계획 기록·발행·코멘트를 저장하고 별도 세션과 새로고침 후 확인한다. 매 빌드마다 시험 데이터를 추가하지 않도록 일반 배포에서는 실행하지 않는다.

자동 시험은 사람의 피드백이나 실제 AI 실행 검증이 아니다. 실행 결과는 `validation-log.md`에 기록한다.
