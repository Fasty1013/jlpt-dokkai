/**
 * JLPT Dokkai Master - Dictionary API Module
 */

import { request } from './client.js';

/**
 * Lookup Japanese vocabulary word or phrase in backend dictionary.
 * The Russian request is unchanged (no `lang` parameter).
 * @param {string} query
 * @param {string} [lang] 'ru' (default) | 'en' | 'uz' | 'ja'
 * @returns {Promise<{ word: string, reading?: string, meaning: string, level?: string, lang?: string, source?: string, fallback?: boolean }>}
 */
export async function lookupWord(query, lang) {
  const cleanQuery = query.trim();
  const langParam = lang && lang !== 'ru' ? `&lang=${encodeURIComponent(lang)}` : '';
  return request(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}${langParam}`);
}

