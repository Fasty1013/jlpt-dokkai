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
    setCurrentDraftsCache
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
    getCache: getCurrentDraftsCache,
    setCache: setCurrentDraftsCache
};

// Global backward-compatibility bridges for inline onclick attributes and classic scripts
if (typeof window !== 'undefined') {
    window.handlePdfFileSelected = handlePdfFileSelected;
    window.clearSelectedPdfFile = clearSelectedPdfFile;
    window.handlePdfUpload = handlePdfUpload;
    window.fetchAndRenderDrafts = fetchAndRenderDrafts;
    window.renderDraftsList = renderDraftsList;
    window.markDraftCorrectOption = markDraftCorrectOption;
    window.saveDraft = saveDraft;
    window.publishDraft = publishDraft;
    window.deleteDraft = deleteDraft;
    window.initPdfImportUI = initPdfImportUI;
    window.DokkaiPdfImport = DokkaiPdfImport;
}

