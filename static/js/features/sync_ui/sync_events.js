/**
 * JLPT Dokkai Master - Cloud Sync & Firebase Configuration Event Listeners
 */

export function initSyncEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'close-sync-modal': () => actions.closeSyncModal(),
      'cloud-signout': () => {
        if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleCloudSignout) {
          window.DokkaiSyncUI.handleCloudSignout();
        }
      },
      'cloud-signin-google': () => {
        if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleGoogleSignIn) {
          window.DokkaiSyncUI.handleGoogleSignIn();
        }
      },
      'cloud-signin-anon': () => {
        if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleAnonymousSignIn) {
          window.DokkaiSyncUI.handleAnonymousSignIn();
        }
      },
      'export-sync-backup': () => actions.exportProgressJson(),
      'import-sync-backup-trigger': () => {
        const fileInput = document.getElementById('input-import-backup-file');
        if (fileInput) fileInput.click();
      },
      'save-firebase-config': () => {
        if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleSaveCustomFirebaseConfig) {
          window.DokkaiSyncUI.handleSaveCustomFirebaseConfig();
        }
      },
      'clear-firebase-config': () => {
        if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleClearCustomFirebaseConfig) {
          window.DokkaiSyncUI.handleClearCustomFirebaseConfig();
        }
      }
    });
  }

  // Initialize Sync Modal UI form controls
  if (window.initSyncModalUI) {
    window.initSyncModalUI();
  }
}
