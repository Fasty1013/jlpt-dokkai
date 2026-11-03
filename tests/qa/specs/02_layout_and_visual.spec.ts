import { test, expect } from '@playwright/test';
import { VisualOverflowDetector } from '../utils/visual_overflow_detector';
import { TelemetryCollector } from '../utils/telemetry_collector';
import { QAReportGenerator } from '../utils/report_generator';

test.describe('02. Layout, Responsive Viewports & Japanese Typography', () => {
  test('Audit catalog layout, overflow, touch targets and typography', async ({ page, isMobile, viewport }, testInfo) => {
    const telemetry = new TelemetryCollector();
    telemetry.attach(page);

    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // 1. Проверка горизонтальной прокрутки (scrollWidth > clientWidth)
    const overflowIssues = await VisualOverflowDetector.checkHorizontalOverflow(page);
    for (const issue of overflowIssues) {
      QAReportGenerator.registerBug({
        title: issue.message,
        severity: 'critical',
        category: 'visual',
        env: {
          where: testInfo.project.use.baseURL?.includes('localhost') ? 'local' : 'prod',
          url: page.url(),
          viewport: `${viewport?.width}x${viewport?.height}`,
          engine: testInfo.project.use.browserName || 'chromium',
          theme: (testInfo.project.use.colorScheme as any) || 'light',
          network: 'normal',
        },
        steps: ['1. Открыть главную страницу', '2. Измерить scrollWidth относительно clientWidth'],
        expected: 'scrollWidth <= clientWidth, горизонтальный скролл отсутствует',
        actual: issue.message,
        evidence: [JSON.stringify(issue.details || {})],
        reproduced: '1/2',
        suspected_cause: 'Элемент с фиксированной шириной превышает ширину мобильного экрана',
        status: 'new',
      });
    }
    expect(overflowIssues.length, `Обнаружен горизонтальный скролл на ${viewport?.width}x${viewport?.height}`).toBe(0);

    // 2. Проверка адаптивных мобильных табов (< 880px)
    if (viewport && viewport.width < 880) {
      const mobileTabs = page.locator('#stream-mobile-tabs');
      await expect(mobileTabs).toBeVisible();

      // Проверяем переключение табов «⚡ Задания» и «🏆 Решённые»
      await page.click('#tab-col-solved');
      await expect(page.locator('#col-solved-archive')).toBeVisible();

      await page.click('#tab-col-active');
      await expect(page.locator('#col-active-slots')).toBeVisible();
    } else {
      // На десктопе обе колонки видны одновременно
      await expect(page.locator('#col-active-slots')).toBeVisible();
      await expect(page.locator('#col-solved-archive')).toBeVisible();
    }

    // 3. Проверка японской типографики и тегов ruby
    const typographyIssues = await VisualOverflowDetector.checkJapaneseTypography(page);
    for (const issue of typographyIssues) {
      QAReportGenerator.registerBug({
        title: issue.message,
        severity: 'major',
        category: 'content',
        env: {
          where: 'local',
          url: page.url(),
          viewport: `${viewport?.width}x${viewport?.height}`,
          engine: testInfo.project.use.browserName || 'chromium',
          theme: 'light',
          network: 'normal',
        },
        steps: ['1. Загрузить страницу', '2. Проверить вложенность <rt> в <ruby> и наличие битых иероглифов'],
        expected: 'Корректный синтаксис <ruby>...</ruby> и отсутствие "тофу"',
        actual: issue.message,
        evidence: [],
        reproduced: '1/2',
        suspected_cause: 'Некорректная разметка или отсутствие шрифта',
        status: 'new',
      });
    }
    expect(typographyIssues.length, 'Ошибки в японской типографике').toBe(0);

    // 4. Проверка консольных ошибок
    const consoleErrors = telemetry.issues.filter((i) => i.type === 'console_error' || i.type === 'page_error');
    expect(consoleErrors.length, `Консольные ошибки на странице: ${consoleErrors.map((e) => e.message).join('; ')}`).toBe(0);
  });
});

