/**
 * JLPT Dokkai Master - Formatting & Pure Helpers Barrel Export
 * Exposes ES modules and window.DokkaiFormatting bridge.
 */

import { formatFileSize, formatTime, escapeHtml } from './formatters.js';
import { CONFIG_STORAGE_KEY, loadStoredConfig, saveStoredConfig } from './config.js';
import { getUserId } from '../../utils/user.js';

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

  // Direct function bridges on window for compatibility
  window.formatFileSize = formatFileSize;
  window.escapeHtml = escapeHtml;
  window.loadStoredConfig = loadStoredConfig;
  window.saveStoredConfig = saveStoredConfig;
}
