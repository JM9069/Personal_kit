// Book 보기 — 북키트 책을 devview 안에서 연다(Alt+B)
//   왼쪽 = 책 목록(GET api/books — 만든 책의 판 하나가 한 줄 · 최신이 위 · 그룹 없음) — 설문 탭 왼쪽 목록과 같은 모양
//     줄 = «<책 제목> · v<N> · <판 이름>» + 회색 부가 줄(시각 · 블록 · 새로) · 책마다 마지막 판은 파랑 · 앞 판은 회색 · 고른 줄은 테두리
//   오른쪽 = 페이지 서버(포트 +100)의 그 html 을 iframe 으로 — 스티커 · 🪄 스티커 마법봉이 페이지 서버 같은 출처라 그대로 동작
//   목록은 탭을 열 때 · «새로고침» 단추로만 다시 읽는다(폴링 없음)
import { api } from './api.js';
import { $, esc, on, store } from './util.js';
import { pageUrl } from './editor.js';

// 화면 부품 · 마지막 목록 · 고른 책(작업 폴더 기준 경로) · 페이지 서버 포트
let el = {};
let list = { books: [] };
let cur = null;
let pagePort = 0;

// Book 보기 준비
// info: 서버 info
export function initBook(info) {
  const view = $('#bookView');
  if (!view) return;
  pagePort = info.page_port || 0;
  cur = store.get('book.cur', null);
  view.innerHTML = `
    <div class="dv-book">
      <aside class="dv-book-side">
        <div class="dv-book-head"><span>책 <span class="dv-book-count"></span></span>
          <button class="dv-ib" type="button" data-act="reload" title="목록 새로고침"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg></button>
        </div>
        <div class="dv-book-list"></div>
      </aside>
      <section class="dv-book-main">
        <div class="dv-book-bar"><span class="dv-book-path"></span>
          <button class="dv-book-open" type="button" data-act="newtab" title="새 탭으로 열기">새 탭으로 열기</button>
        </div>
        <div class="dv-book-empty" hidden></div>
        <iframe class="dv-book-frame" title="책"></iframe>
      </section>
    </div>`;
  el = { list: $('.dv-book-list', view), path: $('.dv-book-path', view), frame: $('.dv-book-frame', view),
    empty: $('.dv-book-empty', view), open: $('.dv-book-open', view), count: $('.dv-book-count', view) };
  view.addEventListener('click', (e) => {
    const a = e.target.closest('[data-act]')?.dataset.act;
    if (a === 'reload') load();
    else if (a === 'newtab' && cur) window.open(pageUrl(cur), '_blank');
    const b = e.target.closest('[data-book]');
    if (b) pick(b.dataset.book);
  });
  on('view', (v) => { if (v === 'book') load(); });
  // 책 안 «노트 목록» 단추 → {book:'toggle-list'} — 왼쪽 목록을 자리째 숨김 ↔ 보임(상태 기억)
  //   다른 출처(페이지 서버 = 포트 +100)라 보낸 창이 이 iframe 인지 · 메시지 모양 · 포트만 본다
  const box = $('.dv-book', view);
  box.classList.toggle('no-side', store.get('book.side', '1') === '0');
  window.addEventListener('message', (e) => {
    if (e.source !== el.frame.contentWindow || e.data?.book !== 'toggle-list') return;
    try { if (pagePort && +new URL(e.origin).port !== pagePort) return; } catch { return; }
    const hide = !box.classList.contains('no-side');
    box.classList.toggle('no-side', hide);
    store.set('book.side', hide ? '0' : '1');
  });
}

// 목록 읽기 → 그리기 · 고른 책이 없거나 사라졌으면 맨 위 책
async function load() {
  try {
    list = await api('books');
  } catch (e) {
    el.list.innerHTML = `<div class="dv-book-none">목록 읽기 실패 — ${esc(e.message || e)}</div>`;
    return;
  }
  if (!list.books.some((b) => b.path === cur)) cur = list.books[0]?.path || null;
  paint();
  show();
}

// 목록 한 줄 — 설문 목록(a.sv)과 같은 모양 · 마지막 판 = 파랑(pend) · 앞 판 = 회색(done)
// b: 판 항목
function row(b) {
  const cls = `dv-book-item ${b.latest ? 'pend' : 'done'}${b.path === cur ? ' is-on' : ''}`;
  return `<button type="button" class="${cls}" data-book="${esc(b.path)}" title="${esc(b.path)}">`
    + `<span class="dv-book-name">${esc(b.title)}</span><small class="dv-book-sub">${esc(b.sub || '')}</small></button>`;
}

function paint() {
  el.count.textContent = list.books.length ? String(list.books.length) : '';
  el.list.innerHTML = list.books.length ? list.books.map(row).join('')
    : '<div class="dv-book-none">만든 책 없음 — $ontology 로 1차판을 만들면 여기에</div>';
}

// 오른쪽 — 고른 책을 페이지 서버 주소로
function show() {
  el.empty.hidden = !!cur && !!pagePort;
  el.frame.hidden = !el.empty.hidden;
  el.open.disabled = !cur || !pagePort;
  if (!pagePort) { el.empty.textContent = '페이지 서버 꺼짐(--page-port 0)'; el.path.textContent = ''; return; }
  if (!cur) { el.empty.textContent = '고른 책 없음'; el.path.textContent = ''; el.frame.removeAttribute('src'); return; }
  const url = pageUrl(cur);
  el.path.textContent = cur;
  el.path.title = url;
  if (el.frame.dataset.url !== url) { el.frame.dataset.url = url; el.frame.src = url; }
}

// 책 고르기
// path: 작업 폴더 기준 경로
function pick(path) {
  if (!path) return;
  cur = path;
  store.set('book.cur', cur);
  paint();
  show();
}

// 시험 · 디버깅용
export function bookDebug() {
  return { cur, list, url: el.frame?.dataset.url || null };
}
