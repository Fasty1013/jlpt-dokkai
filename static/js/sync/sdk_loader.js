/** Firebase Modular SDK loader (Google CDN, 7s timeout) (Step 7c-2). */

import { FIREBASE_SDK_VERSION } from './config_store.js';

export async function loadFirebaseSdk(config) {
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

    const firebaseApp = initializeApp(config);
    const auth = getAuth(firebaseApp);
    const db = getFirestore(firebaseApp);

    const fns = {
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

    return { firebaseApp, auth, db, fns, onAuthStateChanged };
}
