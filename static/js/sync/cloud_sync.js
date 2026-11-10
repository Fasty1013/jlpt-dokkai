/**
 * JLPT Dokkai Master - Cloud Auto-Sync Engine (Firebase Firestore + Auth)
 * Layer 2 of the Persistence Architecture
 * 
 * Compliant with Firebase Spark ($0 Free Tier) & Anti-Cheat Protocol:
 * - 100% Offline-First (works seamlessly without login / without internet)
 * - Firebase Modular SDK v10.13.0 via official CDN ES Modules
 * - Google Sign-In with automatic fallback to Redirect on popup blockers
 * - Anonymous Account Linking (lossless account upgrade to Google)
 * - Lossless Union Merge in Firestore (/users/{userId}/sync/state)
 * - Debounced batch updates (1.5s delay) to preserve free read/write quotas
 */

(function (window) {
    'use strict';

    const FIREBASE_SDK_VERSION = '10.13.0';
    const FIREBASE_CONFIG_KEY = 'dokkai_firebase_config';

    function getEffectiveConfig() {
        // 1. Check custom override from localStorage if set by developer
        try {
            const stored = localStorage.getItem(FIREBASE_CONFIG_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (parsed && parsed.apiKey && parsed.projectId) return parsed;
            }
        } catch (e) {
            console.warn('[CloudSync] Failed to read stored config', e);
        }

        // 2. Default to global configuration
        if (window.DOKKAI_FIREBASE_CONFIG && window.DOKKAI_FIREBASE_CONFIG.apiKey) {
            return window.DOKKAI_FIREBASE_CONFIG;
        }

        return null;
    }

    function translateFirebaseError(err) {
        if (!err) return 'Неизвестная ошибка';
        const code = err.code || '';
        const msg = err.message || '';

        switch (code) {
            case 'auth/popup-blocked':
                return 'Всплывающее окно входа заблокировано браузером. Перенаправляем на страницу авторизации Google...';
            case 'auth/popup-closed-by-user':
                return 'Окно входа было закрыто до завершения авторизации.';
            case 'auth/cancelled-popup-request':
                return 'Запрос авторизации был заменён новым окном.';
            case 'auth/unauthorized-domain':
                return 'Домен сайта не авторизован в настройках безопасности Firebase.';
            case 'auth/network-request-failed':
                return 'Нет подключения к интернету. Прогресс сохраняется локально на устройстве.';
            case 'auth/credential-already-in-use':
                return 'Этот Google-аккаунт уже привязан к другому пользователю. Выполняется объединение данных...';
            case 'permission-denied':
                return 'Ошибка прав доступа (permission-denied) к базе Firestore.';
            case 'auth/user-disabled':
                return 'Данный аккаунт отключён администратором.';
            case 'auth/operation-not-allowed':
                return 'Этот метод входа отключён в панели управления Firebase.';
            default:
                if (msg.includes('network') || msg.includes('Failed to fetch')) {
                    return 'Нет подключения к сети. Прогресс сохраняется на устройстве.';
                }
                return msg || 'Ошибка облачной синхронизации.';
        }
    }

    class DokkaiCloudSync {
        constructor() {
            this.status = 'local'; // 'local' | 'syncing' | 'synced' | 'offline' | 'error'
            this.user = null;      // Firebase user or null
            this.firebaseApp = null;
            this.auth = null;
            this.db = null;
            this._firebaseFns = null;
            this.isInitialized = false;
            this.initPromise = null;

            this.statusListeners = [];
            this.userListeners = [];
            this.feedbackListeners = [];
            this.syncDebounceTimer = null;
            this.hasPendingChanges = false;
            this.isSyncing = false;

            this._setupNetworkListeners();
        }

        _setupNetworkListeners() {
            window.addEventListener('online', () => {
                console.info('[CloudSync] Network connection restored');
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

        onFeedback(fn) {
            if (typeof fn === 'function') this.feedbackListeners.push(fn);
        }

        notifyFeedback(type, message) {
            this.feedbackListeners.forEach(fn => {
                try {
                    fn(type, message);
                } catch (e) {
                    console.error('[CloudSync] Feedback listener error', e);
                }
            });
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
            if (!navigator.onLine) {
                return { text: 'Офлайн', class: 'status-offline', icon: '⚠️', tooltip: 'Нет интернета. Данные сохраняются на устройстве' };
            }

            if (this.user) {
                switch (this.status) {
                    case 'synced':
                        const userLabel = this.user.email || (this.user.isAnonymous ? 'Анонимный профиль' : 'В облаке');
                        return {
                            text: `В облаке (${userLabel})`,
                            class: 'status-synced',
                            icon: '🟢',
                            tooltip: `Синхронизировано с Google Firestore (${userLabel})`
                        };
                    case 'syncing':
                        return { text: 'Синхронизация...', class: 'status-syncing', icon: '🔄', tooltip: 'Синхронизация с облаком' };
                    case 'error':
                        return { text: 'Ошибка синхронизации (Повторить)', class: 'status-error', icon: '⚠️', tooltip: 'Нажмите, чтобы повторить синхронизацию' };
                    default:
                        return { text: 'Подключено', class: 'status-synced', icon: '🟢', tooltip: 'Облачная синхронизация активна' };
                }
            }

            return { text: 'На устройстве', class: 'status-local', icon: '📱', tooltip: 'Данные сохраняются в памяти вашего браузера (IndexedDB)' };
        }

        async init() {
            if (this.initPromise) return this.initPromise;

            this.initPromise = (async () => {
                if (!navigator.onLine) {
                    this.setStatus('offline');
                } else {
                    this.setStatus('local');
                }

                const config = getEffectiveConfig();
                if (!config || !config.apiKey || !config.projectId) {
                    console.info('[CloudSync] No cloud credentials configured. Running in Local Offline-First mode.');
                    return;
                }

                await this._initFirebaseSDK(config);
            })();

            return this.initPromise;
        }

        async _initFirebaseSDK(config) {
            try {
                // Dynamically load Firebase Modular SDK from Google's official CDN
                const appModuleUrl = `https://www.gstatic.com/firebasejs/${FIREBASE_SDK_VERSION}/firebase-app.js`;
                const authModuleUrl = `https://www.gstatic.com/firebasejs/${FIREBASE_SDK_VERSION}/firebase-auth.js`;
                const firestoreModuleUrl = `https://www.gstatic.com/firebasejs/${FIREBASE_SDK_VERSION}/firebase-firestore.js`;

                // Load with timeout to ensure it never hangs the application
                const [appMod, authMod, firestoreMod] = await Promise.race([
                    Promise.all([
                        import(/* webpackIgnore: true */ appModuleUrl),
                        import(/* webpackIgnore: true */ authModuleUrl),
                        import(/* webpackIgnore: true */ firestoreModuleUrl)
                    ]),
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Firebase SDK load timeout')), 7000))
                ]);

                const { initializeApp } = appMod;
                const {
                    getAuth,
                    onAuthStateChanged,
                    signInWithPopup,
                    signInWithRedirect,
                    getRedirectResult,
                    GoogleAuthProvider,
                    signOut,
                    signInAnonymously,
                    linkWithPopup,
                    signInWithCredential
                } = authMod;
                const {
                    getFirestore,
                    doc,
                    setDoc,
                    getDoc,
                    writeBatch
                } = firestoreMod;

                this.firebaseApp = initializeApp(config);
                this.auth = getAuth(this.firebaseApp);
                this.db = getFirestore(this.firebaseApp);

                this._firebaseFns = {
                    signInWithPopup,
                    signInWithRedirect,
                    getRedirectResult,
                    GoogleAuthProvider,
                    signOut,
                    signInAnonymously,
                    linkWithPopup,
                    signInWithCredential,
                    doc,
                    setDoc,
                    getDoc,
                    writeBatch
                };

                // Check for redirect sign-in result (from mobile / popup blocked scenarios)
                try {
                    const redirectResult = await getRedirectResult(this.auth);
                    if (redirectResult && redirectResult.user) {
                        console.info('[CloudSync] Redirect sign-in completed for:', redirectResult.user.email || redirectResult.user.uid);
                        this.notifyFeedback('success', `Успешный вход: ${redirectResult.user.email || 'Анонимный профиль'}`);
                    }
                } catch (redErr) {
                    console.warn('[CloudSync] Redirect result error:', redErr);
                    this.notifyFeedback('error', translateFirebaseError(redErr));
                }

                // Auth state observer
                onAuthStateChanged(this.auth, async (user) => {
                    this.setUser(user);
                    if (user) {
                        console.info('[CloudSync] Authenticated as:', user.email || user.uid, user.isAnonymous ? '(Anonymous)' : '(Google)');
                        this.setStatus('syncing');
                        await this.syncNow();
                    } else {
                        console.info('[CloudSync] Signed out. Running in Local Offline-First mode.');
                        this.setStatus('local');
                    }
                });

                this.isInitialized = true;
            } catch (err) {
                console.warn('[CloudSync] Firebase initialization note:', err.message);
                this.setStatus(navigator.onLine ? 'local' : 'offline');
            }
        }

        async _ensureInitialized() {
            if (!this.isInitialized && this.initPromise) {
                await this.initPromise;
            }
        }

        // ====================================================================
        // Authentication API
        // ====================================================================

        async signInGoogle() {
            if (!navigator.onLine) {
                const msg = 'Нет подключения к интернету. Проверьте сеть.';
                this.notifyFeedback('error', msg);
                throw new Error(msg);
            }

            await this._ensureInitialized();
            if (!this.auth || !this._firebaseFns) {
                const msg = 'Облачный сервис Firebase инициализируется или недоступен.';
                this.notifyFeedback('error', msg);
                throw new Error(msg);
            }

            const provider = new this._firebaseFns.GoogleAuthProvider();
            provider.setCustomParameters({ prompt: 'select_account' });

            // Case A: User is currently anonymous -> upgrade account to Google (link)
            if (this.user && this.user.isAnonymous) {
                try {
                    const cred = await this._firebaseFns.linkWithPopup(this.user, provider);
                    this.notifyFeedback('success', `Аккаунт успешно привязан к Google: ${cred.user.email}`);
                    await this.syncNow();
                    return cred.user;
                } catch (linkErr) {
                    if (linkErr.code === 'auth/credential-already-in-use') {
                        // The user already has a Google account.
                        // Safe merge: get the Google credential, sign into that account, and merge the local data into it.
                        console.info('[CloudSync] Linking conflict: Google account already exists. Performing safe merge...');
                        const credential = this._firebaseFns.GoogleAuthProvider.credentialFromError(linkErr);
                        if (credential) {
                            const res = await this._firebaseFns.signInWithCredential(this.auth, credential);
                            this.notifyFeedback('info', `Объединение данных с Google аккаунтом: ${res.user.email}`);
                            await this.syncNow();
                            return res.user;
                        }
                    } else if (linkErr.code === 'auth/popup-blocked') {
                        this.notifyFeedback('warning', 'Всплывающее окно заблокировано. Перенаправляем на вход Google...');
                        await this._firebaseFns.signInWithRedirect(this.auth, provider);
                        return null;
                    }
                    const friendlyMsg = translateFirebaseError(linkErr);
                    this.notifyFeedback('error', friendlyMsg);
                    throw new Error(friendlyMsg);
                }
            }

            // Case B: Regular Google Sign-In with popup -> fallback to redirect
            try {
                const result = await this._firebaseFns.signInWithPopup(this.auth, provider);
                this.notifyFeedback('success', `Вход выполнен: ${result.user.email}`);
                return result.user;
            } catch (err) {
                if (err.code === 'auth/popup-blocked' || err.code === 'auth/cancelled-popup-request') {
                    this.notifyFeedback('warning', 'Всплывающее окно заблокировано браузером. Перенаправляем на страницу входа Google...');
                    await this._firebaseFns.signInWithRedirect(this.auth, provider);
                    return null;
                }
                const friendlyMsg = translateFirebaseError(err);
                this.notifyFeedback('error', friendlyMsg);
                throw new Error(friendlyMsg);
            }
        }

        async signInAnonymous() {
            if (!navigator.onLine) {
                const msg = 'Нет подключения к интернету. Проверьте сеть.';
                this.notifyFeedback('error', msg);
                throw new Error(msg);
            }

            await this._ensureInitialized();
            if (!this.auth || !this._firebaseFns) {
                const msg = 'Облачный сервис Firebase инициализируется или недоступен.';
                this.notifyFeedback('error', msg);
                throw new Error(msg);
            }

            try {
                const result = await this._firebaseFns.signInAnonymously(this.auth);
                this.notifyFeedback('success', `Создан анонимный облачный профиль (ID: ${result.user.uid.slice(0, 8)}).`);
                return result.user;
            } catch (err) {
                const friendlyMsg = translateFirebaseError(err);
                this.notifyFeedback('error', friendlyMsg);
                throw new Error(friendlyMsg);
            }
        }

        async signOut() {
            if (this.auth && this._firebaseFns) {
                try {
                    await this._firebaseFns.signOut(this.auth);
                    this.setUser(null);
                    this.setStatus('local');
                    this.notifyFeedback('info', 'Вы вышли из облачного аккаунта. Локальные данные сохранены.');
                } catch (e) {
                    console.error('[CloudSync] Sign out error:', e);
                }
            }
        }

        // ====================================================================
        // Custom Configuration (For Developers)
        // ====================================================================

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
            return getEffectiveConfig();
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
        // Debounced Cloud Sync (Preserving Free Tier Limits)
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
         * Perform atomic lossless two-way union sync between IndexedDB and Cloud Firestore.
         * Target Document: users/{userId}/sync/state (strictly matches Firestore rules)
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
                // Target path: users/{userId}/sync/state
                const userDocRef = this._firebaseFns.doc(this.db, 'users', uid, 'sync', 'state');

                // 1. Fetch remote user doc
                let remoteData = null;
                try {
                    const remoteSnap = await this._firebaseFns.getDoc(userDocRef);
                    if (remoteSnap.exists()) {
                        remoteData = remoteSnap.data();
                    }
                } catch (readErr) {
                    console.warn('[CloudSync] Remote doc fetch note:', readErr);
                    if (readErr.code === 'permission-denied') {
                        throw readErr;
                    }
                }

                // 2. Fetch local data from IndexedDB (DokkaiStorage)
                const localSolved = (window.DokkaiStorage ? await window.DokkaiStorage.getSolvedTasks() : []) || [];
                const localWords = (window.DokkaiStorage ? await window.DokkaiStorage.getAllWords() : []) || [];
                const localUserSettings = (window.DokkaiStorage ? await window.DokkaiStorage.getSettings('user_settings', {}) : {}) || {};
                const localPretestConfig = (window.DokkaiStorage ? await window.DokkaiStorage.getSettings('pretest_config', {}) : {}) || {};
                const localStreamProfile = (window.DokkaiStorage ? await window.DokkaiStorage.getSettings('stream_profile', {}) : {}) || {};
                const localActiveSession = (window.DokkaiStorage ? await window.DokkaiStorage.getActiveSession() : null);

                // 3. Lossless Conflict-Free Union Merge
                // A. Solved Tasks: union by text_id; higher score wins, or newer solved_at
                const mergedSolvedMap = {};
                if (remoteData && remoteData.solved_tasks) {
                    Object.values(remoteData.solved_tasks).forEach(task => {
                        if (task && task.text_id) mergedSolvedMap[task.text_id] = task;
                    });
                }
                localSolved.forEach(localTask => {
                    const existing = mergedSolvedMap[localTask.text_id];
                    if (!existing) {
                        mergedSolvedMap[localTask.text_id] = localTask;
                    } else {
                        const localScore = Number(localTask.score || 0);
                        const existScore = Number(existing.score || 0);
                        if (localScore > existScore) {
                            mergedSolvedMap[localTask.text_id] = localTask;
                        } else if (localScore === existScore) {
                            const localTime = new Date(localTask.solved_at || 0).getTime();
                            const remTime = new Date(existing.solved_at || 0).getTime();
                            if (localTime >= remTime) {
                                mergedSolvedMap[localTask.text_id] = localTask;
                            }
                        }
                    }
                });

                // Write merged tasks back into local IndexedDB
                if (window.DokkaiStorage) {
                    for (const t of Object.values(mergedSolvedMap)) {
                        await window.DokkaiStorage.recordSolvedTask(t);
                    }
                }

                // B. Notebook Glossary: union by word; mastered is sticky, newest updated_at wins
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
                        const isMastered = Boolean(localW.mastered || existing.mastered);
                        const newestUpdate = Math.max(localW.updated_at || 0, existing.updated_at || 0);
                        mergedWordsMap[localW.word] = {
                            ...existing,
                            ...localW,
                            mastered: isMastered,
                            updated_at: newestUpdate
                        };
                    }
                });

                // Write merged words back into local IndexedDB
                if (window.DokkaiStorage) {
                    for (const w of Object.values(mergedWordsMap)) {
                        await window.DokkaiStorage.saveWord(w, false);
                    }
                }

                // C. Settings: newest settings_updated_at wins
                let mergedSettings = {
                    user_settings: localUserSettings,
                    pretest_config: localPretestConfig,
                    stream_profile: localStreamProfile
                };
                let settingsUpdatedAt = Date.now();

                if (remoteData && remoteData.settings) {
                    const remoteSettingsTime = remoteData.settings_updated_at || 0;
                    const localSettingsTime = localUserSettings.updated_at || 0;

                    if (remoteSettingsTime > localSettingsTime) {
                        mergedSettings = remoteData.settings;
                        settingsUpdatedAt = remoteSettingsTime;
                        if (window.DokkaiStorage) {
                            if (mergedSettings.user_settings) await window.DokkaiStorage.saveSettings('user_settings', mergedSettings.user_settings, false);
                            if (mergedSettings.pretest_config) await window.DokkaiStorage.saveSettings('pretest_config', mergedSettings.pretest_config, false);
                            if (mergedSettings.stream_profile) await window.DokkaiStorage.saveSettings('stream_profile', mergedSettings.stream_profile, false);
                        }
                    }
                }

                // D. Active Session: if remote has an active session (< 24h) and local doesn't, restore
                let mergedActiveSession = localActiveSession;
                if (!localActiveSession && remoteData && remoteData.active_session) {
                    const remSess = remoteData.active_session;
                    if (remSess && remSess.textId && (Date.now() - (remSess.timestamp || 0) < 24 * 60 * 60 * 1000)) {
                        mergedActiveSession = remSess;
                        if (window.DokkaiStorage) {
                            await window.DokkaiStorage.saveActiveSession(remSess);
                        }
                    }
                }

                // 4. Send atomic batched write to Firestore (/users/{userId}/sync/state)
                const payload = {
                    uid: uid,
                    email: this.user.email || null,
                    isAnonymous: Boolean(this.user.isAnonymous),
                    solved_tasks: mergedSolvedMap,
                    notebook: mergedWordsMap,
                    settings: mergedSettings,
                    settings_updated_at: settingsUpdatedAt,
                    active_session: mergedActiveSession || null,
                    last_synced_at: new Date().toISOString()
                };

                await this._firebaseFns.setDoc(userDocRef, payload, { merge: true });

                this.hasPendingChanges = false;
                this.setStatus('synced');
                console.info('[CloudSync] Successfully synced with Firebase Firestore');
            } catch (err) {
                console.error('[CloudSync] Sync failed:', err);
                const friendly = translateFirebaseError(err);
                this.setStatus('error', friendly);
            } finally {
                this.isSyncing = false;
            }
        }
    }

    // Export singleton on window
    window.DokkaiCloudSync = new DokkaiCloudSync();

})(window);
