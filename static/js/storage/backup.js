/** Full JSON export / import of local data (Step 7c). Payload format is frozen (schema_version 1). */

import { LEGACY_KEYS } from './constants.js';

export async function exportAllData(storage) {
    const solved = await storage.getSolvedTasks();
    const words = await storage.getAllWords();
    const userSettings = await storage.getSettings('user_settings', {});
    const pretestConfig = await storage.getSettings('pretest_config', {});
    const streamProfile = await storage.getSettings('stream_profile', {});

    const exportPayload = {
        app: 'Dokkai Master',
        schema_version: 1,
        exported_at: new Date().toISOString(),
        user_id: localStorage.getItem(LEGACY_KEYS.USER_ID) || 'anonymous',
        data: {
            solved_tasks: solved,
            notebook: words,
            settings: {
                user_settings: userSettings,
                pretest_config: pretestConfig,
                stream_profile: streamProfile
            }
        }
    };

    return JSON.stringify(exportPayload, null, 2);
}

export async function importAllData(storage, jsonString) {
    try {
        const parsed = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
        if (!parsed || !parsed.data) {
            throw new Error('Некорректный формат файла бэкапа');
        }

        const data = parsed.data;

        // 1. Import solved tasks
        if (Array.isArray(data.solved_tasks)) {
            for (const task of data.solved_tasks) {
                if (task && task.text_id) {
                    await storage.recordSolvedTask(task);
                }
            }
        }

        // 2. Import notebook words
        if (Array.isArray(data.notebook)) {
            for (const w of data.notebook) {
                if (w && w.word) {
                    await storage.saveWord(w, false);
                }
            }
        }

        // 3. Import settings
        if (data.settings) {
            if (data.settings.user_settings) {
                await storage.saveSettings('user_settings', data.settings.user_settings, false);
            }
            if (data.settings.pretest_config) {
                await storage.saveSettings('pretest_config', data.settings.pretest_config, false);
            }
            if (data.settings.stream_profile) {
                await storage.saveSettings('stream_profile', data.settings.stream_profile, false);
            }
        }

        storage._notifyMutation('import_complete', { count: (data.solved_tasks || []).length });
        return {
            success: true,
            solvedCount: (data.solved_tasks || []).length,
            wordsCount: (data.notebook || []).length
        };
    } catch (err) {
        console.error('[DokkaiStorage] Import failed:', err);
        return { success: false, error: err.message };
    }
}
