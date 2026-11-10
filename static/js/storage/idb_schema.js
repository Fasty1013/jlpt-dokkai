/** IndexedDB schema (object stores and indexes) for dokkai_master_db v1 (Step 7c). */

export function upgradeSchema(db) {
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
}
