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

import { initSyncEvents } from './sync_events.js';

export {
    showSyncModalAlert,
    openSyncModal,
    closeSyncModal,
    updateSyncStatusUI,
    updateSyncUserUI,
    exportProgressJson,
    handleImportJsonFile,
    initSyncModalUI,
    initSyncEvents
};

export const DokkaiSyncUI = {
    showAlert: showSyncModalAlert,
    open: openSyncModal,
    close: closeSyncModal,
    updateStatus: updateSyncStatusUI,
    updateUser: updateSyncUserUI,
    exportProgress: exportProgressJson,
    importProgress: handleImportJsonFile,
    init: initSyncModalUI,
    initEvents: initSyncEvents
};

// Global backward-compatibility bridges for inline onclick attributes and classic scripts
if (typeof window !== 'undefined') {
    window.DokkaiSyncUI = DokkaiSyncUI;
}

