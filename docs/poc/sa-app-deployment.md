# sa-app 공개 PoC 배포 / Public PoC deployment

2026-10-04 사용자 지시: “성아 서버 sa-app에 올려”. 이 승인에 따라 기존 성아 서버에 내부 합성자료 PoC를 배포했다. 제품 상세명세 확정이나 실제 지원팀 피드백을 뜻하지 않는다.

- URL: https://orch.sungah.kr/medipencil/
- 실제 호스트: sa-apps, Rocky Linux 9.7, Python 3.12.14.
- 직접 입력만 사용. `MEDIPENCIL_POC=1`에서 STT/LLM 비활성화. 원격 로컬 AI worker는 미구현.
- 현재 접근: 후속 사용자 지시 “poc이니까...일단 다 풀어”에 따라 계정·비밀번호 없이 링크로 접속한다. `MEDIPENCIL_PUBLIC_REVIEW=1`을 명시적으로 설정했다. 화면에서 직원(Koskinen), Liisa, Mikko를 선택한다. 서로 독립된 역할 시험에는 별도 브라우저 세션을 사용한다.
- 최초 배포의 비공개 접속정보 파일은 현재 접속에 필요하지 않다. 비밀값/DB/피드백 원문은 저장소에 넣지 않는다.

## 연결과 저장

`HTTPS sa-gateway /medipencil/ → sa-kvm nginx (게이트웨이 IP만 허용) → sa-apps nginx → 127.0.0.1:8767`

현재 게이트웨이는 Basic 인증을 끄고 외부 Authorization/reviewer/secret 헤더를 제거한다. 공개 PoC 모드에서는 proxy/reviewer 인증 없이 세 가지 합성 역할을 선택한다. 선택한 역할의 세션, CSRF, 가족별 자료 권한, 승인·발행·동의 경계는 유지한다. 기존 비공개 모드 구현과 시험은 복구 선택지로 남긴다. HTTPS Secure/HttpOnly/SameSite 쿠키는 `/medipencil/`에 한정한다. SPA basename과 API/asset 경로도 같은 prefix를 사용한다. 앱 포트는 외부에 열지 않았다. 내부 프록시 구간은 사설망 HTTP다.

- 앱: `/opt/medipencil/releases/20261004-public`, `/opt/medipencil/current`
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

다음 계정 관리 절차는 비공개 모드로 복구한 경우에만 적용한다. reviewer 권한 수정은 reviewers.json 변경 후 앱 재시작이 필요하다. 계정 폐기는 gateway htpasswd에서도 즉시 제거하고 nginx를 reload한다. 개인별 피드백 추적이 필요해지면 검토자별 계정을 발급해 역할을 명시적으로 매핑한다.

업데이트는 새 release에 배포하고 해당 release의 API를 venv에 설치한 후 current 전환/재시작한다. 실패 시 이전 release와 editable install을 함께 되돌린다. DB migration은 코드 rollback과 별도로 검토한다. 초기 설치에는 이전 MediPencil release가 없으므로 중단 시 gateway의 추가 location을 먼저 비활성화하고 nginx 문법 검사/reload 후 서비스와 timer를 중지한다. 회차 DB와 백업은 삭제하지 않는다. 공용 SELinux 설정은 다른 서비스 의존성을 확인하지 않고 되돌리지 않는다.

## 최초 비공개 배포 검증 범위 (이력)

- 로컬 API 80개, 기존 브라우저 시험 9개, UI 단위 시험 6개 통과.
- 공개 HTTPS URL에서 독립 Chromium 3 contexts로 직접 입력 루프 통과: 승인/발행 전 비노출, 정정, 가족별 근거 제한, 계획/완료 구분 포함.
- 원격 보안/코멘트 시험 통과: 미인증 401, 헤더 위조 및 역할 상승 차단, 다른 검토 계정의 세션 재사용 차단, 가족 코멘트 접근 403, 직원 코멘트 저장/재조회, 390px 화면.
- 서버 restart 후 기존 세션·가족 발행·코멘트 유지. snapshot+manifest를 별도 임시 DB로 복원해 API 조회 통과.
- 자동 시험 기록/코멘트는 `AUTOMATION_NOT_SUPPORT_TEAM` / `AUTO-SA-DEPLOY`로 구분한다. 실제 지원팀 FB-ID는 0개.
- 공인 HTTPS 도메인은 성아 VPN ON 상태의 Mac에서 검증했다. VPN OFF/다른 외부 회선의 실제 팀원 접속은 아직 미검증.
- 실제 AI 실행, 현장 검증, 최종 제품 운영 준비, 지원팀 실증 완료로 보고하지 않는다.

아래 credential 기반 명령은 최초 비공개 배포용이다. 현재 공개 PoC에는 문서 마지막의 공개 시험 명령을 사용한다. 원격 재시험은 지정한 서버 DB에 합성 시험 데이터를 저장한다. 승인이 있는 검토 회차에만 다음을 사용한다. credential JSON 형식은 `{"mp-staff":{"password":"..."},"mp-liisa":{"password":"..."},"mp-mikko":{"password":"..."}}`이며 파일은 저장소 밖 0600으로 보관한다.

```sh
cd apps/web
MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil \
MEDIPENCIL_REVIEW_CREDENTIALS=/absolute/private/access.json \
npx playwright test --config playwright.shared.config.ts
```

## 공개 PoC 변경

2026-10-04 후속 요청으로 접속 게이트만 해제했다. 독립 합성 DB/기존 코멘트/발행 자료와 daily backup은 보존한다. 이전 비공개 코드 release는 `20261004-shared`, 설정은 `service.env.before-public`, gateway location은 `/etc/nginx/medipencil/gateway.before-public.conf`에 보존했다. 공개 모드는 shared+PoC+HTTPS 조건에서만 가능하고 AI는 꺼져 있다.

현재 원격 시험 명령(자격증명 환경변수 없이 실행):

```sh
cd apps/web
MEDIPENCIL_REVIEW_URL=https://orch.sungah.kr/medipencil \
npx playwright test --config playwright.public.config.ts
```

공개 시험은 새 브라우저의 비밀번호 없는 진입, 모든 합성 역할 선택, 직원 코멘트 화면, 독립 3개 세션의 실제 돌봄 루프를 검증한다. 계정 차단 시험은 비공개 모드의 회귀 시험으로 유지한다. 실제 지원팀 피드백은 별도다.
