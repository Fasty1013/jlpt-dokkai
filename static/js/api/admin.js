/**
 * JLPT Dokkai Master - Admin & PDF Import API Module
 */

import { request } from './client.js';

/**
 * Upload PDF and extract JLPT reading exercises.
 * @param {FormData} formData
 * @returns {Promise<any>}
 */
export async function uploadPdf(formData) {
  return request('/api/admin/upload-pdf', {
    method: 'POST',
    body: formData
  });
}

/**
 * List all imported drafts.
 * @returns {Promise<Array>}
 */
export async function fetchDrafts() {
  return request('/api/admin/drafts');
}

/**
 * Fetch draft by slug.
 * @param {string} slug
 * @returns {Promise<any>}
 */
export async function fetchDraft(slug) {
  return request(`/api/admin/drafts/${slug}`);
}

/**
 * Update draft content.
 * @param {string} slug
 * @param {Object} data
 * @returns {Promise<any>}
 */
export async function updateDraft(slug, data) {
  return request(`/api/admin/drafts/${slug}`, {
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
  return request(`/api/admin/drafts/${slug}/publish`, {
    method: 'POST'
  });
}

/**
 * Delete draft by slug.
 * @param {string} slug
 * @returns {Promise<any>}
 */
export async function deleteDraft(slug) {
  return request(`/api/admin/drafts/${slug}`, {
    method: 'DELETE'
  });
}
