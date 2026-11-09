/**
 * JLPT Dokkai Master - Exercise, Wizard & Active Session Event Listeners
 */

export function initExerciseEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'wizard-prev': () => actions.wizardGoPrev(),
      'wizard-next': () => actions.wizardGoNext(),
      'wizard-submit': () => actions.submitAnswers(),
      'select-option': (el, e, ds) => {
        const qId = Number(ds.questionId || el.dataset.questionId);
        const optId = Number(ds.optionId || el.dataset.optionId);
        if (qId && optId) actions.handleOptionSelect(qId, optId);
      },
      'resume-unfinished': async () => {
        if (!state.activeSession) return;
        await actions.resumeActiveExercise(state.activeSession);
      },
      'dismiss-unfinished': async () => {
        if (elements.unfinishedTestBanner) {
          elements.unfinishedTestBanner.classList.add('hidden');
        }
        state.activeSession = null;
        if (window.DokkaiStorage) {
          await window.DokkaiStorage.clearActiveSession();
        }
      }
    });
  }
}
