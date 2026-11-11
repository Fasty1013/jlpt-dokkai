/**
 * JLPT Dokkai Master - Exercise Reading View Setup
 * Initializes text details, sets up split reading pane, furigana, and launches wizard.
 */

import { t } from '../../i18n/index.js';
import { fetchTextDetail } from '../../api/texts.js';
import { getCategoryName } from '../../constants/labels.js';
import { renderWizard, saveCurrentActiveSession } from './wizard.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * Fetch text details and start reading exercise mode.
 * @param {number} textId
 * @param {Object} [options]
 */
export async function startExercise(textId, options = {}) {
  const s = options.state || storeState;
  const els = options.elements || domElements;
  if (!s) return;

  try {
    let textData;
    if (options.api && options.api.fetchTextDetail) {
      textData = await options.api.fetchTextDetail(textId);
    } else if (typeof window !== 'undefined' && window.DokkaiApi && window.DokkaiApi.fetchTextDetail) {
      textData = await window.DokkaiApi.fetchTextDetail(textId);
    } else {
      textData = await fetchTextDetail(textId);
    }

    s.activeText = textData;
    s.userAnswers = {};
    s.currentQuestionIndex = 0;
    s.currentView = 'exercise';

    // History state for browser/mobile Back button
    if (typeof history !== 'undefined' && history.pushState) {
      history.pushState({ view: 'exercise', textId: textId }, '', '#exercise');
    }

    // Switch Views
    if (els.catalogView) els.catalogView.classList.add('hidden');
    if (els.exerciseView) els.exerciseView.classList.remove('hidden');
    if (els.exerciseHeaderControls) els.exerciseHeaderControls.classList.remove('hidden');
    if (els.analysisBanner) els.analysisBanner.classList.add('hidden');
    if (els.analysisQAContainer) els.analysisQAContainer.classList.add('hidden');
    if (els.supplementaryDrawer) els.supplementaryDrawer.classList.add('hidden');

    // Show Wizard UI
    if (els.wizardHeader) els.wizardHeader.classList.remove('hidden');
    if (els.wizardCardArea) els.wizardCardArea.classList.remove('hidden');
    if (els.wizardNavBar) els.wizardNavBar.classList.remove('hidden');

    // Header tags
    if (els.headerLevelTag) {
      els.headerLevelTag.textContent = textData.level;
      els.headerLevelTag.setAttribute('data-lvl', textData.level);
    }
    if (els.headerCategoryTag) {
      els.headerCategoryTag.textContent = getCategoryName(textData.category) || textData.category;
    }

    if (els.headerExamBadge) {
      if (textData.source_exam) {
        els.headerExamBadge.textContent = textData.source_exam;
        els.headerExamBadge.classList.remove('hidden');
      } else {
        els.headerExamBadge.classList.add('hidden');
      }
    }

    // Initialize Timer Mode (Countdown if chosen, otherwise untimed free reading)
    const pretestConfig = s.pretestConfig || {};
    if (pretestConfig.enableTimer) {
      const chosenMinutes = pretestConfig.timerMinutes || textData.recommended_time_min;
      if (typeof options.startCountdownTimer === 'function') {
        options.startCountdownTimer(chosenMinutes);
      } else if (typeof window !== 'undefined' && typeof window.startCountdownTimer === 'function') {
        window.startCountdownTimer(chosenMinutes);
      } else if (typeof window !== 'undefined' && window.DokkaiTimer && window.DokkaiTimer.startCountdownTimer) {
        window.DokkaiTimer.startCountdownTimer(chosenMinutes);
      }
    } else {
      if (typeof options.startUntimedMode === 'function') {
        options.startUntimedMode();
      } else if (typeof window !== 'undefined' && typeof window.startUntimedMode === 'function') {
        window.startUntimedMode();
      } else if (typeof window !== 'undefined' && window.DokkaiTimer && window.DokkaiTimer.startUntimedMode) {
        window.DokkaiTimer.startUntimedMode();
      }
    }

    // Passage Left Pane
    if (els.passageTitle) els.passageTitle.textContent = textData.title;
    if (els.passageLevel) {
      els.passageLevel.textContent = textData.level;
      els.passageLevel.setAttribute('data-lvl', textData.level);
    }
    if (els.passageCategory) {
      els.passageCategory.textContent = getCategoryName(textData.category) || textData.category;
    }

    if (els.passageExamBadge) {
      if (textData.source_exam) {
        els.passageExamBadge.textContent = textData.source_exam;
        els.passageExamBadge.classList.remove('hidden');
      } else {
        els.passageExamBadge.classList.add('hidden');
      }
    }

    if (els.passageTime) {
      els.passageTime.textContent = t('exercise.minutes', { n: textData.recommended_time_min });
    }

    // Render Japanese HTML
    if (els.passageContent) {
      els.passageContent.innerHTML = textData.content_html;
      const fontSize = (s.settings && s.settings.fontSizePx) ? s.settings.fontSizePx : 20;
      els.passageContent.style.fontSize = `${fontSize}px`;

      // Apply Furigana setting
      if (pretestConfig.showFurigana) {
        if (s.settings) s.settings.furiganaVisible = true;
        els.passageContent.classList.remove('hide-furigana');
        if (els.furiganaStatus) els.furiganaStatus.textContent = t('common.on');
        if (els.btnToggleFurigana) els.btnToggleFurigana.classList.add('active');
      } else {
        if (s.settings) s.settings.furiganaVisible = false;
        els.passageContent.classList.add('hide-furigana');
        if (els.furiganaStatus) els.furiganaStatus.textContent = t('common.off');
        if (els.btnToggleFurigana) els.btnToggleFurigana.classList.remove('active');
      }

      els.passageContent.classList.remove('show-evidence');
    }

    // Hardcore Mode Notice
    if (els.hardcoreNotice) {
      if (!pretestConfig.showHintsAndAnalysis) {
        els.hardcoreNotice.classList.remove('hidden');
      } else {
        els.hardcoreNotice.classList.add('hidden');
      }
    }

    // Render Wizard dots & active question
    renderWizard(s, els);
    saveCurrentActiveSession(s);
    if (els.unfinishedTestBanner) {
      els.unfinishedTestBanner.classList.add('hidden');
    }

  } catch (err) {
    console.error('Ошибка инициализации упражнения:', err);
    throw err;
  }
}
