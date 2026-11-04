import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('12. Service Worker Safety, Network-First Strategy & Cache Integrity', () => {
  test.describe.configure({ mode: 'serial' });

  test('01. Recursive Import Graph: All index.html assets and transitively imported ES modules are precached in sw.js', async () => {
    const staticDir = path.resolve(__dirname, '../../../static');
    const indexPath = path.join(staticDir, 'index.html');
    const swPath = path.join(staticDir, 'sw.js');

    const indexHtml = fs.readFileSync(indexPath, 'utf-8');
    const swJs = fs.readFileSync(swPath, 'utf-8');

    // 1. Extract links and scripts from index.html
    const linkMatches = [...indexHtml.matchAll(/<link\s+[^>]*href="(\/static\/css\/[^"]+)"/g)].map(m => m[1]);
    const scriptMatches = [...indexHtml.matchAll(/<script\s+[^>]*src="(\/static\/[^"]+)"/g)].map(m => m[1]);

    // 2. Recursive ES Module import graph crawler
    const visitedFiles = new Set<string>();
    const discoveredJsModules = new Set<string>();

    function crawlModuleImports(filePath: string) {
      if (visitedFiles.has(filePath) || !fs.existsSync(filePath)) return;
      visitedFiles.add(filePath);

      const content = fs.readFileSync(filePath, 'utf-8');
      // Match static import ... from '...' and dynamic import('...')
      const importRegex = /(?:import\s+.*?from\s+['"]([^'"]+)['"]|import\s*\(\s*['"]([^'"]+)['"]\s*\))/g;
      let match;
      while ((match = importRegex.exec(content)) !== null) {
        const importSpecifier = match[1] || match[2];
        if (importSpecifier && importSpecifier.startsWith('.')) {
          const resolvedPath = path.resolve(path.dirname(filePath), importSpecifier);
          const fullPath = resolvedPath.endsWith('.js') ? resolvedPath : resolvedPath + '.js';
          if (fs.existsSync(fullPath)) {
            // Convert to web-relative /static/... path
            const relativeToStatic = path.relative(staticDir, fullPath).replace(/\\/g, '/');
            const webPath = `/static/${relativeToStatic}`;
            discoveredJsModules.add(webPath);
            crawlModuleImports(fullPath);
          }
        }
      }
    }

    // Crawl all entry scripts
    for (const script of scriptMatches) {
      const cleanPath = script.split('?')[0].replace(/^\/static\//, '');
      const fullPath = path.join(staticDir, cleanPath);
      crawlModuleImports(fullPath);
    }

    const allRequiredAssets = Array.from(new Set([...linkMatches, ...scriptMatches, ...discoveredJsModules]));
    expect(allRequiredAssets.length).toBeGreaterThanOrEqual(15);

    // 3. Extract PRECACHE_ASSETS from sw.js
    const precacheMatch = swJs.match(/const\s+PRECACHE_ASSETS\s*=\s*\[([\s\S]*?)\];/);
    expect(precacheMatch).not.toBeNull();
    const precacheListRaw = precacheMatch![1];

    for (const asset of allRequiredAssets) {
      const assetClean = asset.split('?')[0];
      const isPrecached = precacheListRaw.includes(asset) || precacheListRaw.includes(assetClean);
      expect(isPrecached, `Asset '${asset}' (transitively imported) must be declared in PRECACHE_ASSETS of sw.js`).toBe(true);
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

    // Verify ZERO backend /api/ requests in cache (distinguishing from static /static/js/api/)
    const apiLeaks = cachedUrls.filter(u => {
      try {
        const pathname = new URL(u).pathname;
        return pathname.startsWith('/api/') || pathname === '/api';
      } catch {
        return false;
      }
    });
    expect(apiLeaks, 'Backend /api/ endpoints must NEVER be stored in Service Worker cache').toHaveLength(0);

    // Verify ZERO Firebase / Google cross-origin requests in cache
    const crossOriginLeaks = cachedUrls.filter(u => {
      if (u.includes('/static/firebase-config.js')) return false;
      return u.includes('googleapis.com') || u.includes('gstatic.com') || u.includes('firebase') || u.includes('identitytoolkit');
    });
    expect(crossOriginLeaks, 'Cross-origin Firebase/Google auth requests must NEVER be stored in Service Worker cache').toHaveLength(0);
  });

  test('04. New Version Deployment: Upgrading cache version purges old caches automatically', async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // 1. Ensure initial Service Worker is active and cached
    await page.waitForFunction(() => {
      return caches.keys().then(keys => keys.includes('dokkai-v2.1.0'));
    }, { timeout: 10000 });

    // 2. Deploy Version B (simulated via updated sw.js?version=2.2.0-test)
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker.getRegistrations();
      for (const r of regs) await r.unregister();
      await navigator.serviceWorker.register('/sw.js?version=2.2.0-test', { scope: '/' });
    });

    // 3. Poll cache storage until Version B is active and old Version A is purged
    await expect.poll(async () => {
      return await page.evaluate(async () => await caches.keys());
    }, { timeout: 15000, intervals: [200, 500, 1000] }).toEqual(['dokkai-v2.2.0-test']);

    await context.close();
  });
});
