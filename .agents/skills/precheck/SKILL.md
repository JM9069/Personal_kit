---
name: precheck
description: 사전 체험(15분 안팎) 왕복 점검 — 이 스킬 하나로 끝낸다. 실제 TUI 두 세션 · devview 로 큐 · 허브 연결 · 서브 8개 · 서브 간 대화 · 설문 · 스티커 · 그래프 마법봉 · 기계 환경(envcheck) · 책 재료를 서브가 병렬로 돌리고 전부 키트 precheck.md 한 문서에 적는다. "$precheck" · 사전 체험 왕복 점검.
---

# precheck — 사전 체험 왕복 점검

- 도구 = 같은 폴더의 precheck.py(아래 PC) · 판정은 세션 기록 · 요청 파일 · 답 자리 · HTTP 로 스크립트가 한다 · 모델 말만으로 통과가 아니다
- ready-start 는 돌리지 않는다 · ReadyStart.md 는 prepare 가 정본 함수로 쓴다 · 그대로 대회 명령(`$main`)을 치면 온톨로지가 시작되므로 **시험 세션은 start.sh.txt 의 명령으로** 띄운다(옵션 같음 · 강도 low · 시작 메시지만 다름)
- 고치지 않는다: 자동 설치 · 자동 수리 · 재시도 반복 없음. 실패는 적고 다음으로 · 실패 원인이 분명할 때 여유 시간에 1회만 재시도
- 시험 재료(설문 · 노드 · 스티커 · 표식)에는 모두 run id 가 붙는다 · 결정 문서 반영 · 커밋 · 과제 분석 · 코드 구현 금지 · 끝나면 무엇을 남겼는지는 precheck.md «남긴 것»
- 15분은 제한이지 통과 보장이 아니다 · 끝나지 않은 칸은 «제한 내 미완료» 로 적는다

## 시작 — 첫 세션의 `$precheck`(유저가 치는 스킬은 이것 하나 · 결과는 precheck.md 하나)
- 첫 세션이 할 일: 아래 prepare 를 돌리고 → 유저에게 start.sh.txt 3줄(devview · MAIN · 2ND) · 대화 탭 문장 · 시험 책 주소를 보여 주고 «할 일 = 키트 usercheck.md» 한 줄로 턴을 끝낸다 · 그 뒤는 MAIN 이 서브에게 나눈다
- 유저가 하는 일은 셋뿐: 탭 3개 띄우기 → 화면 U1 ~ U18(칸마다 자세한 순서 = 키트 usercheck.md) → 대화 탭에서 MAIN 에 결과 한 줄 + «정리»
- 키트에서: `python3 skills_src/precheck/precheck.py prepare`(설치본) · 저장소 그대로면 `python3 .agents/skills/precheck/precheck.py prepare`
- ~/.codex/skills 가 없어도 돈다(P1 실패로 적힘) · prepare 는 끝에 devview 명령 · 시작 명령 파일 · 대화 탭 문장 · 시험 책 주소를 찍는다
- «등록 충돌 🟠» 이 뜨면 멈추고 유저가 정한다 — 쓰는 main · 2nd 세션이 있으면 시험 세션이 등록을 덮는다(지난 시험의 남은 등록이면 그대로 진행)
- 띄우는 순서(줄마다 새 탭): 0 devview → start.sh.txt 의 MAIN → 2ND. 모양은 이렇다(값은 start.sh.txt 정본):

        codex -C <키트> --add-dir <루트> -m gpt-6.1-sol -c model_reasoning_effort=low -c model_verbosity=high -c service_tier=fast -c features.multi_agent_v2.enabled=true … --approve-for-me '<이 파일> 를 읽고 «MAIN» 절대로 한다 · run <run> · 도구 <PC>'
        codex -C <키트> --add-dir <루트> -m gpt-6.1-sol -c model_reasoning_effort=low … --approve-for-me '<이 파일> 를 읽고 «2ND» 절대로 한다 · run <run> · 도구 <PC>'

- «폴더 신뢰» 는 예 · «Hooks need review» 는 2 — 이 화면에서 세션이 멈췄는지 유저가 본다

## 유저 체크표 — 첫 안내에 한 번만 보여 준다

| 체크 | 유저가 할 일 | 함께 확인 |
|---|---|---|
| U1 | 외부 Browser 로 devview 연다(PORT 8701) | 실제 외부 주소 · 화면 |
| U2 | 대화 탭에서 MAIN 에 prepare 가 찍은 문장 전송 | 대화 입력 · 응답 |
| U3 | 시험 설문(위쪽 설문 탭): 첫 문항은 선택지 · 둘째는 «질문» 단추 + 메모 → 제출 한 번 | MAIN · 2ND 분기 · 설명 폼 답 |
| U4 | 시험 책 주소를 PORT 8801 로 열고 스티커 🪄 | 페이지 서버 · 2ND · 스티커 답 |
| U5 | 그래프 «섹션1» 탭의 오른쪽 위 점 셋(작업 · 검증 · 질문 · 멀리서는 제목 없이 점으로 보임 · Main 탭에는 작업만)을 Ctrl+클릭 → 허브 MAIN 행 클릭 → 오른쪽 트레이 마법봉 한 번 — 안 되면 나눠 누르고 그 사실을 적는다 | 선택 · 종류별 분배 · 결과 |
| U6 | 종의 run 알림 · 위 답 표식이 화면에 보이나 | API 와 화면 구분 |

| U7 | 코드 탭에서 CSV 하나 열기 · 그래프 Main 의 AGENTS.md 파일 노드를 고르고 ` | 표로 뜨나 · 파일이 열리나 |
| U8 | Alt+Q/W · Alt+` · 0~8 · Alt+Z/X/C/V 눌러 보기 | Browser 에 안 뺏기나 |
| U9 | 대화 탭 서브 목록을 보고 창을 끌어 보기 | 8개가 보이고 끌리나 |
| U10 | 체험 내내 터미널이 끊기나 | 끊기면 시각 |
| U11 ~ U18 | 그래프 — 화면 스위치 · Main 표시 · 틀 · 자유 배치 · 노드 추가 · 줌 · 자세히 · 설문 노드(usercheck.md 3절) | 칸마다 그 문서 |

- 다 보면 유저가 대화 탭에서 MAIN 에 한 번에: «U1 통과 U2 통과 U5 실패 나눠 눌러야 함 … 정리» — 받아 적는 일은 MAIN(9 · 10번) · 유저는 터미널 명령을 치지 않는다

## 시간 배분(제안 · 실제는 precheck.md 시각)
| 단계 | 분 | 내용 |
|---|---|---|
| 준비 | 0~2 | prepare · devview · 두 세션 · 허브 등록 |
| 서브 | 2~6 | MAIN 8개 생성 · A/B 왕복 · 긴 wait · c3 ~ c8 병렬 점검 |
| 화면 왕복 | 6~11 | 유저 체크표 U1~U18 (서브 단계와 겹쳐도 된다 · MAIN 턴 중이면 입력은 턴이 끝난 뒤 들어간다) |
| 정리 | 11~13 | 마지막 list_agents · `check --final` |
| 여유 | 13~15 | 원인이 분명한 실패 1회 재시도만 |

## MAIN
- 도구 호출은 run · PC 를 시작 메시지 값으로 쓴다 · 표식 낱말의 <run> 도 그 값. 답은 한 줄 · 설명하지 않는다
- 이 세션에서 `$main` · 과제 파악 · 온톨로지 · 문서 읽기를 하지 않는다

1. 허브: `python3 <SK>/codex-hub/hub.py register --nick main` → `whoami` (<SK> = PC 가 든 폴더의 부모)
2. 서브 c1~c8 을 한 턴에 띄운다 — spawn_agent 이름 c1 … c8 · fork_turns none · 강도 low · 지시문은 아래 그대로(N 만 바꿈)

        표식 READY-cN-<run> 한 줄만 답하고 턴을 끝낸다. 파일 · 셸 · 검색 · 서브 생성 금지. 뒤에 일을 더 주면 그때 그 지시의 도구만 쓴다.

   - 8번째가 실패하면 오류 원문을 `python3 <PC> mark S8 실패 --note '원문'` 으로 남기고 만든 서브로 계속
3. 완료를 긴 wait_agent 로 받는다(timeout_ms 600000) → list_agents 한 번(1차 관측 · 없으면 넘어감)
4. c1(A)에게 followup_task — 주소는 전체 경로

        차례대로 도구로 한다. ① send_message 대상 /root/c2 글 HELLO-<run> ② followup_task 대상 /root/c2 글 «표식 B-FOLLOW-<run> 한 줄만 답하고 끝낸다» ③ send_message 대상 /root 글 A-REPORT-<run> ④ 표식 A-DONE-<run> 한 줄로 끝낸다. 서브 생성 금지.

5. wait_agent 로 A-REPORT · A-DONE · B-FOLLOW 를 받는다
6. c2(B)에게 followup_task «표식 B-WAIT-<run> 한 줄만 답하고 끝낸다» → 곧바로 wait_agent(timeout_ms 600000) — 다른 알림으로 일찍 돌아오면 B-WAIT 를 받을 때까지 다시 wait
   - 이번 판은 관문을 뺐다 — 미래 도착 순서는 미확인으로 적힌다
7. 나머지 점검을 c3 ~ c8 에게 **한 번에 나눠** followup_task(병렬) → wait_agent — 끝 줄만 답하게 한다 · 설치 금지
   - c3 «python3 <PC> sub-worktree 를 돌리고 끝난 줄 그대로 답한다»
   - c4 «~/.codex/skills/insp/SKILL.md(없으면 <SK>/insp/SKILL.md)의 처음 나오는 «## » 줄을 읽어 python3 <PC> sub-skill '그 줄' 을 돌리고 결과 한 낱말을 답한다»
   - c5 «샌드박스 밖 실행 승인으로 python3 <PC> sub-env»(샌드박스 안이면 소켓 칸이 틀린다)
   - c6 «샌드박스 밖 실행 승인으로 python3 <PC> sub-book»
   - c7 «python3 <PC> sub-file»
   - c8 «샌드박스 밖 실행 승인으로 python3 <PC> ping» — 표식은 내 턴이 끝난 뒤 들어온다
   - 줄 내용을 지시문에 쓰지 않는다(읽었는지 가르는 시험)
8. `python3 <SK>/codex-hub/hub.py send --to 2nd '[precheck <run>] E4-<run> 받았으면 ACK-E4-<run> 한 줄만'`(샌드박스 밖 승인) → 여기까지 턴을 끝내지 않는다 · 끝나면 `DONE-SUBS-<run>` 한 줄로 턴을 끝낸다
9. 이후 입력(queue)마다
   - «[precheck <run>] Q1 · T1 … ACK-…» → 그 ACK 표식 한 줄만
   - 유저의 «U1 통과 U5 실패 …» → 칸마다 `python3 <PC> mark U5 실패 --note '유저가 쓴 말'` · «U 전부 통과» 면 U1 ~ U18 전부 통과(«빼고» 뒤 칸만 그 말대로) · 말하지 않은 칸은 두고 · 끝에 «정리» 가 있으면 10번으로
   - 🪄 설문 → `magic.py show <요청id>`(<SK>/codex-hub/magic.py) 만 하고 결정 문서 · 커밋 · 작업 없이 `ACK-SV-<run>` 한 줄 — 🔴 main-magic 스킬이 실려도 이 절이 앞선다
   - 🪄 노드 → `magic.py show <요청id>` 뒤 main-magic 분배만 실제로 한다(시험 파일만)
     - 작업: `python3 <키트>/devview/flowtree/flowtree.py --role main start <id>` → c5 에게 followup_task «python3 <PC> sub-task <id>» → 받으면 done <id>
     - 검증: c6 에게 followup_task «flowtree.py --role insp verify-start <id> → run <id> pass 'precheck <run> 시험'»
     - 질문: c7 에게 followup_task «flowtree.py --role 2nd answer-start <id> → answer <id> --short 'precheck <run>' '시험 답 <run>'»
     - wait_agent 로 받고 턴을 끝낸다
     - 서브가 없으면 있는 서브로 · 하나도 없으면 직접 하지 말고 mark 로 적는다
10. 유저가 «정리» 라고 하면 list_agents 한 번 더(2차 관측) → c8 에게 followup_task «샌드박스 밖 실행 승인으로 python3 <PC> check --final 을 돌리고 요약 줄을 그대로 답한다» → wait_agent → 유저에게 요약 줄 + precheck.md 경로 · 🔴 승인이 막혀 못 돌면 유저에게 터미널 탭에서 칠 그 한 줄을 준다
- 도구 호출이 막힌 칸은 오류 원문을 mark 로 남긴다(`mark W1 "제한 내 미완료" --note …`) · 내 샌드박스에서 쓰기가 막히면 밖 승인을 청한다

## 2ND
- 이 세션에서 `$2nd` · 대기 서브 · 과제 훑기를 하지 않는다 · 답은 한 줄

1. 허브: `python3 <SK>/codex-hub/hub.py register --nick 2nd` → `whoami` → `READY-2ND-<run>` 한 줄로 턴을 끝낸다
2. «[precheck <run>] E4 … ACK-E4 …» → 그 ACK 표식 한 줄만
3. 🪄 설문 질문 → `magic.py show <요청id>` → `magic.py answer-form <요청id> 'SV-<run> 시험 답'` → `ACK-SV2-<run>` 한 줄(MAIN 에 알리는 send 는 생략)
4. 🪄 책 스티커 → `magic.py show <요청id>` → `magic.py answer-note <요청id> 'ST-<run> 시험 답' --title 'precheck'` → `ACK-ST-<run>` 한 줄
- 🔴 답을 채팅으로만 내면 실패다 — 답 자리 명령을 쓴다 · 2nd-magic 스킬이 실려도 이 절이 앞선다(조사 · 서브 없이)

## 판정 · 끝
- 언제든: `python3 <PC> check` → precheck.md 의 그 run 절만 바뀐다 · 끝: `python3 <PC> check --final`(ReadyStart «준비 상태» 에 한 줄) — 돌리는 쪽은 서브(MAIN 10번)
- 🔴 check 는 샌드박스 밖에서 — devview HTTP 를 봐야 해서 샌드박스 안에서는 D1 · N1 이 «미확인» 으로 남는다(앞선 관측이 있으면 그것을 쓴다)
- queue 시험(Q1)의 접수 종료코드는 통과가 아니다 · check 가 세션 기록에서 입력 · 답 표식을 본다
- 결과 값: 통과 / 실패 / 선행 실패로 차단 / 미확인 / 제한 내 미완료 / 제외 / 미실행 · 치명 항목이 전부 통과 · 제외여야 총 판정 통과
- 재시작 재연결은 이번 범위 밖 · 기계 환경은 sub-env 가 envcheck 를 돌려 E1 칸과 «envcheck 출력» 절에 적는다
- 시험: `python3 -m pytest -q -p no:cacheprovider <SK>/precheck`
