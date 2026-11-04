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
    await page.waitForSelector('.stream-column', { timeout: 15000 });

    // Ожидаем активации Service Worker
    await page.waitForFunction(() => {
      return Boolean(navigator.serviceWorker && navigator.serviceWorker.controller);
    }, { timeout: 8000 }).catch(() => null);

    // Замеряем исходные вычисленные стили онлайн
    const headerBgOnline = await page.locator('.app-header').evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(headerBgOnline).not.toBe('rgba(0, 0, 0, 0)');
    expect(headerBgOnline).not.toBe('');

    const colRadiusOnline = await page.locator('.stream-column').first().evaluate(el => window.getComputedStyle(el).borderRadius);
    expect(colRadiusOnline).not.toBe('0px');

    // 3. Отключаем сеть (полный офлайн)
    await context.setOffline(true);

    // 4. Перезагружаем страницу в офлайн-режиме
    await page.reload({ waitUntil: 'domcontentloaded' });

    // 5. Проверяем, что приложение загрузилось из кэша без белого экрана
    await expect(page.locator('#app')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('#catalog-view')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('#col-active-slots')).toBeVisible({ timeout: 10000 });

    // 6. Проверяем, что стили применены корректно в офлайне из кэша
    const headerBgOffline = await page.locator('.app-header').evaluate(el => window.getComputedStyle(el).backgroundColor);
    expect(headerBgOffline, 'Вычисленный фон шапки в офлайне должен совпадать со стилем из кэша').toBe(headerBgOnline);

    const colRadiusOffline = await page.locator('.stream-column').first().evaluate(el => window.getComputedStyle(el).borderRadius);
    expect(colRadiusOffline, 'Стили колонок каталога применены корректно из кэша').toBe(colRadiusOnline);

    // 7. Восстанавливаем сеть
    await context.setOffline(false);
  });
});
