/**
 * JLPT Dokkai Master - re-render language-dependent dynamic views after a language switch.
 * Static markup is handled by data-i18n in i18n/index.js; this module redraws what JS built with t().
 * Nothing here touches persisted data: only the DOM is redrawn from state that is already in memory
 * (solved archive and PDF drafts are re-requested, because they are not cached client-side).
 */
import { onLangChange, t } from '../i18n/index.js';
import { state } from '../state/store.js';
import { elements } from '../state/elements.js';
import * as A from './actions.js';
import { updateSyncStatusUI, updateSyncUserUI } from '../features/sync_ui/sync_modal.js';
import { rerenderSlotsFromCache } from '../features/stream/stream_slots.js';
import { renderWizard } from '../features/exercise/wizard.js';
import { renderAnalysisView } from '../features/analysis/analysis_view.js';
import { updateModalSettingTags } from '../features/pretest/pretest_modal.js';
import { getCategoryName } from '../constants/labels.js';
import { fetchAndRenderDrafts } from '../features/pdf_import/index.js';

function onOff(flag) {
  return flag ? t('common.on') : t('common.off');
}

function refreshReaderStatuses() {
  const settings = state.settings || {};
  if (elements.furiganaStatus) elements.furiganaStatus.textContent = onOff(settings.furiganaVisible);
  if (elements.evidenceStatus) elements.evidenceStatus.textContent = onOff(settings.evidenceVisible);
  if (elements.popupDictStatus) elements.popupDictStatus.textContent = onOff(state.popupDictEnabled);
}

function refreshExerciseHeader() {
  const text = state.activeText;
  if (!text) return;
  const category = getCategoryName(text.category) || text.category;
  if (category) {
    if (elements.headerCategoryTag) elements.headerCategoryTag.textContent = category;
    if (elements.passageCategory) elements.passageCategory.textContent = category;
  }
  if (elements.passageTime && text.recommended_time_min !== undefined) {
    elements.passageTime.textContent = t('exercise.minutes', { n: text.recommended_time_min });
  }
}

function safely(label, fn) {
  try {
    const result = fn();
    if (result && typeof result.catch === 'function') result.catch((e) => console.warn(`[Dokkai i18n] ${label}:`, e));
  } catch (e) {
    console.warn(`[Dokkai i18n] ${label}:`, e);
  }
}

export function refreshLocalizedViews() {
  safely('popup', () => A.hidePopupDictionary());
  safely('sync status', () => {
    updateSyncStatusUI();
    updateSyncUserUI(window.DokkaiCloudSync ? window.DokkaiCloudSync.user : null);
  });
  safely('slots', () => rerenderSlotsFromCache());
  safely('solved', () => A.fetchAndRenderSolvedTasks());
  safely('notebook', () => A.renderNotebookWords());
  safely('statuses', refreshReaderStatuses);
  safely('pretest tags', () => {
    if (elements.pretestModalBackdrop && !elements.pretestModalBackdrop.classList.contains('hidden')) {
      updateModalSettingTags(elements);
    }
  });
  if (state.currentView === 'catalog') {
    safely('unfinished banner', () => A.checkAndPromptActiveSession());
  }
  if (state.currentView === 'exercise') {
    safely('exercise header', refreshExerciseHeader);
    safely('wizard', () => renderWizard(state, elements));
  }
  if (state.currentView === 'analysis' && state.activeText && Array.isArray(state.activeText.questions)) {
    safely('exercise header', refreshExerciseHeader);
    safely('analysis', () => renderAnalysisView(state.activeText, state, elements));
  }
  if (state.activeTab === 'import') {
    safely('drafts', () => fetchAndRenderDrafts());
  }
}

export function initLanguageRefresh() {
  // The static "ВКЛ" of the pop-up dictionary toggle is a JS-owned placeholder: localize it from state at start-up.
  safely('popup status', () => {
    if (elements.popupDictStatus) elements.popupDictStatus.textContent = onOff(state.popupDictEnabled);
  });
  onLangChange(refreshLocalizedViews);
}
