/**
 * JLPT Dokkai Master - Offline-First Local Storage Engine (IndexedDB + Fallback)
 * Layer 1 of the Persistence Architecture
 * 
 * Provides atomic, persistent, offline-first storage for:
 * 1. solved_tasks: Completed tests with scores, time spent, and dates
 * 2. notebook: Personal vocabulary glossary with "learning" / "mastered" status
 * 3. settings: User preferences (font size, furigana toggle, timer, profile)
 * 4. active_session: In-progress test recovery state (questions, answers, timer)
 */

(function (window) {
    'use strict';

    const DB_NAME = 'dokkai_master_db';
    const DB_VERSION = 1;

    // Legacy localStorage keys for seamless 1-click migration
    const LEGACY_KEYS = {
        WORDS: 'dokkai_saved_words',
        CONFIG: 'dokkai_pretest_config',
        USER_ID: 'dokkai_user_id'
    };

    class DokkaiStorage {
        constructor() {
            this.db = null;
            this.isReady = false;
            this.useFallback = false;
            this.fallbackMemory = {
                solved_tasks: {},
                notebook: {},
                settings: {},
                active_session: {}
            };
            this.syncListeners = [];
            this.debounceTimers = {};
            this.initPromise = this._initDB();
        }

        async _initDB() {
            // 1. Request persistent storage if supported by browser
            try {
                if (navigator.storage && navigator.storage.persist) {
                    const isPersisted = await navigator.storage.persist();
                    console.info('[DokkaiStorage] Persistent storage granted:', isPersisted);
                }
            } catch (err) {
                console.warn('[DokkaiStorage] navigator.storage.persist check failed:', err);
            }

            // 2. Open IndexedDB
            return new Promise((resolve) => {
                if (!window.indexedDB) {
                    console.warn('[DokkaiStorage] IndexedDB not available, using localStorage fallback');
                    this.useFallback = true;
                    this._loadFallbackFromLocalStorage();
                    this.isReady = true;
                    resolve(this);
                    return;
                }

                try {
                    const request = window.indexedDB.open(DB_NAME, DB_VERSION);

                    request.onupgradeneeded = (event) => {
                        const db = event.target.result;

                        // Store 1: solved_tasks (keyed by text_id)
                        if (!db.objectStoreNames.contains('solved_tasks')) {
                            const solvedStore = db.createObjectStore('solved_tasks', { keyPath: 'text_id' });
                            solvedStore.createIndex('level', 'level', { unique: false });
                            solvedStore.createIndex('solved_at', 'solved_at', { unique: false });
                        }

                        // Store 2: notebook (keyed by word)
                        if (!db.objectStoreNames.contains('notebook')) {
                            const noteStore = db.createObjectStore('notebook', { keyPath: 'word' });
                            noteStore.createIndex('mastered', 'mastered', { unique: false });
                            noteStore.createIndex('updated_at', 'updated_at', { unique: false });
                        }

                        // Store 3: settings (keyed by key)
                        if (!db.objectStoreNames.contains('settings')) {
                            db.createObjectStore('settings', { keyPath: 'key' });
                        }

                        // Store 4: active_session (keyed by id, single record 'current')
                        if (!db.objectStoreNames.contains('active_session')) {
                            db.createObjectStore('active_session', { keyPath: 'id' });
                        }
                    };

                    request.onsuccess = (event) => {
                        this.db = event.target.result;
                        this.isReady = true;
                        resolve(this);

                        // Perform automatic one-time migration from legacy localStorage in next tick
                        setTimeout(() => this._migrateLegacyLocalStorage(), 10);
                    };

                    request.onerror = (event) => {
                        console.warn('[DokkaiStorage] IndexedDB open error, falling back to localStorage:', event.target.error);
                        this.useFallback = true;
                        this._loadFallbackFromLocalStorage();
                        this.isReady = true;
                        resolve(this);
                    };
                } catch (err) {
                    console.warn('[DokkaiStorage] Exception opening IndexedDB:', err);
                    this.useFallback = true;
                    this._loadFallbackFromLocalStorage();
                    this.isReady = true;
                    resolve(this);
                }
            });
        }

        // ====================================================================
        // Fallback LocalStorage Mechanism (Private Browsing / Blocked IDB)
        // ====================================================================

        _loadFallbackFromLocalStorage() {
            try {
                const solvedRaw = localStorage.getItem('dokkai_idb_solved_tasks');
                if (solvedRaw) this.fallbackMemory.solved_tasks = JSON.parse(solvedRaw);

                const noteRaw = localStorage.getItem('dokkai_idb_notebook') || localStorage.getItem(LEGACY_KEYS.WORDS);
                if (noteRaw) {
                    const wordsArr = JSON.parse(noteRaw);
                    if (Array.isArray(wordsArr)) {
                        wordsArr.forEach(w => {
                            if (w && w.word) this.fallbackMemory.notebook[w.word] = w;
                        });
                    } else if (typeof wordsArr === 'object') {
                        this.fallbackMemory.notebook = wordsArr;
                    }
                }

                const setRaw = localStorage.getItem('dokkai_idb_settings');
                if (setRaw) this.fallbackMemory.settings = JSON.parse(setRaw);

                const actRaw = localStorage.getItem('dokkai_idb_active_session');
                if (actRaw) this.fallbackMemory.active_session = JSON.parse(actRaw);
            } catch (e) {
                console.warn('[DokkaiStorage] Fallback localStorage parse failed', e);
            }
        }

        _saveFallbackToLocalStorage(storeName) {
            try {
                const key = 'dokkai_idb_' + storeName;
                localStorage.setItem(key, JSON.stringify(this.fallbackMemory[storeName]));
            } catch (e) {
                console.warn('[DokkaiStorage] Fallback localStorage save failed', e);
            }
        }

        // ====================================================================
        // Legacy Migration
        // ====================================================================

        async _migrateLegacyLocalStorage() {
            try {
                if (localStorage.getItem('dokkai_idb_migrated_v1')) return;

                // 1. Migrate saved words
                const legacyWordsRaw = localStorage.getItem(LEGACY_KEYS.WORDS);
                if (legacyWordsRaw) {
                    const words = JSON.parse(legacyWordsRaw);
                    if (Array.isArray(words) && words.length > 0) {
                        for (const w of words) {
                            if (w && w.word) {
                                await this.saveWord({
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
                        await this.saveSettings('pretest_config', cfg, false);
                    }
                }

                localStorage.setItem('dokkai_idb_migrated_v1', 'true');
            } catch (err) {
                console.warn('[DokkaiStorage] Legacy migration warning:', err);
            }
        }

        // ====================================================================
        // Core Transaction Helper
        // ====================================================================

        async _runTx(storeName, mode, callback) {
            await this.initPromise;

            if (this.useFallback || !this.db) {
                return callback(null, this.fallbackMemory[storeName]);
            }

            return new Promise((resolve, reject) => {
                try {
                    const tx = this.db.transaction(storeName, mode);
                    const store = tx.objectStore(storeName);

                    const result = callback(store);

                    tx.oncomplete = () => resolve(result);
                    tx.onerror = (e) => reject(e.target.error);
                } catch (err) {
                    reject(err);
                }
            });
        }

        _notifyMutation(type, details) {
            this.syncListeners.forEach(listener => {
                try {
                    listener(type, details);
                } catch (e) {
                    console.error('[DokkaiStorage] Listener error:', e);
                }
            });
        }

        onSyncNeeded(listener) {
            if (typeof listener === 'function') {
                this.syncListeners.push(listener);
            }
        }

        // ====================================================================
        // 1. Solved Tasks API
        // ====================================================================

        async recordSolvedTask(taskData) {
            if (!taskData || !taskData.text_id) return null;

            const record = {
                text_id: Number(taskData.text_id),
                title: taskData.title || '',
                level: taskData.level || 'N5',
                category: taskData.category || 'short',
                score: typeof taskData.score === 'number' ? taskData.score : (taskData.score_percent || 0),
                correct_count: taskData.correct_count || 0,
                total_questions: taskData.total_questions || 0,
                perfect: Boolean(taskData.perfect || (taskData.score_percent === 100)),
                solved_at: taskData.solved_at || new Date().toISOString(),
                time_spent_sec: taskData.time_spent_sec || 0,
                answers: taskData.answers || [],
                updated_at: Date.now()
            };

            await this._runTx('solved_tasks', 'readwrite', (store, fallback) => {
                if (store) {
                    store.put(record);
                } else if (fallback) {
                    fallback[record.text_id] = record;
                    this._saveFallbackToLocalStorage('solved_tasks');
                }
            });

            this._notifyMutation('solved_task', record);
            return record;
        }

        async getSolvedTasks(levelFilter = null, modeFilter = 'all') {
            await this.initPromise;

            return new Promise(async (resolve) => {
                if (this.useFallback || !this.db) {
                    let items = Object.values(this.fallbackMemory.solved_tasks || {});
                    if (levelFilter) items = items.filter(t => t.level === levelFilter);
                    if (modeFilter === 'perfect') items = items.filter(t => t.perfect);
                    else if (modeFilter === 'errors') items = items.filter(t => !t.perfect);
                    items.sort((a, b) => new Date(b.solved_at) - new Date(a.solved_at));
                    resolve(items);
                    return;
                }

                try {
                    const tx = this.db.transaction('solved_tasks', 'readonly');
                    const store = tx.objectStore('solved_tasks');
                    const req = store.getAll();

                    req.onsuccess = () => {
                        let items = req.result || [];
                        if (levelFilter) items = items.filter(t => t.level === levelFilter);
                        if (modeFilter === 'perfect') items = items.filter(t => t.perfect);
                        else if (modeFilter === 'errors') items = items.filter(t => !t.perfect);
                        items.sort((a, b) => new Date(b.solved_at) - new Date(a.solved_at));
                        resolve(items);
                    };

                    req.onerror = () => resolve([]);
                } catch (e) {
                    resolve([]);
                }
            });
        }

        async getSolvedTaskById(textId) {
            await this.initPromise;
            const numericId = Number(textId);

            return new Promise((resolve) => {
                if (this.useFallback || !this.db) {
                    resolve(this.fallbackMemory.solved_tasks[numericId] || null);
                    return;
                }
                try {
                    const tx = this.db.transaction('solved_tasks', 'readonly');
                    const req = tx.objectStore('solved_tasks').get(numericId);
                    req.onsuccess = () => resolve(req.result || null);
                    req.onerror = () => resolve(null);
                } catch (e) {
                    resolve(null);
                }
            });
        }

        // ====================================================================
        // 2. Personal Vocabulary Notebook API
        // ====================================================================

        async saveWord(wordData, triggerSync = true) {
            if (!wordData || !wordData.word) return null;

            const record = {
                word: String(wordData.word).trim(),
                reading: wordData.reading || '',
                meaning: wordData.meaning || '',
                level: wordData.level || 'JLPT',
                mastered: Boolean(wordData.mastered),
                added_at: wordData.added_at || new Date().toISOString(),
                updated_at: Date.now()
            };

            await this._runTx('notebook', 'readwrite', (store, fallback) => {
                if (store) {
                    store.put(record);
                } else if (fallback) {
                    fallback[record.word] = record;
                    this._saveFallbackToLocalStorage('notebook');
                }
            });

            // Keep legacy localStorage in sync for backwards compatibility
            await this._syncLegacyWordsStore();

            if (triggerSync) {
                this._notifyMutation('notebook_word', record);
            }
            return record;
        }

        async removeWord(wordText) {
            if (!wordText) return;
            const key = String(wordText).trim();

            await this._runTx('notebook', 'readwrite', (store, fallback) => {
                if (store) {
                    store.delete(key);
                } else if (fallback) {
                    delete fallback[key];
                    this._saveFallbackToLocalStorage('notebook');
                }
            });

            await this._syncLegacyWordsStore();
            this._notifyMutation('notebook_remove', { word: key });
        }

        async toggleWordMastered(wordText, isMastered) {
            if (!wordText) return;
            const key = String(wordText).trim();

            let wordRecord = await this.getWord(key);
            if (!wordRecord) return;

            wordRecord.mastered = Boolean(isMastered);
            wordRecord.updated_at = Date.now();

            await this.saveWord(wordRecord, true);
            return wordRecord;
        }

        async getWord(wordText) {
            await this.initPromise;
            const key = String(wordText).trim();

            return new Promise((resolve) => {
                if (this.useFallback || !this.db) {
                    resolve(this.fallbackMemory.notebook[key] || null);
                    return;
                }
                try {
                    const tx = this.db.transaction('notebook', 'readonly');
                    const req = tx.objectStore('notebook').get(key);
                    req.onsuccess = () => resolve(req.result || null);
                    req.onerror = () => resolve(null);
                } catch (e) {
                    resolve(null);
                }
            });
        }

        async getAllWords(filter = 'all', query = '') {
            await this.initPromise;

            return new Promise((resolve) => {
                const filterList = (items) => {
                    let result = items || [];
                    if (filter === 'learning') {
                        result = result.filter(w => !w.mastered);
                    } else if (filter === 'learned' || filter === 'mastered') {
                        result = result.filter(w => w.mastered);
                    }
                    if (query && query.trim()) {
                        const q = query.trim().toLowerCase();
                        result = result.filter(w =>
                            (w.word && w.word.toLowerCase().includes(q)) ||
                            (w.reading && w.reading.toLowerCase().includes(q)) ||
                            (w.meaning && w.meaning.toLowerCase().includes(q))
                        );
                    }
                    result.sort((a, b) => (b.updated_at || 0) - (a.updated_at || 0));
                    return result;
                };

                if (this.useFallback || !this.db) {
                    resolve(filterList(Object.values(this.fallbackMemory.notebook || {})));
                    return;
                }

                try {
                    const tx = this.db.transaction('notebook', 'readonly');
                    const req = tx.objectStore('notebook').getAll();
                    req.onsuccess = () => resolve(filterList(req.result));
                    req.onerror = () => resolve([]);
                } catch (e) {
                    resolve([]);
                }
            });
        }

        async _syncLegacyWordsStore() {
            try {
                const words = await this.getAllWords('all');
                localStorage.setItem(LEGACY_KEYS.WORDS, JSON.stringify(words));
            } catch (e) {
                // Ignore sync errors
            }
        }

        // ====================================================================
        // 3. Settings API
        // ====================================================================

        async saveSettings(key, value, triggerSync = true) {
            if (!key) return;

            const record = {
                key: String(key),
                value: value,
                updated_at: Date.now()
            };

            await this._runTx('settings', 'readwrite', (store, fallback) => {
                if (store) {
                    store.put(record);
                } else if (fallback) {
                    fallback[record.key] = record;
                    this._saveFallbackToLocalStorage('settings');
                }
            });

            // Keep legacy config synced
            if (key === 'pretest_config') {
                try {
                    localStorage.setItem(LEGACY_KEYS.CONFIG, JSON.stringify(value));
                } catch (e) { }
            }

            if (triggerSync) {
                this._notifyMutation('settings', record);
            }
            return record;
        }

        async getSettings(key, defaultValue = null) {
            await this.initPromise;
            const lookupKey = String(key);

            return new Promise((resolve) => {
                if (this.useFallback || !this.db) {
                    const rec = this.fallbackMemory.settings[lookupKey];
                    resolve(rec ? rec.value : defaultValue);
                    return;
                }

                try {
                    const tx = this.db.transaction('settings', 'readonly');
                    const req = tx.objectStore('settings').get(lookupKey);
                    req.onsuccess = () => {
                        if (req.result && req.result.value !== undefined) {
                            resolve(req.result.value);
                        } else {
                            resolve(defaultValue);
                        }
                    };
                    req.onerror = () => resolve(defaultValue);
                } catch (e) {
                    resolve(defaultValue);
                }
            });
        }

        // ====================================================================
        // 4. In-Progress Test Recovery (Active Session)
        // ====================================================================

        async saveActiveSession(sessionData) {
            if (!sessionData || !sessionData.textId) return;

            const record = {
                id: 'current',
                textId: Number(sessionData.textId),
                title: sessionData.title || '',
                level: sessionData.level || 'N5',
                currentQuestionIndex: Number(sessionData.currentQuestionIndex || 0),
                userAnswers: sessionData.userAnswers || {},
                timer: sessionData.timer || null,
                timestamp: Date.now()
            };

            await this._runTx('active_session', 'readwrite', (store, fallback) => {
                if (store) {
                    store.put(record);
                } else if (fallback) {
                    fallback['current'] = record;
                    this._saveFallbackToLocalStorage('active_session');
                }
            });

            return record;
        }

        async getActiveSession() {
            await this.initPromise;

            return new Promise((resolve) => {
                const evaluate = (rec) => {
                    if (!rec || !rec.textId) return null;
                    // Expire sessions older than 24 hours to prevent stale ghost tests
                    const MAX_AGE_MS = 24 * 60 * 60 * 1000;
                    if (Date.now() - (rec.timestamp || 0) > MAX_AGE_MS) {
                        this.clearActiveSession();
                        return null;
                    }
                    return rec;
                };

                if (this.useFallback || !this.db) {
                    resolve(evaluate(this.fallbackMemory.active_session['current']));
                    return;
                }

                try {
                    const tx = this.db.transaction('active_session', 'readonly');
                    const req = tx.objectStore('active_session').get('current');
                    req.onsuccess = () => resolve(evaluate(req.result));
                    req.onerror = () => resolve(null);
                } catch (e) {
                    resolve(null);
                }
            });
        }

        async clearActiveSession() {
            await this._runTx('active_session', 'readwrite', (store, fallback) => {
                if (store) {
                    store.delete('current');
                } else if (fallback) {
                    delete fallback['current'];
                    this._saveFallbackToLocalStorage('active_session');
                }
            });
        }

        // ====================================================================
        // 5. Complete JSON Export & Import (Anti-Data-Loss Insurance)
        // ====================================================================

        async exportAllData() {
            const solved = await this.getSolvedTasks();
            const words = await this.getAllWords();
            const userSettings = await this.getSettings('user_settings', {});
            const pretestConfig = await this.getSettings('pretest_config', {});
            const streamProfile = await this.getSettings('stream_profile', {});

            const exportPayload = {
                app: 'Dokkai Master',
                schema_version: 1,
                exported_at: new Date().toISOString(),
                user_id: localStorage.getItem(LEGACY_KEYS.USER_ID) || 'anonymous',
                data: {
                    solved_tasks: solved,
                    notebook: words,
                    settings: {
                        user_settings: userSettings,
                        pretest_config: pretestConfig,
                        stream_profile: streamProfile
                    }
                }
            };

            return JSON.stringify(exportPayload, null, 2);
        }

        async importAllData(jsonString) {
            try {
                const parsed = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
                if (!parsed || !parsed.data) {
                    throw new Error('Некорректный формат файла бэкапа');
                }

                const data = parsed.data;

                // 1. Import solved tasks
                if (Array.isArray(data.solved_tasks)) {
                    for (const task of data.solved_tasks) {
                        if (task && task.text_id) {
                            await this.recordSolvedTask(task);
                        }
                    }
                }

                // 2. Import notebook words
                if (Array.isArray(data.notebook)) {
                    for (const w of data.notebook) {
                        if (w && w.word) {
                            await this.saveWord(w, false);
                        }
                    }
                }

                // 3. Import settings
                if (data.settings) {
                    if (data.settings.user_settings) {
                        await this.saveSettings('user_settings', data.settings.user_settings, false);
                    }
                    if (data.settings.pretest_config) {
                        await this.saveSettings('pretest_config', data.settings.pretest_config, false);
                    }
                    if (data.settings.stream_profile) {
                        await this.saveSettings('stream_profile', data.settings.stream_profile, false);
                    }
                }

                this._notifyMutation('import_complete', { count: (data.solved_tasks || []).length });
                return {
                    success: true,
                    solvedCount: (data.solved_tasks || []).length,
                    wordsCount: (data.notebook || []).length
                };
            } catch (err) {
                console.error('[DokkaiStorage] Import failed:', err);
                return { success: false, error: err.message };
            }
        }
    }

    // Export singleton on window
    window.DokkaiStorage = new DokkaiStorage();

})(window);

