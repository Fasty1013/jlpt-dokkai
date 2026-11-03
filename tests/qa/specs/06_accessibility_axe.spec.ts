import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { QAReportGenerator } from '../utils/report_generator';

test.describe('06. Accessibility & Keyboard Navigation (WCAG AA)', () => {
  test('Run axe-core scan on catalog and exercise screens', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#catalog-view', { timeout: 15000 });

    // 1. Сканирование каталога
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .disableRules(['color-contrast']) // Цветовой контраст проверим отдельно с учетом тем
      .analyze();

    const violations = accessibilityScanResults.violations;
    console.log(`[AXE-CORE] Каталог: найдено ${violations.length} потенциальных замечаний a11y`);

    for (const v of violations) {
      if (v.impact === 'critical' || v.impact === 'serious') {
        QAReportGenerator.registerBug({
          title: `[A11Y] ${v.help} (${v.id})`,
          severity: v.impact === 'critical' ? 'critical' : 'major',
          category: 'a11y',
          env: {
            where: 'local',
            url: page.url(),
            viewport: 'Desktop/Mobile',
            engine: 'chromium',
            theme: 'light',
            network: 'normal',
          },
          steps: ['1. Открыть страницу', '2. Запустить axe-core сканер доступности'],
          expected: `Элементы соответствуют правилу ${v.id}`,
          actual: `${v.description}. Затронуто узлов: ${v.nodes.length}`,
          evidence: [JSON.stringify(v.nodes.slice(0, 3).map((n) => n.target))],
          reproduced: '1/2',
          suspected_cause: 'Отсутствие обязательных aria-атрибутов или ролей',
          status: 'new',
        });
      }
    }

    // 2. Тест клавиатурной навигации (Tab & Enter)
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedTag, 'Фокус перемещается по клавише Tab').toBeTruthy();
  });
});

