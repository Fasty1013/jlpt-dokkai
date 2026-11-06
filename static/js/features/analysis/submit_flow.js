/**
 * JLPT Dokkai Master - Exercise Submission Flow
 * Handles question validation, idempotency, server submission, score calculation,
 * local persistence (DokkaiStorage), and handoff to Analysis View.
 */

import { getUserId } from '../../utils/user.js';
import { stopTimer } from '../timer/timer.js';
import { renderWizard } from '../exercise/wizard.js';
import { completeStreamTask } from '../../api/stream.js';
import { renderAnalysisView } from './analysis_view.js';

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
 * Submit answered exercise questions for verification.
 * @param {Object} [options]
 * @returns {Promise<Object>} Stream submission result
 */
export async function submitAnswers(options = {}) {
  const s = resolveState(options.state);
  const els = resolveElements(options.elements);
  if (!s || !s.activeText || !s.activeText.questions) {
    throw new Error('No active exercise session found to submit');
  }

  const totalQuestions = s.activeText.questions.length;
  const answeredCount = Object.keys(s.userAnswers || {}).length;

  if (answeredCount < totalQuestions) {
    if (typeof options.onIncomplete === 'function') {
      options.onIncomplete(answeredCount, totalQuestions);
    } else if (typeof window !== 'undefined' && typeof window.alert === 'function') {
      window.alert('Пожалуйста, ответьте на все вопросы перед отправкой!');
    }
    return null;
  }

  // Stop timer and record elapsed seconds
  if (typeof options.stopTimer === 'function') {
    options.stopTimer();
  } else if (typeof window !== 'undefined' && typeof window.stopTimer === 'function') {
    window.stopTimer();
  } else {
    stopTimer(s, els);
  }

  const timeSpent = (s.timer && typeof s.timer.secondsSpent === 'number') ? s.timer.secondsSpent : 0;

  const answersPayload = Object.entries(s.userAnswers).map(([qId, optId]) => ({
    question_id: parseInt(qId, 10),
    selected_option_id: parseInt(optId, 10)
  }));

  try {
    if (els.btnWizardSubmit) {
      els.btnWizardSubmit.disabled = true;
      els.btnWizardSubmit.textContent = 'Проверка ответов...';
    }

    s.currentSubmitIdempotencyKey = s.currentSubmitIdempotencyKey || ('idem-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9));
    const idempotencyKey = s.currentSubmitIdempotencyKey;
    const solvedWhen = (s.streamProfile && s.streamProfile.solvedWhen) || 'all_questions_answered';

    const userId = (typeof options.getUserId === 'function') ? options.getUserId() : getUserId();

    const payload = {
      user_id: userId,
      text_id: s.activeText.id,
      answers: answersPayload,
      idempotency_key: idempotencyKey,
      mode: s.isRetryMode ? 'retry' : 'first',
      solved_when: solvedWhen,
      all_correct_max_attempts: 2
    };

    let streamResult;
    if (options.api && typeof options.api.completeStreamTask === 'function') {
      streamResult = await options.api.completeStreamTask(payload);
    } else if (typeof window !== 'undefined' && window.DokkaiApi && typeof window.DokkaiApi.completeStreamTask === 'function') {
      streamResult = await window.DokkaiApi.completeStreamTask(payload);
    } else {
      streamResult = await completeStreamTask(payload);
    }

    // Если режим "all_correct" и есть ошибки (задание еще не решено)
    if (!streamResult.is_solved) {
      const errCount = streamResult.error_question_ids ? streamResult.error_question_ids.length : 1;
      const warnMsg = `Внимательно перепроверьте свои ответы! В ${errCount} вопросах допущены ошибки. Попытка ${streamResult.attempts_used} из ${streamResult.attempts_max}.`;

      if (typeof options.onRetryWarning === 'function') {
        options.onRetryWarning(warnMsg, streamResult);
      } else if (typeof window !== 'undefined' && typeof window.alert === 'function') {
        window.alert(warnMsg);
      }

      // Reset choices only on erroneous questions without leaking correct answers
      if (streamResult.error_question_ids && Array.isArray(streamResult.error_question_ids)) {
        streamResult.error_question_ids.forEach(qid => {
          delete s.userAnswers[qid];
        });
      }
      if (els.btnWizardSubmit) {
        els.btnWizardSubmit.disabled = false;
        els.btnWizardSubmit.textContent = 'Завершить и проверить ответы ✓';
      }
      s.currentSubmitIdempotencyKey = null; // Reset key for next trial

      // Re-render wizard for error correction
      if (typeof options.renderWizard === 'function') {
        options.renderWizard(s, els);
      } else if (typeof window !== 'undefined' && typeof window.renderWizard === 'function') {
        window.renderWizard();
      } else {
        renderWizard(s, els);
      }
      return streamResult;
    }

    // Submission succeeded, clear key
    s.currentSubmitIdempotencyKey = null;
    const analysisData = streamResult;
    s.activeText = analysisData;
    s.currentView = 'analysis';
    s.analysisActiveTabIdx = 0;

    // PERSISTENCE: Save to DokkaiStorage and clear active in-progress session
    const storage = options.storage || (typeof window !== 'undefined' ? window.DokkaiStorage : null);
    if (storage && typeof storage.recordSolvedTask === 'function') {
      try {
        await storage.recordSolvedTask({
          text_id: s.activeText.id,
          title: s.activeText.title,
          level: s.activeText.level,
          category: s.activeText.category,
          score: analysisData.score_percent,
          score_percent: analysisData.score_percent,
          last_score: analysisData.score_percent,
          correct_count: analysisData.correct_count,
          total_questions: analysisData.total_questions,
          perfect: (analysisData.score_percent === 100),
          time_spent_sec: timeSpent,
          solved_at: new Date().toISOString()
        });
        if (typeof storage.clearActiveSession === 'function') {
          await storage.clearActiveSession();
        }
      } catch (err) {
        console.warn('[Dokkai] Failed to record solved task to local storage:', err);
      }
    }

    // Render Analysis View
    if (typeof options.renderAnalysisView === 'function') {
      options.renderAnalysisView(analysisData, s, els);
    } else {
      renderAnalysisView(analysisData, s, els);
    }

    // Refresh slots and solved tasks list
    if (analysisData.replacement) {
      if (typeof options.handleSlotReplacement === 'function') {
        options.handleSlotReplacement(analysisData.text_id, analysisData.replacement);
      } else if (typeof window !== 'undefined' && typeof window.handleSlotReplacement === 'function') {
        window.handleSlotReplacement(analysisData.text_id, analysisData.replacement);
      }
    } else {
      if (typeof options.fetchAndRenderSlots === 'function') {
        options.fetchAndRenderSlots();
      } else if (typeof window !== 'undefined' && typeof window.fetchAndRenderSlots === 'function') {
        window.fetchAndRenderSlots();
      }
    }

    if (typeof options.fetchAndRenderSolvedTasks === 'function') {
      options.fetchAndRenderSolvedTasks();
    } else if (typeof window !== 'undefined' && typeof window.fetchAndRenderSolvedTasks === 'function') {
      window.fetchAndRenderSolvedTasks();
    }

    return streamResult;

  } catch (err) {
    console.error('Ошибка отправки ответов на проверку:', err);
    if (typeof options.onError === 'function') {
      options.onError(err);
    } else if (typeof window !== 'undefined' && typeof window.alert === 'function') {
      window.alert(err.message || 'Не удалось отправить ответы на проверку. Ваши ответы сохранены.');
    }
    if (els.btnWizardSubmit) {
      els.btnWizardSubmit.disabled = false;
      els.btnWizardSubmit.textContent = 'Повторить отправку ответов ↻';
    }
    throw err;
  }
}
