/** Effective Firebase config resolution: localStorage override, then window.DOKKAI_FIREBASE_CONFIG (Step 7c-2). */

export const FIREBASE_SDK_VERSION = '10.13.0';
export const FIREBASE_CONFIG_KEY = 'dokkai_firebase_config';

export function getEffectiveConfig() {
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
