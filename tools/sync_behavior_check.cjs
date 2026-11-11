/**
 * Step 11b: Firestore write-frequency check (fake clock, stubbed Firebase).
 * Expected output (current code): A=1, B_after_14s=1, B_after_16s=2, C_flush_on_hidden=3, D_idle_2min=3.
 * Old code (before 11b) gave A=39 / D=126: syncNow() echoed recordSolvedTask -> new sync every ~1.5s.
 * Usage: node tools/sync_behavior_check.cjs   (server on :8000)
 */
const { chromium } = require('../tests/qa/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ serviceWorkers: 'block' })).newPage();
  await page.clock.install();
  await page.goto((process.env.BASE_URL || 'http://localhost:8000/'));
  await page.waitForFunction(() => window.DokkaiCloudSync && window.DokkaiStorage && window.DokkaiStorage.syncListeners.length > 0); await page.waitForTimeout(4000);
  await page.evaluate(async () => {
    const C = window.DokkaiCloudSync, S = window.DokkaiStorage;
    await S.initPromise;
    await C.initPromise; await new Promise(r => setTimeout(r, 0)); window.__w = [];
    C.user = { uid: 'u', email: null, isAnonymous: true };
    C.db = {};
    C._firebaseFns = {
      doc: (d, ...s) => ({ path: s.join('/') }),
      getDoc: async () => ({ exists: () => false, data: () => null }),
      setDoc: async () => { window.__w.push(Date.now()); }
    };
    await S.recordSolvedTask({ text_id: 1, score: 100 }, false);
    await S.recordSolvedTask({ text_id: 2, score: 50 }, false);
  });
  const writes = async () => { await page.waitForTimeout(600); return page.evaluate(() => window.__w.length); };
  const out = {};
  await page.evaluate(() => window.DokkaiCloudSync.syncNow());            // manual sync (old code looped after this)
  await page.clock.runFor(60000);
  out.A_manual_sync_then_60s_idle = await writes();                       // expect 1
  await page.evaluate(async () => { for (const w of ['a','b','c']) await window.DokkaiStorage.saveWord({ word: w }); });
  await page.clock.runFor(14000);
  out.B_after_14s = await writes();                                       // expect 1 (still debounced)
  await page.clock.runFor(2000);
  out.B_after_16s = await writes();
  await page.evaluate(() => window.DokkaiStorage.saveWord({ word: 'd' }));
  await page.evaluate(() => { Object.defineProperty(document, 'visibilityState', { value: 'hidden', configurable: true }); document.dispatchEvent(new Event('visibilitychange')); });
  await page.clock.runFor(1500);
  out.C_flush_on_hidden = await writes();                                 // expect 3
  await page.clock.runFor(120000);
  out.D_idle_2min = await writes();                                       // expect 3
  console.log(JSON.stringify(out));
  await browser.close();
})();
