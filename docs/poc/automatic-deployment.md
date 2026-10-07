# 돌봄루프 API·DB·화면 자동 배포

배포 브랜치: `poc/remote-validation`. 일반 팀원은 저장소 Write 권한만 있으면 된다. VPN은 배포 관리자에게만 기존 서버 접속 방법으로 남는다.

## 정상 흐름

1. GitHub Actions build가 API/DB·배포 복구·UI·브라우저 시험과 빌드를 완료한다.
2. publish-api가 `sungah-<sha>-<run_id>-<attempt>` prerelease에 allowlist로 만든 코드/웹 파일 번들을 게시한다.
3. 서버 `medipencil-deploy.timer`가 3분 간격으로 공개 GitHub를 조회한다. 실제 서버에 토큰을 저장하지 않고, 성공한 동일 run/attempt의 build/publish job 및 origin repository/branch/commit/hash를 검사한다.
4. 별도 release/venv에 앱을 설치한다. 설치 스크립트와 앱/migration은 medipencil 사용자로 실행한다. root 배포 agent는 파일 전환·백업·systemd만 관리한다.
5. 운영 DB의 복사본에서 새 migration을 시험한다. 성공한 경우에만 유지보수 응답을 켜고 실제 API를 정지한다.
6. 정지 상태에서 SQLite snapshot과 run manifest를 백업하고 새 migration을 실행한다. DB 무결성·외래키를 검사한다.
7. current symlink 전환 후 API를 기동한다. local health와 정확한 commit을 확인하고 유지보수 응답을 해제한다.
8. GitHub deploy-api가 공개 HTTPS health의 같은 commit을 확인한 뒤 Pages를 배포하고, GitHub 실행기에서 화면/API를 검사한다.

기존 질문·동의·발행·팀 코멘트는 같은 `/var/lib/medipencil/review-20261004` DB에 남는다. 이 작업은 데이터 초기화가 아니다. 전환 중 잠시503 응답이 발생할 수 있다. UI 저장 실패 시 입력을 보존하고 연결 복구 후 다시 시도한다.

## 실패와 복구

- 설치/복사본 migration 실패: 이전 API는 그대로 실행된다.
- 실제 migration/기동 실패: API가 정지되고 외부 요청이 막힌 상태에서 이전 SQLite와 코드로 복구한 뒤 재개한다.
- 배포 프로세스 중단: root 소유 transaction.json을 다음 실행에서 읽고 완료 또는 복구한다.
- 새 API가 정상으로 공개된 후: 이후 사용자 쓰기를 지우는 DB 자동 되감기를 하지 않는다. API healthy 이후의 장애는 운영자가 현재 데이터를 보존하며 복구한다.
- 실패 tag는 재시도하지 않는다. 수정 push 또는 Re-run all jobs의 새 attempt로 다시 배포한다.
- 백업은 서버 로컬에 보관한다. 서버 자체 손실을 대비한 외부 백업은 별도다. 새 release는 최소800MB 여유가 없으면 설치를 시작하지 않는다. 오래된 release/배포 백업 자동 삭제는 하지 않으므로 운영자가 디스크를 관리한다.
- 공개 GitHub API의 rate limit/네트워크 장애 시 다음 timer 실행을 기다린다. GitHub wait 단계 제한을 초과하면 실패로 표시되며 기존 Pages를 교체하지 않는다.

## 관리자 명령과 파일

```sh
systemctl status medipencil-deploy.timer medipencil-deploy.service
journalctl -u medipencil-deploy.service --since today
systemctl start medipencil-deploy.service
systemctl stop medipencil-deploy.timer
```

- 고정 배포 agent/launcher: `/usr/local/lib/medipencil-deploy/` (root 소유)
- API launcher override: `/etc/systemd/system/medipencil.service.d/deployment-launcher.conf`
- 배포 상태/복구 journal/실패 tag/백업: `/var/lib/medipencil-deploy/` (root0700)
- 유지보수 marker: `/usr/share/nginx/html/medipencil-maintenance`
- release/venv: `/opt/medipencil/releases/sungah-<sha>-<run>-<attempt>/`
- runtime config: 기존 `/etc/medipencil/service.env` 유지

점검 marker나 복구 journal을 임의 삭제하지 않는다. 복구가 실패하면 marker가 유지되므로 로그와 snapshot을 먼저 확인한다. 기존 수동 release와 `/opt/medipencil/venv`는 첫 자동 배포의 롤백을 위해 보존한다. 현재 릴리스와 복구용 이전 릴리스는 제거하지 않는다.

이 자동 배포는 앱/API와 버전 관리된 SQLite migration에 적용된다. OS 패키지·nginx/systemd·고정 배포 agent 자체 변경, secrets 변경은 별도 관리자 작업이다. 배포 파일이나 DB 원문을 CI 로그에 출력하지 않는다.

Rocky Linux 최초 설치 시 `/tmp`에서 복사한 파일은 SELinux 레이블을 확인한다. `restorecon -Rv /etc/systemd/system/medipencil-deploy.service /etc/systemd/system/medipencil-deploy.timer /usr/local/lib/medipencil-deploy /etc/systemd/system/medipencil.service.d` 후 `systemctl daemon-reload`와 timer enable을 실행한다. SELinux를 끄지 않는다.
