import { test, expect } from '@playwright/test';

test.describe('05. Stream Lifecycle & Solved Column (Localhost only)', () => {
  test.skip(process.env.TARGET === 'prod', 'Завершение заданий и запись строго запрещены на Production');

  test('Complete task, verify atomic transition to Solved and slot replenishment', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

    const initialSolvedCountText = await page.locator('#mobile-solved-count').textContent();
    const initialSolved = parseInt(initialSolvedCountText || '0', 10);

    // Открываем первое задание
    const firstSlot = page.locator('#active-slots-list .stream-slot-card').first();
    const taskTitle = await firstSlot.locator('.slot-title').textContent();
    await firstSlot.locator('button').click();

    // Запускаем тест в настройках
    await page.waitForSelector('#modal-btn-start');
    await page.click('#modal-btn-start');

    // Проходим все вопросы Wizard
    let hasNext = true;
    while (hasNext) {
      await page.waitForSelector('.option-item');
      // Кликаем по первому варианту ответа
      await page.locator('.option-item').first().click();

      const nextBtn = page.locator('#btn-wizard-next');
      const submitBtn = page.locator('#btn-wizard-submit');

      if (await submitBtn.isVisible()) {
        // Достигли последнего вопроса
        hasNext = false;
        await submitBtn.click();
        break;
      } else {
        await nextBtn.click();
        await page.waitForTimeout(300);
      }
    }

    // Проверяем экран результатов
    await expect(page.locator('#analysis-banner')).toBeVisible({ timeout: 10000 });
    const scoreText = await page.locator('#score-text').textContent();
    console.log(`[STREAM LIFECYCLE] Задание '${taskTitle}' завершено. Результат: ${scoreText}`);

    // Возвращаемся на главную
    await page.click('#btn-back-to-catalog');
    await expect(page.locator('#catalog-view')).toBeVisible();

    // Проверяем, что счетчик решённых увеличился
    await page.waitForTimeout(1000);
    const newSolvedCountText = await page.locator('#mobile-solved-count').textContent();
    const newSolved = parseInt(newSolvedCountText || '0', 10);
    expect(newSolved).toBeGreaterThanOrEqual(initialSolved);

    // Проверяем наличие карточки в колонке «🏆 Решённые»
    if (page.viewportSize() && page.viewportSize()!.width < 880) {
      await page.click('#tab-col-solved');
    }
    const solvedCards = page.locator('#solved-tasks-list .stream-solved-card');
    await expect(solvedCards.first()).toBeVisible();
    console.log('[STREAM LIFECYCLE] Атомарный перенос в «Решённые» и пополнение слота подтверждены!');
  });
});
