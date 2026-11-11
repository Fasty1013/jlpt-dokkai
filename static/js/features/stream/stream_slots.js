/**
 * JLPT Dokkai Master - Stream Slots & Dynamic Catalog Feature Module
 */

import { t as tr } from '../../i18n/index.js';
import { fetchStreamSlots } from '../../api/stream.js';
import { escapeHtml } from '../../utils/dom.js';
import { getUserId } from '../../utils/user.js';
import { getCategoryName } from '../../constants/labels.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

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
          <div class="placeholder-title">${tr('stream.placeholderTitle')}</div>
          <div class="placeholder-desc">${tr('stream.placeholderDesc', { profile: escapeHtml(profileKey) })}</div>
      </div>
    `;
  }

  const t = slot.text;
  let originBadge = '';
  if (t.origin === 'parametric') {
    originBadge = `<span class="origin-badge-param">${tr('stream.originParam')}</span>`;
  } else if (t.origin === 'ai_generated') {
    originBadge = `<span class="origin-badge-param" style="background:#eff6ff;color:#1e40af;border-color:#bfdbfe;">${tr('stream.originAi')}</span>`;
  } else if (t.category === 'nhk' || (t.title && t.title.includes('NHK'))) {
    originBadge = '<span class="nhk-badge">NHK WORLD</span>';
  } else {
    originBadge = '<span class="exam-archive-badge">📜 JLPT 過去問</span>';
  }

  return `
    <div class="stream-slot-card" data-slot-id="${escapeHtml(slot.id)}" data-text-id="${escapeHtml(t.id)}" data-position="${escapeHtml(slot.position)}" data-action="open-pretest" role="button" tabindex="0" style="cursor: pointer;">
        <div class="slot-position-badge">${tr('stream.slot', { n: slot.position })}</div>
        <div class="slot-meta-row">
            <span class="level-tag" data-lvl="${t.level}">${t.level}</span>
            <span class="category-tag">${getCategoryName(t.category) || t.category}</span>
            ${originBadge}
        </div>
        <h3 class="slot-title" lang="ja">${escapeHtml(t.title)}</h3>
        <div class="slot-footer">
            <div class="slot-specs">
                <span>⏱️ ${tr('exercise.minutes', { n: t.recommended_time_min })}</span>
                <span>${tr('stream.questions', { n: t.question_count })}</span>
            </div>
            <button type="button" class="btn btn-primary btn-sm" data-action="open-pretest" data-text-id="${t.id}">
                ${tr('stream.start')}
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
let lastProfileKey = '';

/** Re-render the already loaded slot cards (language switch) without a network request. */
export function rerenderSlotsFromCache(context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;
  if (!elements || !elements.activeSlotsList || !state || !Array.isArray(state.cachedSlots) || state.cachedSlots.length === 0) return;
  elements.activeSlotsList.innerHTML = state.cachedSlots.map(slot => renderSlotCardHtml(slot, lastProfileKey)).join('');
}

export async function fetchAndRenderSlots(isExplicitRefresh = false, context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;
  if (!elements || !elements.activeSlotsList) return;
  elements.activeSlotsList.innerHTML = `<div class="loading-spinner">${tr('stream.loading')}</div>`;

  const userId = (typeof context.getUserId === 'function') ? context.getUserId() : getUserId();
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

    lastProfileKey = data?.profile_key || '';
    elements.activeSlotsList.innerHTML = slots.map(slot => renderSlotCardHtml(slot, lastProfileKey)).join('');
  } catch (err) {
    console.error(err);
    elements.activeSlotsList.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--vermilion);">
          <p>${tr('stream.loadError')}</p>
          <button type="button" class="btn btn-secondary btn-sm" data-action="refresh-slots" style="margin-top: 0.5rem;">
              ${tr('stream.retry')}
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
