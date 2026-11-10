/**
 * Listener Leak Audit Test (Step 6d)
 * Verifies that:
 * 1. Re-rendering dynamic lists (slots, solved tasks, notebook words) 5 times does NOT attach duplicate listeners.
 * 2. Re-invoking initEventListeners() or switching views does not accumulate listeners on window/document.
 * 3. Total listener accumulation delta = 0 across repeated lifecycle passes.
 */

const path = require('path');
const { chromium } = require(path.resolve(__dirname, 'qa/node_modules/@playwright/test'));

async function runListenerLeakAudit() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.error('PAGE ERROR:', err));

  // Inject tracking before page scripts run
  await page.addInitScript(() => {
    window.__eventListenerRegistry = new Map();

    const originalAdd = EventTarget.prototype.addEventListener;
    const originalRemove = EventTarget.prototype.removeEventListener;

    EventTarget.prototype.addEventListener = function(type, listener, options) {
      if (!this.__activeListeners) {
        this.__activeListeners = [];
      }
      this.__activeListeners.push({ type, listener, options });
      return originalAdd.call(this, type, listener, options);
    };

    EventTarget.prototype.removeEventListener = function(type, listener, options) {
      if (this.__activeListeners) {
        const idx = this.__activeListeners.findIndex(l => l.type === type && l.listener === listener);
        if (idx !== -1) {
          this.__activeListeners.splice(idx, 1);
        }
      }
      return originalRemove.call(this, type, listener, options);
    };
  });

  await page.goto('http://localhost:8000/');
  await page.waitForSelector('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder', { timeout: 15000 });

  console.log('Auditing Event Listener Leaks across 5 dynamic render & navigation passes...');

  const auditReport = await page.evaluate(async () => {
    const results = [];

    const getListenerCounts = () => {
      let docCount = document.__activeListeners ? document.__activeListeners.length : 0;
      let winCount = window.__activeListeners ? window.__activeListeners.length : 0;
      let elementCount = 0;
      const allEls = document.querySelectorAll('*');
      for (const el of allEls) {
        if (el.__activeListeners) {
          elementCount += el.__activeListeners.length;
        }
      }
      return { docCount, winCount, elementCount, total: docCount + winCount + elementCount };
    };

    const initial = getListenerCounts();

    // Pass 1-5: Re-render dynamic lists repeatedly
    for (let pass = 1; pass <= 5; pass++) {
      // 1. Re-render notebook words
      if (window.renderNotebookWords) {
        window.renderNotebookWords();
      }

      // 2. Re-render solved tasks
      if (window.fetchAndRenderSolvedTasks) {
        await window.fetchAndRenderSolvedTasks();
      }

      // 3. Re-render slots
      if (window.fetchAndRenderSlots) {
        await window.fetchAndRenderSlots(true);
      }

      // 4. Tab navigation cycle
      if (window.switchMainTab) {
        window.switchMainTab('notebook', false);
        window.switchMainTab('import', false);
        window.switchMainTab('catalog', false);
      }
    }

    const afterRenders = getListenerCounts();

    // Pass 6-10: Repeated initEventListeners calls
    for (let pass = 1; pass <= 5; pass++) {
      if (typeof window.initEventListeners === 'function') {
        window.initEventListeners();
      }
    }

    const afterReInit = getListenerCounts();

    results.push({
      metric: 'Window & Document Listeners',
      initial: initial.winCount + initial.docCount,
      after5Renders: afterRenders.winCount + afterRenders.docCount,
      after5ReInits: afterReInit.winCount + afterReInit.docCount,
      leaked: (afterReInit.winCount + afterReInit.docCount) - (initial.winCount + initial.docCount)
    });

    results.push({
      metric: 'DOM Elements Listeners',
      initial: initial.elementCount,
      after5Renders: afterRenders.elementCount,
      after5ReInits: afterReInit.elementCount,
      leaked: afterReInit.elementCount - initial.elementCount
    });

    results.push({
      metric: 'Total System Listeners',
      initial: initial.total,
      after5Renders: afterRenders.total,
      after5ReInits: afterReInit.total,
      leaked: afterReInit.total - initial.total
    });

    return results;
  });

  await browser.close();

  console.log('\n=============================================================');
  console.log('EVENT LISTENER LEAK AUDIT REPORT (Step 6d)');
  console.log('=============================================================');
  console.log('| Metric | Initial | After 5 Dynamic Renders | After 5 Re-Inits | Leaked Delta | Status |');
  console.log('| :--- | :---: | :---: | :---: | :---: | :---: |');

  let hasLeak = false;
  for (const r of auditReport) {
    const status = r.leaked === 0 ? '**PASS (0 leak)**' : '**FAIL**';
    if (r.leaked !== 0) hasLeak = true;
    console.log(`| ${r.metric} | ${r.initial} | ${r.after5Renders} | ${r.after5ReInits} | ${r.leaked} | ${status} |`);
  }

  if (!hasLeak) {
    console.log('\n✓ ZERO LISTENER LEAKS CONFIRMED! Full idempotency verified.');
    process.exit(0);
  } else {
    console.error('\n✗ LISTENER LEAK DETECTED!');
    process.exit(1);
  }
}

runListenerLeakAudit().catch(err => {
  console.error('Audit execution error:', err);
  process.exit(1);
});
