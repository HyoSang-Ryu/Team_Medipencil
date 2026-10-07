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

## 2026-10-07 전체 자동 배포로 확장

위의 화면만 자동 배포하던 제한을 해제했다. 이제 배포 브랜치 코드 push의 순서는 **build → publish-api → deploy-api → deploy-pages → verify-pages**다. 팀원은 API 코드와 `apps/api/src/medipencil/migrations/versions/`의 Alembic revision도 같은 브랜치로 배포할 수 있다. GitHub/서버의 비밀 설정값이나 OS 설정 자체를 코드 저장소에 넣는 방식은 아니다.

성아 서버가 3분 간격으로 GitHub의 검증된 공개 배포 파일을 받아 적용한다. CI에 VPN·SSH 키·서버 비밀번호를 넣지 않는다. publish-api는 임시 GitHub 토큰으로 배포 번들을 공개 prerelease에 올리며, DB/사용자 자료/환경파일/모델은 번들에 포함하지 않는다. 서버는 저장소·브랜치·커밋·동일 run/attempt의 build/publish 성공·파일 SHA256을 검사한다.

DB 복사본에서 마이그레이션을 먼저 실행한 뒤, 실제 전환 때만 잠시 503 점검 응답을 반환한다. API 정지 → SQLite 백업 → 실제 Alembic upgrade → 새 API 기동·커밋/DB 검사 순서다. 기동 또는 마이그레이션 실패 시 점검 상태에서 이전 코드와 DB를 복원한다. 새 버전이 건강한 상태로 공개된 뒤 받은 사용자 입력을 과거 백업으로 되돌리지는 않는다.

GitHub deploy-api는 최대 약13분 동안 공개 health의 커밋을 확인하고, 일치한 뒤에만 Pages를 갱신한다. API 실패 시 기존 Pages는 유지된다. API가 이미 정상 배포된 뒤 Pages 배포만 실패하면 정상 API는 유지하고 Pages 단계 실패를 표시한다. API는 다음 화면 배포까지 기존 화면과 호환되도록 변경해야 한다.

DB 구조 변경은 새 Alembic revision으로 작성하고 테스트한다. 기존 revision을 소급 수정하거나 운영 DB 파일을 GitHub에 올리지 않는다. 실패한 같은 배포는 서버에서 반복하지 않는다. 원인을 수정해 push하거나 Actions의 **Re-run all jobs**로 새 attempt를 만들면 다시 시도한다. 수동으로 서버 DB 파일을 수정하는 절차는 필요하지 않다.

상세 운영·복구 절차: [자동 배포 운영 안내](automatic-deployment.md).
