import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('12. Service Worker Safety, Network-First Strategy & Cache Integrity', () => {

  test('01. Automated Asset Parity: All index.html <link> and <script> tags are precached in sw.js', async () => {
    const indexPath = path.resolve(__dirname, '../../../static/index.html');
    const swPath = path.resolve(__dirname, '../../../static/sw.js');

    const indexHtml = fs.readFileSync(indexPath, 'utf-8');
    const swJs = fs.readFileSync(swPath, 'utf-8');

    // Extract all local css links
    const linkMatches = [...indexHtml.matchAll(/<link\s+[^>]*href="(\/static\/css\/[^"]+)"/g)].map(m => m[1]);
    // Extract all local script src
    const scriptMatches = [...indexHtml.matchAll(/<script\s+[^>]*src="(\/static\/[^"]+)"/g)].map(m => m[1]);

    const requiredAssets = [...linkMatches, ...scriptMatches];
    expect(requiredAssets.length).toBeGreaterThan(0);

    // Extract PRECACHE_ASSETS from sw.js
    const precacheMatch = swJs.match(/const\s+PRECACHE_ASSETS\s*=\s*\[([\s\S]*?)\];/);
    expect(precacheMatch).not.toBeNull();
    const precacheListRaw = precacheMatch![1];

    for (const asset of requiredAssets) {
      // Normalize asset path (with or without ?v= query)
      const assetClean = asset.split('?')[0];
      const isPrecached = precacheListRaw.includes(asset) || precacheListRaw.includes(assetClean);
      expect(isPrecached, `Asset '${asset}' from index.html must be declared in PRECACHE_ASSETS of sw.js`).toBe(true);
    }
  });

  test('02. Network-First Strategy: Online users always receive fresh content from network', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // Wait for Service Worker controller to be ready
    await page.waitForFunction(() => Boolean(navigator.serviceWorker && navigator.serviceWorker.controller), { timeout: 8000 }).catch(() => null);

    // Track network request for static asset
    let networkFetched = false;
    page.on('response', resp => {
      if (resp.url().includes('/static/css/catalog.css')) {
        networkFetched = true;
      }
    });

    // Reload page while online: Network-First MUST trigger network request
    await page.reload({ waitUntil: 'domcontentloaded' });
    expect(networkFetched, 'Network-First must issue network requests when online, avoiding stale cache-first lock').toBe(true);
  });

  test('03. Strict Isolation: /api/* endpoints and Firebase/Google Auth NEVER enter Cache Storage', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

    // Trigger API calls and ensure cache does not touch them
    await page.evaluate(async () => {
      await fetch('/api/texts');
      await fetch('/api/stream/slots');
    });

    // Inspect Cache Storage keys
    const cachedUrls: string[] = await page.evaluate(async () => {
      const keys = await caches.keys();
      const allUrls: string[] = [];
      for (const k of keys) {
        const cache = await caches.open(k);
        const reqs = await cache.keys();
        for (const r of reqs) {
          allUrls.push(r.url);
        }
      }
      return allUrls;
    });

    // Verify ZERO /api/ requests in cache
    const apiLeaks = cachedUrls.filter(u => u.includes('/api/'));
    expect(apiLeaks, 'Backend /api/ endpoints must NEVER be stored in Service Worker cache').toHaveLength(0);

    // Verify ZERO Firebase / Google cross-origin requests in cache
    const crossOriginLeaks = cachedUrls.filter(u => {
      if (u.includes('/static/firebase-config.js')) return false;
      return u.includes('googleapis.com') || u.includes('gstatic.com') || u.includes('firebase') || u.includes('identitytoolkit');
    });
    expect(crossOriginLeaks, 'Cross-origin Firebase/Google auth requests must NEVER be stored in Service Worker cache').toHaveLength(0);
  });
});
