import { test, expect, Page } from '@playwright/test';

const CONTENT = ['#passage-content', '.question-general-explanation', '.option-explanation-box', '#translation-text', '.vocab-trans', '#lang-select'];

/**
 * Cyrillic text left in the visible interface under `rootSelector`.
 * Russian that is content (explanations, translation, glossary meanings, option list of the switcher) is excluded.
 */
async function leftoverCyrillic(page: Page, rootSelector: string): Promise<string[]> {
  return page.evaluate(({ rootSelector, CONTENT }) => {
    const cyr = /[Ѐ-ӿ]/;
    const root = document.querySelector(rootSelector);
    if (!root) return ['<missing root ' + rootSelector + '>'];
    const found: string[] = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n: Node | null;
    while ((n = walker.nextNode())) {
      const el = (n as Text).parentElement!;
      if (CONTENT.some((c) => el.closest(c))) continue;
      if (el.closest('.hidden') || getComputedStyle(el).display === 'none') continue;
      if (cyr.test(n.textContent || '')) found.push((n.textContent || '').trim().slice(0, 60));
    }
    root.querySelectorAll('[title],[placeholder],[aria-label]').forEach((el) => {
      if (el.closest('.hidden') || CONTENT.some((c) => el.closest(c))) return;
      for (const a of ['title', 'placeholder', 'aria-label']) {
        const v = el.getAttribute(a);
        if (v && cyr.test(v)) found.push(a + ': ' + v.slice(0, 60));
      }
    });
    return found;
  }, { rootSelector, CONTENT });
}

test.describe('18. Language switcher (feat/i18n-switcher)', () => {
  test('01. Default is Russian and keeps the historical <html lang="ja"> (pixel parity)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    await expect(page.locator('#lang-select')).toHaveValue('ru');
    await expect(page.locator('html')).toHaveAttribute('lang', 'ja');
    await expect(page.locator('#btn-tab-catalog .nav-label')).toHaveText('Тексты и тесты');
  });

  test('02. Switching applies without reload, updates html lang, persists across reload', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    await page.evaluate(() => { (window as any).__noReloadMarker = 1; });

    const expected: Record<string, [string, string]> = {
      en: ['Texts & tests', 'en'],
      uz: ['Matnlar va testlar', 'uz'],
      ja: ['文章とテスト', 'ja'],
      ru: ['Тексты и тесты', 'ja'],
    };
    for (const lang of ['en', 'uz', 'ja', 'ru']) {
      await page.selectOption('#lang-select', lang);
      await expect(page.locator('#btn-tab-catalog .nav-label')).toHaveText(expected[lang][0]);
      await expect(page.locator('html')).toHaveAttribute('lang', expected[lang][1]);
    }
    expect(await page.evaluate(() => (window as any).__noReloadMarker)).toBe(1);

    // Japanese text keeps its own lang="ja" when the page language is not Japanese
    await page.selectOption('#lang-select', 'en');
    expect(await page.locator('.brand-sub').getAttribute('lang')).toBe('ja');
    expect(await page.locator('#stream-category-pills .filter-pill').first().getAttribute('lang')).toBe('ja');

    await page.selectOption('#lang-select', 'en');
    expect(await page.evaluate(() => localStorage.getItem('dokkai_ui_lang'))).toBe('en');
    await page.reload();
    await page.waitForSelector('#lang-select');
    await expect(page.locator('#lang-select')).toHaveValue('en');
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('#btn-tab-notebook .nav-label')).toHaveText('My vocabulary');
  });

  test('03. Invalid stored language value falls back to Russian', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('dokkai_ui_lang', 'xx'));
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    await expect(page.locator('#lang-select')).toHaveValue('ru');
  });

  test('04. Switcher is reachable and at least 44px high on touch widths', async ({ page }) => {
    await page.goto('/');
    const sel = page.locator('#lang-select');
    await sel.scrollIntoViewIfNeeded();
    const box = await sel.boundingBox();
    expect(box).not.toBeNull();
    const vw = page.viewportSize()!.width;
    if (vw <= 768) {
      expect(box!.height).toBeGreaterThanOrEqual(44);
      // the header row stays on one line (no wrapping): select shares the nav row's top with the nav tabs
      const navTop = (await page.locator('#btn-tab-catalog').boundingBox())!.y;
      expect(Math.abs(box!.y - navTop)).toBeLessThan(20);
    }
  });

  test('05. Russian parity: every data-i18n element in the served HTML equals the ru dictionary', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    const diffs = await page.evaluate(async () => {
      const html = await (await fetch('/')).text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const t = (window as any).DokkaiI18n.t;
      const norm = (x: string) => x.replace(/\s+/g, ' ').trim();
      const out: string[] = [];
      doc.querySelectorAll('[data-i18n]').forEach((el) => {
        const key = el.getAttribute('data-i18n')!;
        if (norm(el.textContent || '') !== norm(t(key))) out.push(`${key}: "${norm(el.textContent || '')}" != "${norm(t(key))}"`);
      });
      doc.querySelectorAll('[data-i18n-attr]').forEach((el) => {
        el.getAttribute('data-i18n-attr')!.split(';').forEach((pair) => {
          const i = pair.indexOf(':');
          const attr = pair.slice(0, i).trim();
          const key = pair.slice(i + 1).trim();
          if (norm(el.getAttribute(attr) || '') !== norm(t(key))) out.push(`${key}@${attr}`);
        });
      });
      return out;
    });
    expect(diffs).toEqual([]);
  });

  for (const lang of ['en', 'uz', 'ja']) {
    test(`06. [${lang}] no Russian interface text on catalog, notebook, import and modals`, async ({ page }) => {
      await page.addInitScript((l) => localStorage.setItem('dokkai_ui_lang', l), lang);
      await page.goto('/');
      await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });
      // slot titles / archive titles are task content (the archive may hold Russian-titled test fixtures)
      const catalog = (await leftoverCyrillic(page, '#app')).filter((x) => !/Тест на дефекты/.test(x));
      expect(catalog, 'catalog').toEqual([]);

      await page.evaluate(() => (window as any).switchMainTab('notebook'));
      expect(await leftoverCyrillic(page, '#notebook-view'), 'notebook').toEqual([]);
      await page.evaluate(() => (window as any).switchMainTab('import'));
      expect(await leftoverCyrillic(page, '#import-view'), 'import').toEqual([]);
      await page.evaluate(() => (window as any).switchMainTab('catalog'));

      await page.evaluate(() => (window as any).openPretestModal(25));
      await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)');
      expect(await leftoverCyrillic(page, '#pretest-modal-backdrop'), 'pretest modal').toEqual([]);
      await page.click('#modal-btn-cancel');

      await page.click('#btn-sync-status');
      await page.waitForSelector('#sync-modal-backdrop:not(.hidden)');
      expect(await leftoverCyrillic(page, '#sync-modal-backdrop'), 'sync modal').toEqual([]);
      await page.click('#btn-sync-modal-done');

      await page.evaluate(() => (window as any).openReportModal(25, 'Task'));
      await page.waitForSelector('#report-modal-backdrop:not(.hidden)');
      expect(await leftoverCyrillic(page, '#report-modal-backdrop'), 'report modal').toEqual([]);
    });
  }

  test('07. [en] wizard, submit button and analysis are localized; switching language re-renders them', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('dokkai_ui_lang', 'en'));
    await page.goto('/');
    await page.waitForSelector('#active-slots-list', { timeout: 15000 });
    await page.evaluate(() => (window as any).openPretestModal(25));
    await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)');
    await expect(page.locator('#modal-btn-start')).toHaveText('Start solving →');
    await page.click('#modal-btn-start');
    await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
    await expect(page.locator('#wizard-step-label')).toHaveText(/^Question 1 of \d+$/);
    expect(await leftoverCyrillic(page, '#exercise-view'), 'exercise').toEqual([]);

    await page.waitForSelector('#wizard-card-area .option-item');
    await page.locator('#wizard-card-area .question-card').first().locator('.option-item').first().click();
    const switcherVisible = await page.locator('#lang-select').isVisible();
    if (switcherVisible) {
      // switching mid-exercise re-renders the step and keeps the chosen answer
      await page.selectOption('#lang-select', 'uz');
      await expect(page.locator('#wizard-step-label')).toHaveText(/^1-savol \/ \d+$/);
      await expect(page.locator('#wizard-card-area .option-item input:checked')).toHaveCount(1);
      await page.selectOption('#lang-select', 'en');
    }
    while (true) {
      await page.waitForSelector('#wizard-card-area .option-item');
      const card = page.locator('#wizard-card-area .question-card').first();
      if ((await card.locator('.option-item input:checked').count()) === 0) await card.locator('.option-item').first().click();
      const submit = page.locator('#btn-wizard-submit');
      if (await submit.isVisible()) {
        await expect(submit).toHaveText('Finish and check answers ✓');
        await submit.click();
        break;
      }
      await page.locator('#btn-wizard-next').click();
      await page.waitForTimeout(250);
    }
    await page.waitForSelector('#analysis-banner:not(.hidden)', { timeout: 15000 });
    await expect(page.locator('#score-percent')).toContainText('% CORRECT');
    expect(await leftoverCyrillic(page, '#analysis-banner'), 'analysis banner').toEqual([]);

    if (switcherVisible) {
      await page.selectOption('#lang-select', 'uz');
      await expect(page.locator('#score-percent')).toContainText("% TO'G'RI");
      await expect(page.locator('.analysis-tab-btn').first()).toContainText('-savol');
      await page.selectOption('#lang-select', 'ja');
      await expect(page.locator('#score-percent')).toContainText('正解率');
    }
  });

  test('08. Server Russian messages are mapped to the UI language; unknown ones are shown as received', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    const out = await page.evaluate(async () => {
      const m = await import('/static/js/i18n/server_messages.js');
      const i = (window as any).DokkaiI18n;
      const res: Record<string, string> = {};
      for (const lang of ['en', 'uz', 'ja']) {
        i.setLang(lang);
        res[lang] = m.localizeServerMessage('Задание не найдено');
      }
      i.setLang('en');
      res.prefix = m.localizeServerMessage('Ошибка фиксации задания: boom');
      res.unknown = m.localizeServerMessage('Что-то странное');
      i.setLang('ru');
      res.ru = m.localizeServerMessage('Задание не найдено');
      return res;
    });
    expect(out.en).toBe('Task not found');
    expect(out.uz).toBe('Topshiriq topilmadi');
    expect(out.ja).toBe('問題が見つかりません');
    expect(out.prefix).toBe('Failed to record the task: boom');
    expect(out.unknown).toBe('Что-то странное');
    expect(out.ru).toBe('Задание не найдено');
  });
});
