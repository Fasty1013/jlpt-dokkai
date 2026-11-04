/**
 * JLPT Dokkai Master - Stream & Tasks API Module
 */

import { request } from './client.js';

/**
 * Fetch active stream slots for current profile and filters.
 * @param {Object} params
 * @param {string} params.userId
 * @param {string} params.level
 * @param {string} [params.category]
 * @param {boolean} [params.refresh]
 * @returns {Promise<{ slots: Array, profile_key: string }>}
 */
export async function fetchStreamSlots({ userId, level, category = '', refresh = false }) {
  const query = new URLSearchParams();
  query.append('user_id', userId);
  query.append('level', level);
  if (category) {
    query.append('category', category);
  }
  if (refresh) {
    query.append('refresh', 'true');
  }
  query.append('_t', Date.now().toString());

  return request(`/api/stream/slots?${query.toString()}`, {
    cache: 'no-store',
    headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
  });
}

/**
 * Fetch list of solved tasks for user archive.
 * @param {Object} params
 * @param {string} params.userId
 * @param {string} [params.level]
 * @param {string} [params.filter] - 'all' | 'perfect' | 'errors'
 * @returns {Promise<{ items: Array, total: number }>}
 */
export async function fetchSolvedTasks({ userId, level = '', filter = 'all' }) {
  const query = new URLSearchParams();
  query.append('user_id', userId);
  if (level) {
    query.append('level', level);
  }
  if (filter && filter !== 'all') {
    query.append('filter', filter);
  }
  query.append('_t', Date.now().toString());

  return request(`/api/stream/solved?${query.toString()}`, {
    cache: 'no-store',
    headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
  });
}

/**
 * Fetch full post-submit analysis of a solved task (Anti-Cheat protected).
 * @param {number|string} textId
 * @param {string} userId
 * @returns {Promise<any>}
 */
export async function fetchSolvedDetail(textId, userId) {
  return request(`/api/stream/solved/${textId}?user_id=${encodeURIComponent(userId)}`);
}

/**
 * Request retry attempt for a solved task.
 * @param {number|string} textId
 * @param {string} userId
 * @returns {Promise<any>}
 */
export async function retrySolvedTask(textId, userId) {
  return request(`/api/stream/retry/${textId}?user_id=${encodeURIComponent(userId)}`, {
    method: 'POST'
  });
}

/**
 * Submit answers and complete task in stream flow.
 * @param {Object} payload
 * @returns {Promise<any>}
 */
export async function completeStreamTask(payload) {
  return request('/api/stream/complete', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

