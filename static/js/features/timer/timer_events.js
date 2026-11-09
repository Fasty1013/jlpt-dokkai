/**
 * JLPT Dokkai Master - Timer Event Listeners
 */

export function initTimerEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'toggle-timer-pause': () => actions.toggleTimerPause(),
      'add-timer-minute': () => actions.addTimerMinute(),
      'dismiss-timer': () => actions.dismissTimer(),
      'enable-timer-runtime': () => actions.enableTimerAtRuntime(),
      'dismiss-timer-alert': () => {
        if (elements.timerAlertBanner) elements.timerAlertBanner.classList.add('hidden');
      }
    });
  }
}
