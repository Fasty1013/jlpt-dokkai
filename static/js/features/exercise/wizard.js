/**
 * JLPT Dokkai Master - Reading View & Question Wizard Lifecycle Module
 * Step-by-Step Question Wizard navigation, card rendering, and active session persistence.
 */

function resolveState(state) {
  if (state) return state;
  if (typeof window !== 'undefined' && window.state) return window.state;
  return null;
}

function resolveElements(elements) {
  if (elements) return elements;
  if (typeof window !== 'undefined' && window.elements) return window.elements;
  return {};
}

/**
 * Persist active exercise session into DokkaiStorage.
 * @param {Object} [state]
 */
export function saveCurrentActiveSession(state) {
  const s = resolveState(state);
  if (!s || s.currentView !== 'exercise' || !s.activeText) return;

  if (typeof window !== 'undefined' && window.DokkaiStorage && window.DokkaiStorage.saveActiveSession) {
    window.DokkaiStorage.saveActiveSession({
      textId: s.activeText.id,
      title: s.activeText.title,
      level: s.activeText.level,
      currentQuestionIndex: s.currentQuestionIndex,
      userAnswers: s.userAnswers,
      timer: {
        totalSeconds: s.timer ? s.timer.totalSeconds : 0,
        remainingSeconds: s.timer ? s.timer.remainingSeconds : 0,
        secondsSpent: s.timer ? s.timer.secondsSpent : 0,
        enabled: s.timer ? s.timer.enabled : false
      }
    });
  }
}

/**
 * Render single active question card, track dots, and update navigation buttons.
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function renderWizard(state, elements) {
  const s = resolveState(state);
  const els = resolveElements(elements);
  if (!s || !s.activeText || !s.activeText.questions) return;

  const questions = s.activeText.questions;
  const totalQ = questions.length;
  const currentQIdx = s.currentQuestionIndex || 0;
  const currentQ = questions[currentQIdx];

  // Status label & progress
  if (els.wizardStepLabel) {
    els.wizardStepLabel.textContent = `Вопрос ${currentQIdx + 1} из ${totalQ}`;
  }
  if (els.totalQuestionsCount) {
    els.totalQuestionsCount.textContent = totalQ;
  }
  if (els.answeredCount) {
    els.answeredCount.textContent = Object.keys(s.userAnswers || {}).length;
  }

  // Track dots
  if (els.wizardTrack) {
    els.wizardTrack.innerHTML = questions.map((q, idx) => {
      const isAnswered = s.userAnswers && s.userAnswers[q.id] !== undefined;
      const isActive = idx === currentQIdx;
      let dotClass = 'wizard-dot';
      if (isActive) dotClass += ' active';
      else if (isAnswered) dotClass += ' answered';
      return `<span class="${dotClass}" title="Вопрос ${idx + 1}"></span>`;
    }).join('');
  }

  // Render single active question card
  const selectedOptId = s.userAnswers ? s.userAnswers[currentQ.id] : undefined;

  if (els.wizardCardArea) {
    els.wizardCardArea.innerHTML = `
        <div class="question-card" id="card-q-${currentQ.id}">
            <div class="question-top">
                <span class="question-num-badge">№${currentQ.question_number}</span>
                <p class="question-prompt">${currentQ.question_text}</p>
            </div>
            <div class="options-group">
                ${currentQ.options.map(opt => {
      const isChecked = selectedOptId === opt.id;
      return `
                        <div class="option-item ${isChecked ? 'selected' : ''}" id="opt-item-${opt.id}">
                            <label class="option-label" for="radio-opt-${opt.id}">
                                <input 
                                    type="radio" 
                                    id="radio-opt-${opt.id}" 
                                    name="question_${currentQ.id}" 
                                    value="${opt.id}" 
                                    class="option-radio"
                                    ${isChecked ? 'checked' : ''}
                                    data-action="select-option"
                                    data-question-id="${currentQ.id}"
                                    data-option-id="${opt.id}"
                                >
                                <span class="option-text">${opt.option_number}. ${opt.option_text}</span>
                            </label>
                        </div>
                    `;
    }).join('')}
            </div>
        </div>
    `;
  }

  // Navigation buttons state: "Назад" на первом вопросе возвращает на главную
  if (els.btnWizardPrev) {
    els.btnWizardPrev.disabled = false;
    if (currentQIdx === 0) {
      els.btnWizardPrev.textContent = '← На главную';
      els.btnWizardPrev.title = 'Вернуться на главную страницу каталога';
    } else {
      els.btnWizardPrev.textContent = '← Назад';
      els.btnWizardPrev.title = 'Вернуться к предыдущему вопросу';
    }
  }

  const isCurrentAnswered = selectedOptId !== undefined;
  const isLastQuestion = (currentQIdx === totalQ - 1);
  const allAnswered = Object.keys(s.userAnswers || {}).length === totalQ;

  if (els.btnWizardNext && els.btnWizardSubmit) {
    if (isLastQuestion) {
      els.btnWizardNext.classList.add('hidden');
      els.btnWizardSubmit.classList.remove('hidden');
      els.btnWizardSubmit.disabled = !allAnswered;
    } else {
      els.btnWizardNext.classList.remove('hidden');
      els.btnWizardSubmit.classList.add('hidden');
      els.btnWizardNext.disabled = !isCurrentAnswered;
    }
  }
}

/**
 * Handle user selection of a radio option.
 * @param {number} questionId
 * @param {number} optionId
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function handleOptionSelect(questionId, optionId, state, elements) {
  const s = resolveState(state);
  const els = resolveElements(elements);
  if (!s) return;

  if (!s.userAnswers) s.userAnswers = {};
  s.userAnswers[questionId] = optionId;

  // Highlight selected visually
  const card = document.getElementById(`card-q-${questionId}`);
  if (card) {
    card.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
    const optItem = document.getElementById(`opt-item-${optionId}`);
    if (optItem) optItem.classList.add('selected');
  }

  // Refresh Wizard status and next button availability
  renderWizard(s, els);

  // Auto-save active test progress
  saveCurrentActiveSession(s);
}

/**
 * Advance wizard to next question if within bounds.
 * @param {Object} [state]
 * @param {Object} [elements]
 */
export function wizardGoNext(state, elements) {
  const s = resolveState(state);
  const els = resolveElements(elements);
  if (!s || !s.activeText || !s.activeText.questions) return;

  const totalQ = s.activeText.questions.length;
  if (s.currentQuestionIndex < totalQ - 1) {
    s.currentQuestionIndex += 1;
    renderWizard(s, els);
    saveCurrentActiveSession(s);
  }
}

/**
 * Navigate to previous question or return to catalog if at first question.
 * @param {Object} [state]
 * @param {Object} [elements]
 * @param {Function} [onReturnToCatalog]
 */
export function wizardGoPrev(state, elements, onReturnToCatalog) {
  const s = resolveState(state);
  const els = resolveElements(elements);
  if (!s) return;

  if (s.currentQuestionIndex > 0) {
    s.currentQuestionIndex -= 1;
    renderWizard(s, els);
    saveCurrentActiveSession(s);
  } else {
    // Return to catalog on Q1
    if (typeof onReturnToCatalog === 'function') {
      onReturnToCatalog();
    } else if (typeof window !== 'undefined' && typeof window.returnToCatalog === 'function') {
      window.returnToCatalog();
    }
  }
}
