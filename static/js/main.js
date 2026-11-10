/**
 * JLPT Dokkai Master - Application Entry Point (Step 6e-3)
 * Replaces the former classic script static/app.js.
 * Orchestration only: wires events, restores persistence/sync, renders the first screen.
 */

import './storage/storage.js'; // defines window.DokkaiStorage (Step 7c)
import './sync/cloud_sync.js'; // defines window.DokkaiCloudSync (Step 7c)
import './state/index.js';
import './utils/index.js';
import './api/index.js';
import './features/events/index.js';
import { fetchAndRenderDrafts } from './features/pdf_import/index.js';
import { initEventListeners } from './app/init_events.js';
import { initPersistenceAndSync } from './app/persistence.js';
import * as actions from './app/actions.js';

// ----------------------------------------------------------------------------
// Temporary runtime bridges (to be removed in Step 9).
// Kept only for consumers that still resolve these names through `window`:
//   * pdf_staging.js / sync_modal.js / notebook_storage.js (guarded runtime calls)
//   * Playwright specs and tools/compare_*.cjs, which drive the page via evaluate()
// Before Step 6e-3 these were implicit globals created by the classic app.js.
// ----------------------------------------------------------------------------
Object.assign(window, {
  fetchAndRenderCatalog: actions.fetchAndRenderCatalog,
  fetchAndRenderSlots: actions.fetchAndRenderSlots,
  fetchAndRenderSolvedTasks: actions.fetchAndRenderSolvedTasks,
  renderNotebookWords: actions.renderNotebookWords,
  updateNotebookBadge: actions.updateNotebookBadge,
  openPretestModal: actions.openPretestModal,
  openReportModal: actions.openReportModal,
  switchMainTab: actions.switchMainTab,
  showPopupDictionary: actions.showPopupDictionary,
  hidePopupDictionary: actions.hidePopupDictionary,
  initEventListeners
});

async function boot() {
  history.replaceState({ view: 'catalog' }, '', window.location.pathname);
  initEventListeners();
  try {
    await Promise.race([
      initPersistenceAndSync(),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Persistence init timeout')), 2000))
    ]);
  } catch (err) {
    console.warn('[Dokkai] Persistence/Sync init non-blocking warning:', err);
  }
  actions.fetchAndRenderCatalog();
  fetchAndRenderDrafts();
}

// Module scripts are deferred: the DOM is parsed, but DOMContentLoaded has not fired yet.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
