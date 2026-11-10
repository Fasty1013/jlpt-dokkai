/**
 * JLPT Dokkai Master - PDF Import Feature Module
 * Public interface and backwards-compatibility window bridges for PDF staging & administration.
 */

import {
    handlePdfFileSelected,
    clearSelectedPdfFile,
    handlePdfUpload,
    fetchAndRenderDrafts,
    renderDraftsList,
    markDraftCorrectOption,
    saveDraft,
    publishDraft,
    deleteDraft,
    initPdfImportUI,
    getCurrentDraftsCache,
    setCurrentDraftsCache
} from './pdf_staging.js';

import { initPdfEvents } from './pdf_events.js';

export {
    handlePdfFileSelected,
    clearSelectedPdfFile,
    handlePdfUpload,
    fetchAndRenderDrafts,
    renderDraftsList,
    markDraftCorrectOption,
    saveDraft,
    publishDraft,
    deleteDraft,
    initPdfImportUI,
    getCurrentDraftsCache,
    setCurrentDraftsCache,
    initPdfEvents
};

export const DokkaiPdfImport = {
    handleFileSelected: handlePdfFileSelected,
    clearFile: clearSelectedPdfFile,
    upload: handlePdfUpload,
    fetchDrafts: fetchAndRenderDrafts,
    renderDrafts: renderDraftsList,
    markCorrectOption: markDraftCorrectOption,
    saveDraft: saveDraft,
    publishDraft: publishDraft,
    deleteDraft: deleteDraft,
    init: initPdfImportUI,
    initEvents: initPdfEvents,
    getCache: getCurrentDraftsCache,
    setCache: setCurrentDraftsCache
};

// Global backward-compatibility bridges for inline onclick attributes and classic scripts
if (typeof window !== 'undefined') {
    window.DokkaiPdfImport = DokkaiPdfImport;
}

