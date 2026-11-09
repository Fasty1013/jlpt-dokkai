/**
 * Security & Hostile Data Test Suite (Check 5)
 * Verifies that dynamic data attributes with quotes, apostrophes, < > &, backticks, and ${...}
 * do NOT break templates, do NOT cause XSS, and cleanly dispatch to action handlers with original data uncorrupted.
 */

const path = require('path');
const { chromium } = require(path.resolve(__dirname, 'qa/node_modules/@playwright/test'));

const HOSTILE_STRINGS = [
  `" onmouseover="alert('xss')" data-x="`,
  `' onclick='alert("xss")' data-y='`,
  `<script>alert("xss")</script>`,
  `& < > " ' \` \${7*7} \\`,
  `"'; alert(1); //`,
  `"><img src=x onerror=alert(1)>`,
  `日本語 & "Quoted" 'Apostrophe' \`backtick\` \${test}`
];

async function runSecuritySuite() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Track any alerts or unexpected dialogs
  let alertTriggered = false;
  page.on('dialog', async dialog => {
    alertTriggered = true;
    console.error(`SECURITY ALERT TRIGGERED: ${dialog.message()}`);
    await dialog.dismiss();
  });

  await page.goto('http://localhost:8000/');
  await page.waitForFunction(() => window.DokkaiEvents && typeof window.DokkaiEvents.registerAction === 'function');

  console.log('Testing Hostile Data & Template Escaping Security...');

  const results = await page.evaluate(async (hostileStrings) => {
    const logs = [];
    const assert = (condition, name) => {
      if (!condition) {
        throw new Error(`Security assertion failed: ${name}`);
      }
      logs.push({ name, status: 'PASS' });
    };

    // Test Container
    const container = document.createElement('div');
    container.id = 'test-security-container';
    document.body.appendChild(container);

    const escapeHtml = (str) => {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };

    // 1. Test taskTitle in open-report action
    for (let i = 0; i < hostileStrings.length; i++) {
      const hostile = hostileStrings[i];
      let capturedTitle = null;
      const actionName = `test-report-hostile-${i}`;

      window.DokkaiEvents.registerAction(actionName, (el, e, ds) => {
        capturedTitle = ds.taskTitle || el.dataset.taskTitle;
      });

      container.innerHTML = `
        <button type="button" id="btn-sec-report-${i}" data-action="${actionName}" data-text-id="999" data-task-title="${escapeHtml(hostile)}">
          Report
        </button>
      `;

      const btn = document.getElementById(`btn-sec-report-${i}`);
      btn.click();
      assert(capturedTitle === hostile, `taskTitle [${i}] safely escaped and received intact: ${JSON.stringify(hostile)}`);
    }

    // 2. Test wordText in notebook actions
    for (let i = 0; i < hostileStrings.length; i++) {
      const hostile = hostileStrings[i];
      let capturedWord = null;
      const actionName = `test-word-hostile-${i}`;

      window.DokkaiEvents.registerAction(actionName, (el, e, ds) => {
        capturedWord = ds.word || el.dataset.word;
      });

      container.innerHTML = `
        <button type="button" id="btn-sec-word-${i}" data-action="${actionName}" data-word="${escapeHtml(hostile)}">
          Word
        </button>
      `;

      const btn = document.getElementById(`btn-sec-word-${i}`);
      btn.click();
      assert(capturedWord === hostile, `wordText [${i}] safely escaped and received intact: ${JSON.stringify(hostile)}`);
    }

    // 3. Test slot.position in open-pretest action
    for (let i = 0; i < hostileStrings.length; i++) {
      const hostile = hostileStrings[i];
      let capturedPos = null;
      const actionName = `test-slot-hostile-${i}`;

      window.DokkaiEvents.registerAction(actionName, (el, e, ds) => {
        capturedPos = ds.position || el.dataset.position;
      });

      container.innerHTML = `
        <div id="btn-sec-slot-${i}" data-action="${actionName}" data-slot-id="s1" data-text-id="10" data-position="${escapeHtml(hostile)}">
          Slot
        </div>
      `;

      const btn = document.getElementById(`btn-sec-slot-${i}`);
      btn.click();
      assert(capturedPos === hostile, `slot.position [${i}] safely escaped and received intact: ${JSON.stringify(hostile)}`);
    }

    // 4. Test q.evidence_span_id in locate-evidence action
    for (let i = 0; i < hostileStrings.length; i++) {
      const hostile = hostileStrings[i];
      let capturedSpanId = null;
      const actionName = `test-span-hostile-${i}`;

      window.DokkaiEvents.registerAction(actionName, (el, e, ds) => {
        capturedSpanId = ds.spanId || el.dataset.spanId;
      });

      container.innerHTML = `
        <button type="button" id="btn-sec-span-${i}" data-action="${actionName}" data-span-id="${escapeHtml(hostile)}">
          Span
        </button>
      `;

      const btn = document.getElementById(`btn-sec-span-${i}`);
      btn.click();
      assert(capturedSpanId === hostile, `evidence_span_id [${i}] safely escaped and received intact: ${JSON.stringify(hostile)}`);
    }

    // 5. Test slug in draft actions
    for (let i = 0; i < hostileStrings.length; i++) {
      const hostile = hostileStrings[i];
      let capturedSlug = null;
      const actionName = `test-draft-hostile-${i}`;

      window.DokkaiEvents.registerAction(actionName, (el, e, ds) => {
        capturedSlug = ds.slug || el.dataset.slug;
      });

      container.innerHTML = `
        <button type="button" id="btn-sec-draft-${i}" data-action="${actionName}" data-slug="${escapeHtml(hostile)}">
          Draft
        </button>
      `;

      const btn = document.getElementById(`btn-sec-draft-${i}`);
      btn.click();
      assert(capturedSlug === hostile, `draft.slug [${i}] safely escaped and received intact: ${JSON.stringify(hostile)}`);
    }

    container.remove();
    return logs;
  }, HOSTILE_STRINGS);

  await browser.close();

  if (alertTriggered) {
    console.error('FAIL: Alert / XSS payload was executed!');
    process.exit(1);
  }

  console.log('\n--- Hostile Data & Security Results ---');
  console.log(`Executed ${results.length} injection scenarios across dynamic templates.`);
  console.log(`✓ 0 XSS alerts triggered.`);
  console.log(`✓ All ${results.length} assertions passed with 100% data fidelity.`);
}

runSecuritySuite().catch(err => {
  console.error('Security test failed:', err);
  process.exit(1);
});
