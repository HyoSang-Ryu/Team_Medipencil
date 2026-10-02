# 범용 개발환경 smoke (P-01)

이 디렉터리는 제품과 무관한 echo API·메모리 SQLite rollback·React 단일 문장 빌드로 도구 호환성만 확인한다. 가족 질문, 승인, 권한, 기록, 센서, 동의, 화면1~5, AI prompt, 제품 fixture는 포함하지 않는다. **C-01 구현이나 T-01~T-10 통과가 아니다.** 준비 자산으로 작성 시점과 commit을 보존한다.

검증 플랫폼: macOS arm64, Python 3.12.15, SQLite runtime 3.53.1, Node 22.16.0, npm 10.9.2, uv 0.12.22. Python dependencies는 requirements.lock.txt(hash 포함), Node dependencies는 web/package-lock.json에 고정했다. 앱 구현 단계에서는 필요한 의존성을 다시 선택·검증한다. 이 lock은 앱의 최종 lock이 아니다.

## 이 장비에서 재실행

저장소 루트에서 실행한다. PATH 변경은 아래 shell 세션에만 적용되며 전역 Python/Node를 교체하지 않는다.

```bash
MP_PREP=/Users/hyosang/.local/share/medipencil-preparation
export PATH="$MP_PREP/node-v22.16.0-darwin-arm64/bin:$PATH"
"$MP_PREP/bootstrap/bin/uv" pip sync --python "$MP_PREP/venv/bin/python" tools/preparation/requirements.lock.txt
"$MP_PREP/bootstrap/bin/uv" pip check --python "$MP_PREP/venv/bin/python"
"$MP_PREP/venv/bin/python" tools/preparation/smoke.py
npm --prefix tools/preparation/web ci
npm --prefix tools/preparation/web run typecheck
npm --prefix tools/preparation/web run build
```

Python smoke는 프로세스 내부 TestClient와 메모리 DB만 쓴다. 포트·실제 DB 파일·AI 호출 없음. 프론트 smoke는 타입 검사와 production bundle 생성까지이며 브라우저 검증은 NOT_RUN이다. `web/node_modules`와 `web/dist`는 추적하지 않는다.

## 새 장비 준비

위 절대경로는 관측 장비용이다. 새 장비에는 별도의 준비 폴더에서 Python 3.12와 Node 22.12 이상 22.x를 설치하고 `MP_PREP`를 맞춘다. 이 장비에서는 다음 방법으로 설치했다.

- Python 3.11의 venv에 uv 0.12.22를 설치하고 `UV_PYTHON_INSTALL_DIR`을 준비 폴더로 지정하여 `uv python install 3.12 --no-bin` 수행. 실제 선택된 버전은 3.12.15이며 재현 시 `3.12.15`로 지정한다.
- nodejs.org의 `v22.16.0/node-v22.16.0-darwin-arm64.tar.gz`를 같은 폴더에 다운로드하고 같은 배포의 `SHASUMS256.txt`와 `shasum -a 256 -c`로 일치 확인 후 압축 해제. 다른 OS/CPU는 해당 배포가 필요하다.
- `uv venv --python 3.12`로 저장소 밖 환경을 생성했다. 환경에는 실제 제품 데이터나 엔진 설정이 없다.

## 관측된 제한

- FastAPI TestClient에서 Starlette의 httpx 사용 deprecation warning 발생. smoke는 통과했지만 향후 앱의 test client 선택 때 재검토한다. 경고를 숨기지 않았다.
- Alembic/pytest/uvicorn은 설치 및 의존성 해석 확인까지만 수행했다. migration·pytest 수용 테스트·실제 socket 서버 검증은 하지 않았다.
- Homebrew 경로는 ca-certificates 링크 충돌로 실패하여 사용하지 않았다. 전역 링크를 강제로 바꾸거나 tap trust 정책을 완화하지 않았다.
- 라이선스·재배포 전체 검토, 실제 STT/LLM, FI 의미 검수, 앱 보안, 브라우저 동작은 이 smoke로 입증되지 않는다.
