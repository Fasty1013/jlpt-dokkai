// JLPT Dokkai Master - Service Worker
// Scope: Same-origin static assets ONLY (/ and /static/*)
// Strategy: Network-First with 3.5s Timeout & Offline Cache Fallback

const CACHE_VERSION = '2.1.0';
const CACHE_NAME = `dokkai-v${CACHE_VERSION}`;
const NETWORK_TIMEOUT_MS = 3500;

// Static resources precached for offline resilience
const PRECACHE_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/css/variables.css?v=2.1.0',
  '/static/css/base.css?v=2.1.0',
  '/static/css/layout.css?v=2.1.0',
  '/static/css/catalog.css?v=2.1.0',
  '/static/css/reader.css?v=2.1.0',
  '/static/css/wizard.css?v=2.1.0',
  '/static/css/analysis.css?v=2.1.0',
  '/static/css/dictionary.css?v=2.1.0',
  '/static/css/pdf_import.css?v=2.1.0',
  '/static/css/modals.css?v=2.1.0',
  '/static/css/responsive.css?v=2.1.0',
  '/static/storage.js?v=2.1.0',
  '/static/firebase-config.js?v=2.1.0',
  '/static/cloud_sync.js?v=2.1.0',
  '/static/app.js?v=2.1.0',
  '/static/js/constants/settings.js?v=2.1.0',
  '/static/js/constants/labels.js?v=2.1.0',
  '/static/js/content/texts/ru.js?v=2.1.0',
  '/static/js/utils/user.js?v=2.1.0',
  '/static/js/utils/dom.js?v=2.1.0',
  '/static/js/utils/time.js?v=2.1.0',
  '/static/js/utils/math.js?v=2.1.0',
  '/static/js/utils/format.js?v=2.1.0',
  '/static/js/utils/index.js?v=2.1.0',
  '/static/js/api/client.js?v=2.1.0',
  '/static/js/api/stream.js?v=2.1.0',
  '/static/js/api/texts.js?v=2.1.0',
  '/static/js/api/dictionary.js?v=2.1.0',
  '/static/js/api/admin.js?v=2.1.0',
  '/static/js/api/index.js?v=2.1.0',
  '/static/js/features/timer/timer.js?v=2.1.0',
  '/static/js/features/timer/index.js?v=2.1.0',
  '/static/js/features/settings/reader_settings.js?v=2.1.0',
  '/static/js/features/settings/index.js?v=2.1.0',
  '/static/js/features/formatting/config.js?v=2.1.0',
  '/static/js/features/formatting/index.js?v=2.1.0',
  '/static/js/features/pretest/config.js?v=2.1.0',
  '/static/js/features/pretest/pretest_modal.js?v=2.1.0',
  '/static/js/features/pretest/index.js?v=2.1.0',
  '/static/js/features/stream/stream_slots.js?v=2.1.0',
  '/static/js/features/stream/index.js?v=2.1.0',
  '/static/js/features/solved/solved_tasks.js?v=2.1.0',
  '/static/js/features/solved/report_modal.js?v=2.1.0',
  '/static/js/features/solved/index.js?v=2.1.0'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Resilient precaching: individual failures won't break service worker install
      await Promise.allSettled(
        PRECACHE_ASSETS.map((asset) =>
          cache.add(asset).catch((err) => {
            console.warn(`[ServiceWorker] Failed to precache ${asset}:`, err);
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

function fetchWithTimeout(request, timeoutMs) {
  return new Promise((resolve, reject) => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      controller.abort();
      reject(new Error(`Network timeout after ${timeoutMs}ms`));
    }, timeoutMs);

    fetch(request, { signal: controller.signal })
      .then((res) => {
        clearTimeout(timer);
        resolve(res);
      })
      .catch((err) => {
        clearTimeout(timer);
        reject(err);
      });
  });
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Strict same-origin isolation: NEVER intercept cross-origin (Firebase, Firestore, Google Auth, gstatic, fonts)
  if (url.origin !== self.location.origin) {
    return;
  }

  // 2. Strict method isolation: NEVER intercept non-GET (POST, PUT, DELETE)
  if (request.method !== 'GET') {
    return;
  }

  // 3. Strict API isolation: NEVER intercept backend REST endpoints (/api/*)
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // 4. Strict scope: Only handle HTML App Shell ('/' or '/index.html') and static assets ('/static/*')
  const isStaticAsset = url.pathname === '/' || url.pathname === '/index.html' || url.pathname.startsWith('/static/');
  if (!isStaticAsset) {
    return;
  }

  // 5. Network-First Strategy with 3.5s Timeout & Offline Cache Fallback
  event.respondWith(
    fetchWithTimeout(request, NETWORK_TIMEOUT_MS)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(async (err) => {
        // Network failed or timed out: fall back to cached version
        const cached = await caches.match(request, { ignoreSearch: true });
        if (cached) {
          return cached;
        }
        if (request.mode === 'navigate') {
          const rootCached = await caches.match('/');
          if (rootCached) return rootCached;
        }
        throw new Error(`[ServiceWorker] Asset unavailable (${err.message}): ${url.pathname}`);
      })
  );
});
