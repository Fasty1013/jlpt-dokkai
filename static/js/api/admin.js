/**
 * JLPT Dokkai Master - Admin & PDF Import API Module
 */

import { request } from './client.js';
import { withAdminHeaders } from './admin_token.js';

// /api/admin/* needs the admin key in production (X-Admin-Token, see admin_token.js).
const adminRequest = (url, options = {}) => request(url, { ...options, headers: withAdminHeaders(options.headers || {}) });

/**
 * Upload PDF and extract JLPT reading exercises.
 * @param {FormData} formData
 * @returns {Promise<any>}
 */
export async function uploadPdf(formData) {
  return adminRequest('/api/admin/upload-pdf', {
    method: 'POST',
    body: formData
  });
}

/**
 * List all imported drafts.
 * @returns {Promise<Array>}
 */
export async function fetchDrafts() {
  return adminRequest('/api/admin/drafts');
}

/**
 * Fetch draft by slug.
 * @param {string} slug
 * @returns {Promise<any>}
 */
export async function fetchDraft(slug) {
  return adminRequest(`/api/admin/drafts/${slug}`);
}

/**
 * Update draft content.
 * @param {string} slug
 * @param {Object} data
 * @returns {Promise<any>}
 */
export async function updateDraft(slug, data) {
  return adminRequest(`/api/admin/drafts/${slug}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

/**
 * Publish draft into database.
 * @param {string} slug
 * @returns {Promise<any>}
 */
export async function publishDraft(slug) {
  return adminRequest(`/api/admin/drafts/${slug}/publish`, {
    method: 'POST'
  });
}

/**
 * Delete draft by slug.
 * @param {string} slug
 * @returns {Promise<any>}
 */
export async function deleteDraft(slug) {
  return adminRequest(`/api/admin/drafts/${slug}`, {
    method: 'DELETE'
  });
}

