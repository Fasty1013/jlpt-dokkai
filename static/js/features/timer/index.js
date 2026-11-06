/**
 * JLPT Dokkai Master - Timer Feature Barrel Export
 * Provides modern ES module exports and window.DokkaiTimer bridge.
 */

import {
  stopTimer,
  startUntimedMode,
  startCountdownTimer,
  toggleTimerPause,
  addTimerMinute,
  dismissTimer,
  enableTimerAtRuntime
} from './timer.js';

export {
  stopTimer,
  startUntimedMode,
  startCountdownTimer,
  toggleTimerPause,
  addTimerMinute,
  dismissTimer,
  enableTimerAtRuntime
};

if (typeof window !== 'undefined') {
  window.DokkaiTimer = {
    stopTimer,
    startUntimedMode,
    startCountdownTimer,
    toggleTimerPause,
    addTimerMinute,
    dismissTimer,
    enableTimerAtRuntime
  };

  // Direct function bridges on window for compatibility
  window.stopTimer = stopTimer;
  window.startUntimedMode = startUntimedMode;
  window.startCountdownTimer = startCountdownTimer;
  window.toggleTimerPause = toggleTimerPause;
  window.addTimerMinute = addTimerMinute;
  window.dismissTimer = dismissTimer;
  window.enableTimerAtRuntime = enableTimerAtRuntime;
}
