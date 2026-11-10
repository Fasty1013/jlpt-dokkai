/**
 * JLPT Dokkai Master - Reader Customization Settings Module
 * Handles font family (Mincho vs Gothic) and text size adjustments (16px..28px).
 */

import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * Persist user settings to DokkaiStorage.
 * @param {Object} [settings]
 */
export function saveUserSettings(settings = (storeState ? storeState.settings : null)) {
  const currentSettings = settings;
  if (typeof window !== 'undefined' && window.DokkaiStorage && currentSettings) {
    window.DokkaiStorage.saveSettings('user_settings', currentSettings);
  }
}

/**
 * Switch reader font family (mincho | gothic).
 * @param {string} typeface
 * @param {Object} [settings]
 * @param {Object} [elements]
 */
export function setReaderFont(typeface, settings = (storeState ? storeState.settings : null), elements = domElements) {
  const s = settings;
  const els = elements || {};

  if (s) {
    s.fontFamily = typeface;
  }

  if (els.passageContent) {
    if (typeface === 'mincho') {
      els.passageContent.classList.remove('font-gothic');
      els.passageContent.classList.add('font-mincho');
    } else {
      els.passageContent.classList.remove('font-mincho');
      els.passageContent.classList.add('font-gothic');
    }
  }

  if (els.btnFontMincho && els.btnFontGothic) {
    if (typeface === 'mincho') {
      els.btnFontMincho.classList.add('active');
      els.btnFontGothic.classList.remove('active');
    } else {
      els.btnFontGothic.classList.add('active');
      els.btnFontMincho.classList.remove('active');
    }
  }

  saveUserSettings(s);
}

/**
 * Adjust font size by delta (+2px or -2px), bounded between 16px and 28px.
 * @param {number} delta
 * @param {Object} [settings]
 * @param {Object} [elements]
 * @returns {number}
 */
export function adjustFontSize(delta, settings = (storeState ? storeState.settings : null), elements = domElements) {
  const s = settings;
  const els = elements || {};
  const currentSize = (s && s.fontSizePx) ? s.fontSizePx : 20;
  const newSize = Math.max(16, Math.min(28, currentSize + delta));

  if (s) {
    s.fontSizePx = newSize;
  }

  if (els.passageContent) {
    els.passageContent.style.fontSize = `${newSize}px`;
  }

  saveUserSettings(s);
  return newSize;
}
