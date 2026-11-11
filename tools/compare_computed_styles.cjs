/**
 * JLPT Dokkai Master - Computed Styles Cross-Branch Comparison Tool
 * Compares getComputedStyle for all DOM elements across main (port 8001) and refactor (port 8000)
 * Covers: Normal, :hover and :focus states across 9 standard screens/modals.
 */

const path = require('path');
const fs = require('fs');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

const REAL_NOW = Date.now();
const RUN_USER_ID = `computed-styles-${REAL_NOW.toString(36)}`;
const APPROVED_FILE = process.env.COMPUTED_STYLES_APPROVED
  ? path.resolve(process.env.COMPUTED_STYLES_APPROVED)
  : path.join(__dirname, 'snapshots', 'computed_styles_approved.json');
const WRITE_APPROVED = process.argv.includes('--write-approved');
const NO_APPROVED = process.argv.includes('--no-approved');

const PROPERTIES_TO_COMPARE = [
  // Dimensions & Box Model
  'width', 'height', 'box-sizing',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  // Typography
  'font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing', 'color', 'text-align',
  // Borders & Radii
  'border-top-width', 'border-top-style', 'border-top-color',
  'border-right-width', 'border-right-style', 'border-right-color',
  'border-bottom-width', 'border-bottom-style', 'border-bottom-color',
  'border-left-width', 'border-left-style', 'border-left-color',
  'border-top-left-radius', 'border-top-right-radius', 'border-bottom-right-radius', 'border-bottom-left-radius',
  // Background & Display
  'background-color', 'display', 'position', 'top', 'left', 'right', 'bottom',
  'flex-direction', 'align-items', 'justify-content', 'gap',
  'opacity', 'visibility', 'cursor'
];

const INTERACTIVE_SELECTORS = [
  'button', 'a[href]', 'input', 'select', 'textarea',
  '[tabindex="0"]', '.btn', '.nav-tab', '.filter-pill',
  '.stream-slot-card button', '.option-item', 'summary'
];

const MOCK_SLOTS = {
  profile_key: 'N5:short',
  user_id: 'computed-styles-user',
  slots: [
    {
      position: 1,
      state: 'active',
      text: {
        id: 1,
        title: '図書館の利用時間変更 (N5) #1',
        level: 'N5',
        category: 'short',
        question_count: 1,
        recommended_time_min: 3
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
        question_count: 1,
        recommended_time_min: 3
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
        question_count: 1,
        recommended_time_min: 3
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

async function extractStylesMap(page, stateName) {
  return await page.evaluate(({ props, interactiveSelectors, stateName }) => {
    const results = {};

    function getUniquePath(el) {
      if (el.id) return `#${el.id}`;
      if (el === document.body) return 'body';
      if (!el.parentElement) return el.tagName.toLowerCase();

      const parentPath = getUniquePath(el.parentElement);
      const tag = el.tagName.toLowerCase();
      const siblings = Array.from(el.parentElement.children).filter(c => c.tagName.toLowerCase() === tag);
      if (siblings.length === 1) {
        const cls = el.className ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
        return `${parentPath} > ${tag}${cls}`;
      }
      const idx = siblings.indexOf(el) + 1;
      return `${parentPath} > ${tag}:nth-of-type(${idx})`;
    }

    const allElements = Array.from(document.body.querySelectorAll('*')).filter(el => {
      const tag = el.tagName.toLowerCase();
      return tag !== 'script' && tag !== 'style' && tag !== 'noscript' && tag !== 'link';
    });

    for (const el of allElements) {
      const pathStr = getUniquePath(el);
      const computed = window.getComputedStyle(el);
      const styles = {};
      for (const p of props) {
        styles[p] = computed.getPropertyValue(p);
      }

      // Check if interactive
      const isInteractive = interactiveSelectors.some(sel => {
        try { return el.matches(sel); } catch { return false; }
      });

      results[pathStr] = {
        path: pathStr,
        tag: el.tagName.toLowerCase(),
        id: el.id || null,
        className: el.className || null,
        isInteractive,
        styles
      };
    }

    return results;
  }, { props: PROPERTIES_TO_COMPARE, interactiveSelectors: INTERACTIVE_SELECTORS, stateName });
}

async function extractPseudoStyles(page, selector, pseudoType) {
  return await page.evaluate(({ sel, pseudoType, props }) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const computed = window.getComputedStyle(el);
    const styles = {};
    for (const p of props) {
      styles[p] = computed.getPropertyValue(p);
    }
    return styles;
  }, { sel: selector, pseudoType, props: PROPERTIES_TO_COMPARE });
}

async function setupMocksAndOpen(page, baseUrl) {
  page.on('console', msg => {
    if (msg.type() === 'error') console.log(`[PAGE ERROR ${baseUrl}]`, msg.text());
  });
  page.on('pageerror', err => console.log(`[PAGE CRASH ${baseUrl}]`, err.message));

  await page.addInitScript((runUserId) => {
    const fixedTime = 1793966400000;
    Date.now = () => fixedTime;
    // Step 11d shuffles options by HMAC(user_id | text_id | attempt). A random per-tab user_id made
    // main and branch show different option orders (and a different order on every run). One fresh
    // user_id per run, shared by both sides, gives both servers the same order (attempt 0).
    try { localStorage.setItem('dokkai_user_id', runUserId); } catch { /* storage unavailable */ }
  }, RUN_USER_ID);

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

  await page.goto(baseUrl);
  await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });
  await page.addStyleTag({ content: '*, *::before, *::after { transition: none !important; animation: none !important; }' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
}

async function runComparison() {
  const browser = await chromium.launch({ headless: true });
  const contextMain = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const contextRef = await browser.newContext({ viewport: { width: 1280, height: 800 } });

  const pageMain = await contextMain.newPage();
  const pageRef = await contextRef.newPage();

  console.log('Connecting to Main (http://localhost:8001) and Branch (http://localhost:8000)...');
  await setupMocksAndOpen(pageMain, 'http://localhost:8001');
  await setupMocksAndOpen(pageRef, 'http://localhost:8000');

  const discrepancies = [];

  const compareMaps = async (screenName, mapMain, mapRef, pageM, pageR) => {
    const allPaths = Array.from(new Set([...Object.keys(mapMain), ...Object.keys(mapRef)]));

    for (const p of allPaths) {
      const itemM = mapMain[p];
      const itemR = mapRef[p];

      if (!itemM) {
        discrepancies.push({ screen: screenName, element: p, state: 'normal', property: 'DOM existence', mainVal: 'MISSING', refVal: 'PRESENT' });
        continue;
      }
      if (!itemR) {
        discrepancies.push({ screen: screenName, element: p, state: 'normal', property: 'DOM existence', mainVal: 'PRESENT', refVal: 'MISSING' });
        continue;
      }

      // Compare normal computed styles
      for (const prop of PROPERTIES_TO_COMPARE) {
        const valM = itemM.styles[prop];
        const valR = itemR.styles[prop];
        if (valM !== valR) {
          discrepancies.push({ screen: screenName, element: p, state: 'normal', property: prop, mainVal: valM, refVal: valR });
        }
      }

      // If interactive, compare hover and focus states
      if (itemM.isInteractive && itemR.isInteractive) {
        try {
          const locM = pageM.locator(p);
          const locR = pageR.locator(p);
          if (await locM.isVisible() && await locR.isVisible()) {
            // Hover
            await locM.hover({ timeout: 1000 });
            await locR.hover({ timeout: 1000 });
            await pageM.waitForTimeout(50);
            await pageR.waitForTimeout(50);
            const hoverStylesM = await extractPseudoStyles(pageM, p, 'hover');
            const hoverStylesR = await extractPseudoStyles(pageR, p, 'hover');
            if (hoverStylesM && hoverStylesR) {
              for (const prop of PROPERTIES_TO_COMPARE) {
                if (hoverStylesM[prop] !== hoverStylesR[prop]) {
                  discrepancies.push({ screen: screenName, element: p, state: ':hover', property: prop, mainVal: hoverStylesM[prop], refVal: hoverStylesR[prop] });
                }
              }
            }

            // Focus
            await locM.focus({ timeout: 1000 });
            await locR.focus({ timeout: 1000 });
            await pageM.waitForTimeout(50);
            await pageR.waitForTimeout(50);
            const focusStylesM = await extractPseudoStyles(pageM, p, 'focus');
            const focusStylesR = await extractPseudoStyles(pageR, p, 'focus');
            if (focusStylesM && focusStylesR) {
              for (const prop of PROPERTIES_TO_COMPARE) {
                if (focusStylesM[prop] !== focusStylesR[prop]) {
                  discrepancies.push({ screen: screenName, element: p, state: ':focus', property: prop, mainVal: focusStylesM[prop], refVal: focusStylesR[prop] });
                }
              }
            }

            // Unfocus
            await pageM.evaluate(() => document.activeElement && document.activeElement.blur());
            await pageR.evaluate(() => document.activeElement && document.activeElement.blur());
          }
        } catch {
          // Non-critical interactive hover/focus check error (e.g. element covered by modal)
        }
      }
    }
  };

  // 1. Каталог
  console.log('[1/9] Comparing Screen: Catalog...');
  let mapM = await extractStylesMap(pageMain, 'catalog');
  let mapR = await extractStylesMap(pageRef, 'catalog');
  await compareMaps('Каталог', mapM, mapR, pageMain, pageRef);

  // 2. Предстартовое окно
  console.log('[2/9] Comparing Screen: Pretest Modal...');
  await pageMain.click('#active-slots-list .stream-slot-card button');
  await pageRef.click('#active-slots-list .stream-slot-card button');
  await pageMain.waitForSelector('#pretest-modal-backdrop:not(.hidden)');
  await pageRef.waitForSelector('#pretest-modal-backdrop:not(.hidden)');
  await pageMain.waitForTimeout(300);
  await pageRef.waitForTimeout(300);
  mapM = await extractStylesMap(pageMain, 'pretest');
  mapR = await extractStylesMap(pageRef, 'pretest');
  await compareMaps('Предстартовое окно', mapM, mapR, pageMain, pageRef);

  // 3. Экран теста
  console.log('[3/9] Comparing Screen: Exercise View...');
  await pageMain.click('#modal-btn-start');
  await pageRef.click('#modal-btn-start');
  await pageMain.waitForSelector('#exercise-view:not(.hidden)');
  await pageRef.waitForSelector('#exercise-view:not(.hidden)');
  await pageMain.waitForTimeout(300);
  await pageRef.waitForTimeout(300);
  mapM = await extractStylesMap(pageMain, 'exercise');
  mapR = await extractStylesMap(pageRef, 'exercise');
  await compareMaps('Экран теста', mapM, mapR, pageMain, pageRef);

  // 4. Разбор (Analysis)
  console.log('[4/9] Comparing Screen: Analysis View...');
  await pageMain.click('.option-item');
  await pageRef.click('.option-item');
  await pageMain.waitForTimeout(200);
  await pageRef.waitForTimeout(200);
  await pageMain.click('#btn-wizard-submit');
  await pageRef.click('#btn-wizard-submit');
  await pageMain.waitForSelector('#analysis-banner:not(.hidden)');
  await pageRef.waitForSelector('#analysis-banner:not(.hidden)');
  // Normalize banner text so dynamic elapsed timer doesn't alter intrinsic text container width
  await pageMain.evaluate(() => {
    const el = document.getElementById('banner-result-meta');
    if (el) el.textContent = 'Затрачено: 00:00 | Режим: Свободное чтение без таймера';
  });
  await pageRef.evaluate(() => {
    const el = document.getElementById('banner-result-meta');
    if (el) el.textContent = 'Затрачено: 00:00 | Режим: Свободное чтение без таймера';
  });
  await pageMain.waitForTimeout(400);
  await pageRef.waitForTimeout(400);
  mapM = await extractStylesMap(pageMain, 'analysis');
  mapR = await extractStylesMap(pageRef, 'analysis');
  await compareMaps('Разбор', mapM, mapR, pageMain, pageRef);

  // Return to catalog
  await pageMain.click('#btn-home');
  await pageRef.click('#btn-home');
  await pageMain.waitForSelector('#catalog-view:not(.hidden)');
  await pageRef.waitForSelector('#catalog-view:not(.hidden)');
  await pageMain.waitForTimeout(300);
  await pageRef.waitForTimeout(300);

  // 5. Окно жалобы
  console.log('[5/9] Comparing Screen: Report Modal...');
  await pageMain.evaluate(() => {
    const modal = document.getElementById('report-modal-backdrop');
    if (modal) modal.classList.remove('hidden');
  });
  await pageRef.evaluate(() => {
    const modal = document.getElementById('report-modal-backdrop');
    if (modal) modal.classList.remove('hidden');
  });
  await pageMain.waitForSelector('#report-modal-backdrop:not(.hidden)');
  await pageRef.waitForSelector('#report-modal-backdrop:not(.hidden)');
  mapM = await extractStylesMap(pageMain, 'report');
  mapR = await extractStylesMap(pageRef, 'report');
  await compareMaps('Окно жалобы', mapM, mapR, pageMain, pageRef);
  await pageMain.evaluate(() => document.getElementById('report-modal-backdrop').classList.add('hidden'));
  await pageRef.evaluate(() => document.getElementById('report-modal-backdrop').classList.add('hidden'));

  // 6. Окно синхронизации
  console.log('[6/9] Comparing Screen: Sync Modal...');
  await pageMain.click('#btn-sync-status');
  await pageRef.click('#btn-sync-status');
  await pageMain.waitForSelector('#sync-modal-backdrop:not(.hidden)');
  await pageRef.waitForSelector('#sync-modal-backdrop:not(.hidden)');
  mapM = await extractStylesMap(pageMain, 'sync_modal');
  mapR = await extractStylesMap(pageRef, 'sync_modal');
  await compareMaps('Окно синхронизации', mapM, mapR, pageMain, pageRef);
  await pageMain.click('#btn-close-sync-modal');
  await pageRef.click('#btn-close-sync-modal');
  await pageMain.waitForSelector('#sync-modal-backdrop', { state: 'hidden' });
  await pageRef.waitForSelector('#sync-modal-backdrop', { state: 'hidden' });

  // 7. «Мой словарь»
  console.log('[7/9] Comparing Screen: Notebook View...');
  await pageMain.click('#btn-tab-notebook');
  await pageRef.click('#btn-tab-notebook');
  await pageMain.waitForSelector('#notebook-view:not(.hidden)');
  await pageRef.waitForSelector('#notebook-view:not(.hidden)');
  mapM = await extractStylesMap(pageMain, 'notebook');
  mapR = await extractStylesMap(pageRef, 'notebook');
  await compareMaps('Мой словарь', mapM, mapR, pageMain, pageRef);

  // 8. Карточка словаря (Popup Dictionary Card)
  console.log('[8/9] Comparing Screen: Popup Dictionary Card...');
  await pageMain.evaluate(() => {
    if (window.showPopupDictionary) {
      window.showPopupDictionary({ word: '環境', reading: 'かんきょう', meaning: 'окружающая среда', level: 'N3' }, 200, 200);
    }
  });
  await pageRef.evaluate(() => {
    if (window.showPopupDictionary) {
      window.showPopupDictionary({ word: '環境', reading: 'かんきょう', meaning: 'окружающая среда', level: 'N3' }, 200, 200);
    }
  });
  await pageMain.waitForSelector('#popup-dictionary-card:not(.hidden)');
  await pageRef.waitForSelector('#popup-dictionary-card:not(.hidden)');
  mapM = await extractStylesMap(pageMain, 'popup_dict');
  mapR = await extractStylesMap(pageRef, 'popup_dict');
  await compareMaps('Карточка словаря', mapM, mapR, pageMain, pageRef);
  await pageMain.evaluate(() => { if (window.hidePopupDictionary) window.hidePopupDictionary(); });
  await pageRef.evaluate(() => { if (window.hidePopupDictionary) window.hidePopupDictionary(); });

  // 9. Импорт PDF
  console.log('[9/9] Comparing Screen: PDF Import View...');
  await pageMain.click('#btn-tab-import');
  await pageRef.click('#btn-tab-import');
  await pageMain.waitForSelector('#import-view:not(.hidden)');
  await pageRef.waitForSelector('#import-view:not(.hidden)');
  mapM = await extractStylesMap(pageMain, 'pdf_import');
  mapR = await extractStylesMap(pageRef, 'pdf_import');
  await compareMaps('Импорт PDF', mapM, mapR, pageMain, pageRef);

  await browser.close();

  if (process.env.DISCREPANCIES_JSON) {
    fs.writeFileSync(process.env.DISCREPANCIES_JSON, JSON.stringify(discrepancies, null, 1));
  }

  if (WRITE_APPROVED) {
    writeApproved(discrepancies);
    process.exit(0);
  }

  const approved = loadApproved();
  let fresh = discrepancies;
  let approvedSeen = 0;
  if (approved) {
    const seen = new Set();
    fresh = discrepancies.filter((d) => {
      const key = discrepancyKey(d);
      if (!approved.keys.has(key)) return true;
      seen.add(key);
      return false;
    });
    approvedSeen = seen.size;
  }

  // Report
  console.log('\n=============================================================');
  console.log('COMPUTED STYLES COMPARISON REPORT');
  console.log('=============================================================');
  if (approved) {
    console.log(`Approved baseline: ${path.relative(process.cwd(), APPROVED_FILE)} ` +
      `(reference: ${approved.meta.reference || 'unknown'}, ${approved.keys.size} entries). ` +
      `Matched ${approvedSeen}; approved but not observed: ${approved.keys.size - approvedSeen}.`);
  }
  if (fresh.length === 0) {
    if (approved) {
      console.log(`✓ 0 DISCREPANCIES outside the approved baseline (${approvedSeen} approved).`);
    } else {
      console.log('✓ 0 DISCREPANCIES FOUND! All computed styles match identically between main and branch across all 9 screens and states.');
    }
    process.exit(0);
  } else {
    const label = approved ? 'NEW (NOT APPROVED) COMPUTED STYLE DIFFERENCES' : 'COMPUTED STYLE DISCREPANCIES';
    console.log(`✗ FOUND ${fresh.length} ${label}:`);
    console.table(fresh.slice(0, 50));
    if (fresh.length > 50) {
      console.log(`... and ${fresh.length - 50} more.`);
    }
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Approved baseline (docs/INTENTIONAL_DIFFERENCES.md, I17).
// A discrepancy is approved only if screen, element, state, property AND both
// values match an entry exactly; anything else is reported as new.
//   node tools/compare_computed_styles.cjs                    -> uses the baseline if the file exists
//   node tools/compare_computed_styles.cjs --no-approved      -> strict mode, every discrepancy counts
//   APPROVED_REFERENCE=404012d node tools/compare_computed_styles.cjs --write-approved
//                                                             -> (re)captures the baseline from this run
// COMPUTED_STYLES_APPROVED=<path> overrides the baseline file location.
// ---------------------------------------------------------------------------
function discrepancyKey(d) {
  return JSON.stringify([d.screen, d.element, d.state, d.property, d.mainVal, d.refVal]);
}

function loadApproved() {
  if (NO_APPROVED || !fs.existsSync(APPROVED_FILE)) return null;
  const data = JSON.parse(fs.readFileSync(APPROVED_FILE, 'utf-8'));
  if (!data || !Array.isArray(data.entries)) {
    throw new Error(`Approved baseline ${APPROVED_FILE} has no "entries" array`);
  }
  return { meta: data.meta || {}, keys: new Set(data.entries.map(discrepancyKey)) };
}

function writeApproved(discrepancies) {
  const entries = discrepancies
    .map((d) => ({ screen: d.screen, element: d.element, state: d.state, property: d.property, mainVal: d.mainVal, refVal: d.refVal }))
    .sort((a, b) => discrepancyKey(a).localeCompare(discrepancyKey(b)));
  const meta = {
    reference: process.env.APPROVED_REFERENCE || 'unknown',
    captured_at: new Date(REAL_NOW).toISOString(),
    count: entries.length,
    note: 'Approved computed-style differences vs the reference served on :8001. See docs/INTENTIONAL_DIFFERENCES.md (I17). Recapture after the reference changes.'
  };
  // One entry per line keeps git diffs of the baseline readable.
  const body = '{\n "meta": ' + JSON.stringify(meta) + ',\n "entries": [\n' +
    entries.map((e) => '  ' + JSON.stringify(e)).join(',\n') + '\n ]\n}\n';
  fs.mkdirSync(path.dirname(APPROVED_FILE), { recursive: true });
  fs.writeFileSync(APPROVED_FILE, body, 'utf-8');
  console.log(`\nApproved baseline written: ${APPROVED_FILE} (${entries.length} entries, reference: ${meta.reference}).`);
}

runComparison().catch(err => {
  console.error('Fatal comparison error:', err);
  process.exit(2);
});

