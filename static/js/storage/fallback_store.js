/** localStorage fallback used when IndexedDB is unavailable (Step 7c). Keys: dokkai_idb_<store>. */

import { LEGACY_KEYS } from './constants.js';

export function loadFallbackFromLocalStorage(fallbackMemory) {
    try {
        const solvedRaw = localStorage.getItem('dokkai_idb_solved_tasks');
        if (solvedRaw) fallbackMemory.solved_tasks = JSON.parse(solvedRaw);

        const noteRaw = localStorage.getItem('dokkai_idb_notebook') || localStorage.getItem(LEGACY_KEYS.WORDS);
        if (noteRaw) {
            const wordsArr = JSON.parse(noteRaw);
            if (Array.isArray(wordsArr)) {
                wordsArr.forEach(w => {
                    if (w && w.word) fallbackMemory.notebook[w.word] = w;
                });
            } else if (typeof wordsArr === 'object') {
                fallbackMemory.notebook = wordsArr;
            }
        }

        const setRaw = localStorage.getItem('dokkai_idb_settings');
        if (setRaw) fallbackMemory.settings = JSON.parse(setRaw);

        const actRaw = localStorage.getItem('dokkai_idb_active_session');
        if (actRaw) fallbackMemory.active_session = JSON.parse(actRaw);
    } catch (e) {
        console.warn('[DokkaiStorage] Fallback localStorage parse failed', e);
    }
}

export function saveFallbackToLocalStorage(fallbackMemory, storeName) {
    try {
        const key = 'dokkai_idb_' + storeName;
        localStorage.setItem(key, JSON.stringify(fallbackMemory[storeName]));
    } catch (e) {
        console.warn('[DokkaiStorage] Fallback localStorage save failed', e);
    }
}
