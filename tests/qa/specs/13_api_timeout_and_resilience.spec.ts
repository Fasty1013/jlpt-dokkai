import { test, expect } from '@playwright/test';

test.describe('13. API Timeout, Cold-start Resilience & Retry Strategy', () => {
  test.setTimeout(60000);

  test('01. 20s Delay Simulation: Shows waking-up notice after 5s and successfully renders catalog after delay', async ({ page }) => {
    // Intercept slot endpoint with 20-second artificial delay
    await page.route('**/api/stream/slots*', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 20000));
      await route.continue();
    });

    await page.goto('/');

    // 1. Initial state: loading spinner should be visible
    const spinner = page.locator('#active-slots-list .loading-spinner');
    await expect(spinner).toBeVisible({ timeout: 5000 });

    // 2. After ~5.5s: Calm server waking-up notification MUST appear
    const wakingNotice = page.locator('text=Сервер просыпается, подождите до минуты…').first();
    await expect(wakingNotice).toBeVisible({ timeout: 10000 });

    // 3. After full 20s delay finishes: Catalog slots MUST load and notice disappears
    const slotCard = page.locator('#active-slots-list .stream-slot-card').first();
    await expect(slotCard).toBeVisible({ timeout: 25000 });

    // 4. Waking notice should now be hidden
    await expect(wakingNotice).toBeHidden({ timeout: 5000 });
  });

  test('02. Network / Timeout Error displays retry button which successfully reloads slots', async ({ page }) => {
    let failFirst = true;

    await page.route('**/api/stream/slots*', async (route) => {
      if (failFirst) {
        failFirst = false;
        await route.abort('timedout');
      } else {
        await route.continue();
      }
    });

    await page.goto('/');

    // Retry button MUST be displayed on error/timeout
    const retryBtn = page.locator('button:has-text("Повторить попытку")');
    await expect(retryBtn).toBeVisible({ timeout: 15000 });

    // Clicking retry button reloads the slots
    await retryBtn.click();
    const slotCard = page.locator('#active-slots-list .stream-slot-card').first();
    await expect(slotCard).toBeVisible({ timeout: 15000 });
  });

  test('03. Submit Answers Resilience: Preserves user answers on network/timeout error and allows successful retry', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    const firstSlot = page.locator('#active-slots-list .stream-slot-card').first();
    await expect(firstSlot).toBeVisible({ timeout: 15000 });
    await firstSlot.locator('button').click();

    // Start pretest
    await page.waitForSelector('#modal-btn-start');
    await page.click('#modal-btn-start');
    await expect(page.locator('#exercise-view')).toBeVisible({ timeout: 10000 });

    // Answer all questions in wizard
    let hasNext = true;
    while (hasNext) {
      await page.waitForSelector('.option-item');
      await page.locator('.option-item').first().click();

      const nextBtn = page.locator('#btn-wizard-next');
      const submitBtn = page.locator('#btn-wizard-submit');

      if (await submitBtn.isVisible()) {
        hasNext = false;
        break;
      } else {
        await nextBtn.click();
        await page.waitForTimeout(300);
      }
    }

    // Verify answers are selected in state
    const initialAnswersCount = await page.evaluate(() => Object.keys(window.state.userAnswers).length);
    expect(initialAnswersCount).toBeGreaterThan(0);

    // Intercept submit endpoint to simulate network/timeout failure on first attempt
    let failSubmit = true;
    await page.route('**/api/stream/complete', async (route) => {
      if (failSubmit) {
        failSubmit = false;
        await route.abort('failed');
      } else {
        await route.continue();
      }
    });

    // Accept error alert
    page.on('dialog', async (dialog) => {
      await dialog.accept();
    });

    // 1. First submit attempt (fails due to network drop)
    const submitBtn = page.locator('#btn-wizard-submit');
    await submitBtn.click();

    // 2. Button must re-enable with retry message
    await expect(submitBtn).toBeEnabled({ timeout: 10000 });
    await expect(submitBtn).toHaveText(/Повторить|Завершить/);

    // 3. User answers MUST NOT be lost from state
    const answersAfterFailure = await page.evaluate(() => Object.keys(window.state.userAnswers).length);
    expect(answersAfterFailure).toBe(initialAnswersCount);

    // 4. Second attempt (succeeds)
    await submitBtn.click();

    // 5. Verification: Analysis banner and score are displayed
    await expect(page.locator('#analysis-banner')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('#score-percent')).toBeVisible({ timeout: 10000 });
  });
});

