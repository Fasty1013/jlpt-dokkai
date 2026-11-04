import { test, expect } from '@playwright/test';

test.describe('07. PWA Shell, Web App Manifest & Offline Resilience', () => {
  test('Audit web app manifest, service worker caching, and offline page reload resilience', async ({ page, baseURL, context }) => {
    // 1. Проверка Web App Manifest
    const manifestRes = await page.request.get(`${baseURL}/static/manifest.json`);
    if (manifestRes.status() === 200) {
      const manifest = await manifestRes.json();
      expect(manifest).toHaveProperty('name');
      expect(manifest).toHaveProperty('short_name');
      expect(manifest).toHaveProperty('start_url');
      expect(manifest.display).toBe('standalone');
      expect(Array.isArray(manifest.icons)).toBeTruthy();
      console.log(`[PWA] Manifest проверен: '${manifest.name}' (display: ${manifest.display})`);
    }

    // 2. Первичная онлайн-загрузка страницы
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });
    await page.waitForSelector('#active-slots-list .stream-slot-card, .catalog-card', { timeout: 15000 });

    // Ожидаем готовности Service Worker
    await page.evaluate(async () => {
      if ('serviceWorker' in navigator) {
        await navigator.serviceWorker.ready;
      }
    });

    // Прогреваем кэш API через Service Worker
    await page.evaluate(async () => {
      const uid = localStorage.getItem('dokkai_user_id') || 'user-default';
      await Promise.allSettled([
        fetch(`/api/stream/slots?user_id=${uid}`),
        fetch('/api/texts'),
        fetch('/static/css/variables.css?v=2.1.0'),
        fetch('/static/css/base.css?v=2.1.0'),
        fetch('/static/css/layout.css?v=2.1.0'),
        fetch('/static/css/catalog.css?v=2.1.0')
      ]);
    });
    await page.waitForTimeout(600);

    // Замеряем исходные стили онлайн
    const headerBgOnline = await page.locator('.app-header').evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(headerBgOnline).not.toBe('rgba(0, 0, 0, 0)');
    expect(headerBgOnline).not.toBe('');

    const cardRadiusOnline = await page.locator('.stream-slot-card, .catalog-card').first().evaluate(el => window.getComputedStyle(el).borderRadius);
    expect(cardRadiusOnline).not.toBe('0px');

    // 3. Отключаем сеть (полный офлайн)
    await context.setOffline(true);

    // 4. Перезагружаем страницу в офлайн-режиме
    await page.reload({ waitUntil: 'domcontentloaded' });

    // 5. Проверяем, что приложение загрузилось из кэша
    await expect(page.locator('#app')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('#catalog-view')).toBeVisible({ timeout: 10000 });

    // 6. Проверяем стили в офлайне
    const headerBgOffline = await page.locator('.app-header').evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(headerBgOffline, 'Вычисленный фон шапки в офлайне должен совпадать со стилем из кэша').toBe(headerBgOnline);

    const cardOffline = page.locator('.stream-slot-card, .catalog-card').first();
    await expect(cardOffline, 'Карточка задания из кэша отображается в офлайне').toBeVisible({ timeout: 10000 });

    const cardRadiusOffline = await cardOffline.evaluate(el => window.getComputedStyle(el).borderRadius);
    expect(cardRadiusOffline, 'Стили карточки применены корректно из кэша').toBe(cardRadiusOnline);

    // 7. Восстанавливаем сеть
    await context.setOffline(false);
  });
});
