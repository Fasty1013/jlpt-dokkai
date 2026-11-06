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

export {
  renderSolvedCardHtml,
  fetchAndRenderSolvedTasks,
  reviewSolvedTask,
  retrySolvedTask,
  openReportModal,
  closeReportModal,
  submitReportDefect
};

if (typeof window !== 'undefined') {
  window.DokkaiSolved = {
    renderSolvedCardHtml,
    fetchAndRenderSolvedTasks,
    reviewSolvedTask,
    retrySolvedTask,
    openReportModal,
    closeReportModal,
    submitReportDefect
  };

  // Direct bridges for backward compatibility until Step 6 event delegation
  window.fetchAndRenderSolvedTasks = () => fetchAndRenderSolvedTasks();
  window.reviewSolvedTask = (textId) => reviewSolvedTask(textId);
  window.retrySolvedTask = (textId) => retrySolvedTask(textId);
  window.openReportModal = (textId, title) => openReportModal(textId, title);
  window.closeReportModal = () => closeReportModal();
  window.submitReportDefect = () => submitReportDefect();
}
