# P-00/P-01 반입 자산 목록과 환경 관측

관측일: 2026-10-02. 기준 commit: `9c64133960f8305c0dab9e3713009bbb39e46e1c`.
현재 작업은 PREPARATION이다. 아래 목록은 사용권 승인이나 앱 실행 증빙이 아니다.

| 자산 | 버전·기준 | 확인 범위 | 권리·반입 상태 |
| --- | --- | --- | --- |
| 확정 설계 | v1.1, blob `f13a3b9732c1490cdff7f3c9b52dbc474538a03a` | 전체 본문 및 확정 기록 읽음; 기준 commit 9437e5c와 동일 | 기존 저장소 문서; 제품·엔진 재배포 권한 부여 아님 |
| SVG | docs/design/assets의 기존 9개 | 파일 목록 확인, 변경 없음 | 설계 자산; 구현 화면 아님 |
| 상세 개발명세 | MP-PK-DEV 01~03 v1.0 | 전체 읽음 | 구현 계약; 실행 증거 아님 |
| 앱·테스트·lockfile | 없음 | git ls-files 확인 | NOT_IMPLEMENTED / NOT_RUN |
| Python | 3.11.2, /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 | stdlib SQLite 및 범용 FastAPI smoke | 목표 3.12 미설치; 최종 런타임 미확정 |
| SQLite | Python runtime 3.39.4 / CLI 3.51.0 | 메모리 DB FK 거절 확인 | 서로 다른 버전; 앱 DB 생성 없음 |
| Node / npm | 25.2.1 / 11.6.2 | JSON roundtrip | 목표 Node 22.12 이상 22.x와 다름 |
| FastAPI / Pydantic | 0.124.4 / 2.12.5 | 설치 metadata, FastAPI TestClient | metadata MIT; 전체 재배포 검토 미실행 |
| SQLAlchemy / Alembic | 2.0.36 / 1.13.3 | 설치 metadata만 | metadata MIT; migration 미실행 |
| pytest / httpx | 9.1.1 / 0.27.2 | metadata; httpx는 TestClient에 사용 | metadata MIT / BSD-3-Clause |
| Git / GitHub CLI | 2.49.0 / 2.96.0 | 조회·clone·로컬 branch | 사용자 도구; 앱 배포물에 포함하지 않음 |
| uv | PATH에서 없음 | command 조회 | 설치·실행 안 함 |
| 널스펜슬·닥터펜슬/STT/LLM | NOT_VERIFIED | 승인된 버전·commit·endpoint·권리 참조 미제공 | 소스 열람·반입·호출·모델 다운로드 안 함 |
| React/TypeScript/Vite | NOT_VERIFIED | 이 저장소 package/lockfile 없음 | 설치·빌드·호환성 검사 미실행 |

저장소 밖 이름에 medipencil이 포함된 경로가 검색되었으나 동일 제품·버전·권리의 증거로 사용하지 않았다. 비공개 코드·키·실제 자료를 읽거나 복사하지 않았다. OS 전체에 Python 3.12/Node 22가 없다고 단정하지 않으며 PATH와 확인한 표준 설치 위치에서 발견되지 않았다는 뜻이다.

## 추가 반입 시 채울 틀

| 제품명 | 버전 / commit | 준비 범위·작성 시점 | 실행 경로·endpoint 분류 | 권리 확인자·근거 ID | 일반 입력 시험·삭제 receipt | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 미지정 | NOT_VERIFIED | 미확인 | 미확인 | 미확인 | NOT_RUN | 반입 대기 |

Q-03 확인 전 실제 provider는 미설정이다. Veil·파생물·실제 음성·비공개 엔진·키는 이 저장소와 개발 에이전트 입력에 반입하지 않는다.
