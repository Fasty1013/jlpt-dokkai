/**
 * JLPT Dokkai Master - Pretest Modal Feature Module
 */

import { t } from '../../i18n/index.js';
import { saveStoredConfig } from './config.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * Update UI tags reflecting current modal settings.
 * @param {Object} elements
 */
export function updateModalSettingTags(elements) {
  if (!elements) return;

  if (elements.pretestToggleFurigana && elements.tagFurigana) {
    if (elements.pretestToggleFurigana.checked) {
      elements.tagFurigana.textContent = t('pretest.tagTraining');
      elements.tagFurigana.className = 'setting-tag';
    } else {
      elements.tagFurigana.textContent = t('pretest.tagExam');
      elements.tagFurigana.className = 'setting-tag tag-warning';
    }
  }

  if (elements.pretestToggleHints && elements.tagHints) {
    if (elements.pretestToggleHints.checked) {
      elements.tagHints.textContent = t('pretest.tagFull');
      elements.tagHints.className = 'setting-tag';
    } else {
      elements.tagHints.textContent = t('pretest.tagHardcore');
      elements.tagHints.className = 'setting-tag tag-warning';
    }
  }

  if (elements.pretestToggleTimer && elements.tagTimer) {
    const timerActive = elements.pretestToggleTimer.checked;
    const mins = elements.modalTimerMinutes ? elements.modalTimerMinutes.textContent : '3';
    if (timerActive) {
      elements.tagTimer.textContent = t('pretest.tagTimerOn', { mins });
      elements.tagTimer.className = 'setting-tag tag-warning';
      if (elements.timerDurationSelector) elements.timerDurationSelector.classList.remove('hidden');
    } else {
      elements.tagTimer.textContent = t('pretest.tagTimerOff');
      elements.tagTimer.className = 'setting-tag';
      if (elements.timerDurationSelector) elements.timerDurationSelector.classList.add('hidden');
    }
  }
}

/**
 * Open pretest modal and populate metadata.
 * @param {number|string} textId
 * @param {Object} context - { state, elements, getTextInfo }
 */
export function openPretestModal(textId, context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;
  if (!state || !elements) return;

  const targetId = Number(textId);
  state.pendingTextId = targetId;

  if (typeof history !== 'undefined' && history.pushState) {
    history.pushState({ modal: 'pretest', textId: targetId }, '', '#pretest');
  }

  let textInfo = null;
  if (typeof context.getTextInfo === 'function') {
    textInfo = context.getTextInfo(targetId);
  } else if (typeof window !== 'undefined' && Array.isArray(window.cachedCatalogTexts)) {
    textInfo = window.cachedCatalogTexts.find(t => String(t.id) === String(targetId));
  }

  const recMin = textInfo ? textInfo.recommended_time_min : 3;
  if (textInfo && elements.modalTextTitle) {
    elements.modalTextTitle.textContent = textInfo.title;
    if (elements.modalTimeEstimate) elements.modalTimeEstimate.textContent = recMin;
  } else if (elements.modalTextTitle) {
    elements.modalTextTitle.textContent = t('pretest.textTitle');
    if (elements.modalTimeEstimate) elements.modalTimeEstimate.textContent = recMin;
  }

  const cfg = state.pretestConfig || {};
  if (elements.pretestToggleFurigana) {
    elements.pretestToggleFurigana.checked = cfg.showFurigana !== false;
  }
  if (elements.pretestToggleHints) {
    elements.pretestToggleHints.checked = cfg.showHintsAndAnalysis !== false;
  }
  if (elements.pretestToggleTimer) {
    elements.pretestToggleTimer.checked = Boolean(cfg.enableTimer);
  }
  if (elements.modalTimerMinutes) {
    elements.modalTimerMinutes.textContent = cfg.timerMinutes || recMin;
  }

  updateModalSettingTags(elements);
  if (elements.modalBody) elements.modalBody.scrollTop = 0;
  if (elements.pretestModalBackdrop) elements.pretestModalBackdrop.classList.remove('hidden');
}

/**
 * Close pretest modal.
 * @param {Object} context - { state, elements }
 */
export function closePretestModal(context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;

  if (elements && elements.pretestModalBackdrop) {
    elements.pretestModalBackdrop.classList.add('hidden');
  }
  if (state) {
    state.pendingTextId = null;
  }
}

/**
 * Confirm pretest settings, save them and start exercise.
 * @param {Object} context - { state, elements, onStart }
 */
export function confirmPretestSettingsAndStart(context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;
  if (!state || !elements) return;

  const showFurigana = elements.pretestToggleFurigana ? elements.pretestToggleFurigana.checked : true;
  const showHints = elements.pretestToggleHints ? elements.pretestToggleHints.checked : true;
  const enableTimer = elements.pretestToggleTimer ? elements.pretestToggleTimer.checked : false;
  const timerMins = elements.modalTimerMinutes ? parseInt(elements.modalTimerMinutes.textContent, 10) : 3;

  state.pretestConfig = state.pretestConfig || {};
  state.pretestConfig.showFurigana = showFurigana;
  state.pretestConfig.showHintsAndAnalysis = showHints;
  state.pretestConfig.enableTimer = enableTimer;
  state.pretestConfig.timerMinutes = timerMins;
  saveStoredConfig(state.pretestConfig);

  const textId = state.pendingTextId;
  closePretestModal(context);

  if (textId) {
    if (typeof context.onStart === 'function') {
      context.onStart(textId);
    } else if (typeof window !== 'undefined' && typeof window.startExercise === 'function') {
      window.startExercise(textId);
    }
  }
}
