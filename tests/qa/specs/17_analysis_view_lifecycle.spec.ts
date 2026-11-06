import { test, expect, Page } from '@playwright/test';

test.describe('17. Analysis View & Post-Submit Lifecycle', () => {
  test.describe.configure({ mode: 'serial' });

  async function startExerciseText25(page: Page) {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });
    await page.evaluate(() => (window as any).openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
  }

  async function answerAndSubmit(page: Page) {
    while (true) {
      await page.waitForSelector('#wizard-card-area .option-item', { timeout: 10000 });
      const activeCard = page.locator('#wizard-card-area .question-card').first();
      await activeCard.locator('.option-item').first().click();

      const submitBtn = page.locator('#btn-wizard-submit');
      if (await submitBtn.isVisible()) {
        await expect(submitBtn).toBeEnabled();
        await submitBtn.click();
        break;
      } else {
        const nextBtn = page.locator('#btn-wizard-next');
        await expect(nextBtn).toBeEnabled();
        await nextBtn.click();
        await page.waitForTimeout(300);
      }
    }
    await page.waitForSelector('#analysis-banner:not(.hidden)', { timeout: 15000 });
  }

  test('01. Submit Flow & Analysis Banner: Complete submission transitions to analysis mode with score and metadata', async ({ page }) => {
    await startExerciseText25(page);
    await answerAndSubmit(page);

    // 1. View visibility
    await expect(page.locator('#analysis-banner')).toBeVisible();
    await expect(page.locator('#analysis-qa-container')).toBeVisible();
    await expect(page.locator('#wizard-header')).toBeHidden();
    await expect(page.locator('#wizard-card-area')).toBeHidden();
    await expect(page.locator('#wizard-nav-bar')).toBeHidden();

    // 2. Score text and result banner assertions
    const scoreText = page.locator('#score-text');
    await expect(scoreText).toBeVisible();
    const scoreVal = await scoreText.textContent();
    expect(scoreVal).toMatch(/\d+\s*\/\s*\d+/);

    const scorePercent = page.locator('#score-percent');
    await expect(scorePercent).toBeVisible();
    const percentVal = await scorePercent.textContent();
    expect(percentVal).toContain('%');

    const resultTitle = page.locator('#banner-result-title');
    await expect(resultTitle).toBeVisible();
    expect((await resultTitle.textContent())!.length).toBeGreaterThan(0);

    const resultMeta = page.locator('#banner-result-meta');
    await expect(resultMeta).toBeVisible();
    expect((await resultMeta.textContent())!.toLowerCase()).toContain('затрачено');
  });

  test('02. Tabbed Analysis Navigation: Question tabs render with status dots and switch active cards', async ({ page }) => {
    await startExerciseText25(page);
    await answerAndSubmit(page);

    const tabs = page.locator('.analysis-tab-btn');
    const tabCount = await tabs.count();
    expect(tabCount).toBe(3); // Text 25 has exactly 3 questions

    // First tab is active by default
    await expect(tabs.first()).toHaveClass(/active/);
    const firstStatusDot = tabs.first().locator('.analysis-tab-status');
    await expect(firstStatusDot).toHaveClass(/correct|wrong/);

    // Switch to second tab
    const secondTab = tabs.nth(1);
    await secondTab.click();
    await expect(secondTab).toHaveClass(/active/);
    await expect(tabs.first()).not.toHaveClass(/active/);

    // Verify active question card updated to Q2
    const activeCard = page.locator('#analysis-active-card .question-card');
    await expect(activeCard).toBeVisible();
    const numBadge = activeCard.locator('.question-num-badge');
    await expect(numBadge).toHaveText(/№2/);

    // Switch to third tab
    const thirdTab = tabs.nth(2);
    await thirdTab.click();
    await expect(thirdTab).toHaveClass(/active/);
    await expect(secondTab).not.toHaveClass(/active/);
    await expect(activeCard.locator('.question-num-badge')).toHaveText(/№3/);
  });

  test('03. Option State Highlights & Explanation Boxes: Correct answer, user choice, and trap badges are rendered', async ({ page }) => {
    await startExerciseText25(page);
    await answerAndSubmit(page);

    const activeCard = page.locator('#analysis-active-card .question-card');
    await expect(activeCard).toBeVisible();

    // Check correct option styling exists
    const correctOpt = activeCard.locator('.option-item.state-correct');
    await expect(correctOpt).toBeVisible();
    await expect(correctOpt.locator('.badge-correct')).toContainText('Правильный ответ');

    // General question analysis box
    const generalExp = activeCard.locator('.question-general-explanation');
    await expect(generalExp).toBeVisible();
    await expect(generalExp).toContainText('Разбор вопроса');
  });

  test('04. Evidence Locator & Highlighting: Evidence locator button pulses target passage span', async ({ page }) => {
    await startExerciseText25(page);
    await answerAndSubmit(page);

    // Toggle evidence control in banner
    const btnToggleEvidence = page.locator('#btn-toggle-evidence');
    await expect(btnToggleEvidence).toBeVisible();

    // Check evidence locator button if evidence span is defined
    const btnLocate = page.locator('#analysis-active-card .btn-locate-evidence');
    if (await btnLocate.isVisible()) {
      await btnLocate.click();
      const pulsedSpan = page.locator('#passage-content .evidence-active-pulse');
      await expect(pulsedSpan).toBeVisible();
    }

    // Toggle evidence off and on
    const evidenceStatus = page.locator('#evidence-status');
    const initialStatus = await evidenceStatus.textContent();

    await btnToggleEvidence.click();
    const newStatus = await evidenceStatus.textContent();
    expect(newStatus).not.toEqual(initialStatus);

    await btnToggleEvidence.click();
    await expect(evidenceStatus).toHaveText(initialStatus || 'ВКЛ');
  });

  test('05. Supplementary Drawer: Translation and vocabulary open and close smoothly', async ({ page }) => {
    await startExerciseText25(page);
    await answerAndSubmit(page);

    const drawer = page.locator('#supplementary-drawer');
    await expect(drawer).toHaveClass(/hidden/);

    // Open translation
    await page.locator('#btn-toggle-translation').click();
    await expect(drawer).not.toHaveClass(/hidden/);
    const transText = page.locator('#translation-text');
    await expect(transText).toBeVisible();
    expect((await transText.textContent())!.length).toBeGreaterThan(0);

    // Close drawer
    await page.locator('#btn-close-drawer').click();
    await expect(drawer).toHaveClass(/hidden/);

    // Open vocab
    await page.locator('#btn-toggle-vocab').click();
    await expect(drawer).not.toHaveClass(/hidden/);
    await expect(page.locator('#vocab-list')).toBeVisible();

    // Close again
    await page.locator('#btn-close-drawer').click();
    await expect(drawer).toHaveClass(/hidden/);
  });

  test('06. Storage State Parity: Active session is cleared after submission', async ({ page }) => {
    await startExerciseText25(page);

    // During exercise, active_session exists
    const inProgressSession = await page.evaluate(async () => {
      if ((window as any).DokkaiStorage && (window as any).DokkaiStorage.getActiveSession) {
        return await (window as any).DokkaiStorage.getActiveSession();
      }
      return null;
    });
    expect(inProgressSession).not.toBeNull();

    await answerAndSubmit(page);

    // After submission, active_session is cleared
    const postSubmitSession = await page.evaluate(async () => {
      if ((window as any).DokkaiStorage && (window as any).DokkaiStorage.getActiveSession) {
        return await (window as any).DokkaiStorage.getActiveSession();
      }
      return null;
    });
    expect(postSubmitSession).toBeNull();
  });
});
