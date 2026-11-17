/**
 * JLPT Dokkai Master - admin panel, "Импорт PDF" tab (I36).
 * Upload a PDF book -> drafts in the staging area -> check answers -> publish into the catalog.
 * Moved here from the main site's "Импорт PDF" tab: the feature is for the administrator only.
 * Text from the PDF is rendered with textContent; the passage HTML goes into a sandboxed iframe.
 * Helpers (el, toast, guarded, AuthError) are injected by admin.js to keep the import graph acyclic.
 */
import { adminFetch } from '../api/admin_token.js';

const CATEGORY_LABELS = {
  short: '短文', medium: '中文', long: '長文', info_search: '情報検索', article: '記事・論説',
};

let ctx = null;
let drafts = [];
let selectedFile = null;

const $ = (sel) => document.querySelector(sel);

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function detailMessage(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail.errors)) return detail.errors.join('\n');
  if (Array.isArray(detail)) return detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
  return JSON.stringify(detail);
}

async function call(path, options = {}, fallback = 'Ошибка запроса') {
  const resp = await adminFetch(path, options);
  if (resp.status === 401) throw new ctx.AuthError('unauthorized');
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok || data.success === false) {
    throw new Error(data.error || detailMessage(data.detail, `${fallback} (${resp.status})`));
  }
  return data;
}

function putDraft(draft) {
  return call(`/api/admin/drafts/${encodeURIComponent(draft.slug)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draft),
  }, 'Не удалось сохранить черновик');
}

// ------------------------------------------------------------------ file selection

function selectFile(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    ctx.toast('Нужен файл в формате .pdf', true);
    return;
  }
  selectedFile = file;
  $('#imp-file-name').textContent = file.name;
  $('#imp-file-size').textContent = formatSize(file.size);
  $('#imp-file-prompt').hidden = true;
  $('#imp-file-info').hidden = false;
}

function clearFile() {
  selectedFile = null;
  $('#imp-file-input').value = '';
  $('#imp-file-prompt').hidden = false;
  $('#imp-file-info').hidden = true;
}

async function upload() {
  if (!selectedFile) {
    ctx.toast('Сначала выберите PDF-файл', true);
    return;
  }
  const form = new FormData();
  form.append('file', selectedFile);
  form.append('level', $('#imp-level').value);
  form.append('category', $('#imp-category').value);
  const title = $('#imp-title').value.trim();
  if (title) form.append('title_override', title);

  const btn = $('#imp-upload-btn');
  btn.disabled = true;
  $('#imp-progress').hidden = false;
  try {
    const data = await call('/api/admin/upload-pdf', { method: 'POST', body: form }, 'Не удалось распознать PDF');
    clearFile();
    $('#imp-title').value = '';
    await loadDrafts();
    ctx.toast(`Распознано черновиков: ${data.drafts ? data.drafts.length : 0}`);
  } finally {
    btn.disabled = false;
    $('#imp-progress').hidden = true;
  }
}

// ------------------------------------------------------------------ drafts

function setDraftsBadge(count) {
  const badge = $('#adm-drafts-badge');
  badge.textContent = String(count);
  badge.hidden = !count;
  $('#imp-drafts-count').textContent = String(count);
}

function passageFrame(html) {
  const frame = ctx.el('iframe', { class: 'adm-passage', sandbox: '', title: 'Текст черновика' });
  frame.srcdoc = `<!DOCTYPE html><meta charset="utf-8"><style>body{font-family:'Noto Sans JP','Yu Gothic',sans-serif;line-height:1.9;margin:12px;color:#18191a}rt{font-size:.55em;color:#767e85}</style>${html || ''}`;
  return frame;
}

function draftCard(draft) {
  const { el } = ctx;
  const pct = Math.round((draft.confidence || 0) * 100);
  const questions = draft.questions || [];

  const questionNodes = questions.map((q, qIdx) => el('div', { class: 'adm-question' },
    el('p', { class: 'adm-question-text', lang: 'ja' },
      `${q.question_number || qIdx + 1}. ${q.prompt || ''} `,
      el('span', { class: q.answer_matched ? 'adm-imp-ok' : 'adm-imp-missing', text: q.answer_matched ? '✓ ответ из ключа' : '⚠ ответ не найден' })),
    ...(q.options || []).map((opt) => {
      const radio = el('input', {
        type: 'radio', name: `imp-${draft.slug}-${qIdx}`, 'data-draft-option': `${draft.slug}:${qIdx}:${opt.option_number}`,
        'aria-label': `Вариант ${opt.option_number} правильный`,
      });
      radio.checked = !!opt.is_correct;
      radio.addEventListener('change', () => {
        q.options.forEach((o) => { o.is_correct = o.option_number === opt.option_number; });
        q.answer_matched = true;
      });
      return el('label', { class: 'adm-option-row adm-imp-option' },
        radio,
        el('span', { class: 'adm-option-num', text: `${opt.option_number}.` }),
        el('span', { lang: 'ja', text: opt.text || '' }));
    })));

  const warnings = draft.needs_manual_review && draft.needs_manual_review.length
    ? el('ul', { class: 'adm-imp-warnings' }, draft.needs_manual_review.map((w) => el('li', { text: w })))
    : null;

  const details = el('details', { class: 'adm-imp-details' },
    el('summary', { text: `Текст (${(draft.body_html || '').replace(/<[^>]+>/g, '').length} символов)` }));
  details.addEventListener('toggle', () => {
    if (details.open && !details.querySelector('iframe')) details.append(passageFrame(draft.body_html));
  });

  return el('article', { class: `adm-report adm-imp-draft${draft.needs_review ? '' : ' is-ready'}`, 'data-draft-slug': draft.slug },
    el('div', { class: 'adm-report-head' },
      el('span', { class: 'adm-report-reason', lang: 'ja', text: draft.title || draft.slug }),
      el('span', { class: 'adm-muted', text: `${draft.level} · ${CATEGORY_LABELS[draft.category] || draft.category} · точность ${pct}%` })),
    el('div', { class: 'adm-flag', text: draft.needs_review ? 'Нужна проверка' : 'Готов к публикации' }),
    draft.source_note ? el('div', { class: 'adm-muted', text: draft.source_note }) : null,
    warnings,
    details,
    el('h3', { text: `Вопросы (${questions.length}) — отметьте правильные ответы` }),
    ...questionNodes,
    el('div', { class: 'adm-actions' },
      el('button', { type: 'button', class: 'adm-btn adm-btn-primary', 'data-draft-publish': draft.slug, onclick: () => ctx.guarded(() => publish(draft)) }, 'Опубликовать'),
      el('button', { type: 'button', class: 'adm-btn', 'data-draft-save': draft.slug, onclick: () => ctx.guarded(async () => {
        await putDraft(draft);
        ctx.toast('Черновик сохранён');
      }) }, 'Сохранить'),
      el('button', { type: 'button', class: 'adm-btn adm-btn-danger', 'data-draft-delete': draft.slug, onclick: () => ctx.guarded(async () => {
        if (!confirm('Удалить этот черновик без возможности восстановления?')) return;
        await call(`/api/admin/drafts/${encodeURIComponent(draft.slug)}`, { method: 'DELETE' }, 'Не удалось удалить черновик');
        ctx.toast('Черновик удалён');
        await loadDrafts();
      }) }, 'Удалить')));
}

async function publish(draft) {
  if ((draft.questions || []).some((q) => !(q.options || []).some((o) => o.is_correct))) {
    ctx.toast('Отметьте правильный ответ в каждом вопросе', true);
    return;
  }
  await putDraft(draft);
  await call(`/api/admin/drafts/${encodeURIComponent(draft.slug)}/publish`, { method: 'POST' }, 'Не удалось опубликовать');
  ctx.toast(`Опубликовано: ${draft.title || draft.slug}`);
  await loadDrafts();
}

export async function loadDrafts() {
  const data = await call('/api/admin/drafts', {}, 'Не удалось загрузить черновики');
  drafts = Array.isArray(data) ? data : [];
  setDraftsBadge(drafts.length);
  const list = $('#imp-drafts-list');
  if (!drafts.length) {
    list.replaceChildren(ctx.el('p', { class: 'adm-empty', text: 'Черновиков нет. Загрузите PDF выше.' }));
  } else {
    list.replaceChildren(...drafts.map(draftCard));
  }
}

// ------------------------------------------------------------------ wiring

export function initPdfImport(helpers) {
  ctx = helpers;
  const zone = $('#imp-dropzone');
  const input = $('#imp-file-input');
  zone.addEventListener('click', (e) => {
    if (e.target.closest('#imp-file-clear')) return;
    input.click();
  });
  zone.addEventListener('keydown', (e) => {
    if (e.target === zone && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); input.click(); }
  });
  input.addEventListener('change', () => selectFile(input.files && input.files[0]));
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('is-dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('is-dragover'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('is-dragover');
    selectFile(e.dataTransfer.files && e.dataTransfer.files[0]);
  });
  $('#imp-file-clear').addEventListener('click', (e) => { e.stopPropagation(); clearFile(); });
  $('#imp-form').addEventListener('submit', (e) => {
    e.preventDefault();
    ctx.guarded(upload);
  });
}
