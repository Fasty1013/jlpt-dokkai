/**
 * JLPT Dokkai Master - Application Action Layer (Step 6e-3)
 * Thin adapters that bind the central store/elements into feature modules,
 * plus main-tab navigation and in-progress session recovery.
 * Ported 1:1 from the former classic script static/app.js; behaviour is unchanged.
 * Kept in one module on purpose: returnToCatalog <-> startExercise reference each
 * other, and the dependency graph must stay acyclic.
 */

import { state } from '../state/store.js';
import { elements } from '../state/elements.js';
import { escapeHtml, getUserId, formatTime } from '../utils/index.js';
import * as Timer from '../features/timer/index.js';
import * as Settings from '../features/settings/index.js';
import * as Stream from '../features/stream/index.js';
import * as Solved from '../features/solved/index.js';
import * as Pretest from '../features/pretest/index.js';
import * as Exercise from '../features/exercise/index.js';
import * as Analysis from '../features/analysis/index.js';
import * as Speech from '../features/speech/index.js';
import * as Notebook from '../features/notebook/index.js';
import * as Dictionary from '../features/dictionary/index.js';
import { fetchAndRenderDrafts } from '../features/pdf_import/index.js';

// ============================================================================
// Timer
// ============================================================================

export function stopTimer() {
  Timer.stopTimer(state.timer);
}

export function startUntimedMode() {
  Timer.startUntimedMode(state.timer, elements);
}

export function startCountdownTimer(minutes) {
  Timer.startCountdownTimer(minutes, state.timer, elements);
}

export function toggleTimerPause() {
  Timer.toggleTimerPause(state.timer, elements);
}

export function addTimerMinute() {
  Timer.addTimerMinute(state.timer, elements);
}

export function dismissTimer() {
  Timer.dismissTimer(state.timer, elements);
}

export function enableTimerAtRuntime() {
  const recMin = (state.activeText && state.activeText.recommended_time_min) ? state.activeText.recommended_time_min : 3;
  Timer.enableTimerAtRuntime(recMin, state.timer, elements);
}

// ============================================================================
// Reader customization
// ============================================================================

export function setReaderFont(typeface) {
  Settings.setReaderFont(typeface, state.settings, elements);
}

export function adjustFontSize(delta) {
  return Settings.adjustFontSize(delta, state.settings, elements);
}

// ============================================================================
// Continuous stream (slots + solved archive)
// ============================================================================

let cachedCatalogTexts = [];

export async function fetchAndRenderCatalog() {
  return fetchAndRenderStream();
}

export async function fetchAndRenderStream() {
  await Promise.all([
    fetchAndRenderSlots(),
    fetchAndRenderSolvedTasks()
  ]);
}

export async function fetchAndRenderSlots(isExplicitRefresh = false) {
  await Stream.fetchAndRenderSlots(isExplicitRefresh, { state, elements, getUserId });
  // stream_slots.js publishes the latest slot texts on window.cachedCatalogTexts.
  cachedCatalogTexts = window.cachedCatalogTexts || [];
}

export async function fetchAndRenderSolvedTasks() {
  await Solved.fetchAndRenderSolvedTasks({ state, elements, getUserId });
}

export async function reviewSolvedTask(textId) {
  await Solved.reviewSolvedTask(textId, { state, getUserId, onRenderAnalysis: renderAnalysisView });
}

export async function retrySolvedTask(textId) {
  await Solved.retrySolvedTask(textId, { state, getUserId, onOpenPretest: openPretestModal });
}

export function handleSlotReplacement(solvedTextId, replacement) {
  Stream.handleSlotReplacement(solvedTextId, replacement, fetchAndRenderSlots);
}

export function openReportModal(textId, title) {
  Solved.openReportModal(textId, title, { state, elements });
}

export function closeReportModal() {
  Solved.closeReportModal({ state, elements });
}

export async function submitReportDefect() {
  await Solved.submitReportDefect({ state, elements, getUserId, onRefreshSlots: fetchAndRenderSlots });
}

export function switchMobileStreamCol(col) {
  Stream.switchMobileStreamCol(col, elements);
}

// ============================================================================
// Pre-test settings modal
// ============================================================================

export function openPretestModal(textId) {
  Pretest.openPretestModal(textId, {
    state,
    elements,
    getTextInfo: id => cachedCatalogTexts.find(t => String(t.id) === String(id))
  });
}

export function closePretestModal() {
  Pretest.closePretestModal({ state, elements });
}

export function updateModalSettingTags() {
  Pretest.updateModalSettingTags(elements);
}

export function confirmPretestSettingsAndStart() {
  Pretest.confirmPretestSettingsAndStart({ state, elements, onStart: startExercise });
}

// ============================================================================
// Exercise (reading mode & step-by-step wizard)
// ============================================================================

export async function startExercise(textId) {
  return Exercise.startExercise(textId, {
    state,
    elements,
    startCountdownTimer,
    startUntimedMode,
    returnToCatalog
  });
}

export function renderWizard() {
  return Exercise.renderWizard(state, elements);
}

export function saveCurrentActiveSession() {
  return Exercise.saveCurrentActiveSession(state);
}

export function handleOptionSelect(questionId, optionId) {
  return Exercise.handleOptionSelect(questionId, optionId, state, elements);
}

export function wizardGoNext() {
  return Exercise.wizardGoNext(state, elements);
}

export function wizardGoPrev() {
  return Exercise.wizardGoPrev(state, elements, returnToCatalog);
}

// ============================================================================
// Submission & analysis
// ============================================================================

export async function submitAnswers() {
  return Analysis.submitAnswers({
    state,
    elements,
    handleSlotReplacement,
    fetchAndRenderSlots,
    fetchAndRenderSolvedTasks,
    stopTimer,
    getUserId,
    renderWizard
  });
}

export function renderAnalysisView(data) {
  return Analysis.renderAnalysisView(data, state, elements);
}

export function switchAnalysisTab(idx) {
  return Analysis.switchAnalysisTab(idx, state, elements);
}

export function toggleFurigana() {
  return Analysis.toggleFurigana(state, elements);
}

export function toggleEvidence() {
  return Analysis.toggleEvidence(state, elements);
}

export function locateEvidenceInText(spanId) {
  return Analysis.locateEvidenceInText(spanId, state, elements);
}

export function toggleSupplementaryDrawer(type) {
  return Analysis.toggleSupplementaryDrawer(type, state, elements);
}

// ============================================================================
// Popup dictionary, speech & personal notebook
// ============================================================================

export function speakJapanese(text) {
  return Speech.speakJapanese(text);
}

export function getSavedWords() {
  return Notebook.getSavedWords(state);
}

export async function saveWordsToStorage(words) {
  return Notebook.saveWordsToStorage(words, state, elements);
}

export function updateNotebookBadge() {
  return Notebook.updateNotebookBadge(elements, state);
}

export async function toggleSaveWord(wordData) {
  return Notebook.toggleSaveWord(wordData, state, elements, renderNotebookWords);
}

export function renderNotebookWords() {
  return Notebook.renderNotebookWords(elements, state);
}

export function clearAllSavedWords() {
  return Notebook.clearAllSavedWords(state, elements, renderNotebookWords);
}

export function showPopupDictionary(wordData, clientX, clientY) {
  return Dictionary.showPopupDictionary(wordData, clientX, clientY, elements, state);
}

export function hidePopupDictionary() {
  return Dictionary.hidePopupDictionary(elements, state);
}

export function lookupAndShowWord(query, clientX, clientY) {
  return Dictionary.lookupAndShowWord(query, clientX, clientY, elements, state);
}

export function togglePopupDictStatus() {
  return Dictionary.togglePopupDictStatus(elements, state);
}

// ============================================================================
// Main tab switching & navigation
// ============================================================================

export function switchMainTab(tabName, pushState = true) {
  state.activeTab = tabName;

  if (tabName === 'notebook') {
    stopTimer();
    state.currentView = 'notebook';
    elements.catalogView.classList.add('hidden');
    elements.exerciseView.classList.add('hidden');
    if (elements.importView) elements.importView.classList.add('hidden');
    elements.exerciseHeaderControls.classList.add('hidden');
    elements.supplementaryDrawer.classList.add('hidden');
    elements.hardcoreNotice.classList.add('hidden');
    elements.notebookView.classList.remove('hidden');

    if (elements.btnTabCatalog) elements.btnTabCatalog.classList.remove('active');
    if (elements.btnTabNotebook) elements.btnTabNotebook.classList.add('active');
    if (elements.btnTabImport) elements.btnTabImport.classList.remove('active');

    if (pushState) {
      history.pushState({ view: 'notebook' }, '', '#notebook');
    }
    renderNotebookWords();
  } else if (tabName === 'import') {
    stopTimer();
    state.currentView = 'import';
    elements.catalogView.classList.add('hidden');
    elements.exerciseView.classList.add('hidden');
    elements.notebookView.classList.add('hidden');
    elements.exerciseHeaderControls.classList.add('hidden');
    elements.supplementaryDrawer.classList.add('hidden');
    elements.hardcoreNotice.classList.add('hidden');
    if (elements.importView) elements.importView.classList.remove('hidden');

    if (elements.btnTabCatalog) elements.btnTabCatalog.classList.remove('active');
    if (elements.btnTabNotebook) elements.btnTabNotebook.classList.remove('active');
    if (elements.btnTabImport) elements.btnTabImport.classList.add('active');

    if (pushState) {
      history.pushState({ view: 'import' }, '', '#import');
    }
    fetchAndRenderDrafts();
  } else {
    returnToCatalog(pushState);
  }
}

export function returnToCatalog(pushState = true) {
  stopTimer();
  state.currentView = 'catalog';
  state.activeTab = 'catalog';
  state.activeText = null;
  state.userAnswers = {};
  state.currentQuestionIndex = 0;
  state.isRetryMode = false;

  elements.exerciseView.classList.add('hidden');
  elements.exerciseHeaderControls.classList.add('hidden');
  elements.notebookView.classList.add('hidden');
  if (elements.importView) elements.importView.classList.add('hidden');
  elements.catalogView.classList.remove('hidden');
  elements.supplementaryDrawer.classList.add('hidden');
  elements.hardcoreNotice.classList.add('hidden');

  if (elements.btnTabCatalog) elements.btnTabCatalog.classList.add('active');
  if (elements.btnTabNotebook) elements.btnTabNotebook.classList.remove('active');
  if (elements.btnTabImport) elements.btnTabImport.classList.remove('active');

  closePretestModal();
  closeReportModal();

  if (pushState) {
    history.pushState({ view: 'catalog' }, '', window.location.pathname);
  }

  fetchAndRenderCatalog();
  checkAndPromptActiveSession();
}

// ============================================================================
// In-progress session recovery
// ============================================================================

export async function checkAndPromptActiveSession() {
  if (!window.DokkaiStorage) return;
  try {
    const session = await window.DokkaiStorage.getActiveSession();
    if (session && session.textId && session.title) {
      state.activeSession = session;
      if (elements.unfinishedTestBanner) {
        if (elements.unfinishedTaskTitle) {
          elements.unfinishedTaskTitle.textContent = `Продолжить тест «${escapeHtml(session.title)}»?`;
        }
        if (elements.unfinishedTaskMeta) {
          const qNum = (session.currentQuestionIndex || 0) + 1;
          elements.unfinishedTaskMeta.textContent = `Вопрос ${qNum} • ${session.level || 'N5'}`;
        }
        elements.unfinishedTestBanner.classList.remove('hidden');
      }
    }
  } catch (e) {
    console.warn('[Dokkai] Active session check error:', e);
  }
}

export async function resumeActiveExercise(session) {
  if (!session || !session.textId) return;
  if (elements.unfinishedTestBanner) {
    elements.unfinishedTestBanner.classList.add('hidden');
  }
  try {
    await startExercise(session.textId);
    state.userAnswers = session.userAnswers || {};
    state.currentQuestionIndex = session.currentQuestionIndex || 0;
    if (session.timer && session.timer.enabled) {
      state.timer.enabled = true;
      state.timer.totalSeconds = session.timer.totalSeconds || 180;
      state.timer.remainingSeconds = session.timer.remainingSeconds || 180;
      state.timer.secondsSpent = session.timer.secondsSpent || 0;
      if (elements.timerBox) elements.timerBox.classList.remove('hidden');
      if (elements.timerDisplay) elements.timerDisplay.textContent = formatTime(state.timer.remainingSeconds);
      if (!state.timer.intervalId) {
        startCountdownTimer(Math.ceil(state.timer.remainingSeconds / 60));
      }
    }
    renderWizard();
  } catch (err) {
    console.error('Failed to resume exercise', err);
    alert('Не удалось восстановить незавершённое задание.');
  }
}
