/**
 * JLPT Dokkai Master - Interactive Elements Walkthrough & Parity Test
 * Compares behavior of all interactive elements (buttons, inputs, selects, [role=button], [data-action])
 * across main (port 8001) and refactor (port 8000) under mocked network conditions.
 */

const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

const MOCK_SLOTS = {
  profile_key: 'N5:short',
  user_id: 'walkthrough-user',
  slots: [
    {
      position: 1,
      state: 'active',
      text: {
        id: 1,
        title: '図書館の利用時間変更 (N5) #1',
        level: 'N5',
        category: 'short',
        total_questions: 1,
        estimated_reading_time_sec: 180
      }
    },
    {
      position: 2,
      state: 'active',
      text: {
        id: 2,
        title: '留学生パーティー (N5) #2',
        level: 'N5',
        category: 'short',
        total_questions: 1,
        estimated_reading_time_sec: 180
      }
    },
    {
      position: 3,
      state: 'active',
      text: {
        id: 3,
        title: 'アルバイトの募集 (N5) #3',
        level: 'N5',
        category: 'short',
        total_questions: 1,
        estimated_reading_time_sec: 180
      }
    }
  ]
};

const MOCK_SOLVED = {
  items: [
    {
      id: 991,
      text_id: 1,
      title: '図書館の利用時間変更 (N5) #1',
      last_score: 100,
      score: 100,
      perfect: true,
      solved_at: '2026-11-06T10:00:00Z'
    }
  ],
  total: 1
};

const MOCK_TEXT_DETAIL = {
  id: 1,
  title: '図書館の利用時間変更 (N5) #1',
  level: 'N5',
  category: 'short',
  content: '<ruby>図書館<rt>としょかん</rt></ruby>の<ruby>利用<rt>りよう</rt></ruby><ruby>時間<rt>じかん</rt></ruby>について<ruby>案内<rt>あんない</rt></ruby>します。<span id="ev-1-1">来週の月曜日から、閉館時間が午後8時になります。</span>ご注意ください。',
  questions: [
    {
      id: 101,
      question_number: 1,
      text: '来週の月曜日からどうなりますか。',
      options: [
        { id: 201, option_number: 1, text: '午後8時に閉まります' },
        { id: 202, option_number: 2, text: '午後9時に閉まります' },
        { id: 203, option_number: 3, text: '午前8時に開きます' },
        { id: 204, option_number: 4, text: '休館になります' }
      ]
    }
  ]
};

const MOCK_ANALYSIS_DETAIL = {
  id: 1,
  title: '図書館の利用時間変更 (N5) #1',
  level: 'N5',
  category: 'short',
  content: '<ruby>図書館<rt>としょかん</rt></ruby>の<ruby>利用<rt>りよう</rt></ruby><ruby>時間<rt>じかん</rt></ruby>について<ruby>案内<rt>あんない</rt></ruby>します。<span id="ev-1-1">来週の月曜日から、閉館時間が午後8時になります。</span>ご注意ください。',
  translation_ru: 'Объявление о часах работы библиотеки. Со следующего понедельника библиотека закрывается в 20:00.',
  vocabulary: [
    { word: '図書館', reading: 'としょかん', meaning: 'библиотека' },
    { word: '閉館', reading: 'へいかん', meaning: 'закрытие здания' }
  ],
  questions: [
    {
      id: 101,
      question_number: 1,
      text: '来週の月曜日からどうなりますか。',
      evidence_span_id: 'ev-1-1',
      options: [
        { id: 201, option_number: 1, text: '午後8時に閉まります', is_correct: true, explanation: 'Правильно: в тексте указано, что закрытие в 20:00.' },
        { id: 202, option_number: 2, text: '午後9時に閉まります', is_correct: false, trap_type: 'time_trap', explanation: 'Ловушка времени.' },
        { id: 203, option_number: 3, text: '午前8時に開きます', is_correct: false, trap_type: 'opposite_meaning', explanation: 'Ловушка противоположного значения.' },
        { id: 204, option_number: 4, text: '休館になります', is_correct: false, trap_type: 'extreme', explanation: 'Ловушка крайности.' }
      ]
    }
  ]
};

async function setupPageMocks(page) {
  // Capture console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Ignore favicon or non-critical 404s
      if (!text.includes('favicon.ico')) {
        consoleErrors.push(text);
      }
    }
  });

  // Handle unexpected dialogs
  page.on('dialog', async dialog => {
    console.log(`[Dialog dismissed]: ${dialog.message()}`);
    await dialog.dismiss().catch(() => {});
  });

  await page.route('**/api/stream/slots*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_SLOTS)
    });
  });

  await page.route('**/api/stream/solved*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_SOLVED)
    });
  });

  await page.route('**/api/texts/1', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_TEXT_DETAIL)
    });
  });

  await page.route('**/api/stream/solved/1', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MOCK_ANALYSIS_DETAIL)
    });
  });

  await page.route('**/api/stream/complete', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        is_solved: true,
        status: 'solved',
        score: 100,
        score_percent: 100,
        correct_count: 1,
        total_questions: 1,
        time_spent_sec: 15,
        ...MOCK_ANALYSIS_DETAIL,
        solved_task_details: MOCK_ANALYSIS_DETAIL
      })
    });
  });

  await page.route('**/api/dictionary/lookup*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        found: true,
        word: '図書館',
        reading: 'としょかん',
        meaning: 'библиотека',
        level: 'N5'
      })
    });
  });

  await page.route('**/api/admin/drafts*', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ drafts: [], total: 0 })
    });
  });

  return consoleErrors;
}

async function getElementSnapshot(page, selector) {
  return await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    return {
      exists: true,
      isVisible: el.offsetParent !== null || window.getComputedStyle(el).display !== 'none',
      isDisabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
      ariaLabel: el.getAttribute('aria-label') || null,
      ariaExpanded: el.getAttribute('aria-expanded') || null,
      role: el.getAttribute('role') || el.tagName.toLowerCase(),
      tabIndex: el.tabIndex,
      className: el.className || '',
      dataAction: el.getAttribute('data-action') || null,
      innerText: (el.innerText || '').trim().replace(/\s+/g, ' ')
    };
  }, selector);
}

async function runInteractiveWalkthrough() {
  const browser = await chromium.launch({ headless: true });
  const contextMain = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const contextRef = await browser.newContext({ viewport: { width: 1280, height: 800 } });

  const pageMain = await contextMain.newPage();
  const pageRef = await contextRef.newPage();

  const errsMain = await setupPageMocks(pageMain);
  const errsRef = await setupPageMocks(pageRef);

  console.log('Connecting to Main (http://localhost:8001) and Branch (http://localhost:8000)...');
  await pageMain.goto('http://localhost:8001/');
  await pageRef.goto('http://localhost:8000/');

  await pageMain.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });
  await pageRef.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

  const testResults = [];
  let totalDiscrepancies = 0;

  async function testElementAction(screenName, selector, description, actionFn) {
    console.log(`  -> [${screenName}] ${selector} (${description})`);
    const snapM_before = await getElementSnapshot(pageMain, selector);
    const snapR_before = await getElementSnapshot(pageRef, selector);

    if (!snapM_before && !snapR_before) {
      testResults.push({ screen: screenName, selector, description, status: 'SKIPPED (not in DOM)', diff: null });
      return;
    }
    if (!snapM_before || !snapR_before) {
      totalDiscrepancies++;
      testResults.push({
        screen: screenName,
        selector,
        description,
        status: 'FAIL (presence mismatch)',
        diff: `Main: ${Boolean(snapM_before)}, Branch: ${Boolean(snapR_before)}`
      });
      return;
    }

    // Execute interaction on both
    let resM = null;
    let resR = null;
    let actError = null;

    try {
      resM = await actionFn(pageMain, selector);
    } catch (e) {
      actError = `Main Action Error: ${e.message}`;
    }

    try {
      resR = await actionFn(pageRef, selector);
    } catch (e) {
      actError = (actError ? actError + '; ' : '') + `Branch Action Error: ${e.message}`;
    }

    if (actError) {
      totalDiscrepancies++;
      testResults.push({ screen: screenName, selector, description, status: 'FAIL (execution error)', diff: actError });
      return;
    }

    // Compare observed effects
    const snapM_after = await getElementSnapshot(pageMain, selector);
    const snapR_after = await getElementSnapshot(pageRef, selector);

    const diffs = [];
    if (resM && resR) {
      for (const key of Object.keys(resM)) {
        if (resM[key] !== resR[key]) {
          diffs.push(`effect.${key}: Main='${resM[key]}' vs Ref='${resR[key]}'`);
        }
      }
    }
    if (snapM_after.isVisible !== snapR_after.isVisible) {
      diffs.push(`isVisible: Main=${snapM_after.isVisible} vs Ref=${snapR_after.isVisible}`);
    }
    if (snapM_after.isDisabled !== snapR_after.isDisabled) {
      diffs.push(`isDisabled: Main=${snapM_after.isDisabled} vs Ref=${snapR_after.isDisabled}`);
    }

    if (diffs.length > 0) {
      totalDiscrepancies++;
      testResults.push({ screen: screenName, selector, description, status: 'FAIL (effect mismatch)', diff: diffs.join(', ') });
    } else {
      testResults.push({ screen: screenName, selector, description, status: 'PASS', diff: null });
    }
  }

  // =========================================================================
  // Screen 1: Catalog View (Navigation & Filters)
  // =========================================================================
  console.log('[1/9] Testing Interactive Walkthrough: Catalog...');

  // Top Nav Tabs
  await testElementAction('Catalog', '#btn-tab-notebook', 'Switch to Notebook Tab', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      notebookVisible: await page.evaluate(() => !document.getElementById('notebook-view').classList.contains('hidden')),
      catalogVisible: await page.evaluate(() => !document.getElementById('catalog-view').classList.contains('hidden'))
    };
  });

  await testElementAction('Catalog', '#btn-tab-catalog', 'Switch back to Catalog Tab', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      catalogVisible: await page.evaluate(() => !document.getElementById('catalog-view').classList.contains('hidden'))
    };
  });

  await testElementAction('Catalog', '#btn-tab-import', 'Switch to Import PDF Tab', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      importVisible: await page.evaluate(() => !document.getElementById('import-view').classList.contains('hidden'))
    };
  });

  // Switch back to catalog
  await pageMain.click('#btn-tab-catalog');
  await pageRef.click('#btn-tab-catalog');
  await pageMain.waitForTimeout(200);
  await pageRef.waitForTimeout(200);

  // Level Pills (N4)
  await testElementAction('Catalog', '.filter-pill[data-level="N4"]', 'Click N4 Level Filter Pill', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      isActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel)
    };
  });

  // Level Pills (N5)
  await testElementAction('Catalog', '.filter-pill[data-level="N5"]', 'Click N5 Level Filter Pill', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      isActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel)
    };
  });

  // Category Pills (medium)
  await testElementAction('Catalog', '.filter-pill[data-category="medium"]', 'Click Medium Category Pill', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      isActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel)
    };
  });

  // Category Pills (short)
  await testElementAction('Catalog', '.filter-pill[data-category="short"]', 'Click Short Category Pill', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      isActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel)
    };
  });

  // Solved When Pills (all_correct)
  await testElementAction('Catalog', '.filter-pill[data-solved-when="all_correct"]', 'Click Solved-When All Correct Pill', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      isActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel)
    };
  });

  // Refresh slots button
  await testElementAction('Catalog', '#btn-refresh-slots', 'Click Refresh Slots Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      hasSlots: await page.evaluate(() => document.querySelectorAll('#active-slots-list .stream-slot-card').length)
    };
  });

  // =========================================================================
  // Screen 2: Pretest Modal
  // =========================================================================
  console.log('[2/9] Testing Interactive Walkthrough: Pretest Modal...');

  // Open Pretest Modal from slot card
  await testElementAction('Pretest', '#active-slots-list .stream-slot-card button', 'Click First Slot Card Start Button', async (page, sel) => {
    await page.locator(sel).first().click();
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 5000 });
    return {
      modalOpen: await page.evaluate(() => !document.getElementById('pretest-modal-backdrop').classList.contains('hidden'))
    };
  });

  // Toggle Timer on (makes stepper visible)
  await testElementAction('Pretest', 'label:has(#pretest-toggle-timer)', 'Enable Timer Checkbox', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#timer-duration-selector:not(.hidden)', { timeout: 5000 });
    return {
      timerChecked: await page.evaluate(() => document.getElementById('pretest-toggle-timer').checked),
      stepperVisible: await page.evaluate(() => !document.getElementById('timer-duration-selector').classList.contains('hidden'))
    };
  });

  // Stepper plus & minus
  await testElementAction('Pretest', '#btn-timer-plus', 'Click Timer Stepper Plus Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    return {
      minutesText: await page.evaluate(() => document.getElementById('modal-timer-minutes').textContent.trim())
    };
  });

  await testElementAction('Pretest', '#btn-timer-minus', 'Click Timer Stepper Minus Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    return {
      minutesText: await page.evaluate(() => document.getElementById('modal-timer-minutes').textContent.trim())
    };
  });

  // Close Pretest Modal (Cancel)
  await testElementAction('Pretest', '#modal-btn-cancel', 'Click Modal Cancel Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#pretest-modal-backdrop', { state: 'hidden', timeout: 5000 });
    return {
      modalHidden: await page.evaluate(() => document.getElementById('pretest-modal-backdrop').classList.contains('hidden'))
    };
  });

  // Re-open and start exercise
  await pageMain.locator('#active-slots-list .stream-slot-card button').first().click();
  await pageRef.locator('#active-slots-list .stream-slot-card button').first().click();
  await pageMain.waitForSelector('#pretest-modal-backdrop:not(.hidden)');
  await pageRef.waitForSelector('#pretest-modal-backdrop:not(.hidden)');

  await testElementAction('Pretest', '#modal-btn-start', 'Click Start Exercise Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
    return {
      exerciseVisible: await page.evaluate(() => !document.getElementById('exercise-view').classList.contains('hidden'))
    };
  });

  // =========================================================================
  // Screen 3: Exercise Reading View & Question Wizard
  // =========================================================================
  console.log('[3/9] Testing Interactive Walkthrough: Exercise View...');

  // Reader tools in Exercise: Fonts & Sizing
  await testElementAction('Exercise', '#btn-font-mincho', 'Switch to Mincho Font', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    return {
      isMinchoActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel),
      hasMinchoClass: await page.evaluate(() => document.getElementById('passage-content').classList.contains('font-mincho'))
    };
  });

  await testElementAction('Exercise', '#btn-font-gothic', 'Switch back to Gothic Font', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    return {
      isGothicActive: await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel),
      hasGothicClass: await page.evaluate(() => document.getElementById('passage-content').classList.contains('font-gothic'))
    };
  });

  await testElementAction('Exercise', '#btn-font-increase', 'Increase Font Size', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    return {
      fontSize: await page.evaluate(() => document.getElementById('passage-content').style.fontSize)
    };
  });

  await testElementAction('Exercise', '#btn-toggle-popup-dict', 'Toggle Popup Dict Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    const hasActive = await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel);
    await page.click(sel); // restore
    return { toggled: hasActive };
  });

  // Option selection
  await testElementAction('Exercise', '.option-item input[type="radio"]', 'Select Option Radio 1', async (page, sel) => {
    await page.locator(sel).first().click({ timeout: 3000 });
    await page.waitForTimeout(200);
    return {
      isChecked: await page.evaluate((s) => document.querySelector(s).checked, sel),
      isSubmitEnabled: await page.evaluate(() => !document.getElementById('btn-wizard-submit').disabled)
    };
  });

  // Submit answers -> Transitions to Analysis View
  await testElementAction('Exercise', '#btn-wizard-submit', 'Submit Answers', async (page, sel) => {
    await page.click(sel, { timeout: 3000 });
    await page.waitForSelector('#analysis-banner:not(.hidden)', { timeout: 5000 });
    return {
      analysisOpen: await page.evaluate(() => !document.getElementById('analysis-banner').classList.contains('hidden'))
    };
  });

  // =========================================================================
  // Screen 4: Analysis View
  // =========================================================================
  console.log('[4/9] Testing Interactive Walkthrough: Analysis View...');

  // Reading tools: Furigana toggle
  await testElementAction('Analysis', '#btn-toggle-furigana', 'Toggle Furigana Tool Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    const hasClass = await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel);
    await page.click(sel); // toggle back
    return { toggled: hasClass };
  });

  // Reading tools: Evidence toggle
  await testElementAction('Analysis', '#btn-toggle-evidence', 'Toggle Evidence Highlighting Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(100);
    const hasClass = await page.evaluate((s) => document.querySelector(s).classList.contains('active'), sel);
    await page.click(sel); // toggle back
    return { toggled: hasClass };
  });

  // Reading tools: Translation toggle (opens drawer)
  await testElementAction('Analysis', '#btn-toggle-translation', 'Toggle Supplementary Drawer Translation', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    const drawerOpen = await page.evaluate(() => !document.getElementById('supplementary-drawer').classList.contains('hidden'));
    return { drawerOpen };
  });

  // Close drawer
  await testElementAction('Analysis', '#btn-close-drawer', 'Close Supplementary Drawer', async (page, sel) => {
    await page.click(sel);
    await page.waitForTimeout(200);
    return {
      drawerHidden: await page.evaluate(() => document.getElementById('supplementary-drawer').classList.contains('hidden'))
    };
  });

  // Return to Catalog
  await testElementAction('Analysis', '#btn-home', 'Click Brand Logo to Return to Catalog', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#catalog-view:not(.hidden)', { timeout: 10000 });
    return {
      catalogVisible: await page.evaluate(() => !document.getElementById('catalog-view').classList.contains('hidden'))
    };
  });

  // =========================================================================
  // Screen 5: Cloud Sync Modal
  // =========================================================================
  console.log('[5/9] Testing Interactive Walkthrough: Sync Modal...');

  await testElementAction('Sync', '#btn-sync-status', 'Click Sync Status Button to Open Sync Modal', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#sync-modal-backdrop:not(.hidden)', { timeout: 5000 });
    return {
      syncModalOpen: await page.evaluate(() => !document.getElementById('sync-modal-backdrop').classList.contains('hidden'))
    };
  });

  await testElementAction('Sync', '#btn-close-sync-modal', 'Click Close Sync Modal Button', async (page, sel) => {
    await page.click(sel);
    await page.waitForSelector('#sync-modal-backdrop', { state: 'hidden', timeout: 5000 });
    return {
      syncModalHidden: await page.evaluate(() => document.getElementById('sync-modal-backdrop').classList.contains('hidden'))
    };
  });

  // =========================================================================
  // Screen 6: Report Modal
  // =========================================================================
  console.log('[6/9] Testing Interactive Walkthrough: Report Modal...');

  await testElementAction('Report', '#report-modal-backdrop', 'Open and Close Report Modal', async (page, sel) => {
    await page.evaluate(() => document.getElementById('report-modal-backdrop').classList.remove('hidden'));
    await page.waitForTimeout(100);
    const isOpen = await page.evaluate(() => !document.getElementById('report-modal-backdrop').classList.contains('hidden'));
    await page.click('#btn-cancel-report');
    await page.waitForTimeout(100);
    const isClosed = await page.evaluate(() => document.getElementById('report-modal-backdrop').classList.contains('hidden'));
    return { isOpen, isClosed };
  });

  // =========================================================================
  // Screen 7: Keyboard Navigation (Escape Key to close modals)
  // =========================================================================
  console.log('[7/9] Testing Interactive Walkthrough: Keyboard Escape Navigation...');

  await testElementAction('Keyboard', 'body', 'Press Escape to close open modal', async (page) => {
    // Open sync modal
    await page.click('#btn-sync-status');
    await page.waitForSelector('#sync-modal-backdrop:not(.hidden)');
    // Press Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
    return {
      syncModalClosedOnEscape: await page.evaluate(() => document.getElementById('sync-modal-backdrop').classList.contains('hidden'))
    };
  });

  // Check console errors
  console.log('\n--- Console Errors Check ---');
  console.log(`Main Console Errors: ${errsMain.length}`);
  console.log(`Branch Console Errors: ${errsRef.length}`);
  if (errsRef.length > 0) {
    totalDiscrepancies++;
    console.error('Branch console errors:', errsRef);
  }

  await browser.close();

  // Print Summary Table
  console.log('\n=============================================================');
  console.log('INTERACTIVE WALKTHROUGH TEST REPORT');
  console.log('=============================================================');
  console.log('| Screen / State | Target Element | Action / Description | Status | Discrepancy Details |');
  console.log('| :--- | :--- | :--- | :---: | :--- |');

  for (const r of testResults) {
    console.log(`| ${r.screen} | \`${r.selector}\` | ${r.description} | **${r.status}** | ${r.diff || '—'} |`);
  }

  console.log('\n-------------------------------------------------------------');
  if (totalDiscrepancies === 0 && errsRef.length === 0) {
    console.log(`✓ ALL ${testResults.length} INTERACTIVE CHECKS PASSED IDENTICALLY! (0 discrepancies)`);
    process.exit(0);
  } else {
    console.error(`✗ FOUND ${totalDiscrepancies} DISCREPANCIES / ERRORS!`);
    process.exit(1);
  }
}

runInteractiveWalkthrough().catch(err => {
  console.error(err);
  process.exit(1);
});
