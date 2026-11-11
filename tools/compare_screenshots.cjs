const fs = require('fs');
const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

const RUN_USER_ID = `screenshots-${Date.now().toString(36)}`;
const ANSWER_OPTION_TEXT = '午前9時から午後6時まで'; // text 1, question 1 (wrong answer)

const MOCK_SLOTS = {
  profile_key: 'N5:short',
  user_id: 'screenshot-user',
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

async function captureScreenshotsForTarget(baseUrl, targetName, outDir) {
  const browser = await chromium.launch({ headless: true });

  const viewports = [
    { name: 'desktop', width: 1280, height: 800, isMobile: false },
    { name: 'mobile', width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }
  ];

  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      isMobile: vp.isMobile,
      hasTouch: vp.isMobile,
      deviceScaleFactor: vp.deviceScaleFactor || 1
    });

    const page = await context.newPage();

    // Freeze clock and animations
    await page.addInitScript((runUserId) => {
      // Freeze Date.now and animations
      const fixedTime = 1793966400000;
      Date.now = () => fixedTime;
      // Step 11d shuffles options by HMAC(user_id | text_id | attempt). A random per-tab user_id gave
      // main and branch different option orders. A fresh id per run and viewport, identical for both
      // servers, gives both the same order (attempt 0). See docs/INTENTIONAL_DIFFERENCES.md, I19.
      try { localStorage.setItem('dokkai_user_id', runUserId); } catch { /* storage unavailable */ }
    }, `${RUN_USER_ID}-${vp.name}`);

    // Mock API requests for deterministic data
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

    // 1. Catalog screen
    await page.goto(baseUrl);
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });
    // Disable any CSS transitions/animations for pure visual diff
    await page.addStyleTag({
      content: `*, *::before, *::after { transition: none !important; animation: none !important; }`
    });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);
    const catalogPath = path.join(outDir, `${targetName}_${vp.name}_catalog.png`);
    await page.screenshot({ path: catalogPath, fullPage: false });

    // 2. Pretest Modal
    const slotBtn = page.locator('#active-slots-list .stream-slot-card button').first();
    if (await slotBtn.isVisible()) {
      await slotBtn.click();
      await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(500);
      const pretestPath = path.join(outDir, `${targetName}_${vp.name}_pretest.png`);
      await page.screenshot({ path: pretestPath, fullPage: false });

      // Close modal cleanly via real close button
      const closeBtn = page.locator('#modal-btn-close');
      if (await closeBtn.isVisible()) {
        await closeBtn.click();
        await page.waitForSelector('#pretest-modal-backdrop', { state: 'hidden', timeout: 10000 });
      }
    }

    // 3. Report Modal
    await page.evaluate(() => {
      const modal = document.getElementById('report-modal-backdrop');
      if (modal) {
        modal.classList.remove('hidden');
        const titleEl = document.getElementById('report-modal-task-title');
        if (titleEl) titleEl.textContent = '図書館の利用時間変更 (N5) #1';
      }
    });
    await page.waitForSelector('#report-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.waitForTimeout(500);
    const reportPath = path.join(outDir, `${targetName}_${vp.name}_report.png`);
    await page.screenshot({ path: reportPath, fullPage: false });

    // Cleanly close report modal
    await page.evaluate(() => {
      const modal = document.getElementById('report-modal-backdrop');
      if (modal) modal.classList.add('hidden');
    });

    // 3b. Sync Modal (via DOM click to avoid unintended scroll container displacement on mobile)
    await page.evaluate(() => {
      const btn = document.getElementById('btn-sync-status');
      if (btn) btn.click();
    });
    await page.waitForSelector('#sync-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);
    const syncPath = path.join(outDir, `${targetName}_${vp.name}_sync_modal.png`);
    await page.screenshot({ path: syncPath, fullPage: false });

    // Close sync modal
    await page.evaluate(() => {
      const btn = document.getElementById('btn-close-sync-modal');
      if (btn) btn.click();
    });
    await page.waitForSelector('#sync-modal-backdrop', { state: 'hidden', timeout: 10000 });

    // 3c. PDF Import Screen
    await page.evaluate(() => {
      const btn = document.getElementById('btn-tab-import');
      if (btn) btn.click();
    });
    await page.waitForSelector('#import-view:not(.hidden)', { timeout: 10000 });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);
    const pdfImportPath = path.join(outDir, `${targetName}_${vp.name}_pdf_import.png`);
    await page.screenshot({ path: pdfImportPath, fullPage: false });

    // Return to catalog view cleanly
    await page.evaluate(() => {
      const btn = document.getElementById('btn-tab-catalog');
      if (btn) btn.click();
      window.scrollTo(0, 0);
      const nav = document.getElementById('header-nav');
      if (nav) nav.scrollLeft = 0;
    });
    await page.waitForSelector('#catalog-view:not(.hidden)', { timeout: 10000 });
    await page.waitForTimeout(300);

    // 4. Mobile Column Switch (Mobile only)
    if (vp.isMobile) {
      await page.evaluate(() => {
        const modal = document.getElementById('report-modal-backdrop');
        if (modal) modal.classList.add('hidden');
      });
      const tabSolved = page.locator('#tab-col-solved');
      if (await tabSolved.isVisible()) {
        await tabSolved.click();
        await page.waitForTimeout(400);
        const colPath = path.join(outDir, `${targetName}_mobile_solved_col.png`);
        await page.screenshot({ path: colPath, fullPage: false });
      }
    }

    // 5. Exercise Reading View & Question Wizard
    await page.evaluate(() => {
      const reportModal = document.getElementById('report-modal-backdrop');
      if (reportModal) reportModal.classList.add('hidden');
      if (window.openPretestModal) {
        window.openPretestModal(1);
      }
    });
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
    await page.waitForSelector('#wizard-card-area .option-item', { timeout: 10000 });
    await page.evaluate(() => {
      if (window.state && window.state.timer) {
        if (window.state.timer.intervalId) clearInterval(window.state.timer.intervalId);
        window.state.timer.remainingSeconds = 180;
      }
      const timerDisplay = document.getElementById('timer-display');
      if (timerDisplay) timerDisplay.textContent = '03:00';
    });
    await page.waitForTimeout(500);
    const exercisePath = path.join(outDir, `${targetName}_${vp.name}_exercise.png`);
    await page.screenshot({ path: exercisePath, fullPage: false });

    // 6. Analysis Post-Submit View
    // Pick the answer by text, not by position: the shuffled order changes from run to run, and the
    // first option was sometimes right, sometimes wrong (different banner score). This is the option
    // that was first before the shuffle (a wrong answer, so the trap explanation stays on screen).
    const byText = page.locator('#wizard-card-area .option-item', { hasText: ANSWER_OPTION_TEXT }).first();
    const optItem = (await byText.count()) ? byText : page.locator('#wizard-card-area .option-item').first();
    if (await optItem.isVisible()) {
      await optItem.click();
      await page.waitForTimeout(400);
      const submitBtn = page.locator('#btn-wizard-submit');
      if (await submitBtn.isVisible()) {
        await submitBtn.click();
        await page.waitForSelector('#analysis-banner:not(.hidden)', { timeout: 15000 });
        await page.waitForSelector('#analysis-tabs .analysis-tab-btn', { timeout: 10000 });
        // Elapsed time comes from real setInterval ticks (00:00 vs 00:01 between runs): normalise digits only.
        await page.evaluate(() => {
          const el = document.getElementById('banner-result-meta');
          if (!el) return;
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          for (let n = walker.nextNode(); n; n = walker.nextNode()) {
            n.nodeValue = n.nodeValue.replace(/\d{2}:\d{2}/g, '00:00');
          }
        });
        await page.waitForTimeout(500);
        const analysisPath = path.join(outDir, `${targetName}_${vp.name}_analysis.png`);
        await page.screenshot({ path: analysisPath, fullPage: false });
      }
    }

    await context.close();
  }

  await browser.close();
}

async function main() {
  const outDir = path.resolve(__dirname, '../docs/qa/evidence/screenshots');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  console.log('Capturing screenshots for main (http://localhost:8001)...');
  await captureScreenshotsForTarget('http://localhost:8001', 'main', outDir);

  console.log('Capturing screenshots for refactor (http://localhost:8000)...');
  await captureScreenshotsForTarget('http://localhost:8000', 'refactor', outDir);

  console.log('All screenshots captured successfully into', outDir);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

