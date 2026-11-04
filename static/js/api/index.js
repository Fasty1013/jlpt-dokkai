/**
 * JLPT Dokkai Master - API Client Barrel Export
 * Exposes modern ES module exports and window.DokkaiApi bridge for zero-breaking transitions.
 */

import { ApiError, request } from './client.js';
import {
  fetchStreamSlots,
  fetchSolvedTasks,
  fetchSolvedDetail,
  retrySolvedTask,
  completeStreamTask
} from './stream.js';
import {
  fetchTextDetail,
  fetchCatalogTexts,
  reportTextIssue
} from './texts.js';
import { lookupWord } from './dictionary.js';
import {
  uploadPdf,
  fetchDrafts,
  fetchDraft,
  updateDraft,
  publishDraft,
  deleteDraft
} from './admin.js';

export {
  ApiError,
  request,
  fetchStreamSlots,
  fetchSolvedTasks,
  fetchSolvedDetail,
  retrySolvedTask,
  completeStreamTask,
  fetchTextDetail,
  fetchCatalogTexts,
  reportTextIssue,
  lookupWord,
  uploadPdf,
  fetchDrafts,
  fetchDraft,
  updateDraft,
  publishDraft,
  deleteDraft
};

if (typeof window !== 'undefined') {
  window.DokkaiApi = {
    ApiError,
    request,
    fetchStreamSlots,
    fetchSolvedTasks,
    fetchSolvedDetail,
    retrySolvedTask,
    completeStreamTask,
    fetchTextDetail,
    fetchCatalogTexts,
    reportTextIssue,
    lookupWord,
    uploadPdf,
    fetchDrafts,
    fetchDraft,
    updateDraft,
    publishDraft,
    deleteDraft
  };
}
