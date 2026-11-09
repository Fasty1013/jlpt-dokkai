/**
 * JLPT Dokkai Master - Settings Feature Barrel Export
 * Provides modern ES module exports and window.DokkaiSettings bridge.
 */

import {
  saveUserSettings,
  setReaderFont,
  adjustFontSize
} from './reader_settings.js';

import { initReaderSettingsEvents } from './reader_settings_events.js';

export {
  saveUserSettings,
  setReaderFont,
  adjustFontSize,
  initReaderSettingsEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiSettings = {
    saveUserSettings,
    setReaderFont,
    adjustFontSize,
    initEvents: initReaderSettingsEvents
  };

  // Direct function bridges on window for compatibility
  window.saveUserSettings = saveUserSettings;
  window.setReaderFont = setReaderFont;
  window.adjustFontSize = adjustFontSize;
}
