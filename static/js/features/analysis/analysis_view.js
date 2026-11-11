/**
 * JLPT Dokkai Master - Analysis View & Tabbed Post-Submit Flow
 * Renders score banner, tabbed question analysis, evidence locator, and supplementary study drawer.
 */

import { t } from '../../i18n/index.js';
import { formatTime } from '../../utils/time.js';
import { escapeHtml } from '../../utils/dom.js';
import { getTrapLabel } from '../../constants/labels.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * Render complete post-submission analysis view.
 * @param {Object} data - Verified submission result with answers and explanations
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function renderAnalysisView(data, state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!s || !els || !data) return;

  // Hide Wizard Controls
  if (els.wizardHeader) els.wizardHeader.classList.add('hidden');
  if (els.wizardCardArea) els.wizardCardArea.classList.add('hidden');
  if (els.wizardNavBar) els.wizardNavBar.classList.add('hidden');

  // Show Analysis Banner & Tabbed Area
  if (els.analysisBanner) els.analysisBanner.classList.remove('hidden');
  if (els.analysisQAContainer) els.analysisQAContainer.classList.remove('hidden');

  if (els.scoreText) {
    els.scoreText.textContent = `${data.correct_count} / ${data.total_questions}`;
  }
  if (els.scorePercent) {
    els.scorePercent.textContent = t('analysis.scorePercent', { pct: data.score_percent });
  }

  if (els.bannerResultTitle) {
    if (data.score_percent === 100) {
      els.bannerResultTitle.textContent = t('analysis.titlePerfect');
    } else if (data.score_percent >= 50) {
      els.bannerResultTitle.textContent = t('analysis.titleGood');
    } else {
      els.bannerResultTitle.textContent = t('analysis.titlePractice');
    }
  }

  const spentSeconds = (typeof data.time_spent_sec === 'number')
    ? data.time_spent_sec
    : ((s.timer && typeof s.timer.secondsSpent === 'number') ? s.timer.secondsSpent : 0);
  const spentTimeFormatted = formatTime(spentSeconds);
  if (els.bannerResultMeta) {
    if (s.timer && s.timer.enabled) {
      const targetFormatted = formatTime(s.timer.totalSeconds);
      const inLimit = spentSeconds <= s.timer.totalSeconds;
      els.bannerResultMeta.textContent = t('analysis.metaTimed', { spent: spentTimeFormatted, target: targetFormatted, status: inLimit ? t('analysis.inLimit') : t('analysis.overLimit') });
    } else {
      els.bannerResultMeta.textContent = t('analysis.metaFree', { spent: spentTimeFormatted });
    }
  }

  const allowHints = (s.pretestConfig && typeof s.pretestConfig.showHintsAndAnalysis === 'boolean')
    ? s.pretestConfig.showHintsAndAnalysis
    : true;

  if (allowHints) {
    if (s.settings) s.settings.evidenceVisible = true;
    if (els.passageContent) els.passageContent.classList.add('show-evidence');
    if (els.evidenceStatus) els.evidenceStatus.textContent = t('common.on');
    if (els.btnToggleEvidence) els.btnToggleEvidence.classList.remove('hidden');
    if (els.btnToggleTranslation) els.btnToggleTranslation.classList.remove('hidden');
    if (els.btnToggleVocab) els.btnToggleVocab.classList.remove('hidden');
    if (els.vocabCountBadge) els.vocabCountBadge.textContent = data.vocabulary ? data.vocabulary.length : 0;

    // Prepare Russian Translation & Vocabulary
    if (els.translationText) {
      els.translationText.textContent = data.translation_ru || t('analysis.translationUnavailable');
    }
    if (els.vocabList) {
      els.vocabList.innerHTML = (data.vocabulary && data.vocabulary.length > 0)
        ? data.vocabulary.map(v => `
            <div class="vocab-row">
              <span class="vocab-word" lang="ja">${escapeHtml(v.word)}</span>
              <span class="vocab-furigana">[${escapeHtml(v.furigana)}]</span>
              <span class="vocab-trans">${escapeHtml(v.translation)}</span>
            </div>
          `).join('')
        : `<p style="color: var(--sumi-500);">${t('analysis.vocabEmpty')}</p>`;
    }
  } else {
    if (s.settings) s.settings.evidenceVisible = false;
    if (els.passageContent) els.passageContent.classList.remove('show-evidence');
    if (els.btnToggleEvidence) els.btnToggleEvidence.classList.add('hidden');
    if (els.btnToggleTranslation) els.btnToggleTranslation.classList.add('hidden');
    if (els.btnToggleVocab) els.btnToggleVocab.classList.add('hidden');
    if (els.supplementaryDrawer) els.supplementaryDrawer.classList.add('hidden');
  }

  // Render Analysis Tabs
  renderAnalysisTabs(s, els);
}

/**
 * Render tab buttons for each question in analysis mode.
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function renderAnalysisTabs(state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!s || !s.activeText || !s.activeText.questions || !els.analysisTabs) return;

  const questions = s.activeText.questions;
  const activeIdx = s.analysisActiveTabIdx || 0;

  els.analysisTabs.innerHTML = questions.map((q, idx) => {
    const isActive = idx === activeIdx;
    const isCorrect = q.is_user_correct;
    return `
      <button type="button" class="analysis-tab-btn ${isActive ? 'active' : ''}" data-action="switch-analysis-tab" data-tab-index="${idx}">
        <span class="analysis-tab-status ${isCorrect ? 'correct' : 'wrong'}"></span>
        ${t('analysis.tabQuestion', { n: q.question_number })}
      </button>
    `;
  }).join('');

  renderAnalysisActiveCard(questions[activeIdx], s, els);
}

/**
 * Switch active question tab.
 * @param {number} idx
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function switchAnalysisTab(idx, state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!s) return;
  s.analysisActiveTabIdx = idx;
  renderAnalysisTabs(s, els);
}

/**
 * Render card for active question in analysis mode.
 * @param {Object} q - Question analysis object
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function renderAnalysisActiveCard(q, state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!q || !els.analysisActiveCard) return;

  const allowHints = (s && s.pretestConfig && typeof s.pretestConfig.showHintsAndAnalysis === 'boolean')
    ? s.pretestConfig.showHintsAndAnalysis
    : true;

  els.analysisActiveCard.innerHTML = `
    <div class="question-card" id="card-q-${q.id}">
      <div class="question-top">
        <span class="question-num-badge">№${q.question_number}</span>
        <p class="question-prompt" lang="ja">${q.question_text}</p>
        <span class="option-status-badge ${q.is_user_correct ? 'badge-correct' : 'badge-user-wrong'}">
          ${q.is_user_correct ? t('analysis.correct') : t('analysis.wrong')}
        </span>
      </div>

      <div class="options-group">
        ${(q.options || []).map(opt => {
          let stateClass = '';
          let badgeHtml = '';
          let explanationBoxHtml = '';

          if (opt.is_correct) {
            stateClass = 'state-correct';
            badgeHtml = `<span class="option-status-badge badge-correct">${t('analysis.optCorrect')}</span>`;
          } else if (opt.was_selected) {
            stateClass = 'state-wrong-selected';
            badgeHtml = `<span class="option-status-badge badge-user-wrong">${t('analysis.optYours')}</span>`;
          }

          if (allowHints && opt.option_explanation) {
            const expClass = opt.is_correct ? 'correct-exp' : 'wrong-exp';
            const trapBadge = (!opt.is_correct && opt.trap_type && getTrapLabel(opt.trap_type))
              ? `<div class="trap-type-pill">⚠️ ${escapeHtml(getTrapLabel(opt.trap_type))}</div>`
              : '';
            explanationBoxHtml = `
              <div class="option-explanation-box ${expClass}">
                ${trapBadge}
                <div>${opt.option_explanation}</div>
              </div>
            `;
          }

          return `
            <div class="option-item ${stateClass}">
              <div class="option-label">
                <input 
                  type="radio" 
                  disabled 
                  ${opt.was_selected ? 'checked' : ''} 
                  class="option-radio"
                >
                <span class="option-text" lang="ja">${opt.option_number}. ${opt.option_text}</span>
                ${badgeHtml}
              </div>
              ${explanationBoxHtml}
            </div>
          `;
        }).join('')}
      </div>

      <!-- General question analysis & Evidence locator -->
      ${allowHints ? `
        <div class="question-general-explanation">
          <strong>${t('analysis.explTitle')}</strong>
          <p style="margin-top: 0.35rem;">${q.general_explanation || ''}</p>
          ${q.evidence_span_id ? `
            <button type="button" class="btn-locate-evidence" data-action="locate-evidence" data-span-id="${escapeHtml(q.evidence_span_id)}">
              ${t('analysis.locateEvidence')}
            </button>
          ` : ''}
        </div>
      ` : `
        <div class="question-general-explanation" style="background: #fafaf9; border-left-color: var(--sumi-400); color: var(--sumi-500); font-style: italic;">
          ${t('analysis.hintsHidden')}
        </div>
      `}
    </div>
  `;

  // Automatically highlight the evidence for this question if hints are enabled
  if (allowHints && q.evidence_span_id) {
    locateEvidenceInText(q.evidence_span_id, s, els);
  }
}

/**
 * Toggle furigana visibility on passage content.
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function toggleFurigana(state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!s || !els) return;

  if (!s.settings) s.settings = {};
  s.settings.furiganaVisible = !s.settings.furiganaVisible;

  if (s.settings.furiganaVisible) {
    if (els.passageContent) els.passageContent.classList.remove('hide-furigana');
    if (els.furiganaStatus) els.furiganaStatus.textContent = t('common.on');
    if (els.btnToggleFurigana) els.btnToggleFurigana.classList.add('active');
  } else {
    if (els.passageContent) els.passageContent.classList.add('hide-furigana');
    if (els.furiganaStatus) els.furiganaStatus.textContent = t('common.off');
    if (els.btnToggleFurigana) els.btnToggleFurigana.classList.remove('active');
  }
}

/**
 * Toggle evidence highlighting visibility.
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function toggleEvidence(state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!s || !els) return;
  if (s.pretestConfig && !s.pretestConfig.showHintsAndAnalysis) return;

  if (!s.settings) s.settings = {};
  s.settings.evidenceVisible = !s.settings.evidenceVisible;

  if (s.settings.evidenceVisible) {
    if (els.passageContent) els.passageContent.classList.add('show-evidence');
    if (els.evidenceStatus) els.evidenceStatus.textContent = t('common.on');
    if (els.btnToggleEvidence) els.btnToggleEvidence.classList.add('active');
  } else {
    if (els.passageContent) els.passageContent.classList.remove('show-evidence');
    if (els.evidenceStatus) els.evidenceStatus.textContent = t('common.off');
    if (els.btnToggleEvidence) els.btnToggleEvidence.classList.remove('active');
  }
}

/**
 * Scroll and highlight specific evidence span in reading pane.
 * @param {string} spanId
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function locateEvidenceInText(spanId, state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (s && s.pretestConfig && !s.pretestConfig.showHintsAndAnalysis) return;

  if (s && (!s.settings || !s.settings.evidenceVisible)) {
    toggleEvidence(s, els);
  }

  document.querySelectorAll('.evidence-active-pulse').forEach(el => {
    el.classList.remove('evidence-active-pulse');
  });

  const targetEl = document.getElementById(spanId);
  if (targetEl) {
    targetEl.classList.add('evidence-active-pulse');
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

/**
 * Toggle side/bottom supplementary drawer for translation or vocabulary.
 * @param {string} [type] - 'translation' | 'vocab'
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function toggleSupplementaryDrawer(type, state = storeState, elements = domElements) {
  const s = state;
  const els = elements || {};
  if (!els || !els.supplementaryDrawer) return;
  if (s && s.pretestConfig && !s.pretestConfig.showHintsAndAnalysis) return;

  const isHidden = els.supplementaryDrawer.classList.contains('hidden');
  const transSec = document.getElementById('drawer-translation-section');
  const vocabSec = document.getElementById('drawer-vocab-section');

  if (isHidden) {
    els.supplementaryDrawer.classList.remove('hidden');
    if (type === 'translation' && transSec) {
      transSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if (type === 'vocab' && vocabSec) {
      vocabSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } else {
    els.supplementaryDrawer.classList.add('hidden');
  }
}

