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

  // Direct bridges for backward compatibility until Step 6 event delegation
  window.openPretestModal = (textId) => openPretestModal(textId);
  window.closePretestModal = () => closePretestModal();
  window.updateModalSettingTags = (els) => updateModalSettingTags(els || (window.DokkaiElements ? window.DokkaiElements.elements : null));
  window.confirmPretestSettingsAndStart = () => confirmPretestSettingsAndStart();
  window.loadStoredConfig = loadStoredConfig;
  window.saveStoredConfig = saveStoredConfig;
}
