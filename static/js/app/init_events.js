/**
 * JLPT Dokkai Master - Feature Event Wiring (Step 6e-3)
 * Connects every feature's event initializer with the application actions.
 * Ported 1:1 from initEventListeners() of the former static/app.js.
 */

import { state } from '../state/store.js';
import { elements } from '../state/elements.js';
import { initNavigationEvents, initActionDelegation } from '../features/events/index.js';
import { initStreamEvents } from '../features/stream/index.js';
import { initPretestEvents } from '../features/pretest/index.js';
import { initTimerEvents } from '../features/timer/index.js';
import { initReaderSettingsEvents } from '../features/settings/index.js';
import { initExerciseEvents } from '../features/exercise/index.js';
import { initAnalysisEvents } from '../features/analysis/index.js';
import { initDictionaryEvents } from '../features/dictionary/index.js';
import { initNotebookEvents } from '../features/notebook/index.js';
import { initPdfEvents, clearSelectedPdfFile, fetchAndRenderDrafts } from '../features/pdf_import/index.js';
import { initSyncEvents, openSyncModal, closeSyncModal, exportProgressJson } from '../features/sync_ui/index.js';
import { initReportEvents } from '../features/solved/index.js';
import * as A from './actions.js';

export function initEventListeners() {
  initNavigationEvents({
    state,
    elements,
    actions: {
      returnToCatalog: A.returnToCatalog,
      switchMainTab: A.switchMainTab,
      openSyncModal,
      hidePopupDictionary: A.hidePopupDictionary,
      closeNotebookModal: () => {
        // Parity with main: on main, closeNotebookModal() was an undeclared reference that threw ReferenceError.
        // Scheduled for clean fix in Part III (Step 11).
        throw new ReferenceError('closeNotebookModal is not defined');
      },
      closePretestModal: A.closePretestModal,
      closeSyncModal,
      closeReportModal: A.closeReportModal
    }
  });

  initStreamEvents({
    state,
    elements,
    actions: {
      fetchAndRenderStream: A.fetchAndRenderStream,
      fetchAndRenderSlots: A.fetchAndRenderSlots,
      fetchAndRenderSolvedTasks: A.fetchAndRenderSolvedTasks,
      openPretestModal: A.openPretestModal,
      reviewSolvedTask: A.reviewSolvedTask,
      retrySolvedTask: A.retrySolvedTask,
      switchMobileStreamCol: A.switchMobileStreamCol
    }
  });

  initPretestEvents({
    state,
    elements,
    actions: {
      closePretestModal: A.closePretestModal,
      confirmPretestSettingsAndStart: A.confirmPretestSettingsAndStart,
      updateModalSettingTags: A.updateModalSettingTags
    }
  });

  initTimerEvents({
    state,
    elements,
    actions: {
      toggleTimerPause: A.toggleTimerPause,
      addTimerMinute: A.addTimerMinute,
      dismissTimer: A.dismissTimer,
      enableTimerAtRuntime: A.enableTimerAtRuntime
    }
  });

  initReaderSettingsEvents({
    state,
    elements,
    actions: {
      setReaderFont: A.setReaderFont,
      adjustFontSize: A.adjustFontSize,
      togglePopupDictStatus: A.togglePopupDictStatus
    }
  });

  initExerciseEvents({
    state,
    elements,
    actions: {
      wizardGoPrev: A.wizardGoPrev,
      wizardGoNext: A.wizardGoNext,
      submitAnswers: A.submitAnswers,
      handleOptionSelect: A.handleOptionSelect,
      resumeActiveExercise: A.resumeActiveExercise
    }
  });

  initAnalysisEvents({
    state,
    elements,
    actions: {
      toggleFurigana: A.toggleFurigana,
      toggleEvidence: A.toggleEvidence,
      toggleSupplementaryDrawer: A.toggleSupplementaryDrawer,
      switchAnalysisTab: A.switchAnalysisTab,
      locateEvidenceInText: A.locateEvidenceInText
    }
  });

  initDictionaryEvents({
    state,
    elements,
    actions: {
      hidePopupDictionary: A.hidePopupDictionary,
      speakJapanese: A.speakJapanese,
      toggleSaveWord: A.toggleSaveWord,
      lookupAndShowWord: A.lookupAndShowWord
    }
  });

  initNotebookEvents({
    state,
    elements,
    actions: {
      renderNotebookWords: A.renderNotebookWords,
      exportProgressJson,
      clearAllSavedWords: A.clearAllSavedWords,
      speakJapanese: A.speakJapanese,
      getSavedWords: A.getSavedWords,
      saveWordsToStorage: A.saveWordsToStorage
    }
  });

  initPdfEvents({
    state,
    elements,
    actions: {
      clearSelectedPdfFile,
      fetchAndRenderDrafts
    }
  });

  initSyncEvents({
    state,
    elements,
    actions: {
      closeSyncModal,
      exportProgressJson
    }
  });

  initReportEvents({
    state,
    elements,
    actions: {
      openReportModal: A.openReportModal,
      closeReportModal: A.closeReportModal,
      submitReportDefect: A.submitReportDefect
    }
  });

  initActionDelegation();
}
