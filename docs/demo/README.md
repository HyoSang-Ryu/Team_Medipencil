# Päivän kuulumiset · 음성 차팅 데모 영상

두 영상은 핀란드어 자막으로 같은 순서를 보여줍니다.

1. 입소자 Aino의 합성 일상: 식사, 수면, 걷기
2. 간호사의 녹음 → 한국어 전사 → 핀란드어 차팅 초안 → 웹 기록 검토
3. 보호자의 모바일 화면 예시

| 버전 | 영상 | 음성 원본 | 차이 |
| --- | --- | --- | --- |
| 통합 | [roundloop-demo-fi-integrated.mp4](roundloop-demo-fi-integrated.mp4) | [integrated-dialogue.wav](integrated-dialogue.wav) | 입소자와 간호사의 돌봄 대화 중 녹음 |
| 분리 | [roundloop-demo-fi-separate.mp4](roundloop-demo-fi-separate.mp4) | [separate-dictation.wav](separate-dictation.wav) | 돌봄 후 간호사가 독립 음성 메모 녹음 |

핀란드어 자막: [통합 SRT](roundloop-demo-fi-integrated.srt) · [분리 SRT](roundloop-demo-fi-separate.srt). [포스터](roundloop-demo-fi-integrated-poster.png).

## 검증 범위

음성은 합성 한국어 음성이다. 로컬 Whisper medium으로 실제 전사하고, 로컬 Ollama `gpt-oss:20b`가 전사문을 바탕으로 핀란드어 초안을 생성했다. 검토 장면은 간호사가 문구를 다듬는 예시다.

KaiLab API 주소가 제작 당시 DNS 조회되지 않아 영상의 차팅·웹·모바일 장면은 실제 서비스의 완료 기록 화면이 아니라 **설명용 시각화**다. 실제 앱 승인과 보호자 발송은 수행하지 않았다. 종료 명령 `키데, 정리해줘`는 음성 인식에서 `기대 정리해줘`로 잘못 전사되어 버튼 종료 흐름으로 나타냈다. 모든 인물·돌봄 내용은 합성 시연 자료다.
