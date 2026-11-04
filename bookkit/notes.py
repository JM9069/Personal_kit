# -*- coding: utf-8 -*-
r"""책 스티커 — 유저가 책(devview 페이지 서버로 연 html)에 붙인 질문을 읽고 답을 단다. 답은 책에서 그 스티커 아래 초록 칸으로 보인다

    python3 bookkit/notes.py list                         답이 없는 스티커(모든 책) — [id] 시각 · 책 · 블록 ID · 자리 · 질문
    python3 bookkit/notes.py list --all                   답한 것까지
    python3 bookkit/notes.py list --book <책 이름|폴더>    그 책만
    python3 bookkit/notes.py answer <id> "답"              답 달기(다시 하면 바꿈) — 꾸밈 없는 글 · 줄 바꿈은 \n
    python3 bookkit/notes.py answer <id> --file <답.md>     긴 답은 파일에서
    python3 bookkit/notes.py list --flowtree <tree.json>  (선택 · 기본 끔) 답 없는 스티커를 flowtree 질문 노드로도 보낸다(한 번만)

- 저장: 책 폴더의 notes.json(bookkit/books/<책>/notes.json) — devview 페이지 서버(포트 = devview + 100)가 책 html 옆 «api/notes» 로 쓴다
- 스티커 자리: ctx 의 «b=<블록 ID>» — 블록 ID 가 «장-칸 이름 · 장-항목 id» 로 고정이라 1차판 → 2차판에도 같은 자리에 붙는다
- 답은 2ND 의 서브가 단다(유저 질문 → 그 칸 · 계약을 읽고 답). 책 내용 자체를 고쳐야 하면 답에 적고 그 칸 담당에게 넘긴다
- 스티커 🪄(마법봉) → 페이지 서버가 2ND 에 보냄(notes.json 의 magic_rid) → 2ND 가 codex-hub/magic.py answer-note 로 이 answer 를 부른다
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# bookkit 폴더 · 책 폴더들
KIT = Path(__file__).resolve().parent
BOOKS = KIT / "books"


def note_files(book=None):
    """notes.json 목록 — book = 책 이름(books/<이름>) 또는 폴더 경로 · 없으면 모든 책"""
    if book:
        p = Path(book)
        if not p.is_dir():
            p = BOOKS / book
        return [p / "notes.json"]
    return sorted(BOOKS.glob("*/notes.json"))


def load(p):
    """notes.json → 목록"""
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []


def save(p, notes):
    """notes.json 쓰기(임시 파일 → 바꿔 넣기 — devview 가 같은 파일을 쓴다)"""
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def block_of(n):
    """스티커가 붙은 블록 ID(ctx 의 «b=…»)"""
    m = re.search(r"b=([^\s|]+)", n.get("ctx", ""))
    return m.group(1) if m else "?"


def push_flowtree(tree, p, notes):
    """답 없는 스티커를 flowtree 질문 노드로(유저 질문 — 한 번만 · note["ft"] 에 노드 id) → 보낸 수"""
    sys.path.insert(0, str(KIT.parent / "devview" / "flowtree"))
    import flowtree_store as store
    n_sent = 0
    for n in notes:
        if n.get("answer") or n.get("ft"):
            continue
        r = store.apply(Path(tree), "user", "ask", text=f"[책 스티커 {n['id']} · {n.get('doc', '')} · {block_of(n)}] {n['text']}"[:400])
        n["ft"] = r.get("id") if isinstance(r, dict) else str(r)
        n_sent += 1
    if n_sent:
        save(p, notes)
    return n_sent


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="책 스티커 — 목록 · 답 달기")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_list = sub.add_parser("list", help="스티커 목록(기본 = 답 없는 것)")
    a_list.add_argument("--all", action="store_true", help="답한 것까지")
    a_list.add_argument("--book", help="책 이름(books/<이름>) 또는 폴더")
    a_list.add_argument("--flowtree", help="tree.json — 답 없는 스티커를 flowtree 질문 노드로도(선택)")
    a_ans = sub.add_parser("answer", help="답 달기")
    a_ans.add_argument("id")
    a_ans.add_argument("text", nargs="?", help="답 글")
    a_ans.add_argument("--file", help="답 글 파일(utf-8)")
    a_ans.add_argument("--book", help="책 이름 또는 폴더(없으면 모든 책에서 id 를 찾는다)")
    a = ap.parse_args(argv)

    if a.cmd == "list":
        shown = 0
        for p in note_files(a.book):
            notes = load(p)
            for n in sorted(notes, key=lambda x: x.get("ts", "")):
                if n.get("answer") and not a.all:
                    continue
                shown += 1
                head = f"[{n['id']}] {n.get('ts', '')} · {n.get('doc', '')} · {block_of(n)}" + (" · 답함" if n.get("answer") else "")
                print(f"{head}\n    자리: {n.get('ctx', '')}\n    질문: {n['text']}")
                if n.get("answer"):
                    print(f"    답: {n['answer']}")
                print()
            if a.flowtree and notes:
                print(f"flowtree 질문 노드로 보냄 {push_flowtree(a.flowtree, p, notes)}개 — {p}")
        if not shown:
            print("답할 스티커 없음" if not a.all else "스티커 없음")
        return 0

    text = Path(a.file).read_text(encoding="utf-8") if a.file else (a.text or "").replace("\\n", "\n")
    if not text.strip():
        print("답 글이 비었다 — answer <id> \"답\" 또는 --file")
        return 2
    for p in note_files(a.book):
        notes = load(p)
        hit = next((n for n in notes if n.get("id") == a.id), None)
        if hit is None:
            continue
        hit["answer"] = text.strip()
        hit["answer_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save(p, notes)
        print(f"답 달음 [{a.id}] {block_of(hit)} — {p}")
        return 0
    print(f"스티커 «{a.id}» 를 못 찾았다(책: {a.book or '전부'})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
