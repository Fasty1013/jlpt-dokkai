import { test, expect, Page } from '@playwright/test';

/**
 * Pop-up dictionary in the UI language (feat/i18n-switcher, sub-iteration 3).
 * Data: manual glossary (en/uz), JMdict index (en, app/data/jmdict_en.json), no machine translation.
 */

const CYR = /[Ѐ-ӿ]/;

async function lookup(page: Page, word: string) {
  await page.evaluate(async (w) => {
    const m = await import('/static/js/features/dictionary/popup_dict.js');
    m.lookupAndShowWord(w, 300, 300);
  }, word);
  await page.waitForSelector('#popup-dictionary-card:not(.hidden)', { timeout: 10000 });
}

test.describe('20. Selection translation in the UI language', () => {
  test('01. API: Russian contract unchanged, en/uz/ja rules, bad language rejected', async ({ request }) => {
    const ru = await (await request.get('/api/dictionary/lookup?q=図書館')).json();
    expect(Object.keys(ru).sort()).toEqual(['level', 'meaning', 'reading', 'word']);
    expect(ru.meaning).toBe('библиотека');

    const en = await (await request.get('/api/dictionary/lookup?q=図書館&lang=en')).json();
    expect(en.meaning).toBeTruthy();
    expect(en.meaning).not.toMatch(CYR);
    expect(en.lang).toBe('en');

    const uz = await (await request.get('/api/dictionary/lookup?q=図書館&lang=uz')).json();
    expect(uz).toMatchObject({ meaning: 'kutubxona', lang: 'uz', fallback: false, source: 'manual' });

    const ja = await (await request.get('/api/dictionary/lookup?q=図書館&lang=ja')).json();
    expect(ja).toMatchObject({ meaning: '', reading: 'としょかん', lang: 'ja' });

    expect((await request.get('/api/dictionary/lookup?q=図書館&lang=xx')).status()).toBe(422);
    // no wrong partial match: 本当 is its own JMdict entry, not the project word 本 ("book")
    const real = await (await request.get('/api/dictionary/lookup?q=本当&lang=en')).json();
    expect(real.word).toBe('本当');
    expect(real.meaning).not.toMatch(/book/i);
  });

  test('02. [ru] popup unchanged: Russian meaning, no source note, request without lang', async ({ page }) => {
    const urls: string[] = [];
    page.on('request', (r) => { if (r.url().includes('/api/dictionary/lookup')) urls.push(r.url()); });
    await page.goto('/');
    await page.waitForSelector('#popup-dictionary-card', { state: 'attached' });
    await lookup(page, '図書館');
    await expect(page.locator('#popup-meaning')).toHaveText('библиотека');
    await expect(page.locator('#popup-meaning-note')).toBeHidden();
    expect(urls.length).toBe(1);
    expect(urls[0]).not.toContain('lang=');
  });

  test('03. [en] meaning in English with a source note; request carries lang=en', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('dokkai_ui_lang', 'en'));
    const urls: string[] = [];
    page.on('request', (r) => { if (r.url().includes('/api/dictionary/lookup')) urls.push(r.url()); });
    await page.goto('/');
    await page.waitForSelector('#popup-dictionary-card', { state: 'attached' });
    await lookup(page, '図書館');
    const meaning = (await page.locator('#popup-meaning').textContent()) || '';
    expect(meaning.trim()).not.toBe('');
    expect(meaning).not.toMatch(CYR);
    await expect(page.locator('#popup-reading')).toHaveText('[としょかん]');
    await expect(page.locator('#popup-meaning-note')).toBeVisible();
    expect(((await page.locator('#popup-meaning-note').textContent()) || '')).not.toMatch(CYR);
    await expect(page.locator('#popup-meaning-note')).toContainText('JMdict');
    expect(meaning).toBe('library');
    expect(urls[0]).toContain('lang=en');
    await expect(page.locator('#popup-btn-save-text')).toHaveText('Add to my vocabulary');
  });

  test('04. [uz] Uzbek gloss; a word with no uz data falls back to English and says so; unknown word is marked', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('dokkai_ui_lang', 'uz'));
    await page.goto('/');
    await page.waitForSelector('#popup-dictionary-card', { state: 'attached' });
    await lookup(page, '図書館');
    await expect(page.locator('#popup-meaning')).toHaveText('kutubxona');
    await expect(page.locator('#popup-meaning-note')).toContainText("Loyiha lug'ati");
    await lookup(page, '猫'); // not in the manual glossary: JMdict English gloss, flagged as a fallback
    await expect(page.locator('#popup-meaning')).toContainText('cat'); // waits for the second lookup to replace the first
    expect(((await page.locator('#popup-meaning').textContent()) || '')).not.toMatch(CYR);
    await expect(page.locator('#popup-meaning-note')).toContainText('inglizcha');
  });

  test('05. [ja] reading and level only, with an honest note instead of a made-up definition', async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem('dokkai_ui_lang', 'ja'));
    await page.goto('/');
    await page.waitForSelector('#popup-dictionary-card', { state: 'attached' });
    await lookup(page, '図書館');
    await expect(page.locator('#popup-reading')).toHaveText('[としょかん]');
    await expect(page.locator('#popup-meaning')).toHaveText('日本語の語釈はまだありません');
  });

  test('06. Switching the language hides an open popup (no stale-language text)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('#lang-select');
    await lookup(page, '図書館');
    await page.selectOption('#lang-select', 'en');
    await expect(page.locator('#popup-dictionary-card')).toBeHidden();
  });
});
