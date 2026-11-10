/**
 * JLPT Dokkai Master - PDF Import & Staging Event Listeners
 */

import { initPdfImportUI } from './pdf_staging.js';

export function initPdfEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'clear-pdf-file': () => {
        if (actions.clearSelectedPdfFile) actions.clearSelectedPdfFile();
      },
      'refresh-pdf-drafts': () => {
        if (actions.fetchAndRenderDrafts) actions.fetchAndRenderDrafts();
      },
      'save-draft': (el, e, ds) => {
        const slug = ds.slug || el.dataset.slug;
        if (slug && window.DokkaiPdfImport && window.DokkaiPdfImport.saveDraft) {
          window.DokkaiPdfImport.saveDraft(slug);
        }
      },
      'delete-draft': (el, e, ds) => {
        const slug = ds.slug || el.dataset.slug;
        if (slug && window.DokkaiPdfImport && window.DokkaiPdfImport.deleteDraft) {
          window.DokkaiPdfImport.deleteDraft(slug);
        }
      },
      'publish-draft': (el, e, ds) => {
        const slug = ds.slug || el.dataset.slug;
        if (slug && window.DokkaiPdfImport && window.DokkaiPdfImport.publishDraft) {
          window.DokkaiPdfImport.publishDraft(slug);
        }
      },
      'mark-draft-option': (el, e, ds) => {
        const slug = ds.slug || el.dataset.slug;
        const qIdx = Number(ds.questionIndex || el.dataset.questionIndex);
        const optNum = Number(ds.optionNumber || el.dataset.optionNumber);
        if (slug && !isNaN(qIdx) && !isNaN(optNum) && window.DokkaiPdfImport && window.DokkaiPdfImport.markCorrectOption) {
          window.DokkaiPdfImport.markCorrectOption(slug, qIdx, optNum);
        }
      }
    });
  }

  // Initialize PDF drag-and-drop & form change handlers
  initPdfImportUI();
}
