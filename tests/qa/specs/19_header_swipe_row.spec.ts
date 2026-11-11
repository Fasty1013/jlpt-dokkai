import { test, expect } from '@playwright/test';

// The header tabs + language select do not fit on ~900px: the row must scroll sideways
// (wheel / drag with a mouse; touch swipes natively) instead of being clipped.
test.describe('19. Header tab row scrolls sideways when it does not fit', () => {
  test.beforeEach(async ({ page, isMobile }) => {
    test.skip(isMobile, 'mouse wheel / drag is a desktop interaction; touch swipe is native');
    await page.setViewportSize({ width: 900, height: 700 });
    await page.goto('/');
    await page.waitForSelector('.header-nav .nav-tab');
  });

  const metrics = (page) => page.locator('.header-nav').evaluate((n: HTMLElement) => ({
    scrollLeft: n.scrollLeft,
    max: n.scrollWidth - n.clientWidth,
    overflowX: getComputedStyle(n).overflowX,
    docOverflow: document.documentElement.scrollWidth - innerWidth,
    headerH: (n.closest('.app-header') as HTMLElement).getBoundingClientRect().height,
  }));

  test('01. Row overflows, is scrollable, and the page itself does not scroll sideways', async ({ page }) => {
    const m = await metrics(page);
    expect(m.max).toBeGreaterThan(0);
    expect(m.overflowX).toBe('auto');
    expect(m.docOverflow).toBeLessThanOrEqual(0);
    expect(m.headerH).toBe(66);
  });

  test('02. Mouse wheel over the row scrolls it sideways, not the page', async ({ page }) => {
    const box = (await page.locator('.header-nav').boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.wheel(0, 300);
    await expect.poll(async () => (await metrics(page)).scrollLeft).toBeGreaterThan(0);
    expect(await page.evaluate(() => scrollY)).toBe(0);
  });

  test('03. Dragging with the mouse scrolls the row and does not activate a tab', async ({ page }) => {
    const box = (await page.locator('.header-nav').boundingBox())!;
    const y = box.y + box.height / 2;
    await page.mouse.move(box.x + box.width - 60, y);
    await page.mouse.wheel(0, 500); // scroll to the end first
    await expect.poll(async () => (await metrics(page)).scrollLeft).toBeGreaterThan(0);
    const before = (await metrics(page)).scrollLeft;
    const activeBefore = await page.locator('.nav-tab.active').first().getAttribute('id');

    // Drag over a tab: the row must move right (content follows the pointer) and no click must fire.
    await page.mouse.move(box.x + 120, y);
    await page.mouse.down();
    await page.mouse.move(box.x + 220, y, { steps: 8 });
    await page.mouse.up();

    expect((await metrics(page)).scrollLeft).toBeLessThan(before);
    expect(await page.locator('.nav-tab.active').first().getAttribute('id')).toBe(activeBefore);
  });
});
