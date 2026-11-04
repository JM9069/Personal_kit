---
name: 2nd-magic
description: 허브 마법봉(2ND) — 🪄 질문 + 끝 줄 «$2nd-magic 요청id» 를 받으면 유저가 고른 대상(노드 · 파일 · 글자 · 줄 · 책 스티커)에 대한 질문에 답을 정해진 자리에 넣는다. 허브가 queue 로 보낸다.
---

# 2nd-magic — 무엇에든 질문
- Claude 세션이면 끝 줄이 «/2nd-magic 요청id» 로 온다 — 같은 뜻 · 아래 그대로

1. python3 ~/.codex/skills/codex-hub/magic.py show 요청id → 요청id = 메시지 끝 줄 $2nd-magic 뒤 낱말 · 질문 · 대상 · 답 자리(node · md · code · form · note)와 명령이 나온다
2. 짧은 답(대상 맥락만 읽으면 됨)은 직접 · 조사가 필요하면 **내 서브에게** 조사 + 답 넣기를 시킨다(쓸 곳 = 그 답 자리뿐 · show 의 답 자리 명령을 지시문에 그대로 · 모델 · 강도 · «서브를 또 띄우지 않는다»)
3. 답 자리 명령: node → answer-node(--short 결론 60자) · md → answer-md · code → answer-code · form → answer-form · note → answer-note
   - note(책 스티커) = show 의 블록 ID 로 책 칸 · 계약을 읽고 바로 답(근거 칸 · 계약 id) — 책은 다시 읽을 때 초록 답 칸
4. 답은 짧게, 근거(파일 · 줄 · README 문장) · 자리는 스크립트가 찾는다(손으로 파일을 고치지 않는다 · magic.py 답 넣기는 저장소 쓰기 금지의 예외)
5. 상태 줄만(스크립트가 바꿈) · 누적은 안 한다
