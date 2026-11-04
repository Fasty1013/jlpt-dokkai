/**
 * JLPT Dokkai Master - API Client Core Wrapper
 * Provides safe fetch with timeout (10s default), uniform headers and standardized ApiError.
 */

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const DEFAULT_TIMEOUT_MS = 10000;

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
    if (err.name === 'AbortError') {
      throw new ApiError('Таймаут соединения с сервером (10 с). Пожалуйста, повторите попытку.', 408);
    }
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || 'Ошибка сети. Проверьте подключение к интернету.', 0);
  }
}

