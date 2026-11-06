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

export {
  CONFIG_STORAGE_KEY,
  loadStoredConfig,
  saveStoredConfig,
  openPretestModal,
  closePretestModal,
  updateModalSettingTags,
  confirmPretestSettingsAndStart
};

if (typeof window !== 'undefined') {
  window.DokkaiPretest = {
    CONFIG_STORAGE_KEY,
    loadStoredConfig,
    saveStoredConfig,
    openPretestModal,
    closePretestModal,
    updateModalSettingTags,
    confirmPretestSettingsAndStart
  };

  // Direct bridges for backward compatibility until Step 6 event delegation
  window.openPretestModal = (textId) => openPretestModal(textId);
  window.closePretestModal = () => closePretestModal();
  window.updateModalSettingTags = () => updateModalSettingTags(window.elements);
  window.confirmPretestSettingsAndStart = () => confirmPretestSettingsAndStart();
  window.loadStoredConfig = loadStoredConfig;
  window.saveStoredConfig = saveStoredConfig;
}
