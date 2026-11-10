/**
 * Unit / Semantics Test Suite for Dokkai Action Dispatcher (Check 4)
 * Verifies:
 * (a) 1 click = exactly 1 invocation (no duplicate on label:has(input))
 * (б) stopPropagation in nested buttons prevents parent action dispatch
 * (в) disabled elements (disabled attribute and aria-disabled="true") do not trigger action
 * (г) keyboard (Enter / Space) on [data-action]:not(button) works identically to click
 */

const path = require('path');
const { chromium } = require(path.resolve(__dirname, 'qa/node_modules/@playwright/test'));

async function runSemanticsSuite() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Load the application to get window.DokkaiEvents initialized
  await page.goto('http://localhost:8000/');
  await page.waitForFunction(() => window.DokkaiEvents && typeof window.DokkaiEvents.registerAction === 'function');

  console.log('Testing Action Dispatcher Semantics...');

  const results = await page.evaluate(async () => {
    const logs = [];
    const assert = (condition, name) => {
      if (!condition) {
        throw new Error(`Assertion failed: ${name}`);
      }
      logs.push({ name, status: 'PASS' });
    };

    // Test Container
    const container = document.createElement('div');
    container.id = 'test-dispatcher-container';
    document.body.appendChild(container);

    // =========================================================================
    // Test (a): 1 click = exactly 1 invocation on <label data-action="..."> <input type="checkbox">
    // =========================================================================
    let labelCallCount = 0;
    window.DokkaiEvents.registerAction('test-label-action', () => {
      labelCallCount++;
    });

    container.innerHTML = `
      <label id="test-label" data-action="test-label-action">
        <input type="checkbox" id="test-label-cb"> Clickable Label
      </label>
    `;

    const labelEl = document.getElementById('test-label');
    labelEl.click();
    assert(labelCallCount === 1, `(a) label:has(input) clicked once produces exactly 1 call (got ${labelCallCount})`);

    // =========================================================================
    // Test (b): stopPropagation in nested buttons prevents parent action dispatch
    // =========================================================================
    let parentCallCount = 0;
    let childCallCount = 0;
    window.DokkaiEvents.registerAction('test-parent-action', () => { parentCallCount++; });
    window.DokkaiEvents.registerAction('test-child-action', (el, e) => {
      childCallCount++;
      if (e && e.stopPropagation) e.stopPropagation();
    });

    container.innerHTML = `
      <div id="test-parent-card" data-action="test-parent-action">
        <button type="button" id="test-nested-btn" data-action="test-child-action">Nested Button</button>
      </div>
    `;

    const nestedBtn = document.getElementById('test-nested-btn');
    nestedBtn.click();
    assert(childCallCount === 1, `(b.1) child action called once (got ${childCallCount})`);
    assert(parentCallCount === 0, `(b.2) parent action NOT called when child handles click (got ${parentCallCount})`);

    // Also test native button with addEventListener calling stopPropagation
    let regularChildClicked = false;
    parentCallCount = 0;
    container.innerHTML = `
      <div id="test-parent-card-2" data-action="test-parent-action">
        <button type="button" id="test-native-btn">Native StopPropagation Button</button>
      </div>
    `;
    const nativeBtn = document.getElementById('test-native-btn');
    nativeBtn.addEventListener('click', (e) => {
      regularChildClicked = true;
      e.stopPropagation();
    });
    nativeBtn.click();
    assert(regularChildClicked === true, `(b.3) native button listener invoked`);
    assert(parentCallCount === 0, `(b.4) parent action NOT called when native child calls stopPropagation (got ${parentCallCount})`);

    // =========================================================================
    // Test (c): Disabled elements do NOT trigger action
    // =========================================================================
    let disabledCallCount = 0;
    window.DokkaiEvents.registerAction('test-disabled-action', () => { disabledCallCount++; });

    container.innerHTML = `
      <button type="button" id="test-disabled-btn" data-action="test-disabled-action" disabled>Disabled</button>
      <div id="test-aria-disabled" data-action="test-disabled-action" aria-disabled="true" role="button" tabindex="0">Aria Disabled</div>
    `;

    const disabledBtn = document.getElementById('test-disabled-btn');
    disabledBtn.click();
    assert(disabledCallCount === 0, `(c.1) native disabled button did not trigger action (got ${disabledCallCount})`);

    const ariaDisabled = document.getElementById('test-aria-disabled');
    ariaDisabled.click();
    assert(disabledCallCount === 0, `(c.2) aria-disabled element did not trigger action (got ${disabledCallCount})`);

    // =========================================================================
    // Test (г): Keyboard Enter / Space on [data-action]:not(button) works identically to click
    // =========================================================================
    let keyCallCount = 0;
    window.DokkaiEvents.registerAction('test-key-action', () => { keyCallCount++; });

    container.innerHTML = `
      <div id="test-key-div" data-action="test-key-action" role="button" tabindex="0">
        <span>Keyboard Nav Item</span>
      </div>
    `;

    const keyDiv = document.getElementById('test-key-div');

    // Enter keydown
    keyDiv.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }));
    assert(keyCallCount === 1, `(г.1) Enter key triggered action (got ${keyCallCount})`);

    // Space keydown
    keyDiv.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true, cancelable: true }));
    assert(keyCallCount === 2, `(г.2) Space key triggered action (got ${keyCallCount})`);

    // Clean up
    container.remove();
    return logs;
  });

  await browser.close();

  console.log('\n--- Semantics Test Results ---');
  for (const r of results) {
    console.log(`✓ ${r.name}`);
  }
  console.log(`\nALL ${results.length} ACTION DISPATCHER SEMANTICS TESTS PASSED!`);
}

runSemanticsSuite().catch(err => {
  console.error('Semantics test failed:', err);
  process.exit(1);
});
