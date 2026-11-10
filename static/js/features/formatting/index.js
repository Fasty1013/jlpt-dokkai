/**
 * JLPT Dokkai Master - Formatting & Pretest Config Barrel Export
 * Exposes ES modules and window.DokkaiFormatting bridge.
 */

import { CONFIG_STORAGE_KEY, loadStoredConfig, saveStoredConfig } from './config.js';
import { formatFileSize, formatTime, escapeHtml, getUserId } from '../../utils/index.js';

export {
  formatFileSize,
  formatTime,
  escapeHtml,
  CONFIG_STORAGE_KEY,
  loadStoredConfig,
  saveStoredConfig,
  getUserId
};

if (typeof window !== 'undefined') {
  window.DokkaiFormatting = {
    formatFileSize,
    formatTime,
    escapeHtml,
    CONFIG_STORAGE_KEY,
    loadStoredConfig,
    saveStoredConfig,
    getUserId
  };
}
