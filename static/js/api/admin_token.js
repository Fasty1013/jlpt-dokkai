/**
 * JLPT Dokkai Master - admin key (ADMIN_TOKEN) stored in this browser only.
 * Set on the /admin page; sent as X-Admin-Token to /api/admin/* (admin panel, PDF import).
 * Without a stored key no header is added, so requests stay byte-identical to before.
 */

export const ADMIN_TOKEN_STORAGE_KEY = 'dokkai_admin_token';

export function getAdminToken() {
  try {
    return localStorage.getItem(ADMIN_TOKEN_STORAGE_KEY) || '';
  } catch (e) {
    return '';
  }
}

export function setAdminToken(token) {
  try {
    if (token) localStorage.setItem(ADMIN_TOKEN_STORAGE_KEY, token);
    else localStorage.removeItem(ADMIN_TOKEN_STORAGE_KEY);
  } catch (e) {
    /* storage unavailable: key lives only for this page */
  }
}

/** Headers object with X-Admin-Token when a key is stored, merged over `headers`. */
export function withAdminHeaders(headers = {}) {
  const token = getAdminToken();
  return token ? { ...headers, 'X-Admin-Token': token } : headers;
}

/** fetch() for /api/admin/* that adds the admin key when present. */
export function adminFetch(url, options = {}) {
  const token = getAdminToken();
  if (!token) return fetch(url, options);
  return fetch(url, { ...options, headers: withAdminHeaders(options.headers || {}) });
}
