/**
 * JLPT Dokkai Master - Cloud Auto-Sync Engine (Firebase Firestore + Auth)
 * Layer 2 of the Persistence Architecture
 * 
 * Provides:
 * 1. 100% Free Tier ($0 Spark Plan) Cloud Sync using Firestore + Firebase Auth.
 * 2. Background debounced synchronization (1.5s) on every user action.
 * 3. Conflict-free union merge (latest timestamp & highest score wins).
 * 4. Offline detection & automatic queue flush upon network restoration.
 * 5. Unobtrusive sync status management ('local' | 'syncing' | 'synced' | 'offline' | 'error').
 */

(function (window) {
    'use strict';

    const FIREBASE_CONFIG_KEY = 'dokkai_firebase_config';

    // Default configuration placeholder or user-configured Firebase credentials
    function getStoredFirebaseConfig() {
        try {
            const raw = localStorage.getItem(FIREBASE_CONFIG_KEY);
            if (raw) return JSON.parse(raw);
        } catch (e) {
            console.warn('[CloudSync] Failed to read stored firebase config', e);
        }
        return null;
    }

    class DokkaiCloudSync {
        constructor() {
            this.status = 'local'; // 'local' | 'syncing' | 'synced' | 'offline' | 'error'
            this.user = null;      // Firebase user object or null
            this.firebaseApp = null;
            this.auth = null;
            this.db = null;
            this.isInitialized = false;
            this.statusListeners = [];
            this.userListeners = [];
            this.syncDebounceTimer = null;
            this.hasPendingChanges = false;
            this.isSyncing = false;

            this._setupNetworkListeners();
        }

        _setupNetworkListeners() {
            window.addEventListener('online', () => {
                console.info('[CloudSync] Network is back online');
                if (this.user) {
                    this.setStatus('syncing');
                    this.syncNow();
                } else {
                    this.setStatus('local');
                }
            });

            window.addEventListener('offline', () => {
                console.warn('[CloudSync] Network connection lost');
                this.setStatus('offline');
            });
        }

        onStatusChange(fn) {
            if (typeof fn === 'function') this.statusListeners.push(fn);
        }

        onUserChange(fn) {
            if (typeof fn === 'function') this.userListeners.push(fn);
        }

        setStatus(newStatus, extraInfo = '') {
            this.status = newStatus;
            this.statusListeners.forEach(fn => {
                try {
                    fn(newStatus, extraInfo);
                } catch (e) {
                    console.error('[CloudSync] Status listener error', e);
                }
            });
        }

        setUser(user) {
            this.user = user;
            this.userListeners.forEach(fn => {
                try {
                    fn(user);
                } catch (e) {
                    console.error('[CloudSync] User listener error', e);
                }
            });
        }

        getStatusInfo() {
            switch (this.status) {
                case 'synced':
                    return { text: 'В облаке', class: 'status-synced', icon: '🟢', tooltip: 'Все данные сохранены в облаке' };
                case 'syncing':
                    return { text: 'Синхронизация...', class: 'status-syncing', icon: '🔄', tooltip: 'Синхронизация с облаком' };
                case 'offline':
                    return { text: 'Офлайн', class: 'status-offline', icon: '⚠️', tooltip: 'Нет интернета. Прогресс пишется на устройство' };
                case 'error':
                    return { text: 'Ошибка сети', class: 'status-error', icon: '⚠️', tooltip: 'Ошибка облачной синхронизации' };
                case 'local':
                default:
                    return { text: 'На устройстве', class: 'status-local', icon: '📱', tooltip: 'Данные сохраняются на этом устройстве' };
            }
        }

        /**
         * Initialize Cloud Sync with optional custom config
         */
        async init() {
            if (!navigator.onLine) {
                this.setStatus('offline');
            } else {
                this.setStatus('local');
            }

            const config = getStoredFirebaseConfig();
            if (!config || !config.apiKey || !config.projectId) {
                console.info('[CloudSync] No cloud credentials configured. Running in Local Offline-First mode.');
                return;
            }

            await this._initFirebaseSDK(config);
        }

        async _initFirebaseSDK(config) {
            try {
                // Dynamically import Firebase Modular SDK v10 from official Google CDN
                const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js');
                const {
                    getAuth,
                    onAuthStateChanged,
                    signInWithPopup,
                    GoogleAuthProvider,
                    signOut,
                    signInAnonymously
                } = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js');
                const {
                    getFirestore,
                    doc,
                    setDoc,
                    getDoc
                } = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js');

                this.firebaseApp = initializeApp(config);
                this.auth = getAuth(this.firebaseApp);
                this.db = getFirestore(this.firebaseApp);

                this._firebaseFns = {
                    signInWithPopup,
                    GoogleAuthProvider,
                    signOut,
                    signInAnonymously,
                    doc,
                    setDoc,
                    getDoc
                };

                onAuthStateChanged(this.auth, (user) => {
                    this.setUser(user);
                    if (user) {
                        console.info('[CloudSync] User signed in:', user.email || user.uid);
                        this.setStatus('syncing');
                        this.syncNow();
                    } else {
                        console.info('[CloudSync] User signed out');
                        this.setStatus('local');
                    }
                });

                this.isInitialized = true;
            } catch (err) {
                console.warn('[CloudSync] Firebase dynamic import failed:', err);
                this.setStatus('local');
            }
        }

        async saveFirebaseConfig(config) {
            try {
                localStorage.setItem(FIREBASE_CONFIG_KEY, JSON.stringify(config));
                await this._initFirebaseSDK(config);
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        }

        getStoredConfig() {
            return getStoredFirebaseConfig();
        }

        clearFirebaseConfig() {
            localStorage.removeItem(FIREBASE_CONFIG_KEY);
            if (this.auth && this._firebaseFns) {
                this._firebaseFns.signOut(this.auth);
            }
            this.user = null;
            this.setStatus('local');
        }

        // ====================================================================
        // Authentication API
        // ====================================================================

        async signInGoogle() {
            if (!this.isInitialized || !this.auth) {
                throw new Error('Облачная синхронизация не настроена. Добавьте конфигурацию Firebase.');
            }
            const provider = new this._firebaseFns.GoogleAuthProvider();
            return await this._firebaseFns.signInWithPopup(this.auth, provider);
        }

        async signInAnonymous() {
            if (!this.isInitialized || !this.auth) {
                throw new Error('Облачная синхронизация не настроена.');
            }
            return await this._firebaseFns.signInAnonymously(this.auth);
        }

        async signOut() {
            if (this.auth && this._firebaseFns) {
                await this._firebaseFns.signOut(this.auth);
                this.setUser(null);
                this.setStatus('local');
            }
        }

        // ====================================================================
        // Debounced Cloud Sync
        // ====================================================================

        scheduleAutoSync() {
            this.hasPendingChanges = true;
            if (!this.user || !navigator.onLine) {
                return;
            }

            clearTimeout(this.syncDebounceTimer);
            this.syncDebounceTimer = setTimeout(() => {
                this.syncNow();
            }, 1500);
        }

        /**
         * Perform two-way union sync between local IndexedDB and cloud Firestore
         */
        async syncNow() {
            if (this.isSyncing) return;
            if (!this.user || !this.db || !this._firebaseFns) {
                this.setStatus('local');
                return;
            }
            if (!navigator.onLine) {
                this.setStatus('offline');
                return;
            }

            this.isSyncing = true;
            this.setStatus('syncing');

            try {
                const uid = this.user.uid;
                const userDocRef = this._firebaseFns.doc(this.db, 'users', uid);

                // 1. Fetch remote user doc
                const remoteSnap = await this._firebaseFns.getDoc(userDocRef);
                const remoteData = remoteSnap.exists() ? remoteSnap.data() : null;

                // 2. Fetch local data
                const localSolved = await window.DokkaiStorage.getSolvedTasks();
                const localWords = await window.DokkaiStorage.getAllWords();
                const localUserSettings = await window.DokkaiStorage.getSettings('user_settings', {});
                const localPretestConfig = await window.DokkaiStorage.getSettings('pretest_config', {});
                const localStreamProfile = await window.DokkaiStorage.getSettings('stream_profile', {});

                // 3. Perform Conflict-Free Union Merge
                // --- Merge Solved Tasks ---
                const mergedSolvedMap = {};
                // Put remote solved
                if (remoteData && remoteData.solved_tasks) {
                    Object.values(remoteData.solved_tasks).forEach(task => {
                        if (task && task.text_id) mergedSolvedMap[task.text_id] = task;
                    });
                }
                // Merge local solved (higher score or newer timestamp wins)
                localSolved.forEach(localTask => {
                    const existing = mergedSolvedMap[localTask.text_id];
                    if (!existing) {
                        mergedSolvedMap[localTask.text_id] = localTask;
                    } else {
                        // Take the one with higher score, or newer if equal
                        if ((localTask.score || 0) > (existing.score || 0)) {
                            mergedSolvedMap[localTask.text_id] = localTask;
                        } else if ((localTask.score || 0) === (existing.score || 0)) {
                            const localTime = new Date(localTask.solved_at || 0).getTime();
                            const remTime = new Date(existing.solved_at || 0).getTime();
                            if (localTime >= remTime) {
                                mergedSolvedMap[localTask.text_id] = localTask;
                            }
                        }
                    }
                });

                // Write merged solved back to local storage
                for (const t of Object.values(mergedSolvedMap)) {
                    await window.DokkaiStorage.recordSolvedTask(t);
                }

                // --- Merge Notebook Words ---
                const mergedWordsMap = {};
                if (remoteData && remoteData.notebook) {
                    Object.values(remoteData.notebook).forEach(w => {
                        if (w && w.word) mergedWordsMap[w.word] = w;
                    });
                }
                localWords.forEach(localW => {
                    const existing = mergedWordsMap[localW.word];
                    if (!existing) {
                        mergedWordsMap[localW.word] = localW;
                    } else {
                        // If either marked as mastered, keep mastered
                        const isMastered = localW.mastered || existing.mastered;
                        const newestUpdate = Math.max(localW.updated_at || 0, existing.updated_at || 0);
                        mergedWordsMap[localW.word] = {
                            ...existing,
                            ...localW,
                            mastered: isMastered,
                            updated_at: newestUpdate
                        };
                    }
                });

                // Write merged words back to local storage
                for (const w of Object.values(mergedWordsMap)) {
                    await window.DokkaiStorage.saveWord(w, false);
                }

                // --- Merge Settings (newest updated_at wins) ---
                let mergedSettings = {
                    user_settings: localUserSettings,
                    pretest_config: localPretestConfig,
                    stream_profile: localStreamProfile
                };
                if (remoteData && remoteData.settings) {
                    if (remoteData.settings_updated_at && remoteData.settings_updated_at > (localUserSettings.updated_at || 0)) {
                        mergedSettings = remoteData.settings;
                        if (mergedSettings.user_settings) await window.DokkaiStorage.saveSettings('user_settings', mergedSettings.user_settings, false);
                        if (mergedSettings.pretest_config) await window.DokkaiStorage.saveSettings('pretest_config', mergedSettings.pretest_config, false);
                        if (mergedSettings.stream_profile) await window.DokkaiStorage.saveSettings('stream_profile', mergedSettings.stream_profile, false);
                    }
                }

                // 4. Push complete merged state to Firestore
                const payload = {
                    uid: uid,
                    email: this.user.email || null,
                    solved_tasks: mergedSolvedMap,
                    notebook: mergedWordsMap,
                    settings: mergedSettings,
                    settings_updated_at: Date.now(),
                    last_synced_at: new Date().toISOString()
                };

                await this._firebaseFns.setDoc(userDocRef, payload, { merge: true });

                this.hasPendingChanges = false;
                this.setStatus('synced');
                console.info('[CloudSync] Sync successful with Firebase Firestore');
            } catch (err) {
                console.error('[CloudSync] Sync failed:', err);
                this.setStatus('error', err.message);
            } finally {
                this.isSyncing = false;
            }
        }
    }

    // Export singleton on window
    window.DokkaiCloudSync = new DokkaiCloudSync();

})(window);

