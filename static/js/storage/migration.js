/** One-time migration from legacy localStorage keys into IndexedDB (Step 7c). */

import { LEGACY_KEYS } from './constants.js';

export async function migrateLegacyLocalStorage(storage) {
    try {
        if (localStorage.getItem('dokkai_idb_migrated_v1')) return;

        // 1. Migrate saved words
        const legacyWordsRaw = localStorage.getItem(LEGACY_KEYS.WORDS);
        if (legacyWordsRaw) {
            const words = JSON.parse(legacyWordsRaw);
            if (Array.isArray(words) && words.length > 0) {
                for (const w of words) {
                    if (w && w.word) {
                        await storage.saveWord({
                            word: w.word,
                            reading: w.reading || '',
                            meaning: w.meaning || '',
                            level: w.level || 'JLPT',
                            mastered: Boolean(w.mastered),
                            added_at: w.date || new Date().toISOString(),
                            updated_at: Date.now()
                        }, false);
                    }
                }
            }
        }

        // 2. Migrate pretest config
        const legacyConfigRaw = localStorage.getItem(LEGACY_KEYS.CONFIG);
        if (legacyConfigRaw) {
            const cfg = JSON.parse(legacyConfigRaw);
            if (cfg) {
                await storage.saveSettings('pretest_config', cfg, false);
            }
        }

        localStorage.setItem('dokkai_idb_migrated_v1', 'true');
    } catch (err) {
        console.warn('[DokkaiStorage] Legacy migration warning:', err);
    }
}
