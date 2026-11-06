const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

async function getActiveSessionFrom(baseUrl) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  // Navigate and start exercise 1
  await page.goto(baseUrl);
  await page.waitForSelector('#active-slots-list .stream-slot-card', { timeout: 15000 });
  await page.evaluate(() => window.openPretestModal(1));
  await page.waitForSelector('#pretest-modal-backdrop:not(.hidden)', { timeout: 10000 });
  await page.click('#modal-btn-start');
  await page.waitForSelector('#exercise-view:not(.hidden)', { timeout: 10000 });
  await page.waitForSelector('#wizard-card-area .option-item', { timeout: 10000 });

  // Pick option
  const opt = page.locator('#wizard-card-area .option-item').first();
  await opt.click();
  await page.waitForTimeout(500);

  // Retrieve active session from IndexedDB via DokkaiStorage
  const session = await page.evaluate(async () => {
    if (window.DokkaiStorage && window.DokkaiStorage.getActiveSession) {
      return await window.DokkaiStorage.getActiveSession();
    }
    return null;
  });

  await browser.close();
  return session;
}

async function main() {
  console.log('Retrieving active_session from main (http://localhost:8001)...');
  const sessionMain = await getActiveSessionFrom('http://localhost:8001');

  console.log('Retrieving active_session from refactor (http://localhost:8000)...');
  const sessionRefactor = await getActiveSessionFrom('http://localhost:8000');

  console.log('SESSION MAIN:');
  console.log(JSON.stringify(sessionMain, null, 2));

  console.log('\nSESSION REFACTOR:');
  console.log(JSON.stringify(sessionRefactor, null, 2));

  // Normalize timing deltas (since timestamp and secondsSpent reflect wall-clock execution time)
  const normMain = { ...sessionMain, timestamp: 0, timer: { ...sessionMain.timer, secondsSpent: 0, remainingSeconds: 0 } };
  const normRefactor = { ...sessionRefactor, timestamp: 0, timer: { ...sessionRefactor.timer, secondsSpent: 0, remainingSeconds: 0 } };

  const match = JSON.stringify(normMain) === JSON.stringify(normRefactor);
  console.log('\nPARITY VERDICT:', match ? '100% BIT-FOR-BIT MATCH' : 'DISCREPANCY FOUND');
  if (!match) {
    process.exit(1);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
