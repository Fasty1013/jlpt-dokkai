// JLPT Dokkai Master - Service Worker
// Scope: Same-origin static assets ONLY (/ and /static/*)
// Strategy: Network-First with 3.5s Timeout & Offline Cache Fallback

const CACHE_VERSION = '2.4.0';
const CACHE_NAME = `dokkai-v${CACHE_VERSION}`;
const NETWORK_TIMEOUT_MS = 3500;

// Static resources precached for offline resilience
const PRECACHE_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/icons/favicon.ico',
  '/static/icons/icon-32.png',
  '/static/icons/apple-touch-icon.png',
  '/static/css/variables.css',
  '/static/css/base.css',
  '/static/css/layout.css',
  '/static/css/catalog.css',
  '/static/css/reader.css',
  '/static/css/wizard.css',
  '/static/css/analysis.css',
  '/static/css/dictionary.css',
  '/static/css/pdf_import.css',
  '/static/css/modals.css',
  '/static/css/responsive.css',
  '/static/js/storage/storage.js',
  '/static/js/storage/constants.js',
  '/static/js/storage/idb_schema.js',
  '/static/js/storage/fallback_store.js',
  '/static/js/storage/migration.js',
  '/static/js/storage/backup.js',
  '/static/js/config/firebase-config.js',
  '/static/js/sync/cloud_sync.js',
  '/static/js/sync/config_store.js',
  '/static/js/sync/auth_errors.js',
  '/static/js/sync/sdk_loader.js',
  '/static/js/sync/merge.js',
  '/static/js/main.js',
  '/static/js/i18n/index.js',
  '/static/js/i18n/i18n_events.js',
  '/static/js/i18n/server_messages.js',
  '/static/js/app/i18n_refresh.js',
  '/static/js/i18n/locales/ru.js',
  '/static/js/i18n/locales/en.js',
  '/static/js/i18n/locales/uz.js',
  '/static/js/i18n/locales/ja.js',
  '/static/js/app/actions.js',
  '/static/js/app/init_events.js',
  '/static/js/app/persistence.js',
  '/static/js/constants/settings.js',
  '/static/js/constants/labels.js',
  '/static/js/utils/user.js',
  '/static/js/utils/dom.js',
  '/static/js/utils/time.js',
  '/static/js/utils/math.js',
  '/static/js/utils/format.js',
  '/static/js/utils/index.js',
  '/static/js/api/client.js',
  '/static/js/api/stream.js',
  '/static/js/api/texts.js',
  '/static/js/api/dictionary.js',
  '/static/js/api/admin.js',
  '/static/js/api/admin_token.js',
  '/static/js/api/index.js',
  '/static/js/state/store.js',
  '/static/js/state/elements.js',
  '/static/js/state/index.js',
  '/static/js/features/timer/timer.js',
  '/static/js/features/timer/timer_events.js',
  '/static/js/features/timer/index.js',
  '/static/js/features/settings/reader_settings.js',
  '/static/js/features/settings/reader_settings_events.js',
  '/static/js/features/settings/index.js',
  '/static/js/features/formatting/config.js',
  '/static/js/features/formatting/index.js',
  '/static/js/features/pretest/config.js',
  '/static/js/features/pretest/pretest_modal.js',
  '/static/js/features/pretest/pretest_events.js',
  '/static/js/features/pretest/index.js',
  '/static/js/features/stream/stream_slots.js',
  '/static/js/features/stream/stream_events.js',
  '/static/js/features/stream/index.js',
  '/static/js/features/solved/solved_tasks.js',
  '/static/js/features/solved/report_modal.js',
  '/static/js/features/solved/report_events.js',
  '/static/js/features/solved/index.js',
  '/static/js/features/exercise/wizard.js',
  '/static/js/features/exercise/exercise_view.js',
  '/static/js/features/exercise/exercise_events.js',
  '/static/js/features/exercise/index.js',
  '/static/js/features/analysis/analysis_view.js',
  '/static/js/features/analysis/submit_flow.js',
  '/static/js/features/analysis/analysis_events.js',
  '/static/js/features/analysis/index.js',
  '/static/js/features/speech/speech.js',
  '/static/js/features/speech/index.js',
  '/static/js/features/notebook/notebook_storage.js',
  '/static/js/features/notebook/notebook_view.js',
  '/static/js/features/notebook/notebook_events.js',
  '/static/js/features/notebook/index.js',
  '/static/js/features/dictionary/popup_dict.js',
  '/static/js/features/dictionary/dictionary_events.js',
  '/static/js/features/dictionary/index.js',
  '/static/js/features/sync_ui/sync_modal.js',
  '/static/js/features/sync_ui/sync_events.js',
  '/static/js/features/sync_ui/index.js',
  '/static/js/features/pdf_import/pdf_staging.js',
  '/static/js/features/pdf_import/pdf_events.js',
  '/static/js/features/pdf_import/index.js',
  '/static/js/features/events/action_dispatcher.js',
  '/static/js/features/events/navigation_events.js',
  '/static/js/features/events/swipe_rows.js',
  '/static/js/features/events/index.js'
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
