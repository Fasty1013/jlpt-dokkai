/**
 * i18n consistency check (feat/i18n-switcher). Usage: node tools/i18n_check.mjs
 *  1. ru / uz / en / ja define exactly the same keys, no empty values.
 *  2. {placeholders} are identical in every language for each key.
 *  3. Every key referenced by data-i18n / data-i18n-attr in index.html and by t('...') in static/js exists.
 *  4. Reports (non-fatal) values identical to Russian in en/uz/ja - candidates for missing translation.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const load = async (l) => (await import(pathToFileURL(path.join(root, 'static/js/i18n/locales', l + '.js')).href))[l];
const dict = { ru: await load('ru'), uz: await load('uz'), en: await load('en'), ja: await load('ja') };
let errors = 0;
const fail = (m) => { errors++; console.log('FAIL', m); };

const ruKeys = Object.keys(dict.ru);
for (const l of ['uz', 'en', 'ja']) {
  const keys = new Set(Object.keys(dict[l]));
  for (const k of ruKeys) if (!keys.has(k)) fail(`${l}: missing key ${k}`);
  for (const k of keys) if (!(k in dict.ru)) fail(`${l}: extra key ${k}`);
}
for (const l of Object.keys(dict)) for (const [k, v] of Object.entries(dict[l])) {
  if (typeof v !== 'string' || !v.trim()) fail(`${l}: empty/non-string value for ${k}`);
}
const ph = (s) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',');
for (const k of ruKeys) for (const l of ['uz', 'en', 'ja']) {
  if (dict[l][k] !== undefined && ph(dict[l][k]) !== ph(dict.ru[k])) fail(`${l}: placeholder mismatch in ${k}: ${ph(dict[l][k])} vs ${ph(dict.ru[k])}`);
}

const used = new Set();
const html = fs.readFileSync(path.join(root, 'static/index.html'), 'utf8');
for (const m of html.matchAll(/data-i18n(?:-html)?="([^"]+)"/g)) used.add(m[1]);
for (const m of html.matchAll(/data-i18n-attr="([^"]+)"/g)) for (const pair of m[1].split(';')) used.add(pair.slice(pair.indexOf(':') + 1).trim());
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]);
const dyn = [];
for (const f of walk(path.join(root, 'static/js')).filter((f) => f.endsWith('.js') && !f.includes(`${path.sep}locales${path.sep}`))) {
  const src = fs.readFileSync(f, 'utf8');
  for (const m of src.matchAll(/\b(?:t|tr)\(\s*'([^']+)'/g)) used.add(m[1]);
  for (const m of src.matchAll(/\bt\(\s*`([^`$]+)\$\{/g)) dyn.push(m[1]); // dynamic prefixes (trap., category.)
}
for (const k of used) if (!(k in dict.ru)) fail(`key used but not defined: ${k}`);
for (const p of dyn) if (!ruKeys.some((k) => k.startsWith(p))) fail(`dynamic prefix without keys: ${p}`);

const same = {};
for (const l of ['uz', 'en', 'ja']) same[l] = ruKeys.filter((k) => dict[l][k] === dict.ru[k] && /[\u0400-\u04FF]/.test(dict.ru[k]));
console.log(`keys: ${ruKeys.length} per language; used in code/HTML: ${used.size}`);
for (const l of ['uz', 'en', 'ja']) console.log(`${l}: values identical to Russian (untranslated): ${same[l].length}${same[l].length ? ' -> ' + same[l].slice(0, 5).join(', ') : ''}`);
for (const l of ['uz', 'en', 'ja']) if (same[l].length) fail(`${l}: untranslated Cyrillic values`);
console.log(errors ? `FAILED (${errors})` : 'OK');
process.exit(errors ? 1 : 0);
