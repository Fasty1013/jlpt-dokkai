/**
 * JLPT Dokkai Master - Dictionary API Module
 */

import { request } from './client.js';

/**
 * Lookup Japanese vocabulary word or phrase in backend dictionary.
 * @param {string} query
 * @returns {Promise<{ word: string, reading?: string, meaning: string, level?: string }>}
 */
export async function lookupWord(query) {
  const cleanQuery = query.trim();
  return request(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}`);
}

