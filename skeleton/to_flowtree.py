#!/usr/bin/env python3
# 뼈대로 이미 만든 묶음 → flowtree «완료 노드»(맞는 섹션 밑 · add → start → done) — flowtree.py 명령만 씀
"""
사용: python3 skeleton/to_flowtree.py [--plan skeleton/out/plan.json] [--tree docs/flowtree/tree.json]
        [--bundles K0 K3 …] [--section <섹션 노드 id>] [--map K1=<섹션 id> …] [--graph hand_off|task] [--dry]
- 언제: 구현 방향이 다 잡혀 flowtree 를 처음 그릴 때(섹션 = hand_off 의 구현 순서 · 섹션 노드는 먼저 만들어 둔다)
- 붙이는 곳: --map 묶음=섹션 id > --section > 기본 섹션 «뼈대(skeleton)»(없으면 맨 위에 만듦 · --graph 로 그래프 지정)
- 올릴 묶음: --bundles 로 고른 것(기본 계획표 전부) · 노드 요약 = «이름: 파일 · 함수 …»(60자 안) · 이름 칸(names) = 파일 · 함수 전부 · 설명 = 항목 전부 + 설정 칸
- 같은 제목 노드가 이미 있으면 건너뜀(tree.json 은 읽기만 — 쓰기는 flowtree.py 가)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# 이 파일이 있는 폴더(skeleton) · 키트 폴더
HERE = Path(__file__).resolve().parent
KIT = HERE.parent
# 기본 섹션 노드 제목(--section · --map 이 없을 때)
ROOT_TITLE = "뼈대(skeleton)"
# 요약 최대 글자(flowtree 규칙)
SUMMARY_MAX = 60


# 묶음 노드 제목
# b: 계획표 묶음
def 노드_제목(b):
    return f"뼈대 {b['id']} {b['name']}"


# 요약 — «이름: 파일 · 함수 …» 60자 안
# b: 계획표 묶음
def 요약_만들기(b):
    # 파일 하나 · 함수들
    files = sorted({i["file"] for i in b["items"]})
    funcs = [i["func"] for i in b["items"] if i["func"] != "-"]
    # 요약 글자
    text = f"이름: {' · '.join(files)} · {' · '.join(funcs)}"
    return text if len(text) <= SUMMARY_MAX else text[:SUMMARY_MAX - 1] + "…"


# 이름 칸 처음 값 — 파일(겹침 없이) · 함수 «-» 제외 → « · » 로 이은 글자
# b: 계획표 묶음
def 이름_칸(b):
    # 파일 · 함수 목록
    files = sorted({i["file"] for i in b["items"]})
    funcs = [i["func"] for i in b["items"] if i["func"] != "-"]
    return " · ".join(dict.fromkeys(files + funcs))


# 설명 — 항목 전부 · 설정 칸 · 진입점
# b: 계획표 묶음
def 설명_만들기(b):
    # 줄 목록
    lines = [f"이름: {i['file']} :: {i['func']} — {i['why']}" + (f" ({i['todo']})" if i.get("todo") else "") for i in b["items"]]
    lines.append("비워 둘 설정 칸: " + " · ".join(str(s) for s in b["settings"]))
    if b.get("entry"):
        lines.append(f"진입점(check.py): {b['entry']}")
    lines.append(f"카드: skeleton/cards/{b['id']}.md · 뼈대로 만든 결과(완료)")
    return "\n".join(lines)


# 이미 있는 노드 제목 → id (tree.json 읽기만)
# tree: tree.json 경로
def 있는_제목(tree):
    if not tree.is_file():
        return {}
    try:
        # 그래프 내용
        data = json.loads(tree.read_text(encoding="utf-8"))
    # 쓰는 중 · 형식 오류 — 빈 것으로(flowtree.py 가 다시 판정)
    except (OSError, json.JSONDecodeError):
        return {}
    return {n.get("title"): n.get("id") for n in data.get("nodes", []) if isinstance(n, dict)}


# flowtree.py 한 번 부르기 → (성공?, 출력 한 줄)
# flowtree: flowtree.py 경로 / tree: tree.json / args: 명령 인자
def 명령(flowtree, tree, args):
    # 실행 결과
    r = subprocess.run([sys.executable, str(flowtree), "--role", "main", "--tree", str(tree), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


# 실행
# argv: 인자(없으면 sys.argv)
def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    # 해석기
    ap = argparse.ArgumentParser(description="계획표 → flowtree")
    ap.add_argument("--plan", default=str(HERE / "out" / "plan.json"))
    ap.add_argument("--tree", default=str(KIT / "docs" / "flowtree" / "tree.json"))
    ap.add_argument("--flowtree", default=str(KIT / "devview" / "flowtree" / "flowtree.py"))
    ap.add_argument("--graph", default="hand_off", choices=("hand_off", "task"), help="기본 섹션 노드를 새로 만들 때의 그래프")
    ap.add_argument("--bundles", nargs="*", default=None, help="올릴 묶음 id(기본 계획표 전부) — 예: K0 K3 K5")
    ap.add_argument("--section", default=None, help="붙일 섹션 노드 id(기본 «뼈대(skeleton)» 섹션)")
    ap.add_argument("--map", nargs="*", default=[], help="묶음별 섹션 «K1=t3» (--section 보다 우선)")
    ap.add_argument("--dry", action="store_true", help="올리지 않고 무엇을 올릴지만")
    # 해석 결과
    a = ap.parse_args(argv)
    # 계획표 · 그래프 · 명령 파일
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    tree, flowtree = Path(a.tree), Path(a.flowtree)
    # 묶음 → 섹션 id
    sec_of = {}
    for m in a.map:
        k, _, v = m.partition("=")
        if not v:
            print(f"실패: --map 은 «K1=섹션id» 모양 — {m}", file=sys.stderr)
            return 1
        sec_of[k] = v
    # 올릴 묶음
    todo = [b for b in plan["bundles"] if a.bundles is None or b["id"] in a.bundles]
    if a.dry:
        for b in todo:
            print(f"{노드_제목(b)} | 섹션 {sec_of.get(b['id']) or a.section or ROOT_TITLE} | {요약_만들기(b)} | 이름 칸: {이름_칸(b)}")
        return 0
    if not flowtree.is_file():
        print(f"실패: flowtree.py 없음 — {flowtree}", file=sys.stderr)
        return 1
    # 있는 제목
    have = 있는_제목(tree)
    # 기본 섹션 id — 필요할 때만 만듦
    root = None

    # 기본 섹션 id(없으면 맨 위에 만듦) → 실패면 None
    def 기본_섹션():
        nonlocal root
        if root:
            return root
        root = have.get(ROOT_TITLE)
        if not root:
            ok, out = 명령(flowtree, tree, ["add", "-", ROOT_TITLE, "--summary", f"{plan['task']} 뼈대로 만든 결과", "--graph", a.graph,
                                        "--doc", "skeleton/README.md"])
            if not ok:
                print(f"실패: {out}", file=sys.stderr)
                return None
            root = out.split()[0]
            print(out)
        return root

    # 붙인 노드
    made = []
    # 묶음
    for b in todo:
        # 제목
        title = 노드_제목(b)
        if title in have:
            print(f"{have[title]} 있음 — {title}")
            continue
        # 부모 섹션
        parent = sec_of.get(b["id"]) or a.section or 기본_섹션()
        if not parent:
            return 1
        ok, out = 명령(flowtree, tree, ["add", parent, title, "--summary", 요약_만들기(b), "--text", 설명_만들기(b),
                                    "--doc", f"skeleton/cards/{b['id']}.md", "--names", 이름_칸(b)])
        if not ok:
            print(f"실패: {out}", file=sys.stderr)
            return 1
        # 새 노드 id → 착수 · 완료(뼈대로 이미 만든 것)
        nid = out.split()[0]
        for step in ("start", "done"):
            ok, out2 = 명령(flowtree, tree, [step, nid])
            if not ok:
                print(f"실패: {out2}", file=sys.stderr)
                return 1
        made.append(nid)
        print(f"{nid} 완료 노드 — {title} → {parent}")
    if made:
        print(f"완료 노드 {len(made)}개 붙임")
    return 0


if __name__ == "__main__":
    sys.exit(main())
