import { test, expect } from '@playwright/test';
import { TelemetryCollector } from '../utils/telemetry_collector';
import { QAReportGenerator } from '../utils/report_generator';

test.describe('04. Anti-Cheat Protocol & Network Data Isolation', () => {
  test('Audit reading endpoints for answer key and explanation leakage', async ({ page, baseURL }) => {
    const telemetry = new TelemetryCollector();
    telemetry.attach(page);

    // 1. Открываем каталог и запрашиваем слоты
    await page.goto('/');
    await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });

    // Проверяем собранные запросы
    if (telemetry.antiCheatLeaks.length > 0) {
      for (const leak of telemetry.antiCheatLeaks) {
        QAReportGenerator.registerBug({
          title: `[ANTI-CHEAT LEAK] ${leak.message}`,
          severity: 'blocker',
          category: 'privacy_security',
          env: {
            where: baseURL?.includes('localhost') ? 'local' : 'prod',
            url: leak.url || page.url(),
            viewport: 'N/A',
            engine: 'chromium',
            theme: 'light',
            network: 'normal',
          },
          steps: ['1. Запросить чтение текста через API', '2. Проверить тело JSON ответа'],
          expected: 'Поля is_correct, explanation, trap_type, evidence_span_id отсутствуют в ответе',
          actual: leak.message,
          evidence: [JSON.stringify(leak.details || {})],
          reproduced: '2/2',
          suspected_cause: 'Pydantic-схема ответа TextReadSchema раскрывает скрытые поля',
          status: 'confirmed',
        });
      }
    }

    expect(telemetry.antiCheatLeaks.length, 'ОБНАРУЖЕНА УТЕЧКА КЛЮЧЕЙ ANTI-CHEAT!').toBe(0);

    // 2. Активный зонд: неавторизованный запрос к деталям нерешённого задания
    // Запрашиваем заведомо нерешённый ID текста
    const probeRes = await page.request.get(`${baseURL}/api/stream/solved/99999?user_id=probe-unauthorized-user`);
    // Должен вернуть 403 Forbidden либо 404 Not Found
    expect([403, 404]).toContain(probeRes.status());
    console.log(`[ANTI-CHEAT] Активный зонд /api/stream/solved/99999 вернул статус ${probeRes.status()} (доступ изолирован)`);
  });
});

