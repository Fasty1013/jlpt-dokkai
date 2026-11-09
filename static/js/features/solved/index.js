/**
 * JLPT Dokkai Master - Solved Archive & Defect Reporting Feature Barrel Export
 */

import {
  renderSolvedCardHtml,
  fetchAndRenderSolvedTasks,
  reviewSolvedTask,
  retrySolvedTask
} from './solved_tasks.js';

import {
  openReportModal,
  closeReportModal,
  submitReportDefect
} from './report_modal.js';

import { initReportEvents } from './report_events.js';

export {
  renderSolvedCardHtml,
  fetchAndRenderSolvedTasks,
  reviewSolvedTask,
  retrySolvedTask,
  openReportModal,
  closeReportModal,
  submitReportDefect,
  initReportEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiSolved = {
    renderSolvedCardHtml,
    fetchAndRenderSolvedTasks,
    reviewSolvedTask,
    retrySolvedTask,
    openReportModal,
    closeReportModal,
    submitReportDefect,
    initEvents: initReportEvents
  };

  // Direct bridges for backward compatibility until Step 6 event delegation
  window.fetchAndRenderSolvedTasks = () => fetchAndRenderSolvedTasks();
  window.closeReportModal = () => closeReportModal();
  window.submitReportDefect = () => submitReportDefect();
}
