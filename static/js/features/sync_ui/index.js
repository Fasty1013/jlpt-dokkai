/**
 * JLPT Dokkai Master - Sync UI Feature Module
 * Public interface and backwards-compatibility window bridges for Sync Modal & Cloud Auth UI.
 */

import {
    showSyncModalAlert,
    openSyncModal,
    closeSyncModal,
    updateSyncStatusUI,
    updateSyncUserUI,
    exportProgressJson,
    handleImportJsonFile,
    initSyncModalUI
} from './sync_modal.js';

export {
    showSyncModalAlert,
    openSyncModal,
    closeSyncModal,
    updateSyncStatusUI,
    updateSyncUserUI,
    exportProgressJson,
    handleImportJsonFile,
    initSyncModalUI
};

export const DokkaiSyncUI = {
    showAlert: showSyncModalAlert,
    open: openSyncModal,
    close: closeSyncModal,
    updateStatus: updateSyncStatusUI,
    updateUser: updateSyncUserUI,
    exportProgress: exportProgressJson,
    importProgress: handleImportJsonFile,
    init: initSyncModalUI
};

// Global backward-compatibility bridges for inline onclick attributes and classic scripts
if (typeof window !== 'undefined') {
    window.showSyncModalAlert = showSyncModalAlert;
    window.openSyncModal = openSyncModal;
    window.closeSyncModal = closeSyncModal;
    window.updateSyncStatusUI = updateSyncStatusUI;
    window.updateSyncUserUI = updateSyncUserUI;
    window.exportProgressJson = exportProgressJson;
    window.handleImportJsonFile = handleImportJsonFile;
    window.initSyncModalUI = initSyncModalUI;
    window.DokkaiSyncUI = DokkaiSyncUI;
}

