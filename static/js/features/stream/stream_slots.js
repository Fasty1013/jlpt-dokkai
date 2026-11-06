/**
 * JLPT Dokkai Master - Stream Slots & Dynamic Catalog Feature Module
 */

import { fetchStreamSlots } from '../../api/stream.js';
import { escapeHtml } from '../../utils/dom.js';
import { CATEGORY_NAMES } from '../../constants/labels.js';

/**
 * Generate HTML markup for a single slot card.
 * @param {Object} slot
 * @param {string} profileKey
 * @returns {string}
 */
export function renderSlotCardHtml(slot, profileKey = '') {
  if (slot.state === 'placeholder' || !slot.text) {
    return `
      <div class="stream-slot-placeholder" data-position="${slot.position}">
          <div class="placeholder-pulse">⏳</div>
          <div class="placeholder-title">Готовится новое задание...</div>
          <div class="placeholder-desc">Для профиля ${escapeHtml(profileKey)} генерируется или подбирается оригинальный учебный материал.</div>
      </div>
    `;
  }

  const t = slot.text;
  let originBadge = '';
  if (t.origin === 'parametric') {
    originBadge = '<span class="origin-badge-param">⚡ Параметрический</span>';
  } else if (t.origin === 'ai_generated') {
    originBadge = '<span class="origin-badge-param" style="background:#eff6ff;color:#1e40af;border-color:#bfdbfe;">🤖 ИИ-генерация</span>';
  } else if (t.category === 'nhk' || (t.title && t.title.includes('NHK'))) {
    originBadge = '<span class="nhk-badge">NHK WORLD</span>';
  } else {
    originBadge = '<span class="exam-archive-badge">📜 JLPT 過去問</span>';
  }

  return `
    <div class="stream-slot-card" data-slot-id="${slot.id}" data-text-id="${t.id}" data-position="${slot.position}" onclick="openPretestModal(${t.id})" style="cursor: pointer;">
        <div class="slot-position-badge">Слот #${slot.position}</div>
        <div class="slot-meta-row">
            <span class="level-tag" data-lvl="${t.level}">${t.level}</span>
            <span class="category-tag">${CATEGORY_NAMES[t.category] || t.category}</span>
            ${originBadge}
        </div>
        <h3 class="slot-title">${escapeHtml(t.title)}</h3>
        <div class="slot-footer">
            <div class="slot-specs">
                <span>⏱️ ${t.recommended_time_min} мин</span>
                <span>❓ ${t.question_count} вопр.</span>
            </div>
            <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); openPretestModal(${t.id})">
                Начать решение →
            </button>
        </div>
    </div>
  `;
}

/**
 * Fetch and render slots into DOM container.
 * @param {boolean} isExplicitRefresh
 * @param {Object} context - { state, elements, getUserId }
 */
export async function fetchAndRenderSlots(isExplicitRefresh = false, context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const elements = context.elements || (typeof window !== 'undefined' ? window.elements : null);
  const getUserId = context.getUserId || (typeof window !== 'undefined' ? window.getUserId : () => 'guest');

  if (!elements || !elements.activeSlotsList) return;
  elements.activeSlotsList.innerHTML = '<div class="loading-spinner">Загрузка слотов заданий...</div>';

  const userId = getUserId();
  const profileLevel = state?.streamProfile?.level || 'N5';
  const profileCategory = state?.streamProfile?.category || '';

  try {
    const data = await fetchStreamSlots({
      userId,
      level: profileLevel,
      category: profileCategory,
      refresh: Boolean(isExplicitRefresh)
    });

    const slots = data?.slots || [];
    if (state) {
      state.cachedSlots = slots;
    }

    if (typeof window !== 'undefined') {
      window.cachedCatalogTexts = slots.filter(s => s.text).map(s => s.text);
    }

    if (elements.mobileActiveCount) {
      const activeCount = slots.filter(s => s.state === 'active' && s.text).length;
      elements.mobileActiveCount.textContent = activeCount;
    }

    elements.activeSlotsList.innerHTML = slots.map(slot => renderSlotCardHtml(slot, data?.profile_key || '')).join('');
  } catch (err) {
    console.error(err);
    elements.activeSlotsList.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--vermilion);">
          <p>Не удалось загрузить активные задания.</p>
          <button class="btn btn-secondary btn-sm" onclick="fetchAndRenderSlots()" style="margin-top: 0.5rem;">
              🔄 Повторить попытку
          </button>
      </div>
    `;
  }
}

/**
 * Handle animated replacement of a completed slot.
 * @param {number|string} solvedTextId
 * @param {Object} replacement
 * @param {Function} onRefresh
 */
export function handleSlotReplacement(solvedTextId, replacement, onRefresh) {
  const card = document.querySelector(`.stream-slot-card[data-text-id="${solvedTextId}"]`);
  if (card) {
    card.classList.add('slot-solving-out');
    setTimeout(() => {
      if (typeof onRefresh === 'function') onRefresh();
      else fetchAndRenderSlots();
    }, 350);
  } else {
    if (typeof onRefresh === 'function') onRefresh();
    else fetchAndRenderSlots();
  }
}

/**
 * Switch column visibility on mobile viewports.
 * @param {string} col - 'active' | 'solved'
 * @param {Object} elements
 */
export function switchMobileStreamCol(col, elements) {
  if (!elements || !elements.tabColActive || !elements.tabColSolved) return;
  if (col === 'active') {
    elements.tabColActive.classList.add('active');
    elements.tabColSolved.classList.remove('active');
    if (elements.colActiveSlots) elements.colActiveSlots.classList.remove('hidden-mobile');
    if (elements.colSolvedArchive) elements.colSolvedArchive.classList.add('hidden-mobile');
  } else {
    elements.tabColActive.classList.remove('active');
    elements.tabColSolved.classList.add('active');
    if (elements.colActiveSlots) elements.colActiveSlots.classList.add('hidden-mobile');
    if (elements.colSolvedArchive) elements.colSolvedArchive.classList.remove('hidden-mobile');
  }
}
