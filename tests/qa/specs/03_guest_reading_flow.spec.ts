import { test, expect } from '@playwright/test';
import { TelemetryCollector } from '../utils/telemetry_collector';
import { VisualOverflowDetector } from '../utils/visual_overflow_detector';

test.describe('03. Guest Reading Flow & Interactive Controls', () => {
  test('Complete guest reading lifecycle without submission', async ({ page, viewport }) => {
    const telemetry = new TelemetryCollector();
    telemetry.attach(page);

    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

    // 1. Клик по первому доступному заданию в потоке
    const firstSlot = page.locator('#active-slots-list .stream-slot-card').first();
    await firstSlot.locator('button').click();

    // 2. Проверка модального окна предстартовых настроек
    const modal = page.locator('#pretest-modal-backdrop');
    await expect(modal).toBeVisible();

    // Переключение тумблеров (фуригана, таймер, подсказки)
    const toggleFurigana = page.locator('label:has(#pretest-toggle-furigana)');
    await toggleFurigana.click();
    await toggleFurigana.click(); // вернем обратно

    const toggleTimer = page.locator('label:has(#pretest-toggle-timer)');
    await toggleTimer.click();
    await expect(page.locator('#timer-duration-selector')).toBeVisible();
    await toggleTimer.click(); // выключим таймер

    // 3. Запуск решения
    await page.click('#modal-btn-start');
    await expect(page.locator('#exercise-view')).toBeVisible();
    await expect(page.locator('#passage-content')).toBeVisible();

    // 4. Проверка японского текста и инструментов чтения
    const passageText = await page.locator('#passage-content').textContent();
    expect(passageText && passageText.length > 30).toBeTruthy();

    // Переключение шрифта (Gothic <-> Mincho)
    await page.click('#btn-font-mincho');
    await expect(page.locator('#passage-content')).toHaveClass(/font-mincho/);
    await page.click('#btn-font-gothic');
    await expect(page.locator('#passage-content')).toHaveClass(/font-gothic/);

    // 5. Проверка пошагового мастера вопросов Wizard
    const wizardCard = page.locator('#wizard-card-area');
    await expect(wizardCard).toBeVisible();

    const options = page.locator('.option-item');
    const optionCount = await options.count();
    expect(optionCount).toBe(4); // строго 4 варианта по спецификации JLPT

    // Выбираем первый вариант
    await options.first().click();

    // 6. Проверка всплывающего словаря Yomichan
    // Выделяем слово или кликаем по кандзи
    const firstRuby = page.locator('#passage-content ruby').first();
    if (await firstRuby.isVisible()) {
      await firstRuby.click();
      // Если словарь включен, может появиться всплывающая карточка
      const dictCard = page.locator('#popup-dictionary-card');
      // Закрытие словаря
      if (await dictCard.isVisible()) {
        await page.click('#popup-btn-close');
        await expect(dictCard).toBeHidden();
      }
    }

    // 7. Проверка безопасной кнопки «← На главную»
    const abortBtn = page.locator('#btn-abort-exercise');
    await expect(abortBtn).toBeVisible();
    await abortBtn.click();

    // Возврат в каталог
    await expect(page.locator('#catalog-view')).toBeVisible();

    // 8. Контроль отсутствия критических ошибок
    const fatalErrors = telemetry.issues.filter((i) => i.type === 'page_error');
    expect(fatalErrors.length, 'Необработанные ошибки JS во время выполнения теста').toBe(0);
  });
});