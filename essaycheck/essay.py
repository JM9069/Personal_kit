#!/usr/bin/env python3
"""서술형 예상 문제 — 제출 직전에 HOW_TO_RUN.md · AI_COLLABORATION.md · hand_off.md · 코드 목록을 읽어
«이 제출물로 나올 만한 질문» 을 만들고 5분 연습을 한다(기본 포트 3156 · 표준 라이브러리만).

  python3 kit/essaycheck/essay.py [--root 과제폴더] [--port 3156]
  bash kit/essaycheck/run.sh [start|stop|status]     백그라운드로 켜기 · 끄기

- 읽기만 한다(파일을 쓰지 않음 · 명령을 실행하지 않음 · git 은 읽기 명령만). 연습 답은 브라우저(localStorage)에만 남는다.
- 질문은 AI 가 아니라 규칙으로 만든다: 단톡방 후기에서 모은 유형(구조 · 책임 · 데이터 흐름 · 검증 · 장애 · 확장 · 배포 ·
  선택 이유 · 코드 리뷰 · AI 협업 · 전제 오류)에 제출 문서에 실제로 적힌 글을 끼워 넣는다.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
CODE_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".sql", ".sh")
SKIP_DIRS = {".git", "kit", "jmkit", "node_modules", ".venv", "venv", "__pycache__", "task_copy", "uploads", "docs", ".pytest_cache"}
EMPTY = re.compile(r"^\s*(\((답변|answer)\)|-?\s*)\s*$", re.I)

# 단톡방 후기(2026-10-31 · 11-04)에서 모은 서술형 유형 — 제출물과 상관없이 늘 대비할 것
BANK = [
    ("구조 · 책임", "제출한 프로그램을 부품(화면 · 서버 · 저장 · 계산)으로 나누면 무엇이고, 각 부품의 책임은 무엇인가요? 한 부품이 두 가지 일을 하지는 않나요?"),
    ("데이터 흐름", "제공 자료(CSV 등)가 프로그램에 들어와 화면 결과로 나갈 때까지 어떤 순서로 무엇을 거치나요?"),
    ("선택 이유", "핵심 계산(배정 · 노선 · 최적화 등) 방식을 왜 그렇게 골랐나요? 검토했지만 버린 방식과 그 이유는?"),
    ("검증", "결과가 맞는지 무엇으로 확인했나요(테스트 · 실행 결과)? 확인하지 못한 것은 무엇인가요?"),
    ("장애 지점", "운영 중 서비스가 실패한다면 어디에서 먼저 깨질까요? 그때 사용자는 무엇을 보게 되나요?"),
    ("적용 실패", "자료를 적용하다 중간에 문제가 생기면 어떤 상태가 되나요? «적용 전 상태 그대로» 를 어떻게 보장했나요?"),
    ("같은 요청 두 번", "같은 요청이 두 번 들어오거나 동시에 들어오면 어떻게 처리되나요?"),
    ("확장성", "사용자 · 자료가 10배로 늘면 어디가 먼저 느려지고, 무엇을 바꾸겠나요?"),
    ("배포", "실제 운영(PROD)에 내보낸다면 컨테이너 · 설정 · 저장 · 로그에서 무엇을 더 준비해야 하나요?"),
    ("코드 리뷰", "다시 본다면 가장 먼저 고치고 싶은 코드 한 곳은 어디이고, 왜인가요?"),
    ("담당자 합의", "담당자와 확인한 기준 중 구현을 가장 크게 바꾼 것은 무엇이었나요?"),
    ("AI 협업", "AI 가 만든 결과 중 그대로 쓰지 않고 고친 것은 무엇이고, 어떻게 알아챘나요?"),
    ("전제 오류", "(질문의 전제가 내 구현과 다를 때) «제 제출물은 그렇게 동작하지 않습니다. 실제로는 … 입니다» 로 시작해 실제 동작을 설명하는 연습"),
]

# HOW_TO_RUN 칸 제목 → 그 칸 내용으로 만들 질문
HOW_RULES = [
    (r"실행", "실행 방법에 «{v}» 라고 적었습니다. 이 순서로 띄울 때 각 단계가 무엇을 준비하나요? 처음 실행이 실패하면 어디부터 확인하나요?"),
    (r"화면|주소|들어가", "화면에 들어가는 방법(«{v}»)에서 사용자 구분은 어떻게 하나요? 다른 사람의 정보를 보지 못하게 막는 곳은 어디인가요?"),
    (r"자료|넣기|CSV", "자료 넣기에 «{v}» 라고 적었습니다. 자료에 잘못된 줄이 있으면 어디서 걸러지고, 적용은 어떻게 되나요?"),
    (r"테스트", "테스트(«{v}»)는 무엇을 확인하나요? 이 테스트가 통과해도 놓칠 수 있는 경우는 무엇인가요?"),
    (r"설정", "운영자가 바꾸는 값(«{v}»)을 바꾸면 어떤 계산 · 결과가 달라지나요? 값이 잘못 들어오면(0 · 음수 · 빈칸) 어떻게 되나요?"),
    (r"저장", "데이터를 «{v}» 에 저장합니다. 이 저장 방식을 고른 이유와, 처음 상태로 되돌리는 방법은?"),
    (r"환경|제약", "알려진 제약(«{v}») 때문에 실제 운영에서 생길 수 있는 문제와 대비책은?"),
    (r"구현하지|다르게", "«{v}» — 구현하지 못했거나 담당자와 다르게 정한 이유를 설명하고, 이어서 만든다면 무엇부터 하겠나요?"),
    (r"이어받|먼저 볼", "후임자에게 «{v}» 부터 보라고 한 이유는? 그 파일 · 문서에는 무엇이 있나요?"),
]

AI_RULES = [
    (r"중점", "AI 작업에서 중점으로 봐야 한다고 한 «{v}» 를 이번 작업에서 실제로 어떻게 확인했나요? 구체적인 예를 하나 들어 주세요."),
    (r"극복|버렸", "AI 와 극복한 사례(«{v}»)에서 버린 방법을 다시 골랐다면 무엇이 달라졌을까요? 그 판단을 뒷받침한 증거는?"),
    (r"어려웠", "가장 어려웠던 부분(«{v}»)을 해결한 뒤 같은 문제가 다시 생기지 않게 무엇을 남겼나요(테스트 · 문서)?"),
]


def find_root(arg):
    if arg:
        return os.path.abspath(arg)
    try:
        top = subprocess.run(["git", "-C", KIT, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5).stdout.strip()
        if top:
            return top
    except (OSError, subprocess.TimeoutExpired):
        pass
    return os.path.dirname(KIT)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def sections(text):
    """'## 제목' 마다 본문을 나눈다 → [(제목, 본문)]"""
    out, title, buf = [], None, []
    for line in (text or "").splitlines():
        m = re.match(r"^#{2,3}\s+(.*)", line)
        if m:
            if title is not None:
                out.append((title, "\n".join(buf).strip()))
            title, buf = m.group(1).strip(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        out.append((title, "\n".join(buf).strip()))
    return out


def gist(body, n=90):
    """칸 본문에서 실제로 적힌 글만(양식 줄 '- 라벨:' 뒤 값 · 빈칸 · (답변) · 주석 제외)."""
    vals = []
    for line in body.splitlines():
        line = re.sub(r"<!--.*?-->", "", line).strip()
        if not line or EMPTY.match(line) or line.startswith(">"):
            continue
        m = re.match(r"^-\s*([^:：]+)[:：]\s*(.*)$", line)
        if m:
            if m.group(2).strip():
                vals.append(m.group(2).strip())
            continue
        vals.append(line.lstrip("-*• ").strip())
    s = " · ".join(v for v in vals if v)
    return (s[:n] + "…") if len(s) > n else s


def from_doc(name, text, rules):
    qs, blanks = [], []
    for title, body in sections(text):
        v = gist(body)
        if not v:
            blanks.append(title)
            continue
        for pat, tpl in rules:
            if re.search(pat, title):
                qs.append({"cat": name, "q": tpl.format(v=v), "src": "%s · %s" % (name, title)})
                break
        else:
            qs.append({"cat": name, "q": "«%s» 에 적은 «%s» 를 처음 보는 사람에게 설명해 주세요." % (title, v), "src": "%s · %s" % (name, title)})
    return qs, blanks


def from_hand_off(text):
    qs = []
    for line in (text or "").splitlines():
        m = re.search(r"🟢\s*결정\s*[—-]\s*(.+)", line)
        if m:
            d = re.sub(r"[`*]|\(🚹.*?\)", "", m.group(1)).strip()[:90]
            qs.append({"cat": "결정 이유", "q": "결정 «%s» 의 이유는 무엇이고, 다른 선택을 했다면 무엇을 잃었나요?" % d, "src": "kit/docs/hand_off.md"})
    return qs[:8]


def code_files(root):
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            if fn.endswith(CODE_EXT) and not fn.startswith("test_"):
                p = os.path.join(dp, fn)
                try:
                    files.append((os.path.getsize(p), os.path.relpath(p, root).replace(os.sep, "/")))
                except OSError:
                    pass
    files.sort(reverse=True)
    return [f for _, f in files[:6]]


def git_log(root):
    try:
        out = subprocess.run(["git", "-C", root, "log", "--oneline", "-15"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=5,
                             env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).stdout
        return [l for l in out.splitlines() if l]
    except (OSError, subprocess.TimeoutExpired):
        return []


def build(root):
    docs = {}
    qs, warns = [], []
    for name, rules in (("HOW_TO_RUN.md", HOW_RULES), ("AI_COLLABORATION.md", AI_RULES)):
        text = read(os.path.join(root, name))
        docs[name] = text is not None
        if text is None:
            warns.append("%s 가 과제 폴더에 없음" % name)
            continue
        q, blanks = from_doc(name, text, rules)
        qs += q
        if blanks:
            warns.append("%s 의 빈 칸: %s — 제출 전에 채우세요" % (name, " · ".join(blanks)))
    qs += from_hand_off(read(os.path.join(KIT, "docs", "hand_off.md")))
    files = code_files(root)
    for f in files[:4]:
        qs.append({"cat": "구조 · 책임", "q": "«%s» 파일은 무슨 책임을 맡고, 어떤 파일이 이 파일을 부르나요?" % f, "src": "코드 파일(큰 순)"})
    qs += [{"cat": c, "q": q, "src": "단톡방 후기 유형"} for c, q in BANK]
    for i, x in enumerate(qs, 1):
        x["id"] = "Q%d" % i
    return {"root": root, "docs": docs, "warns": warns, "files": files, "commits": git_log(root), "questions": qs}


def make_handler(root):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path.endswith("/api/questions"):
                return self.send(200, json.dumps(build(root), ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            if path.endswith("/api/health"):
                return self.send(200, b'{"status": "ok"}', "application/json")
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                return self.send(200, f.read(), "text/html; charset=utf-8")
    return H


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure") and (s.encoding or "").lower() not in ("utf-8", "utf8"):
            s.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="서술형 예상 문제")
    ap.add_argument("--root", default=None, help="과제 폴더(기본: 키트가 든 git 루트)")
    ap.add_argument("--host", default="0.0.0.0", help="0.0.0.0 이어야 IDE 미리보기가 열린다")
    ap.add_argument("--port", type=int, default=3156)
    a = ap.parse_args()
    root = find_root(a.root)
    srv = ThreadingHTTPServer((a.host, a.port), make_handler(root))
    print("서술형 예상 문제 — 과제 폴더 %s · IDE 미리보기 PORT %d" % (root, a.port), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
