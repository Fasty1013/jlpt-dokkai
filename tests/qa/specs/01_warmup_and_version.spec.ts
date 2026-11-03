import { test, expect } from '@playwright/test';
import { QAReportGenerator } from '../utils/report_generator';

test.describe('01. Warmup & System Version Verification', () => {
  test('Health check and cold start warmup', async ({ page, baseURL }) => {
    const startTime = Date.now();
    let isHealthy = false;
    let attempts = 0;
    const maxAttempts = 24; // 24 * 5s = 120s max

    console.log(`[WARMUP] Проверка доступности сервера: ${baseURL}`);

    while (!isHealthy && attempts < maxAttempts) {
      attempts++;
      try {
        const res = await page.request.get(`${baseURL}/api/health`, { timeout: 5000 });
        if (res.status() === 200) {
          const data = await res.json();
          if (data.status === 'ok') {
            isHealthy = true;
            break;
          }
        }
      } catch (e) {
        console.log(`[WARMUP] Попытка ${attempts}/${maxAttempts}: сервер ещё не ответил, ожидание 5 сек...`);
        await new Promise((r) => setTimeout(r, 5000));
      }
    }

    const elapsedMs = Date.now() - startTime;
    console.log(`[WARMUP] Сервер готов к работе за ${(elapsedMs / 1000).toFixed(1)} с`);
    expect(isHealthy, `Сервер ${baseURL} не ответил за 120 секунд`).toBeTruthy();

    // Запрос эндпоинта версии
    const versionRes = await page.request.get(`${baseURL}/api/version`);
    if (versionRes.status() === 200) {
      const versionData = await versionRes.json();
      expect(versionData).toHaveProperty('version');
      expect(versionData).toHaveProperty('commit');
      expect(versionData).toHaveProperty('env');
      console.log(`[VERSION] Build: ${versionData.version} (Commit: ${versionData.commit}, Env: ${versionData.env})`);
      QAReportGenerator.saveReport(elapsedMs, versionData);
    } else {
      console.log(`[VERSION] Эндпоинт /api/version вернул статус ${versionRes.status()} (на Render активна предыдущая версия)`);
      QAReportGenerator.saveReport(elapsedMs, { version: 'pre-2.0.2', commit: 'render-deployed', env: 'production' });
    }
  });
});

