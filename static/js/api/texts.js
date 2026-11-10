/**
 * JLPT Dokkai Master - Texts & Feedback API Module
 */

import { request } from './client.js';
import { getUserId } from '../utils/user.js';

/**
 * Fetch text detail for strict reading mode (Anti-Cheat: no answers or explanations).
 * @param {number|string} textId
 * @returns {Promise<any>}
 */
export async function fetchTextDetail(textId) {
  // user_id seeds the per-user option shuffle (Step 11d); options come back with opaque ids
  return request(`/api/texts/${textId}?_t=${Date.now()}&user_id=${encodeURIComponent(getUserId())}`, {
    cache: 'no-store',
    headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
  });
}

/**
 * Fetch catalog texts with optional level and category filters.
 * @param {Object} [params]
 * @param {string} [params.level]
 * @param {string} [params.category]
 * @returns {Promise<Array>}
 */
export async function fetchCatalogTexts(params = {}) {
  const query = new URLSearchParams();
  if (params.level) query.append('level', params.level);
  if (params.category) query.append('category', params.category);
  const qStr = query.toString();
  return request(`/api/texts${qStr ? '?' + qStr : ''}`);
}

/**
 * Send quality report/feedback for a text task.
 * @param {number|string} textId
 * @param {Object} payload
 * @param {string} payload.reason
 * @param {string} payload.details
 * @param {string} payload.user_id
 * @returns {Promise<{ message: string }>}
 */
export async function reportTextIssue(textId, payload) {
  return request(`/api/texts/${textId}/report`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

