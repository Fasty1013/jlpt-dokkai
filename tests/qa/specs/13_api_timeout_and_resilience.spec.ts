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
});
