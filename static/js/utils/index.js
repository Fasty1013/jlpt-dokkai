/**
 * JLPT Dokkai Master - Utilities Barrel Export
 * Single source of truth for pure utility functions across the application.
 */

import { getUserId } from './user.js';
import { escapeHtml } from './dom.js';
import { formatTime, formatLocaleDate } from './time.js';
import { calculateScorePercent } from './math.js';
import { formatFileSize } from './format.js';

export {
  getUserId,
  escapeHtml,
  formatTime,
  formatLocaleDate,
  calculateScorePercent,
  formatFileSize
};

if (typeof window !== 'undefined') {
  window.DokkaiUtils = {
    getUserId,
    escapeHtml,
    formatTime,
    formatLocaleDate,
    calculateScorePercent,
    formatFileSize
  };
}
