---
name: insp-magic
description: 허브 마법봉(INSP) — 🪄 지시 + 끝 줄 «$insp-magic 요청id» 를 받으면 고른 검증 노드의 검증을 복제 서브에게 시킨다. 허브가 queue 로 보낸다.
---

# insp-magic — 고른 검증 노드 검증 지시
- Claude 세션이면 끝 줄이 «/insp-magic 요청id» 로 온다 — 같은 뜻 · 아래 그대로

1. python3 ~/.codex/skills/codex-hub/magic.py show 요청id — 요청id = 메시지 끝 줄 $insp-magic 뒤 낱말 · 검증 노드만 나온다(상태 줄은 스크립트가 바꿈)
2. 검증 노드마다 flowtree.py --role insp verify-start <id> → **복제 서브에게 검증을 시킨다**(insp 검증 서브 지시 · 코드 수정 금지 · 쓸 곳 = hand_off 검증 기록 · 개선 제안 · tests/ 재현 스크립트)
3. 서브가 커밋하면 재현 스크립트를 내가 한 번 다시 돌려 확인 → run <id> pass|fail '근거(커밋 · 시험 명령 · 불일치 N건)'
4. MAIN 미커밋 변경이 볼 파일에 있으면 시험하지 않고 «검증 불가 — MAIN 미커밋(파일)»
5. 섹션 검증이 끝나면 hub.py log 한 줄($codex-hub)
