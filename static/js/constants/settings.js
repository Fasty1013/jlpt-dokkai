/**
 * JLPT Dokkai Master - Core Settings & Storage Keys Constants
 */

export const STORAGE_KEYS = {
    USER_ID: 'dokkai_user_id',
    SAVED_WORDS: 'dokkai_saved_words',
    PRETEST_CONFIG: 'dokkai_pretest_config',
    FIREBASE_CONFIG: 'dokkai_firebase_config',
    IDB_MIGRATED_V1: 'dokkai_idb_migrated_v1'
};

export const READER_SETTINGS = {
    MIN_FONT_SIZE_PX: 16,
    MAX_FONT_SIZE_PX: 28,
    DEFAULT_FONT_SIZE_PX: 20,
    FONT_STEP_PX: 2,
    DEFAULT_FONT_FAMILY: 'gothic'
};

export const TIMER_SETTINGS = {
    DEFAULT_TIMER_SECONDS: 180,
    ONE_MINUTE_SECONDS: 60,
    TIMER_TICK_MS: 1000
};

export const SYNC_SETTINGS = {
    SYNC_DEBOUNCE_MS: 1500,
    STARTUP_TIMEOUT_MS: 2000,
    FIREBASE_INIT_TIMEOUT_MS: 7000,
    MAX_SESSION_AGE_MS: 24 * 60 * 60 * 1000 // 24 hours
};
