import { test, expect } from '@playwright/test';

test.describe('16. Exercise Reading View & Step-by-Step Question Wizard Lifecycle', () => {
  test.describe.configure({ mode: 'serial' });

  test('01. Option Selection: Choosing and switching answers updates radio, card highlight, and answered count', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    // Open Text 25 (3 questions)
    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    // Initial state: Question 1
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 1 из 3');
    await expect(page.locator('#answered-count')).toHaveText('0');
    await expect(page.locator('#total-questions-count')).toHaveText('3');
    await expect(page.locator('#btn-wizard-next')).toBeDisabled();

    // 1. Select Option 1
    const optItems = page.locator('#wizard-card-area .option-item');
    await expect(optItems).toHaveCount(4);
    await optItems.nth(0).click();

    await expect(optItems.nth(0)).toHaveClass(/selected/);
    await expect(optItems.nth(0).locator('input.option-radio')).toBeChecked();
    await expect(page.locator('#answered-count')).toHaveText('1');
    await expect(page.locator('#btn-wizard-next')).toBeEnabled();

    // 2. Switch selection to Option 2
    await optItems.nth(1).click();
    await expect(optItems.nth(1)).toHaveClass(/selected/);
    await expect(optItems.nth(1).locator('input.option-radio')).toBeChecked();
    await expect(optItems.nth(0)).not.toHaveClass(/selected/);
    await expect(page.locator('#answered-count')).toHaveText('1');
  });

  test('02. Step Navigation: Next/Prev navigation, dynamic button labels, and wizard track dots', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    // On Question 1: Prev button returns to catalog
    const btnPrev = page.locator('#btn-wizard-prev');
    const btnNext = page.locator('#btn-wizard-next');
    await expect(btnPrev).toContainText('На главную');

    // Answer Q1
    await page.locator('#wizard-card-area .option-item').nth(1).click();
    await btnNext.click();

    // On Question 2
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 2 из 3');
    await expect(btnPrev).toContainText('Назад');

    // Check wizard dots
    const dots = page.locator('#wizard-track .wizard-dot');
    await expect(dots).toHaveCount(3);
    await expect(dots.nth(0)).toHaveClass(/answered/);
    await expect(dots.nth(1)).toHaveClass(/active/);

    // Navigate back to Q1 and verify selection is preserved
    await btnPrev.click();
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 1 из 3');
    await expect(page.locator('#wizard-card-area .option-item').nth(1)).toHaveClass(/selected/);
    await expect(page.locator('#wizard-card-area .option-item').nth(1).locator('input.option-radio')).toBeChecked();

    // Navigate forward to Q2
    await btnNext.click();
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 2 из 3');
  });

  test('03. Submit Guard: Next button hides and Submit button enables only when all questions are answered', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    // Answer Q1 -> Q2
    await page.locator('#wizard-card-area .option-item').nth(0).click();
    await page.click('#btn-wizard-next');

    // Answer Q2 -> Q3
    await page.locator('#wizard-card-area .option-item').nth(2).click();
    await page.click('#btn-wizard-next');

    // On Last Question (Q3)
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 3 из 3');
    await expect(page.locator('#btn-wizard-next')).toHaveClass(/hidden/);
    const btnSubmit = page.locator('#btn-wizard-submit');
    await expect(btnSubmit).not.toHaveClass(/hidden/);

    // Q3 not yet answered -> Submit button is disabled
    await expect(btnSubmit).toBeDisabled();

    // Answer Q3 -> Submit button is enabled
    await page.locator('#wizard-card-area .option-item').nth(1).click();
    await expect(btnSubmit).toBeEnabled();
    await expect(page.locator('#answered-count')).toHaveText('3');
  });

  test('04. Active Session Storage Parity: Serialized active_session matches schema and values', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    // Answer Q1 and advance to Q2
    await page.locator('#wizard-card-area .option-item').nth(0).click();
    await page.click('#btn-wizard-next');
    await page.locator('#wizard-card-area .option-item').nth(1).click();

    // Inspect stored active_session
    const session = await page.evaluate(async () => {
      if (window.DokkaiStorage) {
        return await window.DokkaiStorage.getActiveSession();
      }
      const raw = localStorage.getItem('dokkai_active_session');
      return raw ? JSON.parse(raw) : null;
    });

    expect(session).not.toBeNull();
    expect(session.textId).toBe(25);
    expect(session.title).toBe('日本での生活と四季 (N5) #1');
    expect(session.level).toBe('N5');
    expect(session.currentQuestionIndex).toBe(1);
    expect(Object.keys(session.userAnswers).length).toBe(2);
    expect(session.timer).toBeDefined();

    // Verify exact contract keys
    const sessionKeys = Object.keys(session).sort();
    expect(sessionKeys).toEqual(['currentQuestionIndex', 'id', 'level', 'textId', 'timer', 'timestamp', 'title', 'userAnswers']);
  });

  test('05. In-Progress Recovery: Unfinished exercise banner prompts and successfully resumes state after reload', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    // Start Text 25, answer Q1, advance to Q2
    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    await page.locator('#wizard-card-area .option-item').nth(0).click();
    await page.click('#btn-wizard-next');

    // Reload page while on exercise view
    await page.reload();
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    // Unfinished test recovery banner must be visible
    const resumeBanner = page.locator('#unfinished-test-banner');
    await expect(resumeBanner).toBeVisible();
    await expect(page.locator('#unfinished-task-title')).toContainText('日本での生活と四季');

    // Click resume
    await page.click('#btn-resume-unfinished');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
    await expect(page.locator('#wizard-step-label')).toHaveText('Вопрос 2 из 3');
  });

  test('06. Interactive Controls: Font switching, sizing and popup dictionary work seamlessly during exercise', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });

    await page.evaluate(() => window.openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });

    const passageContent = page.locator('#passage-content');

    // 1. Font Family Switching (Gothic <-> Mincho)
    await expect(passageContent).toHaveClass(/font-gothic/);
    await page.click('#btn-font-mincho');
    await expect(passageContent).toHaveClass(/font-mincho/);
    await page.click('#btn-font-gothic');
    await expect(passageContent).toHaveClass(/font-gothic/);

    // 2. Adjust Font Size (Increase / Decrease)
    await expect(passageContent).toHaveCSS('font-size', '20px');
    await page.click('#btn-font-increase');
    await expect(passageContent).toHaveCSS('font-size', '22px');
    await page.click('#btn-font-decrease');
    await expect(passageContent).toHaveCSS('font-size', '20px');

    // 3. Popup Dictionary Toggle
    const btnPopupDict = page.locator('#btn-toggle-popup-dict');
    const dictStatus = page.locator('#popup-dict-status');
    await expect(dictStatus).toHaveText('ВКЛ');
    await btnPopupDict.click();
    await expect(dictStatus).toHaveText('ВЫКЛ');
    await btnPopupDict.click();
    await expect(dictStatus).toHaveText('ВКЛ');
  });
});
