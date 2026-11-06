/**
 * JLPT Dokkai Master - Cloud Sync & Backup Modal UI
 * Handles presentation and user interaction for Cloud Sync & Backup.
 * Note: Pure data storage and sync logic are encapsulated in DokkaiStorage and DokkaiCloudSync.
 */

function getElements() {
    return (typeof window !== 'undefined' && window.elements) ? window.elements : {};
}

/**
 * Display an inline notification within the sync modal.
 * @param {'info' | 'success' | 'error' | 'warning'} type 
 * @param {string} message 
 */
export function showSyncModalAlert(type, message) {
    const els = getElements();
    if (!els.syncModalAlert) return;
    els.syncModalAlert.className = `sync-modal-alert alert-${type}`;
    els.syncModalAlert.textContent = message;
    els.syncModalAlert.classList.remove('hidden');

    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            if (els.syncModalAlert) els.syncModalAlert.classList.add('hidden');
        }, 5000);
    }
}

/**
 * Open the Cloud Sync & Backup modal dialog.
 */
export function openSyncModal() {
    const els = getElements();
    if (els.syncModalBackdrop) {
        els.syncModalBackdrop.classList.remove('hidden');
        if (els.syncModalAlert) els.syncModalAlert.classList.add('hidden');
        if (window.DokkaiCloudSync && els.firebaseConfigInput) {
            const cfg = window.DokkaiCloudSync.getStoredConfig();
            if (cfg) els.firebaseConfigInput.value = JSON.stringify(cfg, null, 2);
        }
    }
}

/**
 * Close the Cloud Sync & Backup modal dialog.
 */
export function closeSyncModal() {
    const els = getElements();
    if (els.syncModalBackdrop) {
        els.syncModalBackdrop.classList.add('hidden');
    }
}

/**
 * Update sync status indicators across the header and inside the modal.
 * @param {string} [status]
 * @param {string} [extraInfo]
 */
export function updateSyncStatusUI(status, extraInfo) {
    const els = getElements();
    if (!els.headerSyncDot || !els.headerSyncLabel) return;
    const info = window.DokkaiCloudSync ? window.DokkaiCloudSync.getStatusInfo() : { text: 'На устройстве', class: 'status-local', icon: '📱' };

    els.headerSyncDot.className = `sync-dot ${info.class}`;
    els.headerSyncLabel.textContent = `${info.icon} ${info.text}`;

    if (els.modalSyncDot) {
        els.modalSyncDot.className = `sync-dot ${info.class}`;
    }
    if (els.modalSyncTitle) {
        els.modalSyncTitle.textContent = info.text;
    }
    if (els.modalSyncDesc) {
        if (info.class === 'status-synced') {
            els.modalSyncDesc.textContent = 'Все решённые задания, личный словарь и настройки синхронизированы с Google Firebase ($0 бесплатно).';
        } else if (info.class === 'status-syncing') {
            els.modalSyncDesc.textContent = 'Идёт синхронизация данных с облаком...';
        } else if (info.class === 'status-offline') {
            els.modalSyncDesc.textContent = 'Сеть недоступна. Все данные сохраняются на вашем устройстве (IndexedDB) и синхронизируются при включении интернета.';
        } else if (info.class === 'status-error') {
            els.modalSyncDesc.textContent = extraInfo ? `Ошибка синхронизации: ${extraInfo}` : 'Ошибка соединения с облаком. Данные надёжно сохранены на устройстве.';
        } else {
            els.modalSyncDesc.textContent = 'Все данные надёжно сохраняются на этом устройстве (IndexedDB). Они не пропадут при закрытии вкладки или перезапуске сервера Render.';
        }
    }
}

/**
 * Update authenticated user info / buttons inside the sync modal.
 * @param {any} user
 */
export function updateSyncUserUI(user) {
    const els = getElements();
    if (!els.syncUserInfo || !els.syncAuthActions) return;
    if (user) {
        els.syncUserInfo.classList.remove('hidden');
        if (user.isAnonymous) {
            // Keep Google auth button visible so anonymous user can upgrade account
            els.syncAuthActions.classList.remove('hidden');
            if (els.btnCloudSigninAnon) els.btnCloudSigninAnon.classList.add('hidden');
            if (els.syncLinkGoogleHint) els.syncLinkGoogleHint.classList.remove('hidden');
            if (els.syncUserName) els.syncUserName.textContent = 'Анонимный профиль';
            if (els.syncUserEmail) els.syncUserEmail.textContent = 'Облачный ID: ' + (user.uid ? user.uid.slice(0, 10) : '');
        } else {
            els.syncAuthActions.classList.add('hidden');
            if (els.syncLinkGoogleHint) els.syncLinkGoogleHint.classList.add('hidden');
            if (els.syncUserName) els.syncUserName.textContent = user.displayName || 'Пользователь Google';
            if (els.syncUserEmail) els.syncUserEmail.textContent = user.email || '';
        }
    } else {
        els.syncUserInfo.classList.add('hidden');
        els.syncAuthActions.classList.remove('hidden');
        if (els.btnCloudSigninAnon) els.btnCloudSigninAnon.classList.remove('hidden');
        if (els.syncLinkGoogleHint) els.syncLinkGoogleHint.classList.add('hidden');
    }
}

/**
 * Export full local progress data (settings, solved tasks, notebook words) as a JSON file.
 */
export async function exportProgressJson() {
    if (!window.DokkaiStorage) return;
    try {
        const jsonStr = await window.DokkaiStorage.exportAllData();
        const dateStr = new Date().toISOString().slice(0, 10);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dokkai_master_progress_${dateStr}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (e) {
        console.error('Export failed', e);
        showSyncModalAlert('error', 'Не удалось экспортировать файл: ' + e.message);
    }
}

/**
 * Import a backup JSON file and merge into local IndexedDB.
 * @param {File} file
 */
export async function handleImportJsonFile(file) {
    if (!file || !window.DokkaiStorage) return;
    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target.result;
            const res = await window.DokkaiStorage.importAllData(content);
            if (res.success) {
                showSyncModalAlert('success', `Успешно импортировано: ${res.solvedCount} решённых заданий, ${res.wordsCount} слов в словаре!`);
                if (window.state) {
                    window.state.savedWords = await window.DokkaiStorage.getAllWords();
                }
                if (window.updateNotebookBadge) window.updateNotebookBadge();
                if (window.renderNotebookWords) window.renderNotebookWords();
                if (window.fetchAndRenderSolvedTasks) window.fetchAndRenderSolvedTasks();
                if (window.DokkaiCloudSync) window.DokkaiCloudSync.scheduleAutoSync();
            } else {
                showSyncModalAlert('error', 'Ошибка при импорте файла: ' + (res.error || 'неверный формат'));
            }
        };
        reader.readAsText(file);
    } catch (err) {
        console.error('Import error', err);
        showSyncModalAlert('error', 'Ошибка чтения файла: ' + err.message);
    }
}

/**
 * Initialize event handlers for Sync Modal dialog and Cloud Auth triggers.
 */
export function initSyncModalUI() {
    const els = getElements();

    if (els.btnSyncStatus) {
        els.btnSyncStatus.addEventListener('click', openSyncModal);
    }
    if (els.btnCloseSyncModal) {
        els.btnCloseSyncModal.addEventListener('click', closeSyncModal);
    }
    if (els.btnSyncModalDone) {
        els.btnSyncModalDone.addEventListener('click', closeSyncModal);
    }
    if (els.syncModalBackdrop) {
        els.syncModalBackdrop.addEventListener('click', (e) => {
            if (e.target === els.syncModalBackdrop) closeSyncModal();
        });
    }

    if (els.btnCloudSigninGoogle) {
        els.btnCloudSigninGoogle.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            try {
                showSyncModalAlert('info', 'Подключение к Google...');
                await window.DokkaiCloudSync.signInGoogle();
            } catch (err) {
                showSyncModalAlert('error', err.message);
            }
        });
    }
    if (els.btnCloudSigninAnon) {
        els.btnCloudSigninAnon.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            try {
                showSyncModalAlert('info', 'Создание анонимного облачного профиля...');
                await window.DokkaiCloudSync.signInAnonymous();
            } catch (err) {
                showSyncModalAlert('error', err.message);
            }
        });
    }
    if (els.btnCloudSignout) {
        els.btnCloudSignout.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            await window.DokkaiCloudSync.signOut();
            showSyncModalAlert('info', 'Вы вышли из облачного аккаунта. Локальные данные сохранены.');
        });
    }

    if (els.btnSaveFirebaseConfig) {
        els.btnSaveFirebaseConfig.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync || !els.firebaseConfigInput) return;
            try {
                const parsed = JSON.parse(els.firebaseConfigInput.value.trim());
                const res = await window.DokkaiCloudSync.saveFirebaseConfig(parsed);
                if (res.success) {
                    showSyncModalAlert('success', 'Конфигурация Firebase успешно сохранена!');
                } else {
                    showSyncModalAlert('error', 'Ошибка подключения: ' + res.error);
                }
            } catch (e) {
                showSyncModalAlert('error', 'Пожалуйста, вставьте корректный JSON объект конфигурации Firebase.');
            }
        });
    }
    if (els.btnClearFirebaseConfig) {
        els.btnClearFirebaseConfig.addEventListener('click', () => {
            if (!window.DokkaiCloudSync) return;
            window.DokkaiCloudSync.clearFirebaseConfig();
            if (els.firebaseConfigInput) els.firebaseConfigInput.value = '';
            showSyncModalAlert('info', 'Конфигурация сброшена к настройкам по умолчанию.');
        });
    }

    if (els.modalBtnExport) {
        els.modalBtnExport.addEventListener('click', exportProgressJson);
    }
    if (els.btnExportBackup) {
        els.btnExportBackup.addEventListener('click', exportProgressJson);
    }
    if (els.modalBtnImportTrigger) {
        els.modalBtnImportTrigger.addEventListener('click', () => {
            if (els.inputImportBackupFile) els.inputImportBackupFile.click();
        });
    }
    if (els.btnImportBackupTrigger) {
        els.btnImportBackupTrigger.addEventListener('click', () => {
            if (els.inputImportBackupFile) els.inputImportBackupFile.click();
        });
    }
    if (els.inputImportBackupFile) {
        els.inputImportBackupFile.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleImportJsonFile(e.target.files[0]);
                e.target.value = '';
            }
        });
    }
}
