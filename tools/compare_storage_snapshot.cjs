/**
 * Storage snapshot parity (Step 7b).
 *
 * Drives DokkaiStorage / DokkaiCloudSync through a fixed scenario on `main` (:8001) and on the
 * branch (:8000) with a frozen clock, dumps everything that is persisted or sent to the cloud and
 * compares the dumps byte for byte:
 *   1. IndexedDB (raw): db name/version, stores, keyPaths, indexes, every record (in key order).
 *   2. localStorage (raw): every key/value.
 *   3. exportAllData() backup JSON, and importAllData() round trip.
 *   4. Fallback mode (indexedDB unavailable): fallbackMemory + localStorage mirrors.
 *   5. Legacy localStorage -> IndexedDB migration.
 *   6. Firestore payload written to users/{uid}/sync/state by syncNow() (Firebase is stubbed, the
 *      network is never touched), including the lossless merge against a conflicting remote doc.
 *
 * Usage:
 *   node tools/compare_storage_snapshot.cjs              # main (:8001) vs branch (:8000)
 *   node tools/compare_storage_snapshot.cjs --baseline   # branch (:8000) vs tools/snapshots/storage_snapshot.main.json
 *   node tools/compare_storage_snapshot.cjs --update-baseline   # rewrite the golden file from main
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require(path.resolve(__dirname, '../tests/qa/node_modules/@playwright/test'));

const MAIN_URL = 'http://localhost:8001';
const BRANCH_URL = 'http://localhost:8000';
const BASELINE = path.resolve(__dirname, 'snapshots/storage_snapshot.main.json');
const FIXED_NOW = 1700000000000; // 2023-11-14T22:13:20.000Z

const args = new Set(process.argv.slice(2));

// ---------------------------------------------------------------- page-side helpers
const FREEZE_CLOCK = `(() => {
  const FIXED = ${FIXED_NOW};
  const RealDate = Date;
  class FakeDate extends RealDate {
    constructor(...a) { if (a.length === 0) super(FIXED); else super(...a); }
    static now() { return FIXED; }
  }
  window.Date = FakeDate;
  let seed = 123456789; // deterministic PRNG (the app derives dokkai_user_id from Math.random)
  Math.random = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
})();`;

const NO_INDEXEDDB = `(() => { try { Object.defineProperty(window, 'indexedDB', { value: undefined, configurable: true }); } catch (e) {} })();`;

function seedLegacy() {
  localStorage.setItem('dokkai_user_id', 'legacy-user-1');
  localStorage.setItem('dokkai_saved_words', JSON.stringify([
    { word: '猫', reading: 'ねこ', meaning: 'cat', mastered: false, updated_at: 1600000000000 },
    { word: '犬', reading: 'いぬ', meaning: 'dog', mastered: true, updated_at: 1600000000001 }
  ]));
  localStorage.setItem('dokkai_pretest_config', JSON.stringify({ timerEnabled: true, minutes: 12 }));
}

async function dumpPage(page) {
  return page.evaluate(async () => {
    const out = {};
    // ---- localStorage (sorted by key)
    out.localStorage = {};
    Object.keys(localStorage).sort().forEach((k) => { out.localStorage[k] = localStorage.getItem(k); });

    // ---- IndexedDB raw
    out.indexedDB = null;
    if (window.indexedDB) {
      const dbs = indexedDB.databases ? await indexedDB.databases() : [];
      out.indexedDBDatabases = dbs.map((d) => ({ name: d.name, version: d.version })).sort((a, b) => a.name.localeCompare(b.name));
      out.indexedDB = await new Promise((resolve) => {
        const req = indexedDB.open('dokkai_master_db');
        req.onerror = () => resolve({ error: String(req.error) });
        req.onsuccess = () => {
          const db = req.result;
          const names = Array.from(db.objectStoreNames).sort();
          const dump = { name: db.name, version: db.version, stores: {} };
          if (!names.length) { db.close(); return resolve(dump); }
          const tx = db.transaction(names, 'readonly');
          let pending = names.length;
          names.forEach((n) => {
            const st = tx.objectStore(n);
            const meta = {
              keyPath: st.keyPath,
              autoIncrement: st.autoIncrement,
              indexes: Array.from(st.indexNames).sort().map((i) => {
                const ix = st.index(i);
                return { name: i, keyPath: ix.keyPath, unique: ix.unique, multiEntry: ix.multiEntry };
              })
            };
            const all = st.getAll();
            const keys = st.getAllKeys();
            all.onsuccess = () => {
              keys.onsuccess = () => {
                meta.keys = keys.result;
                meta.records = all.result;
                dump.stores[n] = meta;
                if (--pending === 0) { db.close(); resolve(dump); }
              };
            };
          });
        };
      });
    }

    // ---- DokkaiStorage state
    const S = window.DokkaiStorage;
    out.storage = S ? { useFallback: S.useFallback, isReady: S.isReady, fallbackMemory: S.fallbackMemory } : null;
    if (S) {
      out.api = {
        solved: await S.getSolvedTasks(),
        words: await S.getAllWords(),
        userSettings: await S.getSettings('user_settings', null),
        pretest: await S.getSettings('pretest_config', null),
        streamProfile: await S.getSettings('stream_profile', null),
        activeSession: await S.getActiveSession()
      };
      out.export = JSON.parse(await S.exportAllData());
    }
    return out;
  });
}

async function runScenario(page) {
  return page.evaluate(async () => {
    const S = window.DokkaiStorage;
    await S.initPromise;
    await S.recordSolvedTask({ text_id: 101, title: 'テスト一', level: 'N5', category: 'short', score_percent: 100, correct_count: 3, total_questions: 3, solved_at: '2023-01-01T00:00:00.000Z', time_spent_sec: 61, answers: [{ q: 1, a: 2 }, { q: 2, a: 1 }] });
    await S.recordSolvedTask({ text_id: 102, title: 'テスト二', level: 'N4', category: 'mid', score: 50, correct_count: 1, total_questions: 2, time_spent_sec: 99 });
    await S.recordSolvedTask({ text_id: 101, title: 'テスト一', level: 'N5', category: 'short', score_percent: 66, correct_count: 2, total_questions: 3 }); // overwrite
    await S.saveWord({ word: '学校', reading: 'がっこう', meaning: 'school' });
    await S.saveWord({ word: '先生', reading: 'せんせい', meaning: 'teacher' });
    await S.toggleWordMastered('先生', true);
    await S.removeWord('学校');
    await S.saveWord({ word: '本', reading: 'ほん', meaning: 'book' });
    await S.saveSettings('user_settings', { fontFamily: 'serif', fontSizePx: 20, updated_at: 1700000000000 });
    await S.saveSettings('pretest_config', { timerEnabled: false, minutes: 8 });
    await S.saveSettings('stream_profile', { level: 'N4', category: 'mid' });
    await S.saveActiveSession({ textId: 102, title: 'テスト二', level: 'N4', currentQuestionIndex: 1, userAnswers: { 1: 2 }, timer: { enabled: true, remainingSeconds: 300, secondsSpent: 20 } });
    await S.clearActiveSession();
    await S.saveActiveSession({ textId: 101, title: 'テスト一', level: 'N5', currentQuestionIndex: 2, userAnswers: { 1: 1, 2: 3 }, timer: null });
  });
}

async function runImportRoundTrip(page) {
  return page.evaluate(async () => {
    const S = window.DokkaiStorage;
    await S.initPromise;
    const result = await S.importAllData({
      app: 'Dokkai Master', schema_version: 1,
      data: {
        solved_tasks: [{ text_id: 7, title: 'Imp', level: 'N3', category: 'long', score_percent: 100, correct_count: 4, total_questions: 4, solved_at: '2022-02-02T00:00:00.000Z' }, { bogus: true }],
        notebook: [{ word: '雨', reading: 'あめ', meaning: 'rain', mastered: true, updated_at: 1650000000000 }, { nope: 1 }],
        settings: { user_settings: { fontFamily: 'sans', fontSizePx: 18 }, pretest_config: { timerEnabled: true, minutes: 5 }, stream_profile: { level: 'N3', category: 'long' } }
      }
    });
    let bad;
    try { bad = await S.importAllData('{not json'); } catch (e) { bad = { thrown: String(e) }; }
    let bad2 = await S.importAllData({ nodata: 1 });
    return { result, bad, bad2 };
  });
}

async function runFirestorePayload(page) {
  return page.evaluate(async () => {
    const C = window.DokkaiCloudSync;
    const S = window.DokkaiStorage;
    await S.initPromise;
    const calls = [];
    const statuses = [];
    C.onStatusChange((s, extra) => statuses.push([s, extra || null]));
    C.user = { uid: 'uid-snapshot', email: 'snap@example.test', isAnonymous: false };
    C.db = { __stub: true };
    C.isSyncing = false;
    const remote = {
      solved_tasks: {
        101: { text_id: 101, title: 'REMOTE-101', level: 'N5', category: 'short', score: 100, correct_count: 3, total_questions: 3, perfect: true, solved_at: '2021-01-01T00:00:00.000Z', time_spent_sec: 5, answers: [], updated_at: 1 },
        300: { text_id: 300, title: 'REMOTE-300', level: 'N2', category: 'long', score: 80, correct_count: 4, total_questions: 5, perfect: false, solved_at: '2021-02-02T00:00:00.000Z', time_spent_sec: 7, answers: [], updated_at: 2 }
      },
      notebook: {
        '先生': { word: '先生', reading: 'せんせい', meaning: 'teacher', mastered: false, updated_at: 1900000000000 },
        '空': { word: '空', reading: 'そら', meaning: 'sky', mastered: true, updated_at: 5 }
      },
      settings: { user_settings: { fontFamily: 'remote', fontSizePx: 30 } },
      settings_updated_at: 1600000000000,
      active_session: null
    };
    C._firebaseFns = {
      doc: (db, ...segs) => ({ path: segs.join('/') }),
      getDoc: async (ref) => { calls.push(['getDoc', ref.path]); return { exists: () => true, data: () => JSON.parse(JSON.stringify(remote)) }; },
      setDoc: async (ref, payload, opts) => { calls.push(['setDoc', ref.path, JSON.parse(JSON.stringify(payload)), opts]); }
    };
    await C.syncNow();
    return { calls, statuses, hasPendingChanges: C.hasPendingChanges };
  });
}

// ---------------------------------------------------------------- scenario runner
async function newPage(browser, baseUrl, { initScripts = [], seedLegacyData = false } = {}) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, serviceWorkers: 'block' });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.addInitScript(FREEZE_CLOCK);
  for (const s of initScripts) await page.addInitScript(s);
  if (seedLegacyData) {
    await page.addInitScript(`(() => { if (!localStorage.getItem('dokkai_idb_migrated_v1') && !sessionStorage.getItem('__seeded')) { (${seedLegacy.toString()})(); sessionStorage.setItem('__seeded', '1'); } })();`);
  }
  await page.goto(baseUrl);
  await page.waitForFunction(() => window.DokkaiStorage && window.DokkaiCloudSync, null, { timeout: 15000 });
  await page.evaluate(() => window.DokkaiStorage.initPromise);
  return { context, page, errors };
}

async function snapshot(baseUrl) {
  const browser = await chromium.launch({ headless: true });
  const snap = {};
  try {
    // 1. IndexedDB mode
    {
      const { context, page, errors } = await newPage(browser, baseUrl);
      await page.waitForTimeout(300); // a fresh browser context starts with an empty DB
      await runScenario(page);
      await page.waitForTimeout(300);
      snap.indexeddb_mode = await dumpPage(page);
      snap.firestore_payload = await runFirestorePayload(page);
      snap.indexeddb_mode_after_sync = await dumpPage(page);
      snap.import_roundtrip = { ...(await runImportRoundTrip(page)), dump: await dumpPage(page) };
      snap.indexeddb_mode_errors = errors;
      await context.close();
    }
    // 2. localStorage fallback mode (IndexedDB unavailable)
    {
      const { context, page, errors } = await newPage(browser, baseUrl, { initScripts: [NO_INDEXEDDB] });
      await runScenario(page);
      await page.waitForTimeout(300);
      snap.fallback_mode = await dumpPage(page);
      snap.fallback_firestore_payload = await runFirestorePayload(page);
      snap.fallback_mode_errors = errors;
      await context.close();
    }
    // 3. legacy localStorage -> IndexedDB migration
    {
      const { context, page, errors } = await newPage(browser, baseUrl, { seedLegacyData: true });
      await page.waitForFunction(() => localStorage.getItem('dokkai_idb_migrated_v1') === 'true', null, { timeout: 10000 });
      await page.waitForTimeout(500);
      snap.legacy_migration = await dumpPage(page);
      snap.legacy_migration_errors = errors;
      await context.close();
    }
  } finally {
    await browser.close();
  }
  return snap;
}

// ---------------------------------------------------------------- comparison
function ordered(v) { return JSON.stringify(v, null, 2); }

function firstDiff(a, b, p = '') {
  if (JSON.stringify(a) === JSON.stringify(b)) return null;
  if (a && b && typeof a === 'object' && typeof b === 'object' && Array.isArray(a) === Array.isArray(b)) {
    const ka = Object.keys(a), kb = Object.keys(b);
    if (ka.join('\u0000') !== kb.join('\u0000') && !Array.isArray(a)) {
      const only = ka.filter((k) => !kb.includes(k)).concat(kb.filter((k) => !ka.includes(k)));
      if (only.length) return `${p}: key sets differ (${only.join(', ')})`;
      return `${p}: key ORDER differs`;
    }
    for (const k of new Set([...ka, ...kb])) {
      const d = firstDiff(a[k], b[k], `${p}/${k}`);
      if (d) return d;
    }
  }
  return `${p}: ${JSON.stringify(a)} !== ${JSON.stringify(b)}`;
}

function compare(label, a, b) {
  const sections = Array.from(new Set([...Object.keys(a), ...Object.keys(b)]));
  let bad = 0;
  for (const s of sections) {
    const same = ordered(a[s]) === ordered(b[s]);
    console.log(`${same ? '  PASS' : '  FAIL'}  ${s}`);
    if (!same) { bad++; console.log('        first diff: ' + firstDiff(a[s], b[s], s)); }
  }
  console.log(`${label}: ${sections.length - bad}/${sections.length} sections identical`);
  return bad;
}

(async () => {
  if (args.has('--update-baseline')) {
    console.log('Capturing snapshot from main (' + MAIN_URL + ')...');
    const snap = await snapshot(MAIN_URL);
    fs.mkdirSync(path.dirname(BASELINE), { recursive: true });
    fs.writeFileSync(BASELINE, ordered(snap) + '\n');
    console.log('Baseline written: ' + path.relative(process.cwd(), BASELINE));
    return;
  }

  console.log('Capturing snapshot from branch (' + BRANCH_URL + ')...');
  const branch = await snapshot(BRANCH_URL);

  let bad = 0;
  if (args.has('--baseline')) {
    const golden = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
    bad += compare('branch vs golden baseline', golden, branch);
  } else {
    console.log('Capturing snapshot from main (' + MAIN_URL + ')...');
    const main = await snapshot(MAIN_URL);
    console.log('Capturing second snapshot from main for determinism check...');
    const main2 = await snapshot(MAIN_URL);
    console.log('\nDeterminism (main vs main, must be identical for the comparison to mean anything):');
    const nd = compare('main vs main', main, main2);
    if (nd) { console.log('NON-DETERMINISTIC SNAPSHOT - cannot trust the comparison'); process.exit(2); }
    console.log('\nParity (main vs branch):');
    bad += compare('main vs branch', main, branch);
    fs.mkdirSync(path.resolve(__dirname, '../docs/qa/evidence'), { recursive: true });
    fs.writeFileSync(path.resolve(__dirname, '../docs/qa/evidence/storage_snapshot_main.json'), ordered(main) + '\n');
    fs.writeFileSync(path.resolve(__dirname, '../docs/qa/evidence/storage_snapshot_branch.json'), ordered(branch) + '\n');
  }

  if (bad) { console.log('\nSTORAGE SNAPSHOT DISCREPANCIES FOUND: ' + bad); process.exit(1); }
  console.log('\n✓ STORAGE SNAPSHOT PARITY CONFIRMED (0 discrepancies)');
})().catch((e) => { console.error(e); process.exit(1); });
