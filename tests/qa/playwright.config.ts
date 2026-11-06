import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';

const isProd = process.env.TARGET === 'prod';
const defaultProdUrl = process.env.PROD_URL || 'https://jlpt-dokkai.onrender.com';
const baseURL = isProd ? defaultProdUrl : (process.env.LOCAL_URL || 'http://localhost:8000');
const evidenceDir = path.resolve(__dirname, '../../docs/qa/evidence');

export default defineConfig({
  testDir: './specs',
  timeout: isProd ? 60000 : 30000,
  expect: {
    timeout: 10000,
  },
  fullyParallel: !isProd, // Strict 1 worker on prod to respect free tier limits
  workers: isProd ? 1 : 4,
  forbidOnly: !!process.env.CI,
  retries: 1, // Double-run verification
  reporter: [
    ['list'],
    ['json', { outputFile: path.resolve(__dirname, '../../docs/qa/playwright_raw_results.json') }],
    ['html', { outputFolder: './playwright-report', open: 'never' }]
  ],
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: isProd ? 45000 : 15000,
  },
  outputDir: evidenceDir,

  webServer: isProd ? undefined : {
    command: 'python -m uvicorn main:app --port 8000',
    port: 8000,
    reuseExistingServer: true,
    timeout: 30000,
    env: {
      DOKKAI_TEST_MODE: '1',
    },
  },

  projects: [
    // --- 1. Chromium Desktop ---
    {
      name: 'desktop_hd_light',
      use: {
        browserName: 'chromium',
        viewport: { width: 1920, height: 1080 },
        colorScheme: 'light',
      },
    },
    {
      name: 'desktop_laptop_dark',
      use: {
        browserName: 'chromium',
        viewport: { width: 1366, height: 768 },
        colorScheme: 'dark',
      },
    },
    {
      name: 'desktop_compact',
      use: {
        browserName: 'chromium',
        viewport: { width: 1280, height: 720 },
      },
    },

    // --- 2. Chromium Mobile ---
    {
      name: 'mobile_small_android_360',
      use: {
        browserName: 'chromium',
        viewport: { width: 360, height: 640 },
        deviceScaleFactor: 2.0,
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile_iphone_class_390',
      use: {
        browserName: 'chromium',
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 3.0,
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile_pixel_class_412',
      use: {
        browserName: 'chromium',
        viewport: { width: 412, height: 915 },
        deviceScaleFactor: 2.6,
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'mobile_landscape_844x390',
      use: {
        browserName: 'chromium',
        viewport: { width: 844, height: 390 },
        deviceScaleFactor: 3.0,
        isMobile: true,
        hasTouch: true,
      },
    },

    // --- 3. Chromium Tablet ---
    {
      name: 'tablet_portrait_768',
      use: {
        browserName: 'chromium',
        viewport: { width: 768, height: 1024 },
        deviceScaleFactor: 2.0,
        isMobile: true,
        hasTouch: true,
      },
    },
    {
      name: 'tablet_landscape_1024',
      use: {
        browserName: 'chromium',
        viewport: { width: 1024, height: 768 },
        deviceScaleFactor: 2.0,
        isMobile: true,
        hasTouch: true,
      },
    },

    // --- 4. Firefox Engines ---
    {
      name: 'firefox_desktop',
      use: {
        browserName: 'firefox',
        viewport: { width: 1366, height: 768 },
      },
    },

    // --- 5. WebKit Engine (Safari Emulation) ---
    {
      name: 'webkit_mobile_iphone',
      use: {
        browserName: 'webkit',
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 3.0,
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
});

