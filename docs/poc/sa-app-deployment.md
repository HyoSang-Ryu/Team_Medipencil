# sa-app 팀 검토 배포 / Shared review deployment

2026-10-04 사용자 지시: “성아 서버 sa-app에 올려”. 이 승인에 따라 기존 성아 서버에 내부 합성자료 PoC를 배포했다. 제품 상세명세 확정이나 실제 지원팀 피드백을 뜻하지 않는다.

- URL: https://orch.sungah.kr/medipencil/
- 실제 호스트: sa-apps, Rocky Linux 9.7, Python 3.12.14.
- 직접 입력만 사용. `MEDIPENCIL_POC=1`에서 STT/LLM 비활성화. 원격 로컬 AI worker는 미구현.
- 인증: HTTPS Basic 인증 후 서버 허용 목록. 초기 검토 계정은 직원, Liisa, Mikko용 각 1개다. 실제 사람의 신원 증명/개인별 감사 계정은 아니다. 역할별로 별도 브라우저 프로필을 사용한다. 같은 브라우저는 Basic 자격증명을 기억할 수 있다.
- 개인 Mac의 비공개 접속정보 파일을 사용자에게 전달한다. 비밀번호/프록시 키/DB/피드백 원문은 저장소에 넣지 않는다.

## 연결과 저장

`HTTPS sa-gateway /medipencil/ → sa-kvm nginx (게이트웨이 IP만 허용) → sa-apps nginx → 127.0.0.1:8767`

게이트웨이가 브라우저의 인증 헤더를 검증하고 reviewer/secret 헤더를 덮어쓴다. 백엔드는 매 요청에서 프록시 비밀값과 reviewer를 검사한다. 세션은 reviewer에 결합하고 로그인 및 기존 세션의 역할 권한을 재검사한다. HTTPS Secure/HttpOnly/SameSite 쿠키는 `/medipencil/`에 한정한다. SPA basename과 API/asset 경로도 같은 prefix를 사용한다. 앱 포트는 외부에 열지 않았다. 내부 프록시 구간은 사설망 HTTP다.

- 앱: `/opt/medipencil/releases/20261004-shared`, `/opt/medipencil/current`
- venv: `/opt/medipencil/venv`
- 서비스: `medipencil.service`, 전용 OS 사용자 `medipencil`, 자동 시작/실패 재시작
- 설정: `/etc/medipencil/service.env`, `/etc/medipencil/reviewers.json` (root:medipencil 0640)
- 회차: `/var/lib/medipencil/review-20261004` (0700)
- 백업: `/var/lib/medipencil/backups`, DB snapshot + 동일 이름의 `.run.json`
- 게이트웨이: `/etc/nginx/sa-infra-locations/medipencil.conf`, `/etc/nginx/medipencil/htpasswd`
- KVM: `/etc/nginx/conf.d/medipencil.conf`
- 앱 nginx: `/etc/nginx/default.d/medipencil.conf`

sa-apps 방화벽은 `192.168.122.1/32`에서 TCP 80으로 오는 요청만 추가 허용했다. nginx의 loopback proxy 연결에 필요한 `httpd_can_network_connect`를 off에서 on으로 변경했다. 기존 서비스 설정 파일은 덮어쓰지 않았다. Python 설치 종속성으로 sqlite-libs가 3.34.1-9에서 3.34.1-11로 업데이트됐다.

## 운영 / Operations

```sh
systemctl status medipencil
systemctl restart medipencil
journalctl -u medipencil --since today
systemctl start medipencil-backup.service
systemctl list-timers medipencil-backup.timer
```

매일 서버 시간 03:15(KST)에 SQLite backup API로 일관된 snapshot을 생성한다. 첫 수동 실행 및 별도 임시 디렉터리 복원 후 실제 API 조회를 검증했다. 원본 DB를 덮어쓰지 않았다. 백업은 같은 서버에 있으며 서버 밖 백업·자동 보존기간 정리는 아직 없다. 디스크 여유를 확인하면서 회차 종료 후 보존/삭제를 결정한다.

백업 복원은 별도 디렉터리에 snapshot을 `demo.sqlite`, 동반 manifest를 `run.json`으로 복사하고, 전용 사용자 소유/0700 디렉터리/0600 파일을 유지한다. 별도 포트와 테스트 설정으로 검증한 뒤에만 서비스 정지와 DATA_ROOT 교체를 수행한다. 실행 중 DB의 파일 복사나 WAL 삭제로 복원하지 않는다. 비밀값·reviewer 설정은 DB snapshot에 포함되지 않는다.

reviewer 권한 수정은 reviewers.json 변경 후 앱 재시작이 필요하다. 계정 폐기는 gateway htpasswd에서도 즉시 제거하고 nginx를 reload한다. 개인별 피드백 추적이 필요해지면 검토자별 계정을 발급해 역할을 명시적으로 매핑한다.

업데이트는 새 release에 배포하고 해당 release의 API를 venv에 설치한 후 current 전환/재시작한다. 실패 시 이전 release와 editable install을 함께 되돌린다. DB migration은 코드 rollback과 별도로 검토한다. 초기 설치에는 이전 MediPencil release가 없으므로 중단 시 gateway의 추가 location을 먼저 비활성화하고 nginx 문법 검사/reload 후 서비스와 timer를 중지한다. 회차 DB와 백업은 삭제하지 않는다. 공용 SELinux 설정은 다른 서비스 의존성을 확인하지 않고 되돌리지 않는다.

## 검증 범위

- 로컬 API 80개, 기존 브라우저 시험 9개, UI 단위 시험 6개 통과.
- 공개 HTTPS URL에서 독립 Chromium 3 contexts로 직접 입력 루프 통과: 승인/발행 전 비노출, 정정, 가족별 근거 제한, 계획/완료 구분 포함.
- 원격 보안/코멘트 시험 통과: 미인증 401, 헤더 위조 및 역할 상승 차단, 다른 검토 계정의 세션 재사용 차단, 가족 코멘트 접근 403, 직원 코멘트 저장/재조회, 390px 화면.
- 서버 restart 후 기존 세션·가족 발행·코멘트 유지. snapshot+manifest를 별도 임시 DB로 복원해 API 조회 통과.
- 자동 시험 기록/코멘트는 `AUTOMATION_NOT_SUPPORT_TEAM` / `AUTO-SA-DEPLOY`로 구분한다. 실제 지원팀 FB-ID는 0개.
- 공인 HTTPS 도메인은 성아 VPN ON 상태의 Mac에서 검증했다. VPN OFF/다른 외부 회선의 실제 팀원 접속은 아직 미검증.
- 실제 AI 실행, 현장 검증, 최종 제품 운영 준비, 지원팀 실증 완료로 보고하지 않는다.

원격 재시험은 지정한 서버 DB에 합성 시험 데이터를 저장한다. 승인이 있는 검토 회차에만 다음을 사용한다. credential JSON 형식은 `{"mp-staff":{"password":"..."},"mp-liisa":{"password":"..."},"mp-mikko":{"password":"..."}}`이며 파일은 저장소 밖 0600으로 보관한다.

```sh
cd apps/web
MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil \
MEDIPENCIL_REVIEW_CREDENTIALS=/absolute/private/access.json \
npx playwright test --config playwright.shared.config.ts
```
