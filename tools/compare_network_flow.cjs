const fs = require('fs');
const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

async function runScenario(baseUrl, outputFilename) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  const recordedRequests = [];

  page.on('request', (req) => {
    const urlStr = req.url();
    const parsedUrl = new URL(urlStr);
    // Intercept backend API endpoints strictly (ignoring static /static/js/api/* files)
    if (parsedUrl.pathname.startsWith('/api/')) {
      const queryObj = {};
      parsedUrl.searchParams.forEach((val, key) => {
        if (key === '_t') {
          queryObj[key] = '<TIMESTAMP>';
        } else if (key === 'user_id') {
          queryObj[key] = '<USER_ID>';
        } else {
          queryObj[key] = val;
        }
      });

      let postData = null;
      try {
        const raw = req.postData();
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed.user_id) parsed.user_id = '<USER_ID>';
          if (parsed.time_spent_sec !== undefined) parsed.time_spent_sec = '<TIME_SPENT>';
          if (parsed.idempotency_key) parsed.idempotency_key = '<IDEMPOTENCY_KEY>';
          postData = parsed;
        }
      } catch {
        postData = req.postData();
      }

      // Extract normalized path (e.g. /api/texts/123 -> /api/texts/<TEXT_ID>)
      const normalizedPath = parsedUrl.pathname
        .replace(/\/api\/texts\/\d+\/report/, '/api/texts/<TEXT_ID>/report')
        .replace(/\/api\/texts\/\d+/, '/api/texts/<TEXT_ID>')
        .replace(/\/api\/stream\/tasks\/\d+\/complete/, '/api/stream/tasks/<TEXT_ID>/complete')
        .replace(/\/api\/stream\/solved\/\d+/, '/api/stream/solved/<SOLVED_ID>');

      recordedRequests.push({
        method: req.method(),
        path: normalizedPath,
        query: queryObj,
        body: postData,
        key_headers: {
          'content-type': req.headers()['content-type'] || null,
          'accept': req.headers()['accept'] || null
        }
      });
    }
  });

  // 1. Каталог (начальная загрузка)
  await page.goto(baseUrl);
  await page.waitForSelector('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder', { timeout: 15000 });
  await page.waitForTimeout(500);

  // 2. Переключение уровней N5 -> N4 -> N3 -> N2 -> N1 -> N5
  for (const lvl of ['N4', 'N3', 'N2', 'N1', 'N5']) {
    const lvlBtn = page.locator(`#stream-level-pills .filter-pill[data-level="${lvl}"]`);
    if (await lvlBtn.isVisible()) {
      await lvlBtn.click();
      await page.waitForTimeout(400);
    }
  }

  // 3. Смена формата: medium -> long -> info_search -> short
  for (const cat of ['medium', 'long', 'info_search', 'short']) {
    const catBtn = page.locator(`#stream-category-pills .filter-pill[data-category="${cat}"]`);
    if (await catBtn.isVisible()) {
      await catBtn.click();
      await page.waitForTimeout(400);
    }
  }

  // 4. «Условие сдачи»
  const modeCorrect = page.locator('#stream-mode-pills .filter-pill[data-solved-when="all_correct"]');
  if (await modeCorrect.isVisible()) {
    await modeCorrect.click();
    await page.waitForTimeout(300);
  }
  const modeAll = page.locator('#stream-mode-pills .filter-pill[data-solved-when="all_questions_answered"]');
  if (await modeAll.isVisible()) {
    await modeAll.click();
    await page.waitForTimeout(300);
  }

  // 5. Обновление слотов
  const btnRefresh = page.locator('#btn-refresh-slots');
  if (await btnRefresh.isVisible()) {
    await btnRefresh.click();
    await page.waitForTimeout(500);
  }

  // 6. Открыть задание (через предстартовое окно)
  const firstSlotBtn = page.locator('#active-slots-list .stream-slot-card button').first();
  if (await firstSlotBtn.isVisible()) {
    await firstSlotBtn.click();
    await page.waitForSelector('#pretest-modal-backdrop', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view', { timeout: 10000 });
    await page.waitForTimeout(500);

    // 7. Ответить
    const option = page.locator('.option-item').first();
    if (await option.isVisible()) await option.click();
    await page.waitForTimeout(300);

    while (await page.locator('#wizard-btn-next:visible').count() > 0) {
      await page.click('#wizard-btn-next');
      await page.waitForTimeout(300);
      const nextOpt = page.locator('.option-item').first();
      if (await nextOpt.isVisible()) await nextOpt.click();
    }

    const submitBtn = page.locator('#wizard-btn-submit');
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
      await page.waitForTimeout(1000);
    }
  }

  // 8. Разбор и обращение к решённому заданию
  await page.evaluate(async () => {
    try {
      const res = await fetch('/api/stream/solved?user_id=test-compare-user&level=N5');
      const data = await res.json();
      if (data && data.length > 0) {
        await fetch(`/api/stream/solved/${data[0].id}`);
      }
    } catch (e) {}
  });
  await page.waitForTimeout(400);

  // 9. Словарь
  await page.evaluate(async () => {
    try {
      await fetch('/api/dictionary/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: '持続可能' })
      });
    } catch (e) {}
  });
  await page.waitForTimeout(400);

  // 10. «Решённые» с фильтрами («Все / 100% / С ошибками»)
  const btnHome = page.locator('#btn-home');
  if (await btnHome.isVisible()) {
    await btnHome.click();
  } else {
    await page.goto(baseUrl);
  }
  await page.waitForSelector('#active-slots-list', { timeout: 15000 });
  await page.waitForTimeout(400);

  // Filter 100%
  const filterPerfect = page.locator('#solved-filter-pills button[data-solved-filter="perfect"]');
  if (await filterPerfect.isVisible()) {
    await filterPerfect.click();
    await page.waitForTimeout(400);
  }

  // Filter С ошибками
  const filterErrors = page.locator('#solved-filter-pills button[data-solved-filter="errors"]');
  if (await filterErrors.isVisible()) {
    await filterErrors.click();
    await page.waitForTimeout(400);
  }

  // Filter Все
  const filterAll = page.locator('#solved-filter-pills button[data-solved-filter="all"]');
  if (await filterAll.isVisible()) {
    await filterAll.click();
    await page.waitForTimeout(400);
  }

  // 11. Жалоба
  await page.evaluate(async () => {
    try {
      await fetch('/api/texts/1/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'test-compare-user',
          reason: 'Опечатка в тексте или вопросе',
          details: 'Тестовая жалоба для аудита сетевых логов'
        })
      });
    } catch (e) {}
  });
  await page.waitForTimeout(400);

  await browser.close();

  const formatted = JSON.stringify(recordedRequests, null, 2);
  fs.writeFileSync(outputFilename, formatted, 'utf-8');
  console.log(`Saved ${recordedRequests.length} requests to ${outputFilename}`);
  return recordedRequests;
}

async function main() {
  const dir = path.resolve(__dirname, '../docs/qa/evidence');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const fileMain = path.join(dir, 'requests_main.json');
  const fileRefactor = path.join(dir, 'requests_refactor.json');
  const fileDiff = path.join(dir, 'requests_diff.txt');

  console.log('Recording on main (http://localhost:8001)...');
  const mainReqs = await runScenario('http://localhost:8001', fileMain);

  console.log('Recording on refactor/decomposition (http://localhost:8000)...');
  const refactorReqs = await runScenario('http://localhost:8000', fileRefactor);

  // Automated Diff
  const strMain = JSON.stringify(mainReqs, null, 2);
  const strRefactor = JSON.stringify(refactorReqs, null, 2);

  if (strMain === strRefactor) {
    const diffReport = 'AUTOMATED DIFF RESULT:\n0 DISCREPANCIES FOUND (100% BIT-FOR-BIT MATCH)\n\nAll ' + mainReqs.length + ' API requests match identically between main and refactor/decomposition.\n';
    fs.writeFileSync(fileDiff, diffReport, 'utf-8');
    console.log(diffReport);
  } else {
    let diffReport = 'AUTOMATED DIFF RESULT:\nDISCREPANCIES DETECTED:\n';
    const maxLen = Math.max(mainReqs.length, refactorReqs.length);
    for (let i = 0; i < maxLen; i++) {
      const m = mainReqs[i];
      const r = refactorReqs[i];
      const sm = JSON.stringify(m);
      const sr = JSON.stringify(r);
      if (sm !== sr) {
        diffReport += `\nStep ${i + 1}:\n  MAIN:     ${sm}\n  REFACTOR: ${sr}\n`;
      }
    }
    fs.writeFileSync(fileDiff, diffReport, 'utf-8');
    console.log(diffReport);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
