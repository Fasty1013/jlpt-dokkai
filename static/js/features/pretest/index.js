/**
 * JLPT Dokkai Master - Pretest Feature Barrel Export
 */

import {
  CONFIG_STORAGE_KEY,
  loadStoredConfig,
  saveStoredConfig
} from './config.js';

import {
  openPretestModal,
  closePretestModal,
  updateModalSettingTags,
  confirmPretestSettingsAndStart
} from './pretest_modal.js';

import { initPretestEvents } from './pretest_events.js';

export {
  CONFIG_STORAGE_KEY,
  loadStoredConfig,
  saveStoredConfig,
  openPretestModal,
  closePretestModal,
  updateModalSettingTags,
  confirmPretestSettingsAndStart,
  initPretestEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiPretest = {
    CONFIG_STORAGE_KEY,
    loadStoredConfig,
    saveStoredConfig,
    openPretestModal,
    closePretestModal,
    updateModalSettingTags,
    confirmPretestSettingsAndStart,
    initEvents: initPretestEvents
  };
}
