/**
 * Step 10 stress scenarios (localhost only). Run: node tools/stress_scenarios.cjs [baseUrl]
 * Cold start, blocked/broken IndexedDB, offline reload with Service Worker, wiped caches.
 * Pass criteria: no pageerror, catalog renders (or app shell loads offline).
 */
const path = require('path');
const { chromium } = require(path.join(__dirname, '..', 'tests', 'qa', 'node_modules', 'playwright'));

const BASE = process.argv[2] || 'http://localhost:8000';
if (!/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(BASE)) {
  console.error('Refusing to run against non-localhost URL');
  process.exit(2);
}

const results = [];
async function scenario(name, fn) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  const t0 = Date.now();
  let note = '';
  try {
    note = (await fn(page, ctx)) || '';
  } catch (e) {
    errors.push('SCENARIO: ' + e.message.split('\n')[0]);
  }
  const ok = errors.length === 0;
  results.push({ name, ok, ms: Date.now() - t0, note, errors });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}  (${Date.now() - t0} ms) ${note}${ok ? '' : '\n      ' + errors.join('\n      ')}`);
  await browser.close();
}

const catalogReady = (page) => page.waitForSelector('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder', { timeout: 20000 });

(async () => {
  await scenario('01 cold start', async (page) => {
    await page.goto(BASE + '/');
    await catalogReady(page);
    return 'catalog rendered';
  });

  await scenario('02 IndexedDB unavailable (localStorage fallback)', async (page) => {
    await page.addInitScript(() => { Object.defineProperty(window, 'indexedDB', { value: undefined, configurable: true }); });
    await page.goto(BASE + '/');
    await catalogReady(page);
    const mode = await page.evaluate(() => window.DokkaiStorage.useFallback);
    if (!mode) throw new Error('expected useFallback=true');
    return 'useFallback=true';
  });

  await scenario('03 IndexedDB.open throws', async (page) => {
    await page.addInitScript(() => { window.indexedDB.open = () => { throw new Error('boom'); }; });
    await page.goto(BASE + '/');
    await catalogReady(page);
    const mode = await page.evaluate(() => window.DokkaiStorage.useFallback);
    if (!mode) throw new Error('expected useFallback=true');
    return 'fell back';
  });

  await scenario('04 IndexedDB.open fires error event', async (page) => {
    await page.addInitScript(() => {
      window.indexedDB.open = () => {
        const req = {};
        setTimeout(() => req.onerror && req.onerror({ target: { error: new Error('corrupt') } }), 0);
        return req;
      };
    });
    await page.goto(BASE + '/');
    await catalogReady(page);
    const mode = await page.evaluate(() => window.DokkaiStorage.useFallback);
    if (!mode) throw new Error('expected useFallback=true');
    return 'fell back';
  });

  await scenario('05 corrupted localStorage fallback payloads', async (page) => {
    await page.addInitScript(() => {
      Object.defineProperty(window, 'indexedDB', { value: undefined, configurable: true });
      localStorage.setItem('dokkai_idb_solved_tasks', '{not json');
      localStorage.setItem('dokkai_idb_notebook', '[[[');
      localStorage.setItem('dokkai_idb_settings', 'null{');
      localStorage.setItem('dokkai_firebase_config', '{bad');
    });
    await page.goto(BASE + '/');
    await catalogReady(page);
  });

  await scenario('06 offline reload with Service Worker cache', async (page, ctx) => {
    await page.goto(BASE + '/');
    await catalogReady(page);
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.waitForTimeout(2500);
    await ctx.setOffline(true);
    await page.reload({ waitUntil: 'domcontentloaded' });
    const title = await page.title();
    const hasShell = await page.locator('#app, main, body').first().isVisible();
    if (!title || !hasShell) throw new Error('app shell not served offline');
    return `offline shell ok, title="${title}"`;
  });

  await scenario('07 wiped Cache Storage, then reload', async (page) => {
    await page.goto(BASE + '/');
    await catalogReady(page);
    await page.evaluate(async () => { for (const k of await caches.keys()) await caches.delete(k); });
    await page.reload();
    await catalogReady(page);
  });

  await scenario('08 API down (all /api/* fail) does not crash the page', async (page) => {
    await page.route('**/api/**', (r) => r.abort('failed'));
    await page.goto(BASE + '/');
    await page.waitForTimeout(4000);
    const alive = await page.evaluate(() => document.readyState);
    if (alive !== 'complete') throw new Error('page not loaded: ' + alive);
  });

  await scenario('09 cloud sync without credentials stays local', async (page) => {
    await page.goto(BASE + '/');
    await catalogReady(page);
    const st = await page.evaluate(async () => { await window.DokkaiCloudSync.init(); return window.DokkaiCloudSync.status; });
    if (!['local', 'offline'].includes(st)) throw new Error('unexpected status ' + st);
    return 'status=' + st;
  });

  const failed = results.filter((r) => !r.ok).length;
  console.log(`\n${results.length - failed}/${results.length} scenarios passed`);
  process.exit(failed ? 1 : 0);
})();
