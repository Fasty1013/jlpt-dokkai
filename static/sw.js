// JLPT Dokkai Master - Service Worker
// Scope: Same-origin static assets ONLY (/ and /static/*)
// Strategy: Network-First with Offline Cache Fallback (Zero Cache-First staleness)

const CACHE_VERSION = '2.1.0';
const CACHE_NAME = `dokkai-v${CACHE_VERSION}`;

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
  '/static/js/utils/index.js?v=2.1.0'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS);
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

  // 5. Network-First Strategy with Offline Cache Fallback (Ensures deployments take effect immediately)
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(async () => {
        // Network failed (device is offline): fall back to cached version
        const cached = await caches.match(request, { ignoreSearch: true });
        if (cached) {
          return cached;
        }
        if (request.mode === 'navigate') {
          const rootCached = await caches.match('/');
          if (rootCached) return rootCached;
        }
        throw new Error(`[ServiceWorker] Offline and asset not in cache: ${url.pathname}`);
      })
  );
});
