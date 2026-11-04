// JLPT Dokkai Master - Service Worker (Offline-First App Shell & Granular Asset Cache)
const CACHE_NAME = 'dokkai-v2.1.0';

const PRECACHE_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/styles.css?v=2.1.0',
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
  '/static/app.js?v=2.1.0',
  '/static/storage.js?v=2.1.0',
  '/static/cloud_sync.js?v=2.1.0',
  '/static/firebase-config.js?v=2.1.0',
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

  // Skip non-GET and browser extensions
  if (request.method !== 'GET' || !url.protocol.startsWith('http')) {
    return;
  }

  // API endpoints: Stale-While-Revalidate with offline fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        try {
          const networkResponse = await fetch(request);
          if (networkResponse.status === 200) {
            cache.put(request, networkResponse.clone());
            cache.put(url.pathname, networkResponse.clone());
          }
          return networkResponse;
        } catch (err) {
          const cachedResponse = (await cache.match(request)) || (await cache.match(url.pathname));
          if (cachedResponse) return cachedResponse;
          throw err;
        }
      })
    );
    return;
  }

  // Static assets and App Shell: Cache-First
  event.respondWith(
    caches.match(request, { ignoreSearch: true }).then(async (cached) => {
      if (cached) return cached;
      try {
        const response = await fetch(request);
        if (response.status === 200) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(request, response.clone());
        }
        return response;
      } catch (err) {
        if (request.mode === 'navigate') {
          const rootCached = await caches.match('/');
          if (rootCached) return rootCached;
        }
        throw err;
      }
    })
  );
});
