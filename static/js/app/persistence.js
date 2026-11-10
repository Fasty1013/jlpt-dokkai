/**
 * JLPT Dokkai Master - Persistence & Cloud Sync Bootstrap (Step 6e-3)
 * Restores stored settings/words from DokkaiStorage, wires DokkaiCloudSync to the
 * sync UI and registers active-session flush handlers.
 * Ported 1:1 from initPersistenceAndSync() of the former static/app.js.
 * DokkaiStorage / DokkaiCloudSync are still classic scripts (moved in Step 7).
 */

import { state } from '../state/store.js';
import { elements } from '../state/elements.js';
import { updateSyncStatusUI, updateSyncUserUI, showSyncModalAlert } from '../features/sync_ui/index.js';
import {
  setReaderFont,
  adjustFontSize,
  updateNotebookBadge,
  checkAndPromptActiveSession,
  saveCurrentActiveSession
} from './actions.js';

export async function initPersistenceAndSync() {
  if (!window.DokkaiStorage) return;

  // 1. Wait for DokkaiStorage
  await window.DokkaiStorage.initPromise;

  // 2. Load stored settings
  const storedUserSettings = await window.DokkaiStorage.getSettings('user_settings');
  if (storedUserSettings) {
    state.settings = { ...state.settings, ...storedUserSettings };
    if (state.settings.fontFamily) setReaderFont(state.settings.fontFamily);
    if (state.settings.fontSizePx) adjustFontSize(0);
  }

  const storedStreamProfile = await window.DokkaiStorage.getSettings('stream_profile');
  if (storedStreamProfile) {
    state.streamProfile = { ...state.streamProfile, ...storedStreamProfile };
    if (elements.streamLevelPills) {
      elements.streamLevelPills.querySelectorAll('.filter-pill').forEach(p => {
        p.classList.toggle('active', p.dataset.level === state.streamProfile.level);
      });
    }
    if (elements.streamCategoryPills) {
      elements.streamCategoryPills.querySelectorAll('.filter-pill').forEach(p => {
        p.classList.toggle('active', p.dataset.category === state.streamProfile.category);
      });
    }
  }

  const storedPretest = await window.DokkaiStorage.getSettings('pretest_config');
  if (storedPretest) {
    state.pretestConfig = { ...state.pretestConfig, ...storedPretest };
  }

  // 3. Load words into memory
  state.savedWords = await window.DokkaiStorage.getAllWords();
  updateNotebookBadge();

  // 4. Setup Cloud Sync
  if (window.DokkaiCloudSync) {
    window.DokkaiStorage.onSyncNeeded(() => {
      window.DokkaiCloudSync.scheduleAutoSync();
    });

    window.DokkaiCloudSync.onStatusChange((status, extra) => {
      updateSyncStatusUI(status, extra);
    });

    window.DokkaiCloudSync.onUserChange((user) => {
      updateSyncUserUI(user);
    });

    window.DokkaiCloudSync.onFeedback((type, message) => {
      showSyncModalAlert(type, message);
    });

    // Initialize Firebase asynchronously in background
    window.DokkaiCloudSync.init().catch(err => console.warn('[CloudSync] Init error:', err));
    updateSyncStatusUI();
  }

  // 5. Check if there is an in-progress test to recover
  await checkAndPromptActiveSession();

  // 6. Flush active session on page unload
  window.addEventListener('pagehide', () => saveCurrentActiveSession());
  window.addEventListener('beforeunload', () => saveCurrentActiveSession());
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      saveCurrentActiveSession();
    }
  });
}
