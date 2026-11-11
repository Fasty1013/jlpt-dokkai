/** Human-readable (ru) translation of Firebase Auth/Firestore errors (Step 7c-2). */

import { t } from '../i18n/index.js';

export function translateFirebaseError(err) {
    if (!err) return t('auth.unknown');
    const code = err.code || '';
    const msg = err.message || '';

    switch (code) {
        case 'auth/popup-blocked':
            return t('auth.popupBlocked');
        case 'auth/popup-closed-by-user':
            return t('auth.popupClosed');
        case 'auth/cancelled-popup-request':
            return t('auth.popupCancelled');
        case 'auth/unauthorized-domain':
            return t('auth.domainUnauthorized');
        case 'auth/network-request-failed':
            return t('auth.offlineSaved');
        case 'auth/credential-already-in-use':
            return t('auth.credentialInUse');
        case 'permission-denied':
            return t('auth.permissionDenied');
        case 'auth/user-disabled':
            return t('auth.userDisabled');
        case 'auth/operation-not-allowed':
            return t('auth.operationNotAllowed');
        default:
            if (msg.includes('network') || msg.includes('Failed to fetch')) {
                return t('auth.networkSaved');
            }
            return msg || t('auth.syncError');
    }
}
