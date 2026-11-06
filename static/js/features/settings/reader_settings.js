/**
 * JLPT Dokkai Master - Reader Customization Settings Module
 * Handles font family (Mincho vs Gothic) and text size adjustments (16px..28px).
 */

function resolveSettings(settings) {
  if (settings) return settings;
  if (typeof window !== 'undefined' && window.state && window.state.settings) {
    return window.state.settings;
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
 * Persist user settings to DokkaiStorage.
 * @param {Object} [settings]
 */
export function saveUserSettings(settings) {
  const currentSettings = resolveSettings(settings);
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
export function setReaderFont(typeface, settings, elements) {
  const s = resolveSettings(settings);
  const els = resolveElements(elements);

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
export function adjustFontSize(delta, settings, elements) {
  const s = resolveSettings(settings);
  const els = resolveElements(elements);
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
