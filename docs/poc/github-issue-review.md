# GitHub 이슈 반영 — 2026-10-11

사용자가 지정한 [이슈 목록](https://github.com/HyoSang-Ryu/Team_Medipencil/issues)의 열린 이슈 7개를 실제로 조회했다. 노션의 기존 이슈라고 추정해 작성했던 역할 분담과는 별개의 프로그램 수정 작업이다. 이 문서는 후속 제품 명세 확정이 아니다.

| 이슈 | 조치 | 범위·남은 항목 |
| --- | --- | --- |
| [#2 초기 방향](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/2) | 기존 합성 EMR·공개 범위·직원 검토·카드 UI를 유지. 자동 전달은 확인된 합성 일상 원문만 허용 | 실제 데이터/실제 EMR/자유 AI 요약/업무 절감 검증은 완료 아님 |
| [#4 로그인 사진](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/4) | 기존 PR에서 들어온 login-background.webp 배경 재사용 및 브라우저 확인 | 새로운 사진을 임의로 교체하지 않음 |
| [#8 동의 간소화](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/8) | 항목마다 공개/비공개 스위치·상태 표시, 변경한 경우에만 확인 근거 입력 | 동의 사실·날짜·수신자별 원자적 저장은 보존 |
| [#9 이름](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/9) | Aino Nieminen, Liisa Nieminen, Heli Koskinen. 새 seed 및 기존 DB 이름 마이그레이션 | 기존 ID·기록과 사용자가 달리 지정한 표시명 보존 |
| [#10 보호자 대시보드](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/10) | 색상별 항목을 세로 한 줄로, 글자 확대. 그래프는 상세 화면으로 이동. 건강정보 포함 7항목 순서 통일 | 실제 허용된 항목만 표시하므로 제한된 보호자의 항목 수는 7보다 적을 수 있음. 막대는 기록 건수, 건강 점수 아님 |
| [#11 보호자 상세](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/11) | 오늘의 안부/기간별 안부/가족확인사항/설정 4개 패널. 중복 바로가기 삭제. 문의 작성·답글은 가족확인사항 안에 통합 | 질문 기능과 기존 이력은 삭제하지 않음. 탭 이동 중 작성 내용 유지 |
| [#12 직원 화면](https://github.com/HyoSang-Ryu/Team_Medipencil/issues/12) | 서버의 담당 권한 목록·병동 표시, 합성 EMR v1 표기, 질문 전체/대기 수, 대기 질문의 답글 칸 바로 표시, 동의 스위치. 정기 전달은 회차별 승인 없는 별도 경로 | **부분 반영**: 현재 운영 대상자 Aino 1명. 실제 교대 편성/여러 환자 작업공간 전환은 미구현. 일반 AI/수기 초안의 근거 검토·승인은 유지하며 모든 AI 결과 무검토 발행으로 확대하지 않음 |

정기 전달은 최초 한 번 시작한 보호자에게 매일 Europe/Helsinki 18시에 앱 내 발행한다. 현재 독립 합성 EMR의 확인된 식사/이동 관찰 원문만 대상이고 미확인 계획은 직원 확인 목록에 남긴다. 실제 AI·실제 EMR·문자/이메일 발송 없음. 기본 중지이며 운영 보호자의 설정을 이번 작업에서 임의로 켜지 않는다.

GitHub 이슈는 자동으로 닫거나 현지팀 검증 완료로 표시하지 않는다. 실제 수정·시험·배포 증빙은 validation-log.md에 기록하며, 개선된 화면에 대한 사람 재확인은 별도다.
