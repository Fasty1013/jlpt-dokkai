/**
 * JLPT Dokkai Master - Solved Archive Feature Module
 */

import { fetchSolvedTasks, fetchSolvedDetail, retrySolvedTask as apiRetrySolvedTask } from '../../api/stream.js';
import { escapeHtml } from '../../utils/dom.js';
import { getUserId } from '../../utils/user.js';

/**
 * Generate HTML markup for a single solved task card.
 * @param {Object} t
 * @returns {string}
 */
export function renderSolvedCardHtml(t) {
  const isPerfect = (t.last_score === 100 || t.score === 100 || t.perfect);
  const scoreBadgeClass = isPerfect ? 'score-perfect' : 'score-errors';
  const displayScore = (t.last_score !== undefined) ? t.last_score : (t.score !== undefined ? t.score : 0);
  const scoreBadgeText = isPerfect ? '100% ★ Идеально' : `${displayScore}% с ошибками`;
  const dateStr = t.solved_at
    ? new Date(t.solved_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
    : '';

  return `
    <div class="stream-solved-card" data-text-id="${t.text_id}">
        <div class="solved-card-header">
            <span class="solved-score-badge ${scoreBadgeClass}">${scoreBadgeText}</span>
            <span class="solved-card-date">${dateStr}</span>
        </div>
        <h4 class="solved-card-title">${escapeHtml(t.title)}</h4>
        <div class="solved-card-actions">
            <button class="btn-solved-action btn-review" onclick="reviewSolvedTask(${t.text_id})">
                🔍 Обзор разбора
            </button>
            <button class="btn-solved-action" onclick="retrySolvedTask(${t.text_id})">
                🔁 Пройти заново
            </button>
            <button class="btn-solved-action" onclick="openReportModal(${t.text_id}, '${escapeHtml(t.title)}')">
                ⚠️ Сообщить об ошибке
            </button>
        </div>
    </div>
  `;
}

/**
 * Fetch and render solved tasks archive.
 * @param {Object} context - { state, elements, getUserId }
 */
export async function fetchAndRenderSolvedTasks(context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const elements = context.elements || (typeof window !== 'undefined' ? window.elements : null);
  const userId = (typeof context.getUserId === 'function') ? context.getUserId() : getUserId();

  if (!elements?.solvedTasksList) return;

  try {
    let localSolved = [];
    if (typeof window !== 'undefined' && window.DokkaiStorage) {
      try {
        localSolved = await window.DokkaiStorage.getSolvedTasks(state?.streamProfile?.level || 'N5', state?.solvedFilter || 'all');
      } catch (e) {
        console.warn('[Dokkai] Failed to read local solved tasks:', e);
      }
    }

    const profileLevel = state?.streamProfile?.level || 'N5';
    const solvedFilter = state?.solvedFilter || 'all';

    let items = localSolved;

    try {
      const data = await fetchSolvedTasks({
        userId,
        level: profileLevel,
        filter: solvedFilter
      });
      const serverItems = data?.items || [];

      if (typeof window !== 'undefined' && window.DokkaiStorage && serverItems.length > 0) {
        for (const sTask of serverItems) {
          await window.DokkaiStorage.recordSolvedTask(sTask);
        }
        items = await window.DokkaiStorage.getSolvedTasks(profileLevel, solvedFilter);
      } else if (serverItems.length > 0 && items.length === 0) {
        items = serverItems;
      }
    } catch (err) {
      console.warn('Backend solved tasks fetch failed (using local offline storage):', err);
    }

    if (state) state.cachedSolved = items;

    if (elements.solvedArchiveTotal) elements.solvedArchiveTotal.textContent = items.length;
    if (elements.mobileSolvedCount) elements.mobileSolvedCount.textContent = items.length;

    if (items.length === 0) {
      elements.solvedTasksList.innerHTML = `
        <div class="stream-empty-solved">
            <span class="empty-icon">📖</span>
            <p>Здесь будут сохраняться решённые вами задания.</p>
            <span class="empty-hint">Выберите любое задание из левой колонки «Задания», чтобы начать!</span>
        </div>
      `;
      return;
    }

    elements.solvedTasksList.innerHTML = items.map(t => renderSolvedCardHtml(t)).join('');
  } catch (err) {
    console.error(err);
    elements.solvedTasksList.innerHTML = `
      <div style="text-align: center; padding: 1.5rem; color: var(--vermilion);">
          Не удалось загрузить архив решённых заданий.
      </div>
    `;
  }
}

/**
 * Review analysis of a previously solved task.
 * @param {number|string} textId
 * @param {Object} context - { state, getUserId, onRenderAnalysis }
 */
export async function reviewSolvedTask(textId, context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const userId = (typeof context.getUserId === 'function') ? context.getUserId() : getUserId();

  try {
    let data;
    try {
      data = await fetchSolvedDetail(textId, userId);
    } catch (err) {
      if (err.status === 403) {
        alert('Anti-Cheat: Задание ещё не решено. Разбор ответов недоступен.');
        return;
      }
      throw err;
    }

    if (state) {
      state.activeText = data;
      state.currentView = 'analysis';
      state.analysisActiveTabIdx = 0;
    }
    if (typeof history !== 'undefined' && history.pushState) {
      history.pushState({ view: 'analysis', textId }, '', '#analysis');
    }

    if (typeof context.onRenderAnalysis === 'function') {
      context.onRenderAnalysis(data);
    } else if (typeof window !== 'undefined' && typeof window.renderAnalysisView === 'function') {
      window.renderAnalysisView(data);
    }
  } catch (e) {
    console.error(e);
    alert('Не удалось загрузить разбор задания');
  }
}

/**
 * Retry a solved task.
 * @param {number|string} textId
 * @param {Object} context - { state, getUserId, onOpenPretest }
 */
export async function retrySolvedTask(textId, context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const userId = (typeof context.getUserId === 'function') ? context.getUserId() : getUserId();

  try {
    const data = await apiRetrySolvedTask(textId, userId);
    if (state) {
      state.isRetryMode = true;
      state.pendingTextData = data;
    }

    if (typeof context.onOpenPretest === 'function') {
      context.onOpenPretest(textId);
    } else if (typeof window !== 'undefined' && typeof window.openPretestModal === 'function') {
      window.openPretestModal(textId);
    }
  } catch (e) {
    console.error(e);
    alert('Не удалось запустить повторное прохождение');
  }
}
