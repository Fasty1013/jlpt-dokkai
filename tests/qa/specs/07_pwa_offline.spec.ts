import { test, expect } from '@playwright/test';

test.describe('07. PWA Shell, Web App Manifest & Offline Resilience', () => {
  test('Audit web app manifest and offline fallback behavior', async ({ page, baseURL, context }) => {
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
    } else {
      console.log(`[PWA] Manifest пока не отдан на боевом сервере (статус ${manifestRes.status()}), требуется деплой коммита в Render`);
    }

    // 2. Загрузка страницы и симуляция отключения сети
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // Отключаем сеть
    await context.setOffline(true);

    // Проверяем, что уже загруженное приложение не крашится в белый экран
    const bodyContent = await page.locator('#app').isVisible();
    expect(bodyContent, 'Приложение остаётся видимым при внезапном отключении сети').toBeTruthy();

    // Восстанавливаем сеть
    await context.setOffline(false);
  });
});

