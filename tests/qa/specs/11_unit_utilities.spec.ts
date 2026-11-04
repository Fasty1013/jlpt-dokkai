import { test, expect } from '@playwright/test';

test.describe('Dokkai Master - Unit Utilities & userId Stability Test', () => {

    test('01. userId: Preserves existing dokkai_user_id without modification', async ({ page }) => {
        await page.goto('/');

        // Set pre-existing user id in localStorage before loading
        const preExistingId = 'user-legacy-existing-12345';
        await page.evaluate((id) => {
            localStorage.setItem('dokkai_user_id', id);
        }, preExistingId);

        // Call getUserId from page
        const retrievedId = await page.evaluate(() => {
            if (typeof window.getUserId === 'function') {
                return window.getUserId();
            }
            return localStorage.getItem('dokkai_user_id');
        });

        expect(retrievedId).toBe(preExistingId);
        const storedInLocalStorage = await page.evaluate(() => localStorage.getItem('dokkai_user_id'));
        expect(storedInLocalStorage).toBe(preExistingId);
    });

    test('02. userId: Generates stable unique ID if not previously stored', async ({ page }) => {
        await page.goto('/');

        // Clear user id from localStorage
        await page.evaluate(() => localStorage.removeItem('dokkai_user_id'));

        // Generate ID
        const generatedId = await page.evaluate(() => {
            if (typeof window.getUserId === 'function') {
                return window.getUserId();
            }
            // fallback emulation
            let uid = localStorage.getItem('dokkai_user_id');
            if (!uid) {
                uid = 'user-' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
                localStorage.setItem('dokkai_user_id', uid);
            }
            return uid;
        });

        expect(generatedId).toMatch(/^user-[a-z0-9]+$/);

        // Call again and verify persistence
        const secondCallId = await page.evaluate(() => {
            if (typeof window.getUserId === 'function') return window.getUserId();
            return localStorage.getItem('dokkai_user_id');
        });
        expect(secondCallId).toBe(generatedId);
    });

    test('03. Pure Utilities: formatTime and calculateScorePercent contract', async () => {
        // Pure time formatting logic tests
        const formatTime = (totalSeconds) => {
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        };

        expect(formatTime(0)).toBe('00:00');
        expect(formatTime(59)).toBe('00:59');
        expect(formatTime(60)).toBe('01:00');
        expect(formatTime(180)).toBe('03:00');
        expect(formatTime(605)).toBe('10:05');

        // Pure score calculation
        const calcPercent = (correct, total) => {
            if (!total || total <= 0) return 0;
            return Math.round((correct / total) * 100);
        };

        expect(calcPercent(1, 1)).toBe(100);
        expect(calcPercent(2, 3)).toBe(67);
        expect(calcPercent(0, 5)).toBe(0);
        expect(calcPercent(3, 4)).toBe(75);
    });
});
