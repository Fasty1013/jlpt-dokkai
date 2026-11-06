/**
 * JLPT Dokkai Master - Timer Feature Module
 * Supports both untimed free-reading mode and configurable countdown timers.
 */

import { formatTime } from '../../utils/time.js';

function resolveTimerState(timerState) {
  if (timerState) return timerState;
  if (typeof window !== 'undefined' && window.state && window.state.timer) {
    return window.state.timer;
  }
  return null;
}

function resolveElements(elements) {
  if (elements) return elements;
  if (typeof window !== 'undefined' && window.elements) {
    return window.elements;
  }
  return {};
}

/**
 * Stop active timer interval without resetting state.
 * @param {Object} [timerState]
 */
export function stopTimer(timerState) {
  const state = resolveTimerState(timerState);
  if (state && state.intervalId) {
    clearInterval(state.intervalId);
    state.intervalId = null;
  }
}

/**
 * Switch into untimed free-reading mode (records seconds spent in background).
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function startUntimedMode(timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  if (!state) return;

  stopTimer(state);
  state.enabled = false;
  state.secondsSpent = 0;
  state.isPaused = false;

  if (els.timerBox) els.timerBox.classList.add('hidden');
  if (els.btnEnableTimerRuntime) els.btnEnableTimerRuntime.classList.remove('hidden');
  if (els.timerAlertBanner) els.timerAlertBanner.classList.add('hidden');

  state.intervalId = setInterval(() => {
    if (!state.isPaused) {
      state.secondsSpent += 1;
    }
  }, 1000);
}

/**
 * Start countdown timer with specified minutes duration.
 * @param {number|string} minutes
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function startCountdownTimer(minutes, timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  if (!state) return;

  stopTimer(state);
  const durMins = Math.max(1, parseInt(minutes, 10) || 3);
  const totalSec = durMins * 60;

  state.enabled = true;
  state.totalSeconds = totalSec;
  state.remainingSeconds = totalSec;
  state.secondsSpent = 0;
  state.isPaused = false;

  if (els.timerBox) {
    els.timerBox.classList.remove('hidden', 'timer-warning', 'timer-expired', 'is-paused');
  }
  if (els.btnEnableTimerRuntime) {
    els.btnEnableTimerRuntime.classList.add('hidden');
  }
  if (els.timerAlertBanner) {
    els.timerAlertBanner.classList.add('hidden');
  }
  if (els.timerDisplay) {
    els.timerDisplay.textContent = formatTime(totalSec);
  }
  if (els.btnTimerTogglePause) {
    els.btnTimerTogglePause.textContent = '⏸️';
  }

  state.intervalId = setInterval(() => {
    if (state.isPaused) return;

    state.secondsSpent += 1;
    state.remainingSeconds -= 1;

    if (els.timerDisplay) {
      els.timerDisplay.textContent = formatTime(Math.max(0, state.remainingSeconds));
    }

    if (state.remainingSeconds <= 60 && state.remainingSeconds > 0) {
      if (els.timerBox) els.timerBox.classList.add('timer-warning');
    }

    if (state.remainingSeconds <= 0) {
      state.remainingSeconds = 0;
      stopTimer(state);

      if (els.timerBox) {
        els.timerBox.classList.remove('timer-warning');
        els.timerBox.classList.add('timer-expired');
      }
      if (els.timerAlertBanner) {
        els.timerAlertBanner.classList.remove('hidden');
      }
    }
  }, 1000);
}

/**
 * Toggle pause state of countdown timer.
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function toggleTimerPause(timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  if (!state || !state.enabled) return;

  state.isPaused = !state.isPaused;

  if (els.timerBox) {
    els.timerBox.classList.toggle('is-paused', state.isPaused);
  }
  if (els.btnTimerTogglePause) {
    els.btnTimerTogglePause.textContent = state.isPaused ? '▶️' : '⏸️';
  }
}

/**
 * Add 1 minute (+60s) to active countdown timer.
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function addTimerMinute(timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  if (!state) return;

  if (!state.enabled) {
    startCountdownTimer(3, state, els);
    return;
  }
  state.remainingSeconds += 60;
  state.totalSeconds += 60;

  if (els.timerDisplay) {
    els.timerDisplay.textContent = formatTime(state.remainingSeconds);
  }
  if (els.timerBox) {
    els.timerBox.classList.remove('timer-expired');
    if (state.remainingSeconds > 60) {
      els.timerBox.classList.remove('timer-warning');
    }
  }
  if (els.timerAlertBanner) {
    els.timerAlertBanner.classList.add('hidden');
  }
  if (!state.intervalId && !state.isPaused) {
    startCountdownTimer(Math.ceil(state.remainingSeconds / 60), state, els);
  }
}

/**
 * Confirm and dismiss countdown timer, switching to untimed free-reading mode.
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function dismissTimer(timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  if (confirm('Выключить таймер и продолжить решать в спокойном темпе?')) {
    startUntimedMode(state, els);
  }
}

/**
 * Enable countdown timer at runtime from header button.
 * @param {number} [recMin]
 * @param {Object} [timerState]
 * @param {Object} [elements]
 */
export function enableTimerAtRuntime(recMin, timerState, elements) {
  const state = resolveTimerState(timerState);
  const els = resolveElements(elements);
  const mins = recMin || 3;
  startCountdownTimer(mins, state, els);
}
