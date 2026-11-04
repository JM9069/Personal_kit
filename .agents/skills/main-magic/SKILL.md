---
name: main-magic
description: 허브 마법봉(MAIN) — 🪄 지시 + 끝 줄 «$main-magic 요청id» 를 받으면 고른 hand_off 작업 노드의 구현을 내 서브에게 시킨다. 허브가 queue 로 보낸다.
---

# main-magic — 고른 hand_off 작업 노드 구현 지시
- Claude 세션이면 끝 줄이 «/main-magic 요청id» 로 온다 — 같은 뜻 · 아래 그대로

1. python3 ~/.codex/skills/codex-hub/magic.py show 요청id — 요청id = 메시지 끝 줄 $main-magic 뒤 낱말(m월일-시분초-4자리) · 고른 노드 · 함수 표 · 요약이 나온다(상태 줄은 스크립트가 바꿈)
2. 작업 노드마다 flowtree.py --role main start <id> → **내 서브에게 구현을 시킨다**(내가 코드를 쓰지 않는다)
   - 지시문: 목표(노드 제목 · 요약) · 읽을 것(hand_off 그 섹션 · show 의 함수 표) · 쓸 파일(섹션 수정 범위만 · 밖이면 멈추고 보고) · 끝 신호(시험 명령 · 커밋) · 보고 형식 · 모델 · 강도 · «서브를 또 띄우지 않는다»
   - show 의 함수 표(파일 | 함수 | 설명 | ⭐) 이름으로 만든다 · «이름 바뀜: 옛 → 새» 가 있으면 그 이름으로 코드 · 시험 · 문서를 바꾸는 일까지 서브에게 시키고(CODE_RULE 9-1) 끝나면 flowtree.py --role main funcs-ack <id>
3. 서브 커밋을 받으면 서브 보고의 끝 신호(시험 명령)만 한 번 돌려 통과면 done <id>(diff 를 읽지 않는다 — 검토는 INSP · 검증을 기다리지 않는다)
4. 섹션을 시작 · 끝낼 때 hand_off «섹션 작업 순서» 실제 칸에 한 줄 덧붙인다(서브에게 · 기존 줄은 안 고침)
5. 그 밖 노드(요구 · 결정 · 파일 · 질문)는 맥락만 · «멈춤»(작업 노드 0개)이면 노드를 만들지 말고 유저에게 묻고 턴을 끝낸다
6. 끝나면 상태 줄 · 큰 단위였으면 hub.py log 한 줄($codex-hub)
