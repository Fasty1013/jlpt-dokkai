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
 * - Debounced batch updates (15s debounce, 30s max wait, flushed on tab hide / pagehide)
 *   to preserve free read/write quotas (Step 11b)
 */

import { t } from '../i18n/index.js';
import { getEffectiveConfig, FIREBASE_CONFIG_KEY } from './config_store.js';
import { translateFirebaseError } from './auth_errors.js';
import { loadFirebaseSdk } from './sdk_loader.js';
import { mergeSolvedTasks, mergeNotebook } from './merge.js';

// Step 11b: sync only on meaningful user changes, batched.
const SYNC_DEBOUNCE_MS = 15000;      // quiet period after the last change
const SYNC_MAX_WAIT_MS = 30000;      // upper bound from the first unsynced change
const SYNCING_BADGE_DELAY_MS = 900;  // background syncs show "syncing" only if they take longer

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
        this.firstPendingAt = 0;
        this.changeSeq = 0;

        this._setupNetworkListeners();
        this._setupLifecycleFlush();
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

    /** Push pending changes right away when the tab is hidden or the page is closed. */
    _setupLifecycleFlush() {
        if (typeof document === 'undefined') return;
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') this.flushPending();
        });
        window.addEventListener('pagehide', () => this.flushPending());
    }

    flushPending() {
        if (!this.hasPendingChanges || !this.user || !navigator.onLine) return;
        clearTimeout(this.syncDebounceTimer);
        this.syncDebounceTimer = null;
        this.syncNow({ silent: true });
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
            return { text: t('cloud.offlineText'), class: 'status-offline', icon: '⚠️', tooltip: t('cloud.offlineTip') };
        }

        if (this.user) {
            switch (this.status) {
                case 'synced':
                    const userLabel = this.user.email || (this.user.isAnonymous ? t('cloud.anonProfile') : t('cloud.inCloudLabel'));
                    return {
                        text: t('cloud.inCloudText', { user: userLabel }),
                        class: 'status-synced',
                        icon: '🟢',
                        tooltip: t('cloud.syncedTip', { user: userLabel })
                    };
                case 'syncing':
                    return { text: t('cloud.syncingText'), class: 'status-syncing', icon: '🔄', tooltip: t('cloud.syncingTip') };
                case 'error':
                    return { text: t('cloud.errorText'), class: 'status-error', icon: '⚠️', tooltip: t('cloud.errorTip') };
                default:
                    return { text: t('cloud.connectedText'), class: 'status-synced', icon: '🟢', tooltip: t('cloud.connectedTip') };
            }
        }

        return { text: t('cloud.localText'), class: 'status-local', icon: '📱', tooltip: t('cloud.localTip') };
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
            const sdk = await loadFirebaseSdk(config);
            this.firebaseApp = sdk.firebaseApp;
            this.auth = sdk.auth;
            this.db = sdk.db;
            this._firebaseFns = sdk.fns;
            const { onAuthStateChanged } = sdk;

            // Check for redirect sign-in result (from mobile / popup blocked scenarios)
            try {
                const redirectResult = await this._firebaseFns.getRedirectResult(this.auth);
                if (redirectResult && redirectResult.user) {
                    console.info('[CloudSync] Redirect sign-in completed for:', redirectResult.user.email || redirectResult.user.uid);
                    this.notifyFeedback('success', t('cloud.loginOk', { user: redirectResult.user.email || t('cloud.anonProfile') }));
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
            const msg = t('cloud.noInternet');
            this.notifyFeedback('error', msg);
            throw new Error(msg);
        }

        await this._ensureInitialized();
        if (!this.auth || !this._firebaseFns) {
            const msg = t('cloud.firebaseUnavailable');
            this.notifyFeedback('error', msg);
            throw new Error(msg);
        }

        const provider = new this._firebaseFns.GoogleAuthProvider();
        provider.setCustomParameters({ prompt: 'select_account' });

        // Case A: User is currently anonymous -> upgrade account to Google (link)
        if (this.user && this.user.isAnonymous) {
            try {
                const cred = await this._firebaseFns.linkWithPopup(this.user, provider);
                this.notifyFeedback('success', t('cloud.linkedGoogle', { user: cred.user.email }));
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
                        this.notifyFeedback('info', t('cloud.merging', { user: res.user.email }));
                        await this.syncNow();
                        return res.user;
                    }
                } else if (linkErr.code === 'auth/popup-blocked') {
                    this.notifyFeedback('warning', t('cloud.popupBlockedRedirect'));
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
            this.notifyFeedback('success', t('cloud.signedIn', { user: result.user.email }));
            return result.user;
        } catch (err) {
            if (err.code === 'auth/popup-blocked' || err.code === 'auth/cancelled-popup-request') {
                this.notifyFeedback('warning', t('cloud.popupBlockedRedirect2'));
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
            const msg = t('cloud.noInternet');
            this.notifyFeedback('error', msg);
            throw new Error(msg);
        }

        await this._ensureInitialized();
        if (!this.auth || !this._firebaseFns) {
            const msg = t('cloud.firebaseUnavailable');
            this.notifyFeedback('error', msg);
            throw new Error(msg);
        }

        try {
            const result = await this._firebaseFns.signInAnonymously(this.auth);
            this.notifyFeedback('success', t('cloud.anonCreated', { id: result.user.uid.slice(0, 8) }));
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
                this.notifyFeedback('info', t('cloud.signedOut'));
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
        this.changeSeq++;
        if (!this.firstPendingAt) this.firstPendingAt = Date.now();
        if (!this.user || !navigator.onLine) {
            return;
        }

        const waitLeft = Math.max(0, this.firstPendingAt + SYNC_MAX_WAIT_MS - Date.now());
        const delay = Math.min(SYNC_DEBOUNCE_MS, waitLeft);
        clearTimeout(this.syncDebounceTimer);
        this.syncDebounceTimer = setTimeout(() => {
            this.syncDebounceTimer = null;
            this.syncNow({ silent: true });
        }, delay);
    }

    /**
     * Perform atomic lossless two-way union sync between IndexedDB and Cloud Firestore.
     * Target Document: users/{userId}/sync/state (strictly matches Firestore rules)
     */
    async syncNow({ silent = false } = {}) {
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
        const seqAtStart = this.changeSeq;
        // Background (debounced) syncs do not flash the status badge unless they are slow
        let badgeTimer = null;
        if (silent) {
            badgeTimer = setTimeout(() => this.setStatus('syncing'), SYNCING_BADGE_DELAY_MS);
        } else {
            this.setStatus('syncing');
        }

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
        const mergedSolvedMap = mergeSolvedTasks(remoteData, localSolved);

            // Write merged tasks back into local IndexedDB
            if (window.DokkaiStorage) {
                for (const t of Object.values(mergedSolvedMap)) {
                    await window.DokkaiStorage.recordSolvedTask(t, false); // no echo: writing merged data back must not schedule another sync
                }
            }

        const mergedWordsMap = mergeNotebook(remoteData, localWords);

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

            clearTimeout(badgeTimer);
            if (seqAtStart === this.changeSeq) {
                this.hasPendingChanges = false;
                this.firstPendingAt = 0;
            } else {
                // New changes arrived while this sync was running: batch them in the next one
                this.firstPendingAt = Date.now();
                this.scheduleAutoSync();
            }
            this.setStatus('synced');
            console.info('[CloudSync] Successfully synced with Firebase Firestore');
        } catch (err) {
            clearTimeout(badgeTimer);
            console.error('[CloudSync] Sync failed:', err);
            const friendly = translateFirebaseError(err);
            this.setStatus('error', friendly);
        } finally {
            this.isSyncing = false;
        }
    }
}

// Single shared instance + window alias kept for classic consumers, tests and DevTools.
export const dokkaiCloudSync = new DokkaiCloudSync();
window.DokkaiCloudSync = dokkaiCloudSync;
