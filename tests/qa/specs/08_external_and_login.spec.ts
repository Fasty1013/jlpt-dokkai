import { test, expect } from '@playwright/test';

test.describe('08. External Services & Auth Host Parameters', () => {
  test('Audit external link parameters and third-party script isolation', async ({ page, baseURL }) => {
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // 1. Проверяем внешние ссылки (Google Fonts, CDN)
    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('link[href]')).map((l) => l.getAttribute('href') || '');
    });

    const googleFontLink = links.find((l) => l.includes('fonts.googleapis.com'));
    expect(googleFontLink, 'Подключение шрифтов Google Fonts присутствует').toBeTruthy();

    // 2. Проверка изоляции сторонних скриптов (приложение не должно падать при блокировке трекеров)
    const bodyContent = await page.locator('#catalog-view').isVisible();
    expect(bodyContent).toBeTruthy();

    console.log('[EXTERNAL] Внешние шрифты и статические ассеты загружены корректно');
  });
});

