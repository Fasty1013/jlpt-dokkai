/** Storage constants (Step 7c). Names and keys are frozen: they define the on-disk format. */

export const DB_NAME = 'dokkai_master_db';
export const DB_VERSION = 1;

// Legacy localStorage keys for seamless 1-click migration
export const LEGACY_KEYS = {
    WORDS: 'dokkai_saved_words',
    CONFIG: 'dokkai_pretest_config',
    USER_ID: 'dokkai_user_id'
};
