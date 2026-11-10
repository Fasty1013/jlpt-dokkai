/**
 * JLPT Dokkai Master - Pretest Modal Event Listeners
 */

export function initPretestEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'close-pretest-modal': () => actions.closePretestModal(),
      'start-exercise': () => actions.confirmPretestSettingsAndStart(),
      'timer-duration-minus': () => {
        let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
        if (cur > 1) {
          elements.modalTimerMinutes.textContent = cur - 1;
          actions.updateModalSettingTags();
        }
      },
      'timer-duration-plus': () => {
        let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
        if (cur < 20) {
          elements.modalTimerMinutes.textContent = cur + 1;
          actions.updateModalSettingTags();
        }
      }
    });
  }

  // Pre-test modal setting change handlers (idempotent guard)
  if (elements.pretestToggleFurigana && !elements.pretestToggleFurigana._dokkaiBound) {
    elements.pretestToggleFurigana._dokkaiBound = true;
    elements.pretestToggleFurigana.addEventListener('change', () => actions.updateModalSettingTags());
  }
  if (elements.pretestToggleHints && !elements.pretestToggleHints._dokkaiBound) {
    elements.pretestToggleHints._dokkaiBound = true;
    elements.pretestToggleHints.addEventListener('change', () => actions.updateModalSettingTags());
  }
  if (elements.pretestToggleTimer && !elements.pretestToggleTimer._dokkaiBound) {
    elements.pretestToggleTimer._dokkaiBound = true;
    elements.pretestToggleTimer.addEventListener('change', () => actions.updateModalSettingTags());
  }
  if (elements.pretestModalBackdrop && !elements.pretestModalBackdrop._dokkaiBound) {
    elements.pretestModalBackdrop._dokkaiBound = true;
    elements.pretestModalBackdrop.addEventListener('click', (e) => {
      if (e.target === elements.pretestModalBackdrop) {
        actions.closePretestModal();
      }
    });
  }
}
