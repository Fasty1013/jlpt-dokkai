/**
 * JLPT Dokkai Master - admin panel (/admin).
 * All user-supplied text (report details, titles) is rendered with textContent — never innerHTML.
 */
import { getAdminToken, setAdminToken, adminFetch } from '../api/admin_token.js';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const state = {
  tab: 'dashboard',
  reportStatus: 'new',
  textsOffset: 0,
  textsLimit: 50,
};

const CATEGORY_NAMES = {
  short: '短文', medium: '中文', long: '長文', info_search: '情報検索', article: 'Статья',
};

class AuthError extends Error {}

// Latest-request-wins: a slower earlier response must not overwrite a newer one
// (e.g. opening "Задания" then searching immediately).
const requestSeq = {};
function nextSeq(key) { requestSeq[key] = (requestSeq[key] || 0) + 1; return requestSeq[key]; }
function isStale(key, seq) { return requestSeq[key] !== seq; }

async function api(path, options = {}) {
  const resp = await adminFetch(path, options);
  if (resp.status === 401) throw new AuthError('unauthorized');
  let data = null;
  const type = resp.headers.get('content-type') || '';
  if (type.includes('application/json')) data = await resp.json();
  if (!resp.ok) throw new Error((data && data.detail) || `Ошибка ${resp.status}`);
  return data;
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function shortUser(id) {
  if (!id) return 'аноним';
  return id.length > 14 ? `${id.slice(0, 12)}…` : id;
}

let toastTimer = null;
function toast(message, isError = false) {
  const node = $('#adm-toast');
  node.textContent = message;
  node.classList.toggle('is-error', isError);
  node.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { node.hidden = true; }, 3000);
}

async function guarded(fn) {
  try {
    await fn();
  } catch (err) {
    if (err instanceof AuthError) {
      showLogin('Ключ не подошёл или не задан на сервере.');
      return;
    }
    console.error(err);
    toast(err.message || 'Ошибка запроса', true);
  }
}

// ------------------------------------------------------------------ auth

function showLogin(errorText = '') {
  $('#adm-login').hidden = false;
  $('#adm-tabs').hidden = true;
  $('#adm-logout').hidden = true;
  $$('.adm-panel').forEach((p) => { p.hidden = true; });
  const err = $('#adm-login-error');
  err.textContent = errorText;
  err.hidden = !errorText;
  $('#adm-token-input').focus();
}

function showApp() {
  $('#adm-login').hidden = true;
  $('#adm-tabs').hidden = false;
  $('#adm-logout').hidden = !getAdminToken();
  switchTab(state.tab);
}

async function checkAuth() {
  try {
    await api('/api/admin/check');
    showApp();
  } catch (err) {
    if (err instanceof AuthError) showLogin(getAdminToken() ? 'Сохранённый ключ не подошёл.' : '');
    else showLogin(`Сервер недоступен: ${err.message}`);
  }
}

// ------------------------------------------------------------------ tabs

function switchTab(tab) {
  state.tab = tab;
  $$('.adm-tab').forEach((b) => b.classList.toggle('is-active', b.dataset.tab === tab));
  $$('.adm-panel').forEach((p) => { p.hidden = p.id !== `panel-${tab}`; });
  const loaders = { dashboard: loadDashboard, reports: loadReports, texts: loadTexts, activity: loadActivity };
  if (loaders[tab]) guarded(loaders[tab]);
}

// ------------------------------------------------------------------ dashboard

function statCard(label, value, hint) {
  return el('div', { class: 'adm-stat' },
    el('div', { class: 'adm-stat-value', text: value ?? '—' }),
    el('div', { class: 'adm-stat-label', text: label }),
    hint ? el('div', { class: 'adm-stat-hint', text: hint }) : null);
}

function setReportsBadge(count) {
  const badge = $('#adm-reports-badge');
  badge.textContent = String(count);
  badge.hidden = !count;
}

async function loadDashboard() {
  const s = await api('/api/admin/stats');
  setReportsBadge(s.reports.new);
  $('#adm-stats').replaceChildren(
    statCard('Новые жалобы', s.reports.new, `решено: ${s.reports.resolved}`),
    statCard('Заданий активно', s.texts.active, `скрыто: ${s.texts.hidden}`),
    statCard('Пользователей', s.users.total, `за 7 дней: ${s.users.last_7_days}`),
    statCard('Попыток', s.attempts.total, `за 7 дней: ${s.attempts.last_7_days}`),
    statCard('Средний балл', s.attempts.avg_score === null ? '—' : `${s.attempts.avg_score}%`),
  );
  const rows = Object.entries(s.texts.by_level).map(([level, v]) =>
    el('tr', {}, el('td', { text: level }), el('td', { text: v.active }), el('td', { text: v.hidden })));
  $('#adm-levels').replaceChildren(
    el('thead', {}, el('tr', {}, el('th', { text: 'Уровень' }), el('th', { text: 'Активных' }), el('th', { text: 'Скрытых' }))),
    el('tbody', {}, rows.length ? rows : el('tr', {}, el('td', { colspan: 3, text: 'Нет заданий' }))),
  );
}

// ------------------------------------------------------------------ reports

function textLabel(t) {
  if (!t) return 'Задание удалено';
  return `${t.title} · ${t.level} · ${CATEGORY_NAMES[t.category] || t.category}`;
}

function reportCard(r) {
  const t = r.text;
  const actions = el('div', { class: 'adm-actions' });
  if (r.status === 'new') {
    actions.append(el('button', { type: 'button', class: 'adm-btn adm-btn-primary', onclick: () => guarded(async () => {
      await api(`/api/admin/reports/${r.id}/resolve`, { method: 'POST' });
      toast('Отмечено как решённое');
      await loadReports();
    }) }, 'Решено'));
  } else {
    actions.append(el('button', { type: 'button', class: 'adm-btn adm-btn-ghost', onclick: () => guarded(async () => {
      await api(`/api/admin/reports/${r.id}/reopen`, { method: 'POST' });
      toast('Возвращено в новые');
      await loadReports();
    }) }, 'Вернуть в новые'));
  }
  if (t) {
    actions.append(el('button', { type: 'button', class: 'adm-btn adm-btn-ghost', onclick: () => guarded(() => openText(t.id)) }, 'Открыть задание'));
  }
  actions.append(el('button', { type: 'button', class: 'adm-btn adm-btn-danger', onclick: () => guarded(async () => {
    if (!confirm('Удалить это сообщение без возможности восстановления?')) return;
    await api(`/api/admin/reports/${r.id}`, { method: 'DELETE' });
    toast('Сообщение удалено');
    await loadReports();
  }) }, 'Удалить'));

  return el('article', { class: `adm-report${r.status === 'resolved' ? ' is-resolved' : ''}`, 'data-report-id': r.id },
    el('div', { class: 'adm-report-head' },
      el('span', { class: 'adm-report-reason', text: r.reason }),
      el('span', { class: 'adm-muted', text: fmtDate(r.created_at) })),
    el('div', { class: 'adm-report-task', lang: 'ja', text: textLabel(t) }),
    t && !t.is_active ? el('div', { class: 'adm-flag', text: `Задание скрыто из потока (жалоб: ${t.report_count})` }) : null,
    el('p', { class: 'adm-report-details', text: r.details || 'Без комментария' }),
    el('div', { class: 'adm-muted', text: `Пользователь: ${shortUser(r.user_id)}${r.resolved_at ? ` · решено ${fmtDate(r.resolved_at)}` : ''}` }),
    actions);
}

async function loadReports() {
  $$('[data-report-status]').forEach((b) => b.classList.toggle('is-active', b.dataset.reportStatus === state.reportStatus));
  const seq = nextSeq('reports');
  const data = await api(`/api/admin/reports?status=${state.reportStatus}`);
  if (isStale('reports', seq)) return;
  const list = $('#adm-reports-list');
  if (!data.items.length) {
    list.replaceChildren(el('p', { class: 'adm-empty', text: state.reportStatus === 'new' ? 'Новых сообщений нет.' : 'Сообщений нет.' }));
  } else {
    list.replaceChildren(...data.items.map(reportCard));
  }
  if (state.reportStatus === 'new') setReportsBadge(data.items.length);
}

async function downloadReportsCsv() {
  const resp = await adminFetch('/api/admin/reports.csv');
  if (resp.status === 401) throw new AuthError('unauthorized');
  if (!resp.ok) throw new Error(`Ошибка ${resp.status}`);
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = el('a', { href: url, download: 'dokkai_reports.csv' });
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ------------------------------------------------------------------ texts

async function setTextActive(t, active) {
  const path = active ? `/api/admin/texts/${t.id}/show` : `/api/admin/texts/${t.id}/hide`;
  await api(path, { method: 'POST' });
  toast(active ? 'Задание возвращено в поток (жалобы сброшены)' : 'Задание скрыто из потока');
}

async function loadTexts() {
  const params = new URLSearchParams({ limit: state.textsLimit, offset: state.textsOffset });
  const q = $('#adm-texts-q').value.trim();
  if (q) params.set('q', q);
  if ($('#adm-texts-level').value) params.set('level', $('#adm-texts-level').value);
  if ($('#adm-texts-active').value) params.set('active', $('#adm-texts-active').value);
  if ($('#adm-texts-reported').checked) params.set('reported', 'true');
  const seq = nextSeq('texts');
  const data = await api(`/api/admin/texts?${params}`);
  if (isStale('texts', seq)) return;

  const rows = data.items.map((t) => el('tr', { class: t.is_active ? '' : 'is-hidden-row' },
    el('td', { text: t.id }),
    el('td', { lang: 'ja', text: t.title }),
    el('td', { text: t.level }),
    el('td', { text: CATEGORY_NAMES[t.category] || t.category }),
    el('td', { text: t.report_count }),
    el('td', { text: t.is_active ? 'активно' : 'скрыто' }),
    el('td', { class: 'adm-actions' },
      el('button', { type: 'button', class: 'adm-btn adm-btn-ghost', onclick: () => guarded(() => openText(t.id)) }, 'Просмотр'),
      el('button', { type: 'button', class: `adm-btn ${t.is_active ? 'adm-btn-danger' : 'adm-btn-primary'}`, onclick: () => guarded(async () => {
        await setTextActive(t, !t.is_active);
        await loadTexts();
      }) }, t.is_active ? 'Скрыть' : 'Вернуть'))));

  $('#adm-texts-table').replaceChildren(
    el('thead', {}, el('tr', {}, ...['ID', 'Название', 'Уровень', 'Формат', 'Жалоб', 'Статус', ''].map((h) => el('th', { text: h })))),
    el('tbody', {}, rows.length ? rows : el('tr', {}, el('td', { colspan: 7, text: 'Ничего не найдено' }))),
  );

  const from = data.total ? state.textsOffset + 1 : 0;
  const to = Math.min(state.textsOffset + state.textsLimit, data.total);
  $('#adm-texts-pager').replaceChildren(
    el('button', { type: 'button', class: 'adm-btn adm-btn-ghost', disabled: state.textsOffset === 0, onclick: () => {
      state.textsOffset = Math.max(0, state.textsOffset - state.textsLimit); guarded(loadTexts);
    } }, '← Назад'),
    el('span', { class: 'adm-muted', text: `${from}–${to} из ${data.total}` }),
    el('button', { type: 'button', class: 'adm-btn adm-btn-ghost', disabled: to >= data.total, onclick: () => {
      state.textsOffset += state.textsLimit; guarded(loadTexts);
    } }, 'Вперёд →'),
  );
}

async function openText(textId) {
  const t = await api(`/api/admin/texts/${textId}`);
  $('#adm-dialog-title').textContent = `#${t.id} ${t.title}`;

  // content_html is our own seeded/imported passage markup (ruby furigana); it is rendered in a
  // sandboxed iframe so that no script or handler inside it can run in the admin origin.
  const passage = el('iframe', { class: 'adm-passage', sandbox: '', title: 'Текст задания' });
  passage.srcdoc = `<!DOCTYPE html><meta charset="utf-8"><style>body{font-family:'Noto Sans JP','Yu Gothic',sans-serif;line-height:1.9;margin:12px;color:#18191a}rt{font-size:.55em;color:#767e85}</style>${t.content_html}`;

  const questions = t.questions.map((q) => el('div', { class: 'adm-question' },
    el('p', { class: 'adm-question-text', lang: 'ja', text: `${q.number}. ${q.text}` }),
    el('ol', {}, q.options.map((o) => el('li', { class: o.is_correct ? 'is-correct' : '', lang: 'ja', text: `${o.text}${o.is_correct ? '  ✓' : ''}` }))),
    q.explanation ? el('p', { class: 'adm-muted', text: q.explanation }) : null));

  const reports = t.reports.length
    ? t.reports.map((r) => el('li', {}, el('strong', { text: r.reason }), ` — ${r.details || 'без комментария'} `, el('span', { class: 'adm-muted', text: `(${fmtDate(r.created_at)}, ${r.status === 'new' ? 'новое' : 'решено'})` })))
    : [el('li', { class: 'adm-muted', text: 'Жалоб нет' })];

  const toggle = el('button', { type: 'button', class: `adm-btn ${t.is_active ? 'adm-btn-danger' : 'adm-btn-primary'}`, onclick: () => guarded(async () => {
    await setTextActive(t, !t.is_active);
    await openText(t.id);
    if (state.tab === 'texts') await loadTexts();
    if (state.tab === 'reports') await loadReports();
  }) }, t.is_active ? 'Скрыть из потока' : 'Вернуть в поток');

  $('#adm-dialog-body').replaceChildren(
    el('div', { class: 'adm-muted', text: `${t.level} · ${CATEGORY_NAMES[t.category] || t.category} · ${t.origin} · жалоб: ${t.report_count} · ${t.is_active ? 'активно' : 'скрыто'}${t.source_exam ? ` · ${t.source_exam}` : ''}` }),
    el('div', { class: 'adm-actions' }, toggle),
    el('h3', { text: 'Текст' }), passage,
    el('h3', { text: 'Вопросы и правильные ответы' }), ...questions,
    el('h3', { text: 'Перевод' }), el('p', { class: 'adm-translation', text: t.translation_ru || '—' }),
    el('h3', { text: 'Жалобы на это задание' }), el('ul', { class: 'adm-report-mini' }, reports),
  );
  const dialog = $('#adm-text-dialog');
  if (!dialog.open) dialog.showModal();
}

// ------------------------------------------------------------------ activity

async function loadActivity() {
  const data = await api('/api/admin/activity?limit=100');
  const modes = { first: 'первая', retry: 'повтор', retry_errors: 'работа над ошибками' };
  const rows = data.items.map((a) => el('tr', {},
    el('td', { text: fmtDate(a.created_at) }),
    el('td', { text: shortUser(a.user_id), title: a.user_id }),
    el('td', { lang: 'ja', text: `${a.text.title} (${a.text.level})` }),
    el('td', { text: `${a.score}%` }),
    el('td', { text: modes[a.mode] || a.mode })));
  $('#adm-activity-table').replaceChildren(
    el('thead', {}, el('tr', {}, ...['Когда', 'Пользователь', 'Задание', 'Балл', 'Попытка'].map((h) => el('th', { text: h })))),
    el('tbody', {}, rows.length ? rows : el('tr', {}, el('td', { colspan: 5, text: 'Попыток пока нет' }))),
  );
}

// ------------------------------------------------------------------ wiring

function init() {
  $('#adm-login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    setAdminToken($('#adm-token-input').value.trim());
    $('#adm-token-input').value = '';
    checkAuth();
  });
  $('#adm-logout').addEventListener('click', () => {
    setAdminToken('');
    showLogin('Вы вышли. Ключ удалён из этого браузера.');
  });
  $$('.adm-tab').forEach((b) => b.addEventListener('click', () => switchTab(b.dataset.tab)));
  $$('[data-refresh]').forEach((b) => b.addEventListener('click', () => switchTab(b.dataset.refresh)));
  $$('[data-report-status]').forEach((b) => b.addEventListener('click', () => {
    state.reportStatus = b.dataset.reportStatus;
    guarded(loadReports);
  }));
  $('#adm-reports-csv').addEventListener('click', () => guarded(downloadReportsCsv));
  $('#adm-texts-form').addEventListener('submit', (e) => {
    e.preventDefault();
    state.textsOffset = 0;
    guarded(loadTexts);
  });
  $('#adm-dialog-close').addEventListener('click', () => $('#adm-text-dialog').close());
  checkAuth();
}

init();
