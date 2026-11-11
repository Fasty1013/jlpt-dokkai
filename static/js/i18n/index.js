/**
 * JLPT Dokkai Master - i18n core (feat/i18n-switcher)
 *
 * UI language: ru (default) | uz | en | ja.
 *  - t(key, params)    -> localized string; falls back to ru, then to the key itself.
 *  - setLang(lang)     -> persists to localStorage, updates <html lang>, re-applies [data-i18n*] attributes,
 *                         notifies onLangChange subscribers (dynamic views re-render themselves).
 *  - applyDom(root)    -> data-i18n (textContent), data-i18n-html (innerHTML, trusted dictionary strings only),
 *                         data-i18n-attr="title:key;aria-label:key2".
 * Storage: localStorage only (key dokkai_ui_lang). IndexedDB format and Firestore structure are untouched.
 * This module deliberately imports nothing from state/ or features/ (keeps the dependency graph acyclic).
 */
import { ru } from './locales/ru.js';
import { en } from './locales/en.js';
import { uz } from './locales/uz.js';
import { ja } from './locales/ja.js';

export const SUPPORTED_LANGS = ['ru', 'uz', 'en', 'ja'];
export const DEFAULT_LANG = 'ru';
export const LANG_STORAGE_KEY = 'dokkai_ui_lang';
/** Names are shown in their own language and are never translated. */
export const LANG_NATIVE_NAMES = { ru: 'Русский', uz: "O'zbek", en: 'English', ja: '日本語' };

const DICTIONARIES = { ru, uz, en, ja };
const listeners = new Set();
let currentLang = DEFAULT_LANG;

function readStoredLang() {
  try {
    const v = window.localStorage.getItem(LANG_STORAGE_KEY);
    return SUPPORTED_LANGS.includes(v) ? v : null;
  } catch (e) {
    return null;
  }
}

function writeStoredLang(lang) {
  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch (e) {
    /* private mode / blocked storage: language simply is not remembered */
  }
}

export function getLang() {
  return currentLang;
}

const LOCALE_TAGS = { ru: 'ru-RU', uz: 'uz-UZ', en: 'en-US', ja: 'ja-JP' };

/** BCP-47 tag for Intl / toLocaleDateString of the current UI language. */
export function getLocaleTag() {
  return LOCALE_TAGS[currentLang] || LOCALE_TAGS[DEFAULT_LANG];
}

/**
 * Localized string. Values in dictionaries are strings (optionally with {name} placeholders)
 * or functions taking positional args. Missing key -> Russian text -> the key itself.
 */
export function t(key, ...args) {
  let value = DICTIONARIES[currentLang] && DICTIONARIES[currentLang][key];
  if (value === undefined) value = ru[key];
  if (value === undefined) return key;
  if (typeof value === 'function') return value(...args);
  const params = args[0];
  if (params && typeof params === 'object') {
    return value.replace(/\{(\w+)\}/g, (m, name) => (name in params ? String(params[name]) : m));
  }
  return value;
}

export function applyDom(root = document) {
  if (!root || !root.querySelectorAll) return;
  root.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.getAttribute('data-i18n'));
  });
  root.querySelectorAll('[data-i18n-html]').forEach((el) => {
    el.innerHTML = t(el.getAttribute('data-i18n-html'));
  });
  root.querySelectorAll('[data-i18n-attr]').forEach((el) => {
    el.getAttribute('data-i18n-attr').split(';').forEach((pair) => {
      const idx = pair.indexOf(':');
      if (idx < 1) return;
      const attr = pair.slice(0, idx).trim();
      const key = pair.slice(idx + 1).trim();
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
  const select = root.querySelector ? root.querySelector('#lang-select') : null;
  if (select && select.value !== currentLang) select.value = currentLang;
}

/**
 * For JS-owned elements that show one fixed message at a time (e.g. the submit button):
 * sets the text and remembers the key in data-i18n, so a language switch re-translates it automatically.
 */
export function setI18nText(el, key) {
  if (!el) return;
  el.setAttribute('data-i18n', key);
  el.textContent = t(key);
}

/**
 * <html lang> per UI language. Russian keeps the historical lang="ja" of index.html on purpose:
 * the browser picks fallback fonts by page language (form controls, CJK glyphs), so changing it
 * would alter the Russian rendering (pixel parity rule). It is a known accessibility wart - see
 * docs/INTENTIONAL_DIFFERENCES.md (I2). For uz / en / ja the attribute is the real language and
 * Japanese text is tagged lang="ja" separately (tagJapaneseText).
 */
const HTML_LANG = { ru: 'ja', uz: 'uz', en: 'en', ja: 'ja' };

function applyLang() {
  const htmlLang = HTML_LANG[currentLang] || 'ja';
  document.documentElement.setAttribute('lang', htmlLang);
  applyDom(document);
  if (htmlLang !== 'ja' && document.body) tagJapaneseText(document.body);
}

/** Subscribe to language changes. Returns an unsubscribe function. */
export function onLangChange(callback) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

export function setLang(lang) {
  if (!SUPPORTED_LANGS.includes(lang)) return false;
  const changed = lang !== currentLang;
  currentLang = lang;
  writeStoredLang(lang);
  applyLang();
  if (changed) {
    listeners.forEach((cb) => {
      try {
        cb(lang);
      } catch (err) {
        console.warn('[Dokkai i18n] language listener failed:', err);
      }
    });
  }
  return true;
}

// ---------------------------------------------------------------------------------------------
// <html lang> follows the UI language, so Japanese text must carry its own lang="ja": otherwise the
// browser picks the CJK fallback font by the page language (wrong glyph shapes / line metrics).
// Every element that directly holds CJK characters is tagged lang="ja" (existing lang attributes win).
// ---------------------------------------------------------------------------------------------
const CJK_RE = /[぀-ヿ㐀-䶿一-鿿ｦ-ﾟ]/;
const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'HTML', 'BODY', 'HEAD']);

function tagElementIfJapanese(textNode) {
  if (document.documentElement.getAttribute('lang') === 'ja') return; // page language already Japanese
  const el = textNode.parentElement;
  if (!el || SKIP_TAGS.has(el.tagName) || el.hasAttribute('lang') || el.closest('[lang="ja"]')) return;
  if (CJK_RE.test(textNode.nodeValue || '')) el.setAttribute('lang', 'ja');
}

export function tagJapaneseText(root) {
  if (!root) return;
  if (root.nodeType === 3) {
    tagElementIfJapanese(root);
    return;
  }
  if (root.nodeType !== 1) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) tagElementIfJapanese(node);
}

let japaneseObserver = null;

function startJapaneseTagging() {
  if (japaneseObserver || typeof MutationObserver === 'undefined' || !document.body) return;
  japaneseObserver = new MutationObserver((records) => {
    for (const rec of records) {
      if (rec.type === 'characterData') tagJapaneseText(rec.target);
      else rec.addedNodes.forEach((n) => tagJapaneseText(n));
    }
  });
  japaneseObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
}

/** Called once from main.js before the first render. */
export function initI18n() {
  currentLang = readStoredLang() || DEFAULT_LANG;
  applyLang();
  startJapaneseTagging();
}

if (typeof window !== 'undefined') {
  window.DokkaiI18n = { t, getLang, getLocaleTag, setLang, onLangChange, applyDom, SUPPORTED_LANGS };
}
