import { test, expect } from '@playwright/test';

test.describe('Dokkai Master - Persistence, Offline-First & Auto-Resume Architecture', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');
        await page.waitForSelector('#stream-level-pills');
    });

    test('01. Storage and Cloud Sync modules initialize cleanly in Local mode', async ({ page }) => {
        const isStorageReady = await page.evaluate(async () => {
            if (!window.DokkaiStorage) return false;
            await window.DokkaiStorage.initPromise;
            return window.DokkaiStorage.isReady;
        });
        expect(isStorageReady).toBe(true);

        const syncBadge = page.locator('#btn-sync-status');
        await expect(syncBadge).toBeVisible();
        const syncLabel = page.locator('#header-sync-label');
        await expect(syncLabel).toContainText('На устройстве');
    });

    test('02. Personal vocabulary notebook auto-saves and persists across page reloads', async ({ page }) => {
        // Save test word
        await page.evaluate(async () => {
            await window.DokkaiStorage.saveWord({
                word: '環境問題',
                reading: 'かんきょうもんだい',
                meaning: 'экологические проблемы',
                level: 'N3',
                mastered: false,
                added_at: new Date().toISOString()
            });
        });

        // Reload page to simulate closing and reopening tab
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Check header saved badge
        const badge = page.locator('#header-saved-count');
        await expect(badge).toHaveText('1');

        // Open Notebook tab
        await page.click('#btn-tab-notebook');
        await expect(page.locator('#notebook-view')).toBeVisible();

        // Check word card is rendered
        const wordCard = page.locator('.notebook-word-card[data-word="環境問題"]');
        await expect(wordCard).toBeVisible();
        await expect(wordCard).toContainText('環境問題');

        // Toggle mastered switch
        const switchLabel = wordCard.locator('.switch');
        await switchLabel.click();

        // Verify mastered state in storage
        const isMastered = await page.evaluate(async () => {
            const w = await window.DokkaiStorage.getWord('環境問題');
            return w ? w.mastered : false;
        });
        expect(isMastered).toBe(true);

        // Reload page again and check mastered status persisted
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.click('#btn-tab-notebook');
        const reloadedCard = page.locator('.notebook-word-card[data-word="環境問題"]');
        await expect(reloadedCard).toHaveClass(/is-mastered/);
    });

    test('03. Settings (Font size, Typeface, Filters) auto-save and persist', async ({ page }) => {
        // Save custom settings
        await page.evaluate(async () => {
            await window.DokkaiStorage.saveSettings('user_settings', {
                fontFamily: 'mincho',
                fontSizePx: 24,
                furiganaVisible: false
            });
            await window.DokkaiStorage.saveSettings('stream_profile', {
                level: 'N4',
                category: 'medium',
                solvedWhen: 'all_questions_answered'
            });
        });

        // Reload page
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Check that N4 and medium pills are active
        const n4Pill = page.locator('#stream-level-pills button[data-level="N4"]');
        await expect(n4Pill).toHaveClass(/active/);

        const mediumPill = page.locator('#stream-category-pills button[data-category="medium"]');
        await expect(mediumPill).toHaveClass(/active/);
    });

    test('04. In-progress test recovery: saves active session and prompts to resume', async ({ page }) => {
        // Wait for active slot cards to load
        await page.waitForSelector('.stream-slot-card', { timeout: 10000 });
        const startBtn = page.locator('.stream-slot-card button').first();
        await startBtn.click();

        // Modal opens -> click start
        const modalStart = page.locator('#modal-btn-start');
        await expect(modalStart).toBeVisible();
        await modalStart.click();

        // Wait for exercise view
        await expect(page.locator('#exercise-view')).toBeVisible();

        // Select an option on Question 1
        const firstOption = page.locator('.option-item').first();
        await firstOption.click();

        // Advance to Question 2 if next button is enabled
        const nextBtn = page.locator('#btn-wizard-next');
        if (await nextBtn.isVisible() && await nextBtn.isEnabled()) {
            await nextBtn.click();
        }

        // Simulate abrupt closing of the browser / refresh
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Verify the unfinished test banner appears!
        const banner = page.locator('#unfinished-test-banner');
        await expect(banner).toBeVisible();

        // Click "Продолжить"
        const resumeBtn = page.locator('#btn-resume-unfinished');
        await resumeBtn.click();

        // Exercise view is restored!
        await expect(page.locator('#exercise-view')).toBeVisible();
        await expect(banner).toBeHidden();
    });

    test('05. Export and Import JSON backup restores full state', async ({ page }) => {
        // Populate test data
        await page.evaluate(async () => {
            await window.DokkaiStorage.recordSolvedTask({
                text_id: 999,
                title: 'Тестовое задание для бэкапа',
                level: 'N5',
                category: 'short',
                score: 100,
                perfect: true,
                correct_count: 2,
                total_questions: 2,
                solved_at: new Date().toISOString()
            });
            await window.DokkaiStorage.saveWord({
                word: '試験',
                reading: 'しけん',
                meaning: 'экзамен',
                level: 'N5',
                mastered: true,
                added_at: new Date().toISOString()
            });
        });

        // Export JSON
        const exportJson = await page.evaluate(async () => {
            return await window.DokkaiStorage.exportAllData();
        });

        const parsed = JSON.parse(exportJson);
        expect(parsed.schema_version).toBe(1);
        expect(parsed.data.solved_tasks.some((t: any) => t.text_id === 999)).toBe(true);
        expect(parsed.data.notebook.some((w: any) => w.word === '試験')).toBe(true);

        // Clear local storage
        await page.evaluate(async () => {
            await window.DokkaiStorage.removeWord('試験');
            await window.DokkaiStorage._runTx('solved_tasks', 'readwrite', (store, fallback) => {
                if (store) store.delete(999);
                if (fallback) delete fallback[999];
            });
        });

        // Import the exported JSON
        const importResult = await page.evaluate(async (jsonStr) => {
            return await window.DokkaiStorage.importAllData(jsonStr);
        }, exportJson);

        expect(importResult.success).toBe(true);

        // Verify restoration
        const restoredWord = await page.evaluate(async () => {
            return await window.DokkaiStorage.getWord('試験');
        });
        expect(restoredWord).not.toBeNull();
        expect(restoredWord.reading).toBe('しけん');
        expect(restoredWord.mastered).toBe(true);
    });

    test('06. Anti-Cheat: No answer leaks in active session or storage prior to submit', async ({ page }) => {
        await page.waitForSelector('.stream-slot-card', { timeout: 10000 });
        const startBtn = page.locator('.stream-slot-card button').first();
        await startBtn.click();
        await page.locator('#modal-btn-start').click();
        await expect(page.locator('#exercise-view')).toBeVisible();

        // Check active session stored data
        const sessionData = await page.evaluate(async () => {
            return await window.DokkaiStorage.getActiveSession();
        });

        expect(sessionData).not.toBeNull();
        expect(sessionData.is_correct).toBeUndefined();
        expect(sessionData.correct_option_id).toBeUndefined();
        expect(sessionData.explanation).toBeUndefined();
        expect(sessionData.evidence_span_id).toBeUndefined();
    });
});
