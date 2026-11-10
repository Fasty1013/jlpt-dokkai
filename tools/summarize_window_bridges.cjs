const { execSync } = require('child_process');

const out = execSync('git grep -n "window\\." static/', { encoding: 'utf-8' });
const lines = out.split('\n').filter(Boolean);

const assignments = [];
const fileCounts = {};

for (const line of lines) {
  // Only assignments: window.xyz = ... (excluding comparisons ==, !=, ===, !==, typeof window)
  const match = line.match(/^([^:]+):(\d+):.*?\bwindow\.([A-Za-z0-9_]+)\s*=\s*(.+)$/);
  if (!match) continue;
  const [_, file, lineNo, prop, val] = match;
  if (val.startsWith('=') || val.startsWith('=')) continue;
  assignments.push({ file, lineNo, prop, val: val.trim() });
  fileCounts[file] = (fileCounts[file] || 0) + 1;
}

console.log('--- TOTAL WINDOW ASSIGNMENTS BY FILE ---');
console.table(fileCounts);

const namespaces = assignments.filter(a => a.prop.startsWith('Dokkai') || a.prop.startsWith('DOKKAI') || a.prop === 'state' || a.prop === 'elements' || a.prop === 'cachedCatalogTexts');
const inlineEventBridges = assignments.filter(a => [
  'openPretestModal', 'closePretestModal', 'confirmPretestSettingsAndStart',
  'fetchAndRenderSlots', 'handleSlotReplacement', 'switchMobileStreamCol',
  'reviewSolvedTask', 'retrySolvedTask', 'openReportModal', 'closeReportModal', 'submitReportDefect',
  'handleOptionSelect', 'wizardGoNext', 'wizardGoPrev', 'startExercise',
  'switchAnalysisTab', 'locateEvidenceInText', 'toggleFurigana', 'toggleEvidence', 'toggleSupplementaryDrawer', 'submitAnswers',
  'showPopupDictionary', 'hidePopupDictionary', 'lookupAndShowWord', 'togglePopupDictStatus',
  'toggleSaveWord', 'clearAllSavedWords', 'saveDraft', 'publishDraft', 'deleteDraft', 'markDraftCorrectOption'
].includes(a.prop));

const otherBridges = assignments.filter(a => !namespaces.includes(a) && !inlineEventBridges.includes(a));

console.log(`\n--- 1. NAMESPACE & GLOBAL STATE BRIDGES (${namespaces.length}) ---`);
namespaces.forEach(a => console.log(`  ${a.file}:${a.lineNo} -> window.${a.prop}`));

console.log(`\n--- 2. INLINE EVENT BRIDGES (TO BE REMOVED ON STEP 6) (${inlineEventBridges.length}) ---`);
inlineEventBridges.forEach(a => console.log(`  ${a.file}:${a.lineNo} -> window.${a.prop}`));

console.log(`\n--- 3. PURE UTILITIES, TIMERS & RUNTIME BRIDGES (${otherBridges.length}) ---`);
otherBridges.forEach(a => console.log(`  ${a.file}:${a.lineNo} -> window.${a.prop}`));

console.log(`\nTOTAL UNIQUE WINDOW ASSIGNMENTS: ${assignments.length}`);
