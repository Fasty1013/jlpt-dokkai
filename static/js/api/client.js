/**
 * JLPT Dokkai Master - API Client Core Wrapper
 * Provides safe fetch with timeout (80s default for Render cold starts),
 * cold-start friendly progress notification (>5s), uniform headers and standardized ApiError.
 */

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export const DEFAULT_TIMEOUT_MS = 80000;
export const SLOW_REQUEST_THRESHOLD_MS = 5000;

let activeSlowRequests = 0;
let wakingNoticeEl = null;

function showServerWakingNotice() {
  if (typeof document === 'undefined') return;

  if (!wakingNoticeEl) {
    wakingNoticeEl = document.createElement('div');
    wakingNoticeEl.id = 'server-waking-notice';
    wakingNoticeEl.className = 'server-waking-notice';
    wakingNoticeEl.setAttribute('role', 'status');
    wakingNoticeEl.setAttribute('aria-live', 'polite');
    wakingNoticeEl.innerHTML = `
      <div class="server-waking-content">
        <span class="server-waking-icon">⏳</span>
        <span class="server-waking-text">Сервер просыпается, подождите до минуты…</span>
      </div>
    `;
    document.body.appendChild(wakingNoticeEl);
  }
  wakingNoticeEl.style.display = 'flex';
  wakingNoticeEl.classList.remove('hidden');

  // Also if activeSlotsList is in loading state, add subtle helper text
  const loadingSpinner = document.querySelector('#active-slots-list .loading-spinner');
  if (loadingSpinner && !loadingSpinner.querySelector('.waking-subtext')) {
    const sub = document.createElement('div');
    sub.className = 'waking-subtext';
    sub.style.fontSize = '0.85rem';
    sub.style.marginTop = '0.5rem';
    sub.style.opacity = '0.85';
    sub.textContent = 'Сервер просыпается, подождите до минуты…';
    loadingSpinner.appendChild(sub);
  }
}

function hideServerWakingNotice() {
  if (wakingNoticeEl) {
    wakingNoticeEl.style.display = 'none';
    wakingNoticeEl.classList.add('hidden');
  }
  if (typeof document !== 'undefined') {
    const sub = document.querySelector('.waking-subtext');
    if (sub) sub.remove();
  }
}

/**
 * Universal JSON fetch helper with timeout and error handling.
 * @param {string} url - Request URL
 * @param {RequestInit & { timeoutMs?: number }} options - Fetch options
 * @returns {Promise<any>}
 */
export async function request(url, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers = {}, ...fetchOptions } = options;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let isSlow = false;
  const slowTimer = setTimeout(() => {
    isSlow = true;
    activeSlowRequests += 1;
    showServerWakingNotice();
  }, SLOW_REQUEST_THRESHOLD_MS);

  try {
    const isFormData = fetchOptions.body instanceof FormData;
    const finalHeaders = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...headers
    };

    const response = await fetch(url, {
      ...fetchOptions,
      headers: finalHeaders,
      signal: controller.signal
    });

    clearTimeout(timer);
    clearTimeout(slowTimer);
    if (isSlow) {
      activeSlowRequests = Math.max(0, activeSlowRequests - 1);
      if (activeSlowRequests === 0) hideServerWakingNotice();
    }

    if (!response.ok) {
      let errorData = null;
      try {
        errorData = await response.json();
      } catch {
        // Fallback for non-JSON error responses
      }
      const message = errorData?.detail || `HTTP Error ${response.status}: ${response.statusText}`;
      throw new ApiError(message, response.status, errorData);
    }

    // 204 No Content support
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timer);
    clearTimeout(slowTimer);
    if (isSlow) {
      activeSlowRequests = Math.max(0, activeSlowRequests - 1);
      if (activeSlowRequests === 0) hideServerWakingNotice();
    }

    if (err.name === 'AbortError') {
      throw new ApiError('Таймаут соединения с сервером (80 с). Пожалуйста, повторите попытку.', 408);
    }
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || 'Ошибка сети. Проверьте подключение к интернету.', 0);
  }
}
