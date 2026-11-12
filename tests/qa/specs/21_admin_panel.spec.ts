import { test, expect } from '@playwright/test';
import * as path from 'path';

/**
 * Admin panel (/admin): user reports are stored and shown, moderation actions, admin key flow.
 * The test server runs with DOKKAI_TEST_MODE=1 and no ADMIN_TOKEN, so the admin API is open;
 * the key flow is checked by mocking /api/admin/check.
 */

const SHOTS = process.env.ADMIN_SHOTS_DIR;

async function firstN5TextId(request): Promise<number> {
  const list = await (await request.get('/api/texts?level=N5')).json();
  return list[0].id;
}

test.describe('21. Admin panel', () => {
  test('01. Report text is stored, listed safely, resolved, reopened and deleted', async ({ page, request }, testInfo) => {
    const textId = await firstN5TextId(request);
    const marker = `pw-${testInfo.project.name}-${Date.now()}`;
    const details = `${marker} <img src=x onerror="window.__xss=1"> <b>bold</b>`;
    const resp = await request.post(`/api/texts/${textId}/report`, {
      data: { reason: 'Опечатка в тексте или вопросе', details, user_id: `user-${marker}` },
    });
    expect(resp.ok()).toBeTruthy();
    expect(Object.keys(await resp.json()).sort()).toEqual(['deactivated', 'is_active', 'message', 'report_count', 'status', 'text_id']);

    await page.goto('/admin');
    await expect(page.locator('#adm-stats .adm-stat')).toHaveCount(5);
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${testInfo.project.name}_dashboard.png`), fullPage: true });

    await page.click('[data-tab="reports"]');
    const card = page.locator('.adm-report', { hasText: marker });
    await expect(card).toHaveCount(1);
    await expect(card.locator('.adm-report-details')).toHaveText(details);
    await expect(page.locator('#adm-reports-list img, #adm-reports-list b')).toHaveCount(0);
    expect(await page.evaluate(() => (window as any).__xss)).toBeUndefined();
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${testInfo.project.name}_reports.png`), fullPage: true });

    await card.getByRole('button', { name: 'Решено' }).click();
    await expect(page.locator('.adm-report', { hasText: marker })).toHaveCount(0);
    await page.click('[data-report-status="resolved"]');
    const resolved = page.locator('.adm-report', { hasText: marker });
    await expect(resolved).toHaveClass(/is-resolved/);
    await resolved.getByRole('button', { name: 'Вернуть в новые' }).click();
    await page.click('[data-report-status="new"]');
    await expect(page.locator('.adm-report', { hasText: marker })).toHaveCount(1);

    page.once('dialog', (d) => d.accept());
    await page.locator('.adm-report', { hasText: marker }).getByRole('button', { name: 'Удалить' }).click();
    await expect(page.locator('.adm-report', { hasText: marker })).toHaveCount(0);
  });

  test('02. Tasks: search, preview with correct answers, hide and return', async ({ page, request }, testInfo) => {
    // An active N4 task without reports: hide → return leaves it exactly as it was
    // ("return" resets the report counter, so a reported task would not be restored).
    const candidates = await (await request.get('/api/admin/texts?level=N4&active=active&limit=200')).json();
    // Different task per project: desktop and mobile run in parallel workers.
    const target = candidates.items.filter((t) => t.report_count === 0)[testInfo.project.name.includes('mobile') ? 1 : 0];
    expect(target, 'an active N4 task without reports').toBeTruthy();
    const textId = target.id;
    const detail = await (await request.get(`/api/admin/texts/${textId}`)).json();

    await page.goto('/admin');
    await page.click('[data-tab="texts"]');
    await page.fill('#adm-texts-q', detail.slug || detail.title);
    await page.click('#adm-texts-form button[type="submit"]');
    const row = page.locator('#adm-texts-table tbody tr', { hasText: String(textId) }).first();
    await expect(row).toBeVisible();

    await row.getByRole('button', { name: 'Просмотр' }).click();
    const dialog = page.locator('#adm-text-dialog');
    await expect(dialog).toBeVisible();
    await expect(dialog.locator('.adm-question li.is-correct').first()).toBeVisible();
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, `${testInfo.project.name}_task.png`) });

    const toggle = dialog.locator('.adm-actions button').first();
    const wasActive = detail.is_active;
    await toggle.click();
    await expect(dialog.locator('.adm-actions button').first()).toHaveText(wasActive ? 'Вернуть в поток' : 'Скрыть из потока');
    await dialog.locator('.adm-actions button').first().click();
    await expect(dialog.locator('.adm-actions button').first()).toHaveText(wasActive ? 'Скрыть из потока' : 'Вернуть в поток');
    await page.click('#adm-dialog-close');
    await expect(dialog).toBeHidden();
  });

  test('03. Activity tab renders', async ({ page }) => {
    await page.goto('/admin');
    await page.click('[data-tab="activity"]');
    await expect(page.locator('#adm-activity-table thead th')).toHaveCount(5);
  });

  test('04. Key flow: login form on 401, key saved and sent as X-Admin-Token', async ({ page }) => {
    const seen: (string | undefined)[] = [];
    await page.route('**/api/admin/check', (route) => {
      const key = route.request().headers()['x-admin-token'];
      seen.push(key);
      if (key === 'pw-secret') return route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
      return route.fulfill({ status: 401, contentType: 'application/json', body: '{"detail":"Требуется ключ администратора"}' });
    });
    await page.goto('/admin');
    await expect(page.locator('#adm-login')).toBeVisible();
    await expect(page.locator('#adm-tabs')).toBeHidden();

    await page.fill('#adm-token-input', 'pw-secret');
    await page.click('#adm-login-form button[type="submit"]');
    await expect(page.locator('#adm-tabs')).toBeVisible();
    expect(seen[seen.length - 1]).toBe('pw-secret');
    expect(await page.evaluate(() => localStorage.getItem('dokkai_admin_token'))).toBe('pw-secret');

    await page.click('#adm-logout');
    await expect(page.locator('#adm-login')).toBeVisible();
    expect(await page.evaluate(() => localStorage.getItem('dokkai_admin_token'))).toBeNull();
  });

  test('05. Main site PDF import sends the key only when it is stored', async ({ page }) => {
    const headers: (string | undefined)[] = [];
    page.on('request', (r) => { if (r.url().includes('/api/admin/drafts')) headers.push(r.headers()['x-admin-token']); });

    await page.goto('/');
    await page.evaluate(async () => { const m = await import('/static/js/features/pdf_import/pdf_staging.js'); await m.fetchAndRenderDrafts(); });
    expect(headers.length).toBeGreaterThan(0);
    expect(headers.every((h) => h === undefined)).toBeTruthy();

    headers.length = 0;
    await page.evaluate(() => localStorage.setItem('dokkai_admin_token', 'pw-import-key'));
    await page.evaluate(async () => { const m = await import('/static/js/features/pdf_import/pdf_staging.js'); await m.fetchAndRenderDrafts(); });
    expect(headers).toContain('pw-import-key');
  });
});
