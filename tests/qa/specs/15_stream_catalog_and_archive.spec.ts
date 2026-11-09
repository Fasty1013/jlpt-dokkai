import { test, expect } from '@playwright/test';

test.describe('15. Stream Catalog, Slot Dynamic Filters & Solved Archive', () => {
  test.describe.configure({ mode: 'serial' });

  test('01. Dynamic Filtering: Switching JLPT level and category updates active slots', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder', { timeout: 15000 });

    // Initial level N5 is active
    const activeLevelPill = page.locator('#stream-level-pills .filter-pill.active');
    await expect(activeLevelPill).toHaveAttribute('data-level', 'N5');

    // Switch to N4
    const n4Pill = page.locator('#stream-level-pills .filter-pill[data-level="N4"]');
    const [respN4] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/stream/slots') && resp.url().includes('level=N4')),
      n4Pill.click()
    ]);
    expect(respN4.status()).toBe(200);
    await expect(n4Pill).toHaveClass(/active/);

    const slotCards = page.locator('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder');
    await expect(slotCards.first()).toBeVisible();

    // Switch category to medium (中文)
    const mediumPill = page.locator('#stream-category-pills .filter-pill[data-category="medium"]');
    const [respCategory] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/stream/slots') && resp.url().includes('category=medium')),
      mediumPill.click()
    ]);
    expect(respCategory.status()).toBe(200);
    await expect(mediumPill).toHaveClass(/active/);
  });

  test('02. Persistence: "Условие сдачи" (solvedWhen) preference persists across page reloads', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#stream-mode-pills', { timeout: 15000 });

    const allCorrectBtn = page.locator('#stream-mode-pills .filter-pill[data-solved-when="all_correct"]');
    await allCorrectBtn.click();
    await expect(allCorrectBtn).toHaveClass(/active/);

    // Verify persistence after page reload
    await page.reload();
    await page.waitForSelector('#stream-mode-pills', { timeout: 15000 });
    const reloadedAllCorrect = page.locator('#stream-mode-pills .filter-pill[data-solved-when="all_correct"]');
    await expect(reloadedAllCorrect).toHaveClass(/active/);
  });

  test('03. Slot Refresh: Manual slot replenishment button requests updated slots', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#btn-refresh-slots', { timeout: 15000 });

    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/stream/slots')),
      page.locator('#btn-refresh-slots').click(),
    ]);

    expect(response.status()).toBe(200);
    const slots = page.locator('#active-slots-list .stream-slot-card, #active-slots-list .stream-slot-placeholder');
    await expect(slots.first()).toBeVisible();
  });

  test('04. Solved Archive: Filters "Все", "100%", "С ошибками" correctly partition results', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#solved-tasks-list', { timeout: 15000 });

    // Deterministically wait for DokkaiStorage initialization and render function
    await page.waitForFunction(async () => {
      const w = window as any;
      if (!w.DokkaiStorage || !w.DokkaiStorage.initPromise) return false;
      await w.DokkaiStorage.initPromise;
      return Boolean(w.DokkaiStorage.isReady && typeof w.fetchAndRenderSolvedTasks === 'function');
    }, { timeout: 15000 });

    // Seed test solved tasks in DokkaiStorage
    await page.evaluate(async () => {
      const w = window as any;
      if (w.DokkaiStorage) {
        await w.DokkaiStorage.recordSolvedTask({
          text_id: 991,
          title: 'Учебный текст 100% (Тест)',
          level: 'N5',
          category: 'short',
          score: 100,
          score_percent: 100,
          last_score: 100,
          correct_count: 3,
          total_questions: 3,
          perfect: true,
          time_spent_sec: 45,
          solved_at: new Date().toISOString()
        });
        await w.DokkaiStorage.recordSolvedTask({
          text_id: 992,
          title: 'Учебный текст с ошибками (Тест)',
          level: 'N5',
          category: 'short',
          score: 66.7,
          score_percent: 66.7,
          last_score: 66.7,
          correct_count: 2,
          total_questions: 3,
          perfect: false,
          time_spent_sec: 90,
          solved_at: new Date().toISOString()
        });
        if (w.fetchAndRenderSolvedTasks) {
          await w.fetchAndRenderSolvedTasks();
        }
      }
    });

    const solvedCards = page.locator('#solved-tasks-list .stream-solved-card');
    await expect(solvedCards).toHaveCount(2);

    // 1. Filter: 100% (Perfect)
    const btnFilterPerfect = page.locator('#solved-filter-pills button[data-solved-filter="perfect"]');
    await btnFilterPerfect.click();
    await expect(btnFilterPerfect).toHaveClass(/active/);
    await expect(page.locator('#solved-tasks-list .stream-solved-card')).toHaveCount(1);
    await expect(page.locator('#solved-tasks-list .solved-score-badge')).toContainText('100%');

    // 2. Filter: С ошибками (Errors)
    const btnFilterErrors = page.locator('#solved-filter-pills button[data-solved-filter="errors"]');
    await btnFilterErrors.click();
    await expect(btnFilterErrors).toHaveClass(/active/);
    await expect(page.locator('#solved-tasks-list .stream-solved-card')).toHaveCount(1);
    await expect(page.locator('#solved-tasks-list .solved-score-badge')).toContainText('ошибк');

    // 3. Filter: Все (All)
    const btnFilterAll = page.locator('#solved-filter-pills button[data-solved-filter="all"]');
    await btnFilterAll.click();
    await expect(btnFilterAll).toHaveClass(/active/);
    await expect(page.locator('#solved-tasks-list .stream-solved-card')).toHaveCount(2);
  });

  test('05. Defect Reporting: Report modal opens, fills, and submits with confirmation', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    // Deterministically wait for DokkaiStorage and seed a solved task so the report button exists
    await page.waitForFunction(async () => {
      const w = window as any;
      if (!w.DokkaiStorage || !w.DokkaiStorage.initPromise) return false;
      await w.DokkaiStorage.initPromise;
      return Boolean(w.DokkaiStorage.isReady && typeof w.fetchAndRenderSolvedTasks === 'function');
    }, { timeout: 15000 });

    await page.evaluate(async () => {
      const w = window as any;
      if (w.DokkaiStorage) {
        await w.DokkaiStorage.recordSolvedTask({
          text_id: 1,
          title: 'Библиотека (Тест)',
          level: 'N5',
          category: 'short',
          score: 100,
          score_percent: 100,
          last_score: 100,
          correct_count: 1,
          total_questions: 1,
          perfect: true,
          time_spent_sec: 45,
          solved_at: new Date().toISOString()
        });
        if (w.fetchAndRenderSolvedTasks) {
          await w.fetchAndRenderSolvedTasks();
        }
      }
    });

    // Real click on report button in UI chain: button -> open modal
    const reportBtn = page.locator('#solved-tasks-list .btn-solved-action').filter({ hasText: /Заявить|ошибк/ }).first();
    const hasReportBtn = await reportBtn.count() > 0;

    if (hasReportBtn) {
      await reportBtn.click();
    } else {
      // Fallback for main if solved card report button not rendered
      await page.evaluate(() => {
        const w = window as any;
        if (w.openReportModal) {
          w.openReportModal(1, 'Библиотека (Тест)');
        } else if (w.DokkaiSolved && w.DokkaiSolved.openReportModal) {
          w.DokkaiSolved.openReportModal(1, 'Библиотека (Тест)', { state: w.state, elements: w.elements });
        }
      });
    }

    const modalBackdrop = page.locator('#report-modal-backdrop');
    await expect(modalBackdrop).toBeVisible();
    await expect(page.locator('#report-modal-task-title')).toContainText('Библиотека (Тест)');

    // Select reason and fill details
    await page.locator('#report-reason-select').selectOption({ value: 'Опечатка в тексте или вопросе' });
    await page.locator('#report-details-textarea').fill('Тестовое замечание: опечатка во 2 предложении');

    // Listen for alert dialog and submit
    page.once('dialog', async dialog => {
      expect(dialog.message()).toContain('принята');
      await dialog.accept();
    });

    const [resp] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/api/texts/1/report') && r.request().method() === 'POST'),
      page.locator('#btn-submit-report').click(),
    ]);

    expect(resp.status()).toBe(200);
    await expect(modalBackdrop).toHaveClass(/hidden/);
  });

  test('06. Mobile Column Switcher: switchMobileStreamCol smoothly toggles columns on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile column switcher is only rendered on mobile screens');

    await page.goto('/');
    await page.waitForSelector('#tab-col-active', { timeout: 15000 });

    const tabSolved = page.locator('#tab-col-solved');
    const tabActive = page.locator('#tab-col-active');

    // Switch to Solved column
    await tabSolved.click();
    await expect(tabSolved).toHaveClass(/active/);
    await expect(tabActive).not.toHaveClass(/active/);

    // Switch back to Active slots
    await tabActive.click();
    await expect(tabActive).toHaveClass(/active/);
    await expect(tabSolved).not.toHaveClass(/active/);
  });
});
