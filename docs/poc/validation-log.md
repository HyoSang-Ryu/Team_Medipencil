# PoC 검증 기록

## PC-00 · 출발점 / 2026-10-03

- 실행 기준: 최신 main `4802e81534f273e1ed2507129a91badf93c64f2a`의 AGENTS.md, docs/poc/README.md와 docs/development/README.md를 읽었다. 기존 v1.1/01~03은 승인·근거·권한 추적 참고이며 구현 개수 목표가 아니다.
- 명령: `git status --short --branch`, `git remote -v`, `git fetch origin main`, `git rev-parse origin/main`, `git show origin/main:AGENTS.md`, `git show origin/main:docs/poc/README.md` → 성공.
- 기존 HEAD `e28a746`, branch `codex/care-loop-mvp`, 작업 트리 clean. FastAPI/SQLite/React 직접 입력·로컬 모델·권한/정정 테스트가 이미 있었다. 기존 코드·전체 커밋·작성 시점·설계 SVG를 보존한다. 과거 구현 규모를 새 PoC 요구로 간주하지 않는다.
- `git switch -c poc/remote-validation`; `git merge --no-commit origin/main` → README.md 충돌1. 최신 main의 PoC 우선 구조를 채택하고 기존 로컬 구현·실행 링크를 사실대로 연결하여 해결. AGENTS/PoC README/개발 README는 최신 main을 그대로 반영한다.
- 재사용 선택: 이미 동작하는 서버·DB·세션·승인·발행을 재사용한다. schema/API 추가나 전체 재작성·기존 작업 삭제는 하지 않는다. 이번 검증 범위는 PC-01 직접 입력 + PC-02 핵심 공개 경계다. 이전 실제 AI 시험은 과거 별도 증거이며 PC-01 성공의 조건이 아니다.
- PC-04 공유 서버·배포 권한·접근 제한 방식 미지정. 로컬까지 진행한다. 지원팀 실제 피드백 없음(FB-ID 미발급); PC-05 사람 피드백 기반 재시험/PC-06 명세 결정은 NOT_RUN/AFTER_FEEDBACK.
- 내부 PoC와 대회 사전제작·반입 허용은 별개로 UNCONFIRMED. 공개 배포·주최 측 승인·지원팀 의견을 만들어 보고하지 않는다.
