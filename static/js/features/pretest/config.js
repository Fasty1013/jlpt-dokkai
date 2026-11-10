/**
 * JLPT Dokkai Master - Pretest Configuration Storage
 */

export const CONFIG_STORAGE_KEY = 'dokkai_pretest_config';

/**
 * Load stored pretest configuration from localStorage.
 * @returns {Object}
 */
export function loadStoredConfig() {
  try {
    const stored = localStorage.getItem(CONFIG_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.warn('Failed to load pretest config from localStorage', e);
  }
  return {
    showFurigana: true,
    showHintsAndAnalysis: true,
    enableTimer: false,
    timerMinutes: 3
  };
}

/**
 * Save pretest configuration to localStorage.
 * @param {Object} config
 */
export function saveStoredConfig(config) {
  try {
    localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(config));
  } catch (e) {
    console.warn('Failed to save pretest config to localStorage', e);
  }
}
