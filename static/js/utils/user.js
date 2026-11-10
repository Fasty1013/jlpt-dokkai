/**
 * JLPT Dokkai Master - User Identification Utilities
 * Preserves exact legacy storage key ('dokkai_user_id') and ID format
 */

import { STORAGE_KEYS } from '../constants/settings.js';

export function getUserId() {
    let uid = localStorage.getItem(STORAGE_KEYS.USER_ID);
    if (!uid) {
        uid = 'user-' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
        localStorage.setItem(STORAGE_KEYS.USER_ID, uid);
    }
    return uid;
}
