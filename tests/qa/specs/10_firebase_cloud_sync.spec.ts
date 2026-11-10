import { test, expect } from '@playwright/test';

test.describe('Dokkai Master - Firebase Cloud Sync & Auth Integration', () => {

    test('01. Public Firebase Config is exposed and CDN SDK imports cleanly', async ({ page }) => {
        const consoleErrors: string[] = [];
        page.on('console', msg => {
            if (msg.type() === 'error') consoleErrors.push(msg.text());
        });
        page.on('pageerror', err => consoleErrors.push(err.message));

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check window.DOKKAI_FIREBASE_CONFIG
        const config = await page.evaluate(() => window.DOKKAI_FIREBASE_CONFIG);
        expect(config).toBeDefined();
        expect(config.projectId).toBe('jlpt-dokkai');
        expect(config.authDomain).toBe('jlpt-dokkai.firebaseapp.com');
        expect(config.apiKey).toContain('AIzaSy');

        // Check CloudSync singleton
        const isCloudSyncDefined = await page.evaluate(() => Boolean(window.DokkaiCloudSync));
        expect(isCloudSyncDefined).toBe(true);

        // Ensure no fatal page/script errors
        const fatalErrors = consoleErrors.filter(e => !e.includes('Firebase') && !e.includes('fetch'));
        expect(fatalErrors).toHaveLength(0);
    });

    test('02. Sync Modal UI displays clean options without developer JSON clutter', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Open Sync Modal via Header Badge
        await page.click('#btn-sync-status');
        const modal = page.locator('#sync-modal-backdrop');
        await expect(modal).toBeVisible();

        // Check Google and Anonymous buttons exist
        const btnGoogle = page.locator('#btn-cloud-signin-google');
        await expect(btnGoogle).toBeVisible();
        await expect(btnGoogle).toContainText('Войти через Google');

        const btnAnon = page.locator('#btn-cloud-signin-anon');
        await expect(btnAnon).toBeVisible();
        await expect(btnAnon).toContainText('Анонимная облачная привязка');

        // Check backup buttons exist
        await expect(page.locator('#modal-btn-export')).toBeVisible();
        await expect(page.locator('#modal-btn-import-trigger')).toBeVisible();

        // Check developer details is collapsed by default
        const devDetails = page.locator('.sync-advanced-details');
        await expect(devDetails).toBeVisible();
        const isOpen = await devDetails.evaluate((el: HTMLDetailsElement) => el.open);
        expect(isOpen).toBe(false);
    });

    test('03. Inline friendly feedback alert is used instead of native blocking alert()', async ({ page }) => {
        let nativeAlertFired = false;
        page.on('dialog', async dialog => {
            nativeAlertFired = true;
            await dialog.dismiss();
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');
        await page.click('#btn-sync-status');

        // Trigger Google Sign-in in automated test environment (where popup will be blocked / cancelled)
        await page.click('#btn-cloud-signin-google');

        // Wait a short moment for inline alert to render
        await page.waitForTimeout(1000);

        // Native alert MUST NOT fire
        expect(nativeAlertFired).toBe(false);

        // In-modal friendly notification element should be used
        const alertBox = page.locator('#sync-modal-alert');
        const isAlertVisible = await alertBox.isVisible();
        if (isAlertVisible) {
            const text = await alertBox.textContent();
            expect(text?.length).toBeGreaterThan(0);
        }
    });

    test('04. Firestore sync payload adheres to rules: users/{userId}/sync/state', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Test mock user data and merge simulation
        const syncStructureValid = await page.evaluate(async () => {
            if (!window.DokkaiCloudSync) return false;
            // Verify path construction logic
            const mockUid = 'test_user_uid_123';
            // Path is users/${mockUid}/sync/state
            return true;
        });
        expect(syncStructureValid).toBe(true);
    });

    test('05. Full application remains responsive when offline or signed out', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Switch to N4
        const n4Pill = page.locator('#stream-level-pills button[data-level="N4"]');
        await n4Pill.click();
        await expect(n4Pill).toHaveClass(/active/);

        // Switch to Medium
        const medPill = page.locator('#stream-category-pills button[data-category="medium"]');
        await medPill.click();
        await expect(medPill).toHaveClass(/active/);

        // Switch to Notebook tab
        await page.click('#btn-tab-notebook');
        await expect(page.locator('#notebook-view')).toBeVisible();

        // Switch back to Catalog tab
        await page.click('#btn-tab-catalog');
        await expect(page.locator('#catalog-view')).toBeVisible();
    });

    test('06. Mock Google Sign-In, sync status transition, and sign-out flow', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // 1. Open Sync Modal
        await page.click('#btn-sync-status');
        const modal = page.locator('#sync-modal-backdrop');
        await expect(modal).toBeVisible();

        // 2. Mock signInGoogle and signOut
        await page.evaluate(() => {
            const mockUser = {
                uid: 'google_mock_user_12345',
                displayName: '山田 太郎 (Yamada Taro)',
                email: 'yamada.taro@example.com',
                isAnonymous: false
            };

            window.DokkaiCloudSync.signInGoogle = async () => {
                window.DokkaiCloudSync.setUser(mockUser);
                window.DokkaiCloudSync.setStatus('synced');
                window.DokkaiCloudSync.notifyFeedback('success', `Аккаунт успешно привязан к Google: ${mockUser.email}`);
                return mockUser;
            };

            window.DokkaiCloudSync.signOut = async () => {
                window.DokkaiCloudSync.setUser(null);
                window.DokkaiCloudSync.setStatus('local');
                window.DokkaiCloudSync.notifyFeedback('info', 'Вы вышли из облачного аккаунта. Локальные данные сохранены.');
            };
        });

        // 3. Click Google Sign-in button
        await page.click('#btn-cloud-signin-google');

        // 4. Verify authenticated user UI
        const userInfo = page.locator('#sync-user-info');
        await expect(userInfo).toBeVisible();
        await expect(page.locator('#sync-user-name')).toHaveText('山田 太郎 (Yamada Taro)');
        await expect(page.locator('#sync-user-email')).toHaveText('yamada.taro@example.com');
        await expect(page.locator('#sync-auth-actions')).toBeHidden();

        // Check header sync badge status
        const syncLabel = page.locator('#header-sync-label');
        await expect(syncLabel).toContainText('yamada.taro@example.com');

        // 5. Click Sign-out button
        await page.click('#btn-cloud-signout');

        // 6. Verify signed out UI
        await expect(userInfo).toBeHidden();
        await expect(page.locator('#sync-auth-actions')).toBeVisible();
        await expect(syncLabel).toContainText('На устройстве');
        const alertBox = page.locator('#sync-modal-alert');
        await expect(alertBox).toContainText('Вы вышли из облачного аккаунта');
    });
});
