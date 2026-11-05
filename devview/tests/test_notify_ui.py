"""알림 종 화면 시험 — 임시 작업 폴더 + 빈 포트 시험 서버(그 PID 만 끔) + 헤드리스 크롬

    py -3 tests/test_notify_ui.py [캡처 폴더]        결과 PASS/FAIL · 캡처 tests/shots/notify_*.png
    py -3 -m pytest -q tests/test_notify_ui.py        같은 시험(pytest)

스크립트 한 줄 → 배지 · 목록 → 누름 = 보기 전환 + 그래프 iframe 이 받은 {ft:'focus'} · 읽음 → 배지 감소
· tree.json 에 done(store.apply) → 자동 알림 · 시작 때 기존 기록은 알림 없음 · notes.json answer · 꼬리 답 → 책 #note=
· 새 설문 → 설문 탭 그 설문 · 모두 읽음 · 새로고침 뒤 읽음 유지 · 종 끌기 → 위치 저장 · 창 줄이면 안으로 · 모든 보기에서 종 보임 · 긴 글 줄바꿈
실제 ~/.codex · ~/.devview · 8701 · 8702 무관(서버의 HOME · USERPROFILE · CODEX_HOME 을 임시 폴더로)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_notify as tn  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("-")] if __name__ == "__main__" else []
SHOTS = Path(ARGS[0]) if ARGS else HERE / "shots"
RESULTS = []
# 설문 도구 — 키트 = <키트>/.agents/skills/survey · 로컬 = ~/.claude/skills/adr-survey(시험 서버는 HOME 을 바꾸므로 작업 폴더에 복사)
SURVEY_SRC = next((p for p in (tn.DV.parent / ".agents" / "skills" / "survey" / "survey.py",
                               Path.home() / ".claude" / "skills" / "adr-survey" / "survey.py") if p.is_file()), None)
# 종 상자 위치(.dv-main 기준) · 화면 안 여부
BELL_JS = ("(() => { const b = document.querySelector('#bell').getBoundingClientRect(); const m = document.querySelector('.dv-main').getBoundingClientRect();"
           " return {x: Math.round(b.left - m.left), bottom: Math.round(m.bottom - b.bottom), w: b.width, h: b.height,"
           " inside: b.left >= m.left - .5 && b.top >= m.top - .5 && b.right <= m.right + .5 && b.bottom <= m.bottom + .5}; })()")


def check(name, ok, info=None):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {name}" + ("" if ok or info is None else f" — {info}"), flush=True)
    return ok


def make_world(base):
    root = base / "proj"
    root.mkdir()
    tp, t1 = tn.new_tree(root)
    tn.store.apply(tp, "main", "done", task=t1)                # 시작 전 기록 — 알림 안 돼야 함
    dist = root / "bookkit" / "books" / "demo" / "dist"
    dist.mkdir(parents=True)
    (dist / "demo.html").write_text("<!doctype html><meta charset=utf-8><title>demo</title><body>책</body>", encoding="utf-8")
    note = {"id": "n1", "ts": "2026-11-04 10:00:00", "doc": "demo", "ctx": "x | b=s1-1", "text": "질문 하나"}
    (dist.parent / "notes.json").write_text(json.dumps([note], ensure_ascii=False), encoding="utf-8")
    if SURVEY_SRC:
        d = root / ".agents" / "skills" / "survey"
        d.mkdir(parents=True)
        shutil.copy(SURVEY_SRC, d / "survey.py")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("print('a')\n" * 30, encoding="utf-8")
    return root, tp, t1


def start(root):
    port, pport = tn.free_port(), tn.free_port()
    home = root.parent / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ, DEVVIEW_NO_VAULT="1", HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(home / ".codex"), PYTHONUTF8="1")
    proc = subprocess.Popen([sys.executable, str(tn.DEVVIEW), str(root), "--host", "127.0.0.1", "--port", str(port), "--page-port", str(pport)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    url = f"http://127.0.0.1:{port}"
    for _ in range(150):
        if proc.poll() is not None:
            raise RuntimeError("서버 기동 실패")
        try:
            tn.urllib.request.urlopen(url + "/api/info", timeout=1).read()
            return proc, url
        except OSError:
            time.sleep(0.1)
    proc.kill()
    raise RuntimeError("서버 응답 없음")


def badge(page):
    return page.evaluate("(() => { const b = document.querySelector('#bell .dv-bell-badge'); return b.hidden ? 0 : b.textContent; })()")


def wait_badge(page, want, sec=10):
    return tn.wait(lambda: str(badge(page)) == str(want), sec)


def open_panel(page):
    if not page.is_visible("#notifyPanel"):
        page.click("#bell .dv-bell-btn")
    page.wait_for_selector("#notifyPanel", state="visible", timeout=3000)


def click_item(page, text):
    open_panel(page)
    page.locator("#notifyPanel .dv-notify-item", has_text=text).first.click()
    time.sleep(0.5)


def view(page):
    return page.evaluate("devview.view()")


# 그래프 iframe 에 메시지 기록기 심기 — flowtree 쪽 수신부(Edu_sub)와 무관하게 «메시지가 갔다» 만 봄
def tap_graph(page):
    tn.wait(lambda: page.evaluate("(() => { const f = document.querySelector('#ftView iframe'); return !!f && f.contentDocument?.readyState === 'complete'; })()"), 15)
    page.evaluate("(() => { const w = document.querySelector('#ftView iframe').contentWindow; if (w.__tap) return; w.__tap = [];"
                  " w.addEventListener('message', (e) => { if (e.data && e.data.ft === 'focus') w.__tap.push(e.data); }); })()")


def taps(page):
    return page.evaluate("document.querySelector('#ftView iframe').contentWindow.__tap || []")


def run(br, root, tp, t1, url):
    page = br.new_page(viewport={"width": 1500, "height": 900})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(url + "/")
    page.wait_for_selector("html[data-ready='1']", timeout=30000)
    check("종 보임 · 기본 자리 왼쪽 12 · 아래 32", page.is_visible("#bell") and (lambda b: abs(b["x"] - 12) <= 1 and abs(b["bottom"] - 32) <= 1)(page.evaluate(BELL_JS)),
          page.evaluate(BELL_JS))
    time.sleep(2.5)
    check("시작 때 기존 tree 기록(done) → 알림 없음 · 배지 숨김", badge(page) == 0 and tn.get(url, "notify")["total"] == 0, tn.get(url, "notify"))
    if view(page) != "graph":
        page.evaluate("devview.showView('graph')")
    tap_graph(page)
    page.screenshot(path=str(SHOTS / "notify_1_graph_empty.png"))

    # ① 스크립트 한 줄 → 배지 1 → 코드 보기에서 눌러 그래프로
    tn.cli(root, "add", "--kind", "done", "--title", "t3 완료", "--to", f"graph:{t1}")
    check("① 스크립트 한 줄 → 배지 1", wait_badge(page, 1), badge(page))
    page.evaluate("devview.showView('code')")
    open_panel(page)
    check("① 목록 창에 그 글", page.locator("#notifyPanel .dv-notify-item", has_text="t3 완료").count() == 1)
    page.screenshot(path=str(SHOTS / "notify_2_panel.png"))
    click_item(page, "t3 완료")
    check("① 누름 → 그래프 보기 · iframe 이 {ft:'focus', node} 받음", view(page) == "graph"
          and tn.wait(lambda: any(m.get("node") == t1 for m in taps(page)), 3), taps(page))
    check("① 읽음 → 배지 0 · 목록 창 닫힘", wait_badge(page, 0, 4) and not page.is_visible("#notifyPanel"))

    # ② tree.json 에 done 덧붙임 → 자동 알림
    tn.store.apply(tp, "main", "done", task=t1)
    check("② store.apply done → 자동 알림 배지 1", wait_badge(page, 1))
    items = tn.get(url, "notify")["items"]
    check("② 자동 알림 = 그래프 출처 · 완료 · 그 노드", items[0]["src"] == "tree" and items[0]["kind"] == "done" and items[0]["to"]["node"] == t1, items[0])
    page.evaluate("devview.showView('book')")
    time.sleep(0.3)
    check("② Book 보기에서도 종 보임", page.is_visible("#bell") and page.evaluate(BELL_JS)["inside"])
    n_before = len(taps(page))
    click_item(page, "첫 작업")
    check("② Book 보기에서 눌러 → 그래프 · focus 메시지 하나 더", view(page) == "graph" and tn.wait(lambda: len(taps(page)) == n_before + 1, 3), taps(page))

    # ③ 책 답 · 꼬리 답 → 책 #note=
    nf = root / "bookkit" / "books" / "demo" / "notes.json"
    note = json.loads(nf.read_text(encoding="utf-8"))[0]
    note.update(answer="이게 답", answer_ts="2026-11-04 10:05:00", title="스티커 제목")
    nf.write_text(json.dumps([note], ensure_ascii=False), encoding="utf-8")
    check("③ notes.json answer → 알림", wait_badge(page, 1))
    click_item(page, "스티커 제목")
    src = page.evaluate("document.querySelector('#bookView .dv-book-frame').getAttribute('src') || ''")
    check("③ 누름 → Book 보기 · 책 주소#note=n1", view(page) == "book" and src.endswith("demo/dist/demo.html#note=n1"), (view(page), src))
    page.screenshot(path=str(SHOTS / "notify_3_book.png"))
    note["thread"] = [{"id": "q2", "q": "꼬리 질문", "ts": "x", "a": "꼬리 답", "a_ts": "2026-11-04 10:06:00"}]
    nf.write_text(json.dumps([note], ensure_ascii=False), encoding="utf-8")
    check("③ 꼬리 답 → 알림", wait_badge(page, 1))
    page.evaluate("devview.showView('code')")
    click_item(page, "꼬리 질문")
    src = page.evaluate("document.querySelector('#bookView .dv-book-frame').getAttribute('src') || ''")
    check("③ 꼬리 → #note=n1&t=q2", view(page) == "book" and src.endswith("#note=n1&t=q2"), src)

    # ④ 새 설문 → 설문 탭 그 설문
    if SURVEY_SRC:
        sd = root / "docs" / "surveys" / "proj"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "s-new.json").write_text(json.dumps({"title": "알림 시험 설문", "created": "2026-11-04 12:00:00",
                                                   "questions": [{"id": "1", "question": "고르기", "options": ["A", "B"]}]}, ensure_ascii=False), encoding="utf-8")
        check("④ 새 설문 → 알림", wait_badge(page, 1, 12), tn.get(url, "notify")["items"][:1])
        page.evaluate("devview.showView('graph')")
        click_item(page, "알림 시험 설문")
        ssrc = page.evaluate("document.querySelector('#svView iframe').getAttribute('src')")
        check("④ 누름 → 설문 보기 · 그 설문(id=s-new)", view(page) == "survey" and "id=s-new" in ssrc, (view(page), ssrc))
        tn.wait(lambda: page.evaluate("document.querySelector('#svView iframe').contentDocument?.readyState === 'complete'"), 5)
        page.screenshot(path=str(SHOTS / "notify_4_survey.png"))
    else:
        check("④ 설문 도구 있음(시험 재료)", False, "survey.py 못 찾음")

    # ⑤ 파일 · 대화 이동
    tn.cli(root, "add", "--kind", "report", "--title", "서브 보고 파일", "--to", "file:src/a.py:12")
    wait_badge(page, 1)
    click_item(page, "서브 보고 파일")
    check("⑤ file:경로:줄 → 코드 보기 · 그 파일", view(page) == "code" and page.evaluate("devview.activePath()") == "src/a.py")
    tn.cli(root, "add", "--kind", "hub", "--title", "MAIN 승인 대기", "--to", "hub:main")
    wait_badge(page, 1)
    click_item(page, "MAIN 승인 대기")
    check("⑤ hub:닉 → 대화 보기", view(page) == "chat", view(page))

    # ⑥ 모두 읽음 · 새로고침 뒤 유지 · 긴 글 줄바꿈 · 🔴
    long = "아주긴제목" * 40
    tn.cli(root, "add", "--kind", "queue-fail", "--title", long, "--body", "큐 전달 실패 — " + "원인 " * 60)
    tn.cli(root, "add", "--kind", "decide", "--title", "결정 필요 둘")
    check("⑥ 두 개 → 배지 2", wait_badge(page, 2))
    page.evaluate("devview.showView('git')")
    open_panel(page)
    wrap = page.evaluate("[...document.querySelectorAll('#notifyPanel .dv-notify-item')].slice(0, 2).every((b) =>"
                         " [...b.querySelectorAll('.dv-notify-t, .dv-notify-b')].every((t) => t.scrollWidth <= t.clientWidth + 1) && b.scrollWidth <= b.clientWidth + 1)")
    check("⑥ 긴 제목 · 본문 줄바꿈(가로 넘침 없음)", wrap)
    check("⑥ 큐 전달 실패 = 🔴 줄", page.locator("#notifyPanel .dv-notify-item.is-bad", has_text="큐 전달 실패").count() >= 1)
    pr = page.evaluate("(() => { const r = document.querySelector('#notifyPanel').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom, innerWidth, innerHeight]; })()")
    check("⑥ 목록 창이 화면 안", pr[0] >= 0 and pr[1] >= 0 and pr[2] <= pr[4] and pr[3] <= pr[5], pr)
    page.screenshot(path=str(SHOTS / "notify_5_long.png"))
    page.click("#notifyPanel [data-act='all']")
    check("⑥ 모두 읽음 → 배지 0", wait_badge(page, 0, 4))
    page.reload()
    page.wait_for_selector("html[data-ready='1']", timeout=30000)
    time.sleep(2.5)
    open_panel(page)
    check("⑥ 새로고침 뒤 읽음 유지(배지 0 · 전부 is-read)", badge(page) == 0
          and page.evaluate("[...document.querySelectorAll('#notifyPanel .dv-notify-item')].every((b) => b.classList.contains('is-read'))"))
    page.keyboard.press("Escape")
    check("⑥ Esc → 목록 창 닫힘", tn.wait(lambda: not page.is_visible("#notifyPanel"), 2))

    # ⑦ 모든 보기에서 종 보임
    vis = {}
    for v in ("code", "graph", "git", "survey", "app", "chat", "book"):
        page.evaluate(f"devview.showView('{v}')")
        time.sleep(0.25)
        vis[v] = page.is_visible("#bell") and page.evaluate(BELL_JS)["inside"] and \
            page.evaluate("(() => { const b = document.querySelector('#bell').getBoundingClientRect(); const e = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return !!e && !!e.closest('#bell'); })()")
    check("⑦ 코드 · 그래프 · Git · 설문 · 앱 · 대화 · 책 보기 모두 종 보임(맨 위)", all(vis.values()), vis)

    # ⑧ 끌기 → 위치 저장 · 새로고침 유지 · 창 줄이면 안으로 · 더블클릭 = 기본 자리
    page.evaluate("devview.showView('code')")
    b0 = page.evaluate(BELL_JS)
    bb = page.locator("#bell").bounding_box()
    x, y = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 500, y - 300, steps=8)
    page.mouse.up()
    time.sleep(0.3)
    b1 = page.evaluate(BELL_JS)
    check("⑧ 끌기 → 오른쪽 500 · 위 300 · 목록 창 안 열림", abs(b1["x"] - b0["x"] - 500) <= 2 and abs(b1["bottom"] - b0["bottom"] - 300) <= 2
          and not page.is_visible("#notifyPanel"), (b0, b1))
    check("⑧ 위치 저장(bell.pos)", page.evaluate("Object.keys(localStorage).some((k) => k.endsWith(':bell.pos') && JSON.parse(localStorage[k])?.left > 100)"))
    page.screenshot(path=str(SHOTS / "notify_6_dragged.png"))
    page.click("#bell .dv-bell-btn")
    check("⑧ 옮긴 뒤 누르면 목록 창 열림 · 화면 안", page.is_visible("#notifyPanel"))
    page.keyboard.press("Escape")
    page.reload()
    page.wait_for_selector("html[data-ready='1']", timeout=30000)
    time.sleep(0.5)
    b2 = page.evaluate(BELL_JS)
    check("⑧ 새로고침 뒤 옮긴 자리 유지", abs(b2["x"] - b1["x"]) <= 1 and abs(b2["bottom"] - b1["bottom"]) <= 1, b2)
    page.set_viewport_size({"width": 400, "height": 300})
    time.sleep(0.4)
    check("⑧ 창 400 × 300 → 종이 화면 안", page.evaluate(BELL_JS)["inside"], page.evaluate(BELL_JS))
    page.set_viewport_size({"width": 1500, "height": 900})
    time.sleep(0.4)
    page.dblclick("#bell .dv-bell-btn")
    time.sleep(0.2)
    b3 = page.evaluate(BELL_JS)
    check("⑧ 더블클릭 → 기본 자리(왼쪽 12 · 아래 32)", abs(b3["x"] - 12) <= 1 and abs(b3["bottom"] - 32) <= 1, b3)
    page.keyboard.press("Escape")
    page.evaluate("devview.showView('graph')")
    time.sleep(0.6)
    page.screenshot(path=str(SHOTS / "notify_7_graph_default.png"))

    # ⑨ 펼친 · 접힌 · 최소화 허브 각각 종 기본 자리와 안 겹침(사각형 교차 0 · 허브 --dv-hub-left · --dv-hub-min-left = 60)
    if page.is_visible("#hub"):
        rect_js = ("(() => { const a = document.querySelector('#bell').getBoundingClientRect(); const b = document.querySelector('#hub').getBoundingClientRect();"
                   " return {bell: [a.left, a.top, a.right, a.bottom], hub: [b.left, b.top, b.right, b.bottom]}; })()")

        # 두 사각형 교차 넓이(px²)
        def overlap(rr):
            a, b = rr["bell"], rr["hub"]
            return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))

        cls = lambda c: page.evaluate(f"document.querySelector('#hub').classList.contains('{c}')")  # noqa: E731
        if cls("is-min"):
            page.click("#hub .dv-hub-min")
        if cls("is-folded"):
            page.click("#hub .dv-hub-fold")
        time.sleep(0.3)
        rr = page.evaluate(rect_js)
        check("⑨ 펼친 허브 ↔ 종 기본 자리 교차 0 · 허브가 종 오른쪽", overlap(rr) == 0 and rr["hub"][0] >= rr["bell"][2], rr)
        page.screenshot(path=str(SHOTS / "notify_8_hub_full.png"), clip={"x": 0, "y": 900 - 260, "width": 900, "height": 260})
        page.click("#hub .dv-hub-fold")
        time.sleep(0.3)
        rr = page.evaluate(rect_js)
        check("⑨ 접힌 허브 ↔ 종 기본 자리 교차 0", cls("is-folded") and overlap(rr) == 0, rr)
        page.screenshot(path=str(SHOTS / "notify_8_hub_fold.png"), clip={"x": 0, "y": 900 - 140, "width": 900, "height": 140})
        page.click("#hub .dv-hub-fold")
        page.click("#hub .dv-hub-min")
        time.sleep(0.3)
        rr = page.evaluate(rect_js)
        check("⑨ 최소화 허브 ↔ 종 기본 자리 교차 0 · 허브가 종 오른쪽", cls("is-min") and overlap(rr) == 0 and rr["hub"][0] >= rr["bell"][2], rr)
        page.screenshot(path=str(SHOTS / "notify_8_hub_min.png"))
        page.screenshot(path=str(SHOTS / "notify_8_hub_min_zoom.png"), clip={"x": 0, "y": 900 - 140, "width": 700, "height": 140})
        page.click("#hub .dv-hub-min")
    else:
        check("⑨ 허브 보임(시험 재료)", False, "허브 없음")
    check("페이지 예외 없음", not errs, errs[:3])
    page.close()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)
    RESULTS.clear()
    base = Path(tempfile.mkdtemp(prefix="dv_notify_ui_"))
    proc = None
    try:
        root, tp, t1 = make_world(base)
        proc, url = start(root)
        print("서버 PID:", proc.pid, url, flush=True)
        with sync_playwright() as pw:
            try:
                br = pw.chromium.launch(headless=True)
            except Exception:  # noqa: BLE001
                br = pw.chromium.launch(channel="chrome", headless=True)
            try:
                run(br, root, tp, t1, url)
            finally:
                br.close()
    finally:
        if proc:
            tn.stop(proc)
        shutil.rmtree(base, ignore_errors=True)
    bad = [n for n, ok in RESULTS if not ok]
    print(f"결과: {len(RESULTS) - len(bad)}/{len(RESULTS)} 통과" + (f" · 실패 {bad}" if bad else "") + f" · 캡처 {SHOTS}")
    return 1 if bad else 0


def test_notify_ui():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
