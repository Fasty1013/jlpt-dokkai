import { test, expect } from '@playwright/test';
import * as path from 'path';

/**
 * Admin task editor (/admin → task dialog → «Редактировать»): edit passage with readings in
 * brackets, question, correct answer and translation; save; public API reflects it; validation
 * error is shown inline; history restores the original. Uses an N3 prose task per project so
 * desktop and mobile workers do not edit the same task.
 */

const SHOTS = process.env.ADMIN_SHOTS_DIR;

// A distinct task per (test, project, repeat): parallel workers never edit the same task.
async function pickTask(request, testInfo, testSlot: number) {
  const index = testSlot + 2 * (testInfo.project.name.includes('mobile') ? 1 : 0) + 4 * testInfo.repeatEachIndex;
  const list = await (await request.get('/api/admin/texts?level=N3&active=active&limit=200')).json();
  const prose = [];
  for (const t of list.items) {
    const v = await (await request.get(`/api/admin/texts/${t.id}/edit`)).json();
    if (v.mode === 'markup' && v.evidence_ids.length) prose.push(v);
    if (prose.length > index) break;
  }
  return prose[index];
}

test.describe('22. Admin task editor', () => {
  test('01. Edit, save, see on the site, validation error, restore from history', async ({ page, request }, testInfo) => {
    const v = await pickTask(request, testInfo, 0);
    expect(v, 'a prose N3 task with evidence').toBeTruthy();
    const marker = `編集《へんしゅう》${testInfo.project.name.includes('mobile') ? 'M' : 'D'}${Date.now() % 100000}`;

    await page.goto('/admin');
    await page.click('[data-tab="texts"]');
    await page.fill('#adm-texts-q', v.title);
    await page.click('#adm-texts-form button[type="submit"]');
    const row = page.locator('#adm-texts-table tbody tr', { hasText: String(v.id) }).first();
    await row.getByRole('button', { name: 'Просмотр' }).click();
    await page.locator(`[data-edit-text="${v.id}"]`).click();

    const passage = page.locator('#ed-passage');
    await expect(passage).toHaveValue(v.markup);
    // no stray "null"/"undefined" text nodes from optional blocks
    expect(await page.locator('#adm-dialog-body').evaluate((n) => Array.from(n.childNodes)
      .filter((c) => c.nodeType === 3 && /null|undefined/.test(c.textContent || '')).length)).toBe(0);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${testInfo.project.name}_editor.png`) });

    // validation: remove an evidence marker -> inline error, nothing saved
    const ev = v.evidence_ids[0];
    await passage.fill(v.markup.split(`[${ev}]`).join('').split(`[/${ev}]`).join(''));
    await page.click('#ed-save');
    await expect(page.locator('#ed-error')).toContainText(ev);

    // real edit: passage + question + correct answer + translation
    await passage.fill(`${v.markup}\n\n${marker}`);
    const q = v.questions[0];
    await page.locator(`[data-q-text="${q.id}"]`).fill(`${q.text}（改）`);
    const wrong = q.options.find((o) => !o.is_correct);
    await page.locator(`[data-o-correct="${wrong.id}"]`).check();
    await page.locator('#ed-translation').fill(`${v.translation_ru} [правка]`);
    await page.click('#ed-preview-btn');
    await expect(page.locator('#ed-preview iframe')).toBeVisible();
    await page.click('#ed-save');
    await expect(page.locator('#adm-dialog-title')).not.toHaveText(/Редактирование/);

    const pub = await (await request.get(`/api/texts/${v.id}?user_id=pw-editor`)).json();
    expect(pub.content_html).toContain(marker.replace(/編集《へんしゅう》/, '<ruby>編集<rt>へんしゅう</rt></ruby>'));
    expect(pub.questions[0].question_text).toContain('（改）');
    const saved = await (await request.get(`/api/admin/texts/${v.id}/edit`)).json();
    expect(saved.questions[0].options.find((o) => o.id === wrong.id).is_correct).toBe(true);

    // restore the original from history
    await page.locator(`[data-edit-text="${v.id}"]`).click();
    page.on('dialog', (d) => d.accept());
    await page.locator('#ed-revisions [data-restore]').first().click();
    await expect(page.locator('#ed-passage')).toHaveValue(v.markup);
    const restored = await (await request.get(`/api/admin/texts/${v.id}/edit`)).json();
    expect(restored.title).toBe(v.title);
    expect(restored.translation_ru).toBe(v.translation_ru);
    expect(restored.questions[0].options.map((o) => o.is_correct)).toEqual(q.options.map((o) => o.is_correct));
  });

  test('02. Furigana button adds tokenizer readings; unsaved changes are confirmed on close', async ({ page, request }, testInfo) => {
    const v = await pickTask(request, testInfo, 1);
    expect(v, 'a prose N3 task with evidence').toBeTruthy();
    await page.goto('/admin');
    await page.click('[data-tab="texts"]');
    await page.fill('#adm-texts-q', v.title);
    await page.click('#adm-texts-form button[type="submit"]');
    await page.locator('#adm-texts-table tbody tr', { hasText: String(v.id) }).first().getByRole('button', { name: 'Просмотр' }).click();
    await page.locator(`[data-edit-text="${v.id}"]`).click();

    await page.locator('#ed-passage').fill(`${v.markup}\n\n新しい本です`);
    await page.click('#ed-furigana');
    await expect(page.locator('#ed-passage')).toHaveValue(/新《あたら》しい本《ほん》です/);

    let asked = false;
    page.once('dialog', (d) => { asked = true; d.dismiss(); });
    await page.click('#adm-dialog-close');
    expect(asked).toBe(true);
    await expect(page.locator('#adm-text-dialog')).toBeVisible();

    page.once('dialog', (d) => d.accept());
    await page.click('#adm-dialog-close');
    await expect(page.locator('#adm-text-dialog')).toBeHidden();
    const after = await (await request.get(`/api/admin/texts/${v.id}/edit`)).json();
    expect(after.markup).toBe(v.markup);
  });
});
