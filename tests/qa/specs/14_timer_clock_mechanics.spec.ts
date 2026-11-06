import { test, expect } from '@playwright/test';

test.describe('14. Timer Clock Mechanics & Lifecycle (page.clock)', () => {
  test('01. Complete Timer Lifecycle: Countdown, Pause/Resume, +1 Min, 60s Warning, Expiration & Dismiss', async ({ page }) => {
    // 1. Install fake timers and pause clock so time only advances via runFor
    const fixedTime = new Date('2026-11-06T12:00:00Z');
    await page.clock.install({ time: fixedTime });
    await page.clock.pauseAt(fixedTime);

    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

    // Open first slot
    const firstSlotBtn = page.locator('#active-slots-list .stream-slot-card button').first();
    await firstSlotBtn.click();
    await page.waitForSelector('#pretest-modal-backdrop', { timeout: 10000 });

    // Enable timer in pretest settings
    const toggleTimer = page.locator('label:has(#pretest-toggle-timer)');
    await toggleTimer.click();
    await expect(page.locator('#timer-duration-selector')).toBeVisible();

    // Start exercise
    await page.click('#modal-btn-start');
    await expect(page.locator('#exercise-view')).toBeVisible();

    // A. Countdown Start Verification
    const timerBox = page.locator('#timer-box');
    const timerDisplay = page.locator('#timer-display');
    await expect(timerBox).toBeVisible();
    await expect(timerDisplay).toHaveText('03:00');

    // Advance clock by 5 seconds
    await page.clock.runFor(5000);
    await expect(timerDisplay).toHaveText('02:55');

    // B. Pause and Resume Verification
    const btnPause = page.locator('#btn-timer-toggle-pause');
    await btnPause.click();
    await expect(timerBox).toHaveClass(/is-paused/);
    await expect(btnPause).toHaveText('▶️');

    // Clock ticks while paused: display MUST NOT decrease
    await page.clock.runFor(10000);
    await expect(timerDisplay).toHaveText('02:55');

    // Resume timer
    await btnPause.click();
    await expect(timerBox).not.toHaveClass(/is-paused/);
    await expect(btnPause).toHaveText('⏸️');

    // Clock ticks after resume: display decreases
    await page.clock.runFor(5000);
    await expect(timerDisplay).toHaveText('02:50');

    // C. +1 Minute Verification
    const btnAddMin = page.locator('#btn-timer-add-min');
    await btnAddMin.click();
    await expect(timerDisplay).toHaveText('03:50');

    // D. 60 Seconds Warning Verification
    // Current remaining is 230s (3m 50s). Advance 170s -> remaining is 60s
    await page.clock.runFor(170000);
    await expect(timerDisplay).toHaveText('01:00');
    await expect(timerBox).toHaveClass(/timer-warning/);

    // E. Timer Expiration Verification
    // Advance remaining 60s -> remaining is 00:00
    await page.clock.runFor(60000);
    await expect(timerDisplay).toHaveText('00:00');
    await expect(timerBox).toHaveClass(/timer-expired/);
    await expect(page.locator('#timer-alert-banner')).toBeVisible();

    // F. Dismiss Timer & Runtime Re-enable Verification
    page.once('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Выключить таймер');
      await dialog.accept();
    });

    const btnDismiss = page.locator('#btn-timer-dismiss');
    await btnDismiss.click();
    await expect(timerBox).toBeHidden();

    // Runtime enable button appears
    const btnEnableRuntime = page.locator('#btn-enable-timer-runtime');
    await expect(btnEnableRuntime).toBeVisible();

    // Re-enable timer at runtime
    await btnEnableRuntime.click();
    await expect(timerBox).toBeVisible();
    await expect(btnEnableRuntime).toBeHidden();
  });
});
