/**
 * JLPT Dokkai Master - Frontend Application Logic (Vanilla JS ES6+)
 * Supports Step-by-Step Question Wizard & Tabbed Post-Submit Analysis
 */

// ============================================================================
// Application State & LocalStorage Configuration
// ============================================================================

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

const CONFIG_STORAGE_KEY = 'dokkai_pretest_config';

function loadStoredConfig() {
    try {
        const stored = localStorage.getItem(CONFIG_STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
    } catch (e) {
        console.warn('Failed to load pretest config from localStorage', e);
    }
    return {
        showFurigana: true,
        showHintsAndAnalysis: true,
        enableTimer: false,
        timerMinutes: 3
    };
}

function saveStoredConfig(config) {
    try {
        localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(config));
    } catch (e) {
        console.warn('Failed to save pretest config to localStorage', e);
    }
}

function getUserId() {
    let uid = localStorage.getItem('dokkai_user_id');
    if (!uid) {
        uid = 'user-' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
        localStorage.setItem('dokkai_user_id', uid);
    }
    return uid;
}

const state = {
    currentView: 'catalog', // 'catalog' | 'exercise' | 'notebook'
    activeTab: 'catalog',   // 'catalog' | 'notebook'
    filters: {
        level: '',
        category: '',
        source: '' // '' | 'nhk' | 'exam'
    },
    // Stream State
    streamProfile: {
        level: 'N5',
        category: 'short',
        solvedWhen: 'all_questions_answered'
    },
    cachedSlots: [],
    cachedSolved: [],
    solvedFilter: 'all',
    reportingTextId: null,
    isRetryMode: false,

    activeText: null,        // Loaded TextReadSchema or TextAnalysisSchema
    pendingTextId: null,     // Selected text awaiting modal confirmation
    pendingTextData: null,

    // Step-by-Step Wizard State
    currentQuestionIndex: 0, // 0-based index of the active question
    userAnswers: {},         // questionId -> selectedOptionId

    timer: {
        enabled: false,
        totalSeconds: 180,
        remainingSeconds: 180,
        secondsSpent: 0,
        intervalId: null,
        isPaused: false
    },
    // Pre-test configuration
    pretestConfig: loadStoredConfig(),
    // Runtime UI settings
    settings: {
        furiganaVisible: true,
        evidenceVisible: true,
        fontFamily: 'gothic',  // 'gothic' | 'mincho'
        fontSizePx: 20         // default 20px
    },
    // Analysis tab state
    analysisActiveTabIdx: 0,
    // Interactive Dictionary & Notebook State
    popupDictEnabled: true,
    activePopupWord: null,
    savedWords: [],
    notebookFilter: 'all', // 'all' | 'learning' | 'learned'
    notebookSearchQuery: '',
    // Active session for auto-resume
    activeSession: null
};

// ============================================================================
// DOM Elements Cache
// ============================================================================

const elements = {
    // Top Bar & Navigation Tabs
    btnHome: document.getElementById('btn-home'),
    headerNav: document.getElementById('header-nav'),
    btnTabCatalog: document.getElementById('btn-tab-catalog'),
    btnTabNotebook: document.getElementById('btn-tab-notebook'),
    btnTabImport: document.getElementById('btn-tab-import'),
    exerciseHeaderControls: document.getElementById('exercise-header-controls'),
    headerLevelTag: document.getElementById('header-level-tag'),
    headerCategoryTag: document.getElementById('header-category-tag'),
    headerExamBadge: document.getElementById('header-exam-badge'),
    btnAbortExercise: document.getElementById('btn-abort-exercise'),
    headerSavedCount: document.getElementById('header-saved-count'),
    headerDraftsCount: document.getElementById('header-drafts-count'),

    // Timer Elements in Header
    timerBox: document.getElementById('timer-box'),
    timerDisplay: document.getElementById('timer-display'),
    timerDot: document.getElementById('timer-dot'),
    btnTimerTogglePause: document.getElementById('btn-timer-toggle-pause'),
    btnTimerAddMin: document.getElementById('btn-timer-add-min'),
    btnTimerDismiss: document.getElementById('btn-timer-dismiss'),
    btnEnableTimerRuntime: document.getElementById('btn-enable-timer-runtime'),
    timerAlertBanner: document.getElementById('timer-alert-banner'),
    btnDismissTimerAlert: document.getElementById('btn-dismiss-timer-alert'),

    // Views
    catalogView: document.getElementById('catalog-view'),
    exerciseView: document.getElementById('exercise-view'),
    notebookView: document.getElementById('notebook-view'),
    importView: document.getElementById('import-view'),

    // PDF Import Elements
    formPdfUpload: document.getElementById('form-pdf-upload'),
    pdfDropzone: document.getElementById('pdf-dropzone'),
    pdfFileInput: document.getElementById('pdf-file-input'),
    dropzonePrompt: document.getElementById('dropzone-prompt'),
    dropzoneFileInfo: document.getElementById('dropzone-file-info'),
    dropzoneFileName: document.getElementById('dropzone-file-name'),
    dropzoneFileSize: document.getElementById('dropzone-file-size'),
    btnClearFile: document.getElementById('btn-clear-file'),
    importLevel: document.getElementById('import-level'),
    importCategory: document.getElementById('import-category'),
    importTitleOverride: document.getElementById('import-title-override'),
    btnStartUpload: document.getElementById('btn-start-upload'),
    uploadLoadingSpinner: document.getElementById('upload-loading-spinner'),
    uploadStatusText: document.getElementById('upload-status-text'),
    stagingDraftsList: document.getElementById('staging-drafts-list'),
    draftsCount: document.getElementById('drafts-count'),
    btnRefreshDrafts: document.getElementById('btn-refresh-drafts'),

    // Continuous Stream Elements
    activeSlotsList: document.getElementById('active-slots-list'),
    solvedTasksList: document.getElementById('solved-tasks-list'),
    streamLevelPills: document.getElementById('stream-level-pills'),
    streamCategoryPills: document.getElementById('stream-category-pills'),
    streamModePills: document.getElementById('stream-mode-pills'),
    btnRefreshSlots: document.getElementById('btn-refresh-slots'),
    solvedFilterPills: document.getElementById('solved-filter-pills'),
    solvedArchiveTotal: document.getElementById('solved-archive-total'),
    mobileActiveCount: document.getElementById('mobile-active-count'),
    mobileSolvedCount: document.getElementById('mobile-solved-count'),
    streamMobileTabs: document.getElementById('stream-mobile-tabs'),
    tabColActive: document.getElementById('tab-col-active'),
    tabColSolved: document.getElementById('tab-col-solved'),
    colActiveSlots: document.getElementById('col-active-slots'),
    colSolvedArchive: document.getElementById('col-solved-archive'),

    // Report Defect Modal Elements
    reportModalBackdrop: document.getElementById('report-modal-backdrop'),
    reportModalTaskTitle: document.getElementById('report-modal-task-title'),
    btnCloseReportModal: document.getElementById('btn-close-report-modal'),
    btnCancelReport: document.getElementById('btn-cancel-report'),
    btnSubmitReport: document.getElementById('btn-submit-report'),
    reportReasonSelect: document.getElementById('report-reason-select'),
    reportDetailsTextarea: document.getElementById('report-details-textarea'),

    // Catalog Legacy Fallback (if needed)
    catalogGrid: document.getElementById('catalog-grid'),
    levelPills: document.getElementById('level-filter-pills'),
    categoryPills: document.getElementById('category-filter-pills'),
    sourcePills: document.getElementById('source-filter-pills'),

    // Exercise Left Pane (Passage & Reader tools)
    passageTitle: document.getElementById('passage-title'),
    passageLevel: document.getElementById('passage-level'),
    passageCategory: document.getElementById('passage-category'),
    passageExamBadge: document.getElementById('passage-exam-badge'),
    passageTime: document.getElementById('passage-time'),
    passageContent: document.getElementById('passage-content'),
    btnFontGothic: document.getElementById('btn-font-gothic'),
    btnFontMincho: document.getElementById('btn-font-mincho'),
    btnFontIncrease: document.getElementById('btn-font-increase'),
    btnFontDecrease: document.getElementById('btn-font-decrease'),
    btnTogglePopupDict: document.getElementById('btn-toggle-popup-dict'),
    popupDictStatus: document.getElementById('popup-dict-status'),

    // Yomichan Floating Card
    popupDictionaryCard: document.getElementById('popup-dictionary-card'),
    popupWord: document.getElementById('popup-word'),
    popupReading: document.getElementById('popup-reading'),
    popupLevel: document.getElementById('popup-level'),
    popupMeaning: document.getElementById('popup-meaning'),
    popupBtnAudio: document.getElementById('popup-btn-audio'),
    popupBtnClose: document.getElementById('popup-btn-close'),
    popupBtnSave: document.getElementById('popup-btn-save'),
    popupBtnSaveText: document.getElementById('popup-btn-save-text'),

    // Notebook Modal
    savedWordsModalBackdrop: document.getElementById('saved-words-modal-backdrop'),
    btnCloseNotebook: document.getElementById('btn-close-notebook'),
    notebookSearchInput: document.getElementById('notebook-search-input'),
    notebookWordsList: document.getElementById('notebook-words-list'),
    notebookCountAll: document.getElementById('notebook-count-all'),
    notebookCountLearning: document.getElementById('notebook-count-learning'),
    notebookCountLearned: document.getElementById('notebook-count-learned'),
    notebookStatsText: document.getElementById('notebook-stats-text'),
    btnClearNotebook: document.getElementById('btn-clear-notebook'),

    // Wizard Controls (Right Pane)
    wizardHeader: document.getElementById('wizard-header'),
    wizardStepLabel: document.getElementById('wizard-step-label'),
    wizardTrack: document.getElementById('wizard-track'),
    answeredCount: document.getElementById('answered-count'),
    totalQuestionsCount: document.getElementById('total-questions-count'),
    wizardCardArea: document.getElementById('wizard-card-area'),
    wizardNavBar: document.getElementById('wizard-nav-bar'),
    btnWizardPrev: document.getElementById('btn-wizard-prev'),
    btnWizardNext: document.getElementById('btn-wizard-next'),
    btnWizardSubmit: document.getElementById('btn-wizard-submit'),

    // Analysis Post-Submit Tabbed View
    analysisBanner: document.getElementById('analysis-banner'),
    scoreText: document.getElementById('score-text'),
    scorePercent: document.getElementById('score-percent'),
    bannerResultTitle: document.getElementById('banner-result-title'),
    bannerResultMeta: document.getElementById('banner-result-meta'),
    studyToolsBar: document.getElementById('study-tools-bar'),
    hardcoreNotice: document.getElementById('hardcore-notice'),
    btnToggleFurigana: document.getElementById('btn-toggle-furigana'),
    furiganaStatus: document.getElementById('furigana-status'),
    btnToggleEvidence: document.getElementById('btn-toggle-evidence'),
    evidenceStatus: document.getElementById('evidence-status'),
    btnToggleTranslation: document.getElementById('btn-toggle-translation'),
    btnToggleVocab: document.getElementById('btn-toggle-vocab'),
    vocabCountBadge: document.getElementById('vocab-count-badge'),
    btnBackToCatalog: document.getElementById('btn-back-to-catalog'),
    analysisQAContainer: document.getElementById('analysis-qa-container'),
    analysisTabs: document.getElementById('analysis-tabs'),
    analysisActiveCard: document.getElementById('analysis-active-card'),

    // Supplementary Drawer
    supplementaryDrawer: document.getElementById('supplementary-drawer'),
    drawerTitle: document.getElementById('drawer-title'),
    btnCloseDrawer: document.getElementById('btn-close-drawer'),
    translationText: document.getElementById('translation-text'),
    vocabList: document.getElementById('vocab-list'),

    // Pre-test Modal
    pretestModalBackdrop: document.getElementById('pretest-modal-backdrop'),
    modalBody: document.querySelector('#pretest-modal-backdrop .modal-body'),
    modalTextTitle: document.getElementById('modal-text-title'),
    modalTimeEstimate: document.getElementById('modal-time-estimate'),
    pretestToggleFurigana: document.getElementById('pretest-toggle-furigana'),
    pretestToggleHints: document.getElementById('pretest-toggle-hints'),
    pretestToggleTimer: document.getElementById('pretest-toggle-timer'),
    timerDurationSelector: document.getElementById('timer-duration-selector'),
    modalTimerMinutes: document.getElementById('modal-timer-minutes'),
    btnTimerMinus: document.getElementById('btn-timer-minus'),
    btnTimerPlus: document.getElementById('btn-timer-plus'),
    tagFurigana: document.getElementById('tag-furigana'),
    tagHints: document.getElementById('tag-hints'),
    tagTimer: document.getElementById('tag-timer'),
    modalBtnCancel: document.getElementById('modal-btn-cancel'),
    modalBtnClose: document.getElementById('modal-btn-close'),
    modalBtnStart: document.getElementById('modal-btn-start'),

    // Sync Status & Unfinished Test Banner
    btnSyncStatus: document.getElementById('btn-sync-status'),
    headerSyncDot: document.getElementById('header-sync-dot'),
    headerSyncLabel: document.getElementById('header-sync-label'),
    unfinishedTestBanner: document.getElementById('unfinished-test-banner'),
    unfinishedTaskTitle: document.getElementById('unfinished-task-title'),
    unfinishedTaskMeta: document.getElementById('unfinished-task-meta'),
    btnResumeUnfinished: document.getElementById('btn-resume-unfinished'),
    btnDismissUnfinished: document.getElementById('btn-dismiss-unfinished'),

    // Cloud Sync Modal
    syncModalBackdrop: document.getElementById('sync-modal-backdrop'),
    syncModalAlert: document.getElementById('sync-modal-alert'),
    btnCloseSyncModal: document.getElementById('btn-close-sync-modal'),
    btnSyncModalDone: document.getElementById('btn-sync-modal-done'),
    modalSyncDot: document.getElementById('modal-sync-dot'),
    modalSyncTitle: document.getElementById('modal-sync-title'),
    modalSyncDesc: document.getElementById('modal-sync-desc'),
    syncUserInfo: document.getElementById('sync-user-info'),
    syncUserAvatar: document.getElementById('sync-user-avatar'),
    syncUserName: document.getElementById('sync-user-name'),
    syncUserEmail: document.getElementById('sync-user-email'),
    syncLinkGoogleHint: document.getElementById('sync-link-google-hint'),
    btnCloudSignout: document.getElementById('btn-cloud-signout'),
    syncAuthActions: document.getElementById('sync-auth-actions'),
    btnCloudSigninGoogle: document.getElementById('btn-cloud-signin-google'),
    btnCloudSigninAnon: document.getElementById('btn-cloud-signin-anon'),
    modalBtnExport: document.getElementById('modal-btn-export'),
    modalBtnImportTrigger: document.getElementById('modal-btn-import-trigger'),
    firebaseConfigInput: document.getElementById('firebase-config-input'),
    btnSaveFirebaseConfig: document.getElementById('btn-save-firebase-config'),
    btnClearFirebaseConfig: document.getElementById('btn-clear-firebase-config'),

    // Notebook Backup
    btnExportBackup: document.getElementById('btn-export-backup'),
    btnImportBackupTrigger: document.getElementById('btn-import-backup-trigger'),
    inputImportBackupFile: document.getElementById('input-import-backup-file')
};

if (typeof window !== 'undefined') {
    window.state = state;
    window.elements = elements;
}

// ============================================================================
// Translations & Label Helpers
// ============================================================================

const TRAP_LABELS = {
    'overgeneralization': 'Ловушка: Чрезмерное обобщение (言い過ぎ)',
    'opposite_meaning': 'Ловушка: Противоположный смысл (正反対)',
    'not_mentioned': 'Ловушка: В тексте не сказано (言及なし)',
    'partial_match': 'Ловушка: Частичное совпадение (部分一致の罠)',
    'extreme_condition': 'Ловушка: Ложное категорическое условие (極端な限定)',
    'subject_swap': 'Ловушка: Подмена субъекта/времени (主体のすり替え)',
    'fact_opinion_confusion': 'Ловушка: Смешение факта и мнения автора',
    'temporal_mismatch': 'Ловушка: Несоответствие времени (時間のズレ)',
    'misinterpretation': 'Ловушка: Искажение логики текста (論理の飛躍)'
};

const CATEGORY_NAMES = {
    'short': '短文 (Короткие)',
    'medium': '中文 (Средние)',
    'long': '長文 (Длинные)',
    'info_search': '情報検索 (Поиск инфо)',
    'article': '記事・論説 (Статьи)'
};

function formatTime(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// ============================================================================
// Timer Functions (Delegated to static/js/features/timer/ with fallback)
// ============================================================================

function stopTimer() {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.stopTimer(state.timer);
    } else if (state.timer.intervalId) {
        clearInterval(state.timer.intervalId);
        state.timer.intervalId = null;
    }
}

function startUntimedMode() {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.startUntimedMode(state.timer, elements);
    } else {
        stopTimer();
        state.timer.enabled = false;
        state.timer.secondsSpent = 0;
        state.timer.isPaused = false;
        if (elements.timerBox) elements.timerBox.classList.add('hidden');
        if (elements.btnEnableTimerRuntime) elements.btnEnableTimerRuntime.classList.remove('hidden');
        if (elements.timerAlertBanner) elements.timerAlertBanner.classList.add('hidden');
    }
}

function startCountdownTimer(minutes) {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.startCountdownTimer(minutes, state.timer, elements);
    }
}

function toggleTimerPause() {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.toggleTimerPause(state.timer, elements);
    }
}

function addTimerMinute() {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.addTimerMinute(state.timer, elements);
    }
}

function dismissTimer() {
    if (window.DokkaiTimer) {
        window.DokkaiTimer.dismissTimer(state.timer, elements);
    }
}

function enableTimerAtRuntime() {
    const recMin = (state.activeText && state.activeText.recommended_time_min) ? state.activeText.recommended_time_min : 3;
    if (window.DokkaiTimer) {
        window.DokkaiTimer.enableTimerAtRuntime(recMin, state.timer, elements);
    } else {
        startCountdownTimer(recMin);
    }
}

// ============================================================================
// Reader Customization (Delegated to static/js/features/settings/ with fallback)
// ============================================================================

function saveUserSettings() {
    if (window.DokkaiSettings) {
        window.DokkaiSettings.saveUserSettings(state.settings);
    } else if (window.DokkaiStorage) {
        window.DokkaiStorage.saveSettings('user_settings', state.settings);
    }
}

function setReaderFont(typeface) {
    if (window.DokkaiSettings) {
        window.DokkaiSettings.setReaderFont(typeface, state.settings, elements);
    } else {
        state.settings.fontFamily = typeface;
        if (typeface === 'mincho') {
            elements.passageContent.classList.remove('font-gothic');
            elements.passageContent.classList.add('font-mincho');
            elements.btnFontMincho.classList.add('active');
            elements.btnFontGothic.classList.remove('active');
        } else {
            elements.passageContent.classList.remove('font-mincho');
            elements.passageContent.classList.add('font-gothic');
            elements.btnFontGothic.classList.add('active');
            elements.btnFontMincho.classList.remove('active');
        }
        saveUserSettings();
    }
}

function adjustFontSize(delta) {
    if (window.DokkaiSettings) {
        return window.DokkaiSettings.adjustFontSize(delta, state.settings, elements);
    } else {
        const newSize = Math.max(16, Math.min(28, state.settings.fontSizePx + delta));
        state.settings.fontSizePx = newSize;
        elements.passageContent.style.fontSize = `${newSize}px`;
        saveUserSettings();
        return newSize;
    }
}

// ============================================================================
// ============================================================================
// Continuous Stream Loading & Rendering (Two Columns: «Задания» и «Решённые»)
// ============================================================================

let cachedCatalogTexts = [];

async function fetchAndRenderCatalog() {
    return fetchAndRenderStream();
}

async function fetchAndRenderStream() {
    await Promise.all([
        fetchAndRenderSlots(),
        fetchAndRenderSolvedTasks()
    ]);
}

async function fetchAndRenderSlots(isExplicitRefresh = false) {
    if (!elements.activeSlotsList) return;
    elements.activeSlotsList.innerHTML = '<div class="loading-spinner">Загрузка слотов заданий...</div>';

    const userId = getUserId();
    const params = new URLSearchParams({
        user_id: userId,
        level: state.streamProfile.level,
        category: state.streamProfile.category
    });

    params.append('_t', Date.now().toString());

    try {
        let data;
        if (window.DokkaiApi && window.DokkaiApi.fetchStreamSlots) {
            data = await window.DokkaiApi.fetchStreamSlots({
                userId: getUserId(),
                level: state.streamProfile.level,
                category: state.streamProfile.category,
                refresh: Boolean(isExplicitRefresh)
            });
        } else {
            const response = await fetch(`/api/stream/slots?${params.toString()}`, {
                cache: 'no-store',
                headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
            });
            if (!response.ok) throw new Error('Ошибка загрузки слотов');
            data = await response.json();
        }
        const slots = data.slots || [];
        state.cachedSlots = slots;

        // Также кешируем тексты слотов для совместимости с модалом предстартовых настроек
        cachedCatalogTexts = slots.filter(s => s.text).map(s => s.text);

        if (elements.mobileActiveCount) {
            const activeCount = slots.filter(s => s.state === 'active' && s.text).length;
            elements.mobileActiveCount.textContent = activeCount;
        }

        elements.activeSlotsList.innerHTML = slots.map(slot => {
            if (slot.state === 'placeholder' || !slot.text) {
                return `
                    <div class="stream-slot-placeholder" data-position="${slot.position}">
                        <div class="placeholder-pulse">⏳</div>
                        <div class="placeholder-title">Готовится новое задание...</div>
                        <div class="placeholder-desc">Для профиля ${escapeHtml(data.profile_key)} генерируется или подбирается оригинальный учебный материал.</div>
                    </div>
                `;
            }

            const t = slot.text;
            let originBadge = '';
            if (t.origin === 'parametric') {
                originBadge = '<span class="origin-badge-param">⚡ Параметрический</span>';
            } else if (t.origin === 'ai_generated') {
                originBadge = '<span class="origin-badge-param" style="background:#eff6ff;color:#1e40af;border-color:#bfdbfe;">🤖 ИИ-генерация</span>';
            } else if (t.category === 'nhk' || (t.title && t.title.includes('NHK'))) {
                originBadge = '<span class="nhk-badge">NHK WORLD</span>';
            } else {
                originBadge = '<span class="exam-archive-badge">📜 JLPT 過去問</span>';
            }

            return `
                <div class="stream-slot-card" data-slot-id="${slot.id}" data-text-id="${t.id}" data-position="${slot.position}" onclick="openPretestModal(${t.id})" style="cursor: pointer;">
                    <div class="slot-position-badge">Слот #${slot.position}</div>
                    <div class="slot-meta-row">
                        <span class="level-tag" data-lvl="${t.level}">${t.level}</span>
                        <span class="category-tag">${CATEGORY_NAMES[t.category] || t.category}</span>
                        ${originBadge}
                    </div>
                    <h3 class="slot-title">${escapeHtml(t.title)}</h3>
                    <div class="slot-footer">
                        <div class="slot-specs">
                            <span>⏱️ ${t.recommended_time_min} мин</span>
                            <span>❓ ${t.question_count} вопр.</span>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); openPretestModal(${t.id})">
                            Начать решение →
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error(err);
        elements.activeSlotsList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--vermilion);">
                <p>Не удалось загрузить активные задания.</p>
                <button class="btn btn-secondary btn-sm" onclick="fetchAndRenderSlots()" style="margin-top: 0.5rem;">
                    🔄 Повторить попытку
                </button>
            </div>
        `;
    }
}

async function fetchAndRenderSolvedTasks() {
    if (!elements.solvedTasksList) return;

    try {
        // 1. First retrieve local solved tasks from DokkaiStorage
    let localSolved = [];
    if (window.DokkaiStorage) {
        try {
            localSolved = await window.DokkaiStorage.getSolvedTasks(state.streamProfile.level, state.solvedFilter);
        } catch (e) {
            console.warn('[Dokkai] Failed to read local solved tasks:', e);
        }
    }

    const userId = getUserId();
    const params = new URLSearchParams({
        user_id: userId,
        level: state.streamProfile.level
    });

    if (state.solvedFilter === 'perfect') {
        params.append('only_perfect', 'true');
    } else if (state.solvedFilter === 'errors') {
        params.append('only_errors', 'true');
    }

    params.append('_t', Date.now().toString());

    let items = localSolved;

    try {
        let serverItems = [];
        if (window.DokkaiApi && window.DokkaiApi.fetchSolvedTasks) {
            const data = await window.DokkaiApi.fetchSolvedTasks({
                userId: getUserId(),
                level: state.streamProfile.level,
                filter: state.solvedFilter
            });
            serverItems = data?.items || [];
        } else {
            const response = await fetch(`/api/stream/solved?${params.toString()}`, {
                cache: 'no-store',
                headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
            });
            if (response.ok) {
                const data = await response.json();
                serverItems = data.items || [];
            }
        }
        if (window.DokkaiStorage && serverItems.length > 0) {
            for (const sTask of serverItems) {
                await window.DokkaiStorage.recordSolvedTask(sTask);
            }
            items = await window.DokkaiStorage.getSolvedTasks(state.streamProfile.level, state.solvedFilter);
        }
    } catch (err) {
        console.warn('Backend solved tasks fetch failed (using local offline storage):', err);
    }

    state.cachedSolved = items;

    if (elements.solvedArchiveTotal) {
        elements.solvedArchiveTotal.textContent = items.length;
    }
    if (elements.mobileSolvedCount) {
        elements.mobileSolvedCount.textContent = items.length;
    }

    if (items.length === 0) {
        elements.solvedTasksList.innerHTML = `
            <div class="stream-empty-solved">
                <span class="empty-icon">📖</span>
                <p>Здесь будут сохраняться решённые вами задания.</p>
                <span class="empty-hint">Выберите любое задание из левой колонки «Задания», чтобы начать!</span>
            </div>
        `;
        return;
    }

    elements.solvedTasksList.innerHTML = items.map(t => {
        const isPerfect = (t.last_score === 100 || t.score === 100 || t.perfect);
        const scoreBadgeClass = isPerfect ? 'score-perfect' : 'score-errors';
        const displayScore = (t.last_score !== undefined) ? t.last_score : (t.score !== undefined ? t.score : 0);
        const scoreBadgeText = isPerfect ? '100% ★ Идеально' : `${displayScore}% с ошибками`;
        const dateStr = t.solved_at ? new Date(t.solved_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '';

        return `
            <div class="stream-solved-card" data-text-id="${t.text_id}">
                <div class="solved-card-header">
                    <span class="solved-score-badge ${scoreBadgeClass}">${scoreBadgeText}</span>
                    <span class="solved-card-date">${dateStr}</span>
                </div>
                <h4 class="solved-card-title">${escapeHtml(t.title)}</h4>
                <div class="solved-card-actions">
                    <button class="btn-solved-action btn-review" onclick="reviewSolvedTask(${t.text_id})">
                        🔍 Обзор разбора
                    </button>
                    <button class="btn-solved-action" onclick="retrySolvedTask(${t.text_id})">
                        🔁 Пройти заново
                    </button>
                    <button class="btn-solved-action" onclick="openReportModal(${t.text_id}, '${escapeHtml(t.title)}')">
                        ⚠️ Сообщить об ошибке
                    </button>
                </div>
            </div>
        `;
    }).join('');
    } catch (err) {
        console.error(err);
        elements.solvedTasksList.innerHTML = `
            <div style="text-align: center; padding: 1.5rem; color: var(--vermilion);">
                Не удалось загрузить архив решённых заданий.
            </div>
        `;
    }
}

async function reviewSolvedTask(textId) {
    try {
        let data;
        if (window.DokkaiApi && window.DokkaiApi.fetchSolvedDetail) {
            try {
                data = await window.DokkaiApi.fetchSolvedDetail(textId, getUserId());
            } catch (err) {
                if (err.status === 403) {
                    alert('Anti-Cheat: Задание ещё не решено. Разбор ответов недоступен.');
                    return;
                }
                throw err;
            }
        } else {
            const res = await fetch(`/api/stream/solved/${textId}?user_id=${getUserId()}`);
            if (res.status === 403) {
                alert('Anti-Cheat: Задание ещё не решено. Разбор ответов недоступен.');
                return;
            }
            if (!res.ok) throw new Error('Ошибка загрузки разбора');
            data = await res.json();
        }
        state.activeText = data;
        state.currentView = 'analysis';
        state.analysisActiveTabIdx = 0;
        history.pushState({ view: 'analysis', textId: textId }, '', '#analysis');
        renderAnalysisView(data);
    } catch (e) {
        console.error(e);
        alert('Не удалось загрузить разбор задания');
    }
}

async function retrySolvedTask(textId) {
    try {
        let data;
        if (window.DokkaiApi && window.DokkaiApi.retrySolvedTask) {
            data = await window.DokkaiApi.retrySolvedTask(textId, getUserId());
        } else {
            const res = await fetch(`/api/stream/retry/${textId}?user_id=${getUserId()}`, { method: 'POST' });
            if (!res.ok) throw new Error('Ошибка запуска повтора');
            data = await res.json();
        }
        state.isRetryMode = true;
        state.pendingTextData = data;
        openPretestModal(textId);
    } catch (e) {
        console.error(e);
        alert('Не удалось запустить повторное прохождение');
    }
}

function handleSlotReplacement(solvedTextId, replacement) {
    const card = document.querySelector(`.stream-slot-card[data-text-id="${solvedTextId}"]`);
    if (card) {
        card.classList.add('slot-solving-out');
        setTimeout(() => {
            fetchAndRenderSlots();
        }, 350);
    } else {
        fetchAndRenderSlots();
    }
}

function openReportModal(textId, title) {
    state.reportingTextId = textId;
    history.pushState({ modal: 'report', textId: textId }, '', '#report');
    if (elements.reportModalTaskTitle) {
        elements.reportModalTaskTitle.textContent = title || `Задание #${textId}`;
    }
    if (elements.reportDetailsTextarea) {
        elements.reportDetailsTextarea.value = '';
    }
    if (elements.reportModalBackdrop) {
        elements.reportModalBackdrop.classList.remove('hidden');
    }
}

function closeReportModal() {
    state.reportingTextId = null;
    if (elements.reportModalBackdrop) {
        elements.reportModalBackdrop.classList.add('hidden');
    }
}

async function submitReportDefect() {
    if (!state.reportingTextId) return;
    const reason = elements.reportReasonSelect ? elements.reportReasonSelect.value : 'Опечатка';
    const details = elements.reportDetailsTextarea ? elements.reportDetailsTextarea.value.trim() : '';

    try {
        if (elements.btnSubmitReport) {
            elements.btnSubmitReport.disabled = true;
            elements.btnSubmitReport.textContent = 'Отправка...';
        }
        let resData;
        if (window.DokkaiApi && window.DokkaiApi.reportTextIssue) {
            resData = await window.DokkaiApi.reportTextIssue(state.reportingTextId, {
                reason: reason,
                details: details,
                user_id: getUserId()
            });
        } else {
            const res = await fetch(`/api/texts/${state.reportingTextId}/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reason: reason,
                    details: details,
                    user_id: getUserId()
                })
            });
            if (!res.ok) throw new Error('Ошибка отправки замечания');
            resData = await res.json();
        }
        closeReportModal();
        alert(resData.message || 'Жалоба принята. Спасибо за помощь!');
        fetchAndRenderSlots();
    } catch (e) {
        console.error(e);
        alert('Не удалось отправить замечание.');
    } finally {
        if (elements.btnSubmitReport) {
            elements.btnSubmitReport.disabled = false;
            elements.btnSubmitReport.textContent = 'Отправить замечание';
        }
    }
}

function switchMobileStreamCol(col) {
    if (!elements.tabColActive || !elements.tabColSolved) return;
    if (col === 'active') {
        elements.tabColActive.classList.add('active');
        elements.tabColSolved.classList.remove('active');
        if (elements.colActiveSlots) elements.colActiveSlots.classList.remove('hidden-mobile');
        if (elements.colSolvedArchive) elements.colSolvedArchive.classList.add('hidden-mobile');
    } else {
        elements.tabColActive.classList.remove('active');
        elements.tabColSolved.classList.add('active');
        if (elements.colActiveSlots) elements.colActiveSlots.classList.add('hidden-mobile');
        if (elements.colSolvedArchive) elements.colSolvedArchive.classList.remove('hidden-mobile');
    }
}

window.reviewSolvedTask = reviewSolvedTask;
window.retrySolvedTask = retrySolvedTask;
window.openReportModal = openReportModal;

// ============================================================================
// Pre-Test Settings Modal Logic
// ============================================================================

function openPretestModal(textId) {
    const targetId = Number(textId);
    state.pendingTextId = targetId;
    history.pushState({ modal: 'pretest', textId: targetId }, '', '#pretest');
    const textInfo = cachedCatalogTexts.find(t => String(t.id) === String(targetId));

    const recMin = textInfo ? textInfo.recommended_time_min : 3;
    if (textInfo) {
        elements.modalTextTitle.textContent = textInfo.title;
        elements.modalTimeEstimate.textContent = recMin;
    } else {
        elements.modalTextTitle.textContent = 'Текст задания';
        elements.modalTimeEstimate.textContent = recMin;
    }

    elements.pretestToggleFurigana.checked = state.pretestConfig.showFurigana;
    elements.pretestToggleHints.checked = state.pretestConfig.showHintsAndAnalysis;

    // Timer preferences
    if (elements.pretestToggleTimer) {
        elements.pretestToggleTimer.checked = Boolean(state.pretestConfig.enableTimer);
    }
    if (elements.modalTimerMinutes) {
        elements.modalTimerMinutes.textContent = state.pretestConfig.timerMinutes || recMin;
    }

    updateModalSettingTags();
    if (elements.modalBody) elements.modalBody.scrollTop = 0;
    elements.pretestModalBackdrop.classList.remove('hidden');
}

function closePretestModal() {
    elements.pretestModalBackdrop.classList.add('hidden');
    state.pendingTextId = null;
}

function updateModalSettingTags() {
    if (elements.pretestToggleFurigana.checked) {
        elements.tagFurigana.textContent = 'Обучающий режим';
        elements.tagFurigana.className = 'setting-tag';
    } else {
        elements.tagFurigana.textContent = 'Экзамен (Без фуриганы)';
        elements.tagFurigana.className = 'setting-tag tag-warning';
    }

    if (elements.pretestToggleHints.checked) {
        elements.tagHints.textContent = 'Полный разбор';
        elements.tagHints.className = 'setting-tag';
    } else {
        elements.tagHints.textContent = 'Хардкор (Без подсказок)';
        elements.tagHints.className = 'setting-tag tag-warning';
    }

    if (elements.pretestToggleTimer && elements.tagTimer) {
        const timerActive = elements.pretestToggleTimer.checked;
        const mins = elements.modalTimerMinutes ? elements.modalTimerMinutes.textContent : '3';
        if (timerActive) {
            elements.tagTimer.textContent = `ВКЛ: ${mins} мин`;
            elements.tagTimer.className = 'setting-tag tag-warning';
            if (elements.timerDurationSelector) elements.timerDurationSelector.classList.remove('hidden');
        } else {
            elements.tagTimer.textContent = 'ВЫКЛ: Без таймера';
            elements.tagTimer.className = 'setting-tag';
            if (elements.timerDurationSelector) elements.timerDurationSelector.classList.add('hidden');
        }
    }
}

function confirmPretestSettingsAndStart() {
    const showFurigana = elements.pretestToggleFurigana.checked;
    const showHints = elements.pretestToggleHints.checked;
    const enableTimer = elements.pretestToggleTimer ? elements.pretestToggleTimer.checked : false;
    const timerMins = elements.modalTimerMinutes ? parseInt(elements.modalTimerMinutes.textContent, 10) : 3;

    state.pretestConfig.showFurigana = showFurigana;
    state.pretestConfig.showHintsAndAnalysis = showHints;
    state.pretestConfig.enableTimer = enableTimer;
    state.pretestConfig.timerMinutes = timerMins;
    saveStoredConfig(state.pretestConfig);

    const textId = state.pendingTextId;
    closePretestModal();

    if (textId) {
        startExercise(textId);
    }
}

// ============================================================================
// Exercise (Strict Anti-Cheat Reading Mode & Step-by-Step Wizard)
// ============================================================================

async function startExercise(textId) {
    try {
        let textData;
        if (window.DokkaiApi && window.DokkaiApi.fetchTextDetail) {
            textData = await window.DokkaiApi.fetchTextDetail(textId);
        } else {
            const response = await fetch(`/api/texts/${textId}?_t=${Date.now()}`, {
                cache: 'no-store',
                headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
            });
            if (!response.ok) throw new Error('Не удалось загрузить задание');
            textData = await response.json();
        }
        state.activeText = textData;
        state.userAnswers = {};
        state.currentQuestionIndex = 0;
        state.currentView = 'exercise';

        // History state for phone / browser Back button
        history.pushState({ view: 'exercise', textId: textId }, '', '#exercise');

        // Switch Views
        elements.catalogView.classList.add('hidden');
        elements.exerciseView.classList.remove('hidden');
        elements.exerciseHeaderControls.classList.remove('hidden');
        elements.analysisBanner.classList.add('hidden');
        elements.analysisQAContainer.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');

        // Show Wizard UI
        elements.wizardHeader.classList.remove('hidden');
        elements.wizardCardArea.classList.remove('hidden');
        elements.wizardNavBar.classList.remove('hidden');

        // Header tags
        elements.headerLevelTag.textContent = textData.level;
        elements.headerLevelTag.setAttribute('data-lvl', textData.level);
        elements.headerCategoryTag.textContent = CATEGORY_NAMES[textData.category] || textData.category;

        if (textData.source_exam) {
            elements.headerExamBadge.textContent = textData.source_exam;
            elements.headerExamBadge.classList.remove('hidden');
        } else {
            elements.headerExamBadge.classList.add('hidden');
        }

        // Initialize Timer Mode (Countdown if chosen, otherwise untimed free reading)
        if (state.pretestConfig.enableTimer) {
            const chosenMinutes = state.pretestConfig.timerMinutes || textData.recommended_time_min;
            startCountdownTimer(chosenMinutes);
        } else {
            startUntimedMode();
        }

        // Passage Left Pane
        elements.passageTitle.textContent = textData.title;
        elements.passageLevel.textContent = textData.level;
        elements.passageLevel.setAttribute('data-lvl', textData.level);
        elements.passageCategory.textContent = CATEGORY_NAMES[textData.category] || textData.category;

        if (textData.source_exam) {
            elements.passageExamBadge.textContent = textData.source_exam;
            elements.passageExamBadge.classList.remove('hidden');
        } else {
            elements.passageExamBadge.classList.add('hidden');
        }

        elements.passageTime.textContent = `${textData.recommended_time_min} мин`;

        // Render Japanese HTML
        elements.passageContent.innerHTML = textData.content_html;
        elements.passageContent.style.fontSize = `${state.settings.fontSizePx}px`;

        // Apply Furigana setting
        if (state.pretestConfig.showFurigana) {
            state.settings.furiganaVisible = true;
            elements.passageContent.classList.remove('hide-furigana');
            elements.furiganaStatus.textContent = 'ВКЛ';
            elements.btnToggleFurigana.classList.add('active');
        } else {
            state.settings.furiganaVisible = false;
            elements.passageContent.classList.add('hide-furigana');
            elements.furiganaStatus.textContent = 'ВЫКЛ';
            elements.btnToggleFurigana.classList.remove('active');
        }

        elements.passageContent.classList.remove('show-evidence');

        // Hardcore Mode Notice
        if (!state.pretestConfig.showHintsAndAnalysis) {
            elements.hardcoreNotice.classList.remove('hidden');
        } else {
            elements.hardcoreNotice.classList.add('hidden');
        }

        // Render Wizard dots & active question
        renderWizard();
        saveCurrentActiveSession();
        if (elements.unfinishedTestBanner) {
            elements.unfinishedTestBanner.classList.add('hidden');
        }

    } catch (err) {
        console.error('Ошибка инициализации упражнения:', err);
    }
}

function renderWizard() {
    const questions = state.activeText.questions;
    const totalQ = questions.length;
    const currentQIdx = state.currentQuestionIndex;
    const currentQ = questions[currentQIdx];

    // Status label & progress
    elements.wizardStepLabel.textContent = `Вопрос ${currentQIdx + 1} из ${totalQ}`;
    elements.totalQuestionsCount.textContent = totalQ;
    elements.answeredCount.textContent = Object.keys(state.userAnswers).length;

    // Track dots
    elements.wizardTrack.innerHTML = questions.map((q, idx) => {
        const isAnswered = state.userAnswers[q.id] !== undefined;
        const isActive = idx === currentQIdx;
        let dotClass = 'wizard-dot';
        if (isActive) dotClass += ' active';
        else if (isAnswered) dotClass += ' answered';
        return `<span class="${dotClass}" title="Вопрос ${idx + 1}"></span>`;
    }).join('');

    // Render single active question card
    const selectedOptId = state.userAnswers[currentQ.id];

    elements.wizardCardArea.innerHTML = `
        <div class="question-card" id="card-q-${currentQ.id}">
            <div class="question-top">
                <span class="question-num-badge">№${currentQ.question_number}</span>
                <p class="question-prompt">${currentQ.question_text}</p>
            </div>
            <div class="options-group">
                ${currentQ.options.map(opt => {
        const isChecked = selectedOptId === opt.id;
        return `
                        <div class="option-item ${isChecked ? 'selected' : ''}" id="opt-item-${opt.id}">
                            <label class="option-label" for="radio-opt-${opt.id}">
                                <input 
                                    type="radio" 
                                    id="radio-opt-${opt.id}" 
                                    name="question_${currentQ.id}" 
                                    value="${opt.id}" 
                                    class="option-radio"
                                    ${isChecked ? 'checked' : ''}
                                    onchange="handleOptionSelect(${currentQ.id}, ${opt.id})"
                                >
                                <span class="option-text">${opt.option_number}. ${opt.option_text}</span>
                            </label>
                        </div>
                    `;
    }).join('')}
            </div>
        </div>
    `;

    // Navigation buttons state: "Назад" на первом вопросе возвращает на главную
    elements.btnWizardPrev.disabled = false;
    if (currentQIdx === 0) {
        elements.btnWizardPrev.textContent = '← На главную';
        elements.btnWizardPrev.title = 'Вернуться на главную страницу каталога';
    } else {
        elements.btnWizardPrev.textContent = '← Назад';
        elements.btnWizardPrev.title = 'Вернуться к предыдущему вопросу';
    }

    const isCurrentAnswered = selectedOptId !== undefined;
    const isLastQuestion = (currentQIdx === totalQ - 1);
    const allAnswered = Object.keys(state.userAnswers).length === totalQ;

    if (isLastQuestion) {
        elements.btnWizardNext.classList.add('hidden');
        elements.btnWizardSubmit.classList.remove('hidden');
        elements.btnWizardSubmit.disabled = !allAnswered;
    } else {
        elements.btnWizardNext.classList.remove('hidden');
        elements.btnWizardSubmit.classList.add('hidden');
        elements.btnWizardNext.disabled = !isCurrentAnswered;
    }
}

function saveCurrentActiveSession() {
    if (state.currentView !== 'exercise' || !state.activeText) return;
    if (window.DokkaiStorage) {
        window.DokkaiStorage.saveActiveSession({
            textId: state.activeText.id,
            title: state.activeText.title,
            level: state.activeText.level,
            currentQuestionIndex: state.currentQuestionIndex,
            userAnswers: state.userAnswers,
            timer: {
                totalSeconds: state.timer.totalSeconds,
                remainingSeconds: state.timer.remainingSeconds,
                secondsSpent: state.timer.secondsSpent,
                enabled: state.timer.enabled
            }
        });
    }
}

function handleOptionSelect(questionId, optionId) {
    state.userAnswers[questionId] = optionId;

    // Highlight selected visually
    const card = document.getElementById(`card-q-${questionId}`);
    if (card) {
        card.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
        const optItem = document.getElementById(`opt-item-${optionId}`);
        if (optItem) optItem.classList.add('selected');
    }

    // Refresh Wizard status and next button availability
    renderWizard();

    // Auto-save active test progress
    saveCurrentActiveSession();
}

function wizardGoNext() {
    const totalQ = state.activeText.questions.length;
    if (state.currentQuestionIndex < totalQ - 1) {
        state.currentQuestionIndex += 1;
        renderWizard();
        saveCurrentActiveSession();
    }
}

function wizardGoPrev() {
    if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
        renderWizard();
        saveCurrentActiveSession();
    } else {
        // На первом вопросе кнопка Назад возвращает на главную страницу
        returnToCatalog();
    }
}

// ============================================================================
// Submission & Analysis Mode (Post-Submit Flow with Tabbed Analysis)
// ============================================================================

async function submitAnswers() {
    const totalQuestions = state.activeText.questions.length;
    const answeredCount = Object.keys(state.userAnswers).length;

    if (answeredCount < totalQuestions) {
        alert('Пожалуйста, ответьте на все вопросы перед отправкой!');
        return;
    }

    stopTimer();
    const timeSpent = state.timer.secondsSpent;

    const answersPayload = Object.entries(state.userAnswers).map(([qId, optId]) => ({
        question_id: parseInt(qId, 10),
        selected_option_id: parseInt(optId, 10)
    }));

    try {
        elements.btnWizardSubmit.disabled = true;
        elements.btnWizardSubmit.textContent = 'Проверка ответов...';

        const idempotencyKey = 'idem-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        const solvedWhen = state.streamProfile.solvedWhen || 'all_questions_answered';

        let streamResult;
        const payload = {
            user_id: getUserId(),
            text_id: state.activeText.id,
            answers: answersPayload,
            idempotency_key: idempotencyKey,
            mode: state.isRetryMode ? 'retry' : 'first',
            solved_when: solvedWhen,
            all_correct_max_attempts: 2
        };

        if (window.DokkaiApi && window.DokkaiApi.completeStreamTask) {
            streamResult = await window.DokkaiApi.completeStreamTask(payload);
        } else {
            const response = await fetch('/api/stream/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error('Ошибка сервера при проверке ответов');
            streamResult = await response.json();
        }

        // Если режим "all_correct" и есть ошибки (задание еще не решено)
        if (!streamResult.is_solved) {
            const errCount = streamResult.error_question_ids ? streamResult.error_question_ids.length : 1;
            alert(`Внимательно перепроверьте свои ответы! В ${errCount} вопросах допущены ошибки. Попытка ${streamResult.attempts_used} из ${streamResult.attempts_max}.`);

            // Сбрасываем выбор только в ошибочных вопросах, не сливая правильные ответы!
            if (streamResult.error_question_ids) {
                streamResult.error_question_ids.forEach(qid => {
                    delete state.userAnswers[qid];
                });
            }
            elements.btnWizardSubmit.disabled = false;
            elements.btnWizardSubmit.textContent = 'Завершить и проверить ответы ✓';
            // Перерисовываем Wizard для исправления ошибок
            renderWizard();
            return;
        }

        // Задание успешно завершено (solved)
        const analysisData = streamResult;
        state.activeText = analysisData;
        state.currentView = 'analysis';
        state.analysisActiveTabIdx = 0;

        // PERSISTENCE: Save to DokkaiStorage and clear active in-progress session
        if (window.DokkaiStorage) {
            try {
                await window.DokkaiStorage.recordSolvedTask({
                    text_id: state.activeText.id,
                    title: state.activeText.title,
                    level: state.activeText.level,
                    category: state.activeText.category,
                    score: analysisData.score_percent,
                    score_percent: analysisData.score_percent,
                    last_score: analysisData.score_percent,
                    correct_count: analysisData.correct_count,
                    total_questions: analysisData.total_questions,
                    perfect: (analysisData.score_percent === 100),
                    time_spent_sec: timeSpent,
                    solved_at: new Date().toISOString()
                });
                await window.DokkaiStorage.clearActiveSession();
            } catch (err) {
                console.warn('[Dokkai] Failed to record solved task to local storage:', err);
            }
        }

        renderAnalysisView(analysisData);

        // Атомарно передаем замену слота для плавной анимации
        if (analysisData.replacement) {
            handleSlotReplacement(analysisData.text_id, analysisData.replacement);
        } else {
            fetchAndRenderSlots();
        }
        fetchAndRenderSolvedTasks();

    } catch (err) {
        console.error(err);
        alert('Не удалось отправить ответы на проверку.');
        elements.btnWizardSubmit.disabled = false;
        elements.btnWizardSubmit.textContent = 'Завершить и проверить ответы ✓';
    }
}

function renderAnalysisView(data) {
    // Hide Wizard Controls
    elements.wizardHeader.classList.add('hidden');
    elements.wizardCardArea.classList.add('hidden');
    elements.wizardNavBar.classList.add('hidden');

    // Show Analysis Banner & Tabbed Area
    elements.analysisBanner.classList.remove('hidden');
    elements.analysisQAContainer.classList.remove('hidden');

    elements.scoreText.textContent = `${data.correct_count} / ${data.total_questions}`;
    elements.scorePercent.textContent = `${data.score_percent}% ВЕРНО`;

    if (data.score_percent === 100) {
        elements.bannerResultTitle.textContent = '🎉 Великолепно! Все ответы верны!';
    } else if (data.score_percent >= 50) {
        elements.bannerResultTitle.textContent = '👍 Хорошая работа!';
    } else {
        elements.bannerResultTitle.textContent = '💪 Требуется практика.';
    }

    const spentTimeFormatted = formatTime(data.time_spent_sec || 0);
    if (state.timer.enabled) {
        const targetFormatted = formatTime(state.timer.totalSeconds);
        const inLimit = (data.time_spent_sec || 0) <= state.timer.totalSeconds;
        elements.bannerResultMeta.textContent = `Затрачено: ${spentTimeFormatted} из ${targetFormatted} (${inLimit ? 'Уложились в лимит ✅' : 'Лимит превышен ⏱️'})`;
    } else {
        elements.bannerResultMeta.textContent = `Затрачено: ${spentTimeFormatted} | Режим: Свободное чтение без таймера`;
    }

    const allowHints = state.pretestConfig.showHintsAndAnalysis;

    if (allowHints) {
        state.settings.evidenceVisible = true;
        elements.passageContent.classList.add('show-evidence');
        elements.evidenceStatus.textContent = 'ВКЛ';
        elements.btnToggleEvidence.classList.remove('hidden');
        elements.btnToggleTranslation.classList.remove('hidden');
        elements.btnToggleVocab.classList.remove('hidden');
        elements.vocabCountBadge.textContent = data.vocabulary ? data.vocabulary.length : 0;

        // Prepare Russian Translation & Vocabulary
        elements.translationText.textContent = data.translation_ru || 'Перевод недоступен.';
        elements.vocabList.innerHTML = (data.vocabulary && data.vocabulary.length > 0)
            ? data.vocabulary.map(v => `
                <div class="vocab-row">
                    <span class="vocab-word">${v.word}</span>
                    <span class="vocab-furigana">[${v.furigana}]</span>
                    <span class="vocab-trans">${v.translation}</span>
                </div>
            `).join('')
            : '<p style="color: var(--sumi-500);">Словарь пуст.</p>';
    } else {
        state.settings.evidenceVisible = false;
        elements.passageContent.classList.remove('show-evidence');
        elements.btnToggleEvidence.classList.add('hidden');
        elements.btnToggleTranslation.classList.add('hidden');
        elements.btnToggleVocab.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');
    }

    // Render Analysis Tabs
    renderAnalysisTabs();
}

function renderAnalysisTabs() {
    const questions = state.activeText.questions;
    const activeIdx = state.analysisActiveTabIdx;

    elements.analysisTabs.innerHTML = questions.map((q, idx) => {
        const isActive = idx === activeIdx;
        const isCorrect = q.is_user_correct;
        return `
            <button class="analysis-tab-btn ${isActive ? 'active' : ''}" onclick="switchAnalysisTab(${idx})">
                <span class="analysis-tab-status ${isCorrect ? 'correct' : 'wrong'}"></span>
                Вопрос №${q.question_number}
            </button>
        `;
    }).join('');

    renderAnalysisActiveCard(questions[activeIdx]);
}

function switchAnalysisTab(idx) {
    state.analysisActiveTabIdx = idx;
    renderAnalysisTabs();
}

function renderAnalysisActiveCard(q) {
    const allowHints = state.pretestConfig.showHintsAndAnalysis;

    elements.analysisActiveCard.innerHTML = `
        <div class="question-card" id="card-q-${q.id}">
            <div class="question-top">
                <span class="question-num-badge">№${q.question_number}</span>
                <p class="question-prompt">${q.question_text}</p>
                <span class="option-status-badge ${q.is_user_correct ? 'badge-correct' : 'badge-user-wrong'}">
                    ${q.is_user_correct ? '✓ Верно' : '✗ Ошибка'}
                </span>
            </div>

            <div class="options-group">
                ${q.options.map(opt => {
        let stateClass = '';
        let badgeHtml = '';
        let explanationBoxHtml = '';

        if (opt.is_correct) {
            stateClass = 'state-correct';
            badgeHtml = '<span class="option-status-badge badge-correct">✓ Правильный ответ</span>';
        } else if (opt.was_selected) {
            stateClass = 'state-wrong-selected';
            badgeHtml = '<span class="option-status-badge badge-user-wrong">✗ Ваш выбор</span>';
        }

        if (allowHints && opt.option_explanation) {
            const expClass = opt.is_correct ? 'correct-exp' : 'wrong-exp';
            const trapBadge = (!opt.is_correct && opt.trap_type && TRAP_LABELS[opt.trap_type])
                ? `<div class="trap-type-pill">⚠️ ${escapeHtml(TRAP_LABELS[opt.trap_type])}</div>`
                : '';
            explanationBoxHtml = `
                            <div class="option-explanation-box ${expClass}">
                                ${trapBadge}
                                <div>${opt.option_explanation}</div>
                            </div>
                        `;
        }

        return `
                        <div class="option-item ${stateClass}">
                            <div class="option-label">
                                <input 
                                    type="radio" 
                                    disabled 
                                    ${opt.was_selected ? 'checked' : ''} 
                                    class="option-radio"
                                >
                                <span class="option-text">${opt.option_number}. ${opt.option_text}</span>
                                ${badgeHtml}
                            </div>
                            ${explanationBoxHtml}
                        </div>
                    `;
    }).join('')}
            </div>

            <!-- General question analysis & Evidence locator -->
            ${allowHints ? `
                <div class="question-general-explanation">
                    <strong>💡 Разбор вопроса:</strong>
                    <p style="margin-top: 0.35rem;">${q.general_explanation}</p>
                    ${q.evidence_span_id ? `
                        <button type="button" class="btn-locate-evidence" onclick="locateEvidenceInText('${q.evidence_span_id}')">
                            📍 Показать доказательство в тексте
                        </button>
                    ` : ''}
                </div>
            ` : `
                <div class="question-general-explanation" style="background: #fafaf9; border-left-color: var(--sumi-400); color: var(--sumi-500); font-style: italic;">
                    Разбор и подсказки скрыты в соответствии с вашими предварительными настройками.
                </div>
            `}
        </div>
    `;

    // Automatically highlight the evidence for this question if hints are enabled
    if (allowHints && q.evidence_span_id) {
        locateEvidenceInText(q.evidence_span_id);
    }
}

// ============================================================================
// Interactive Study Tools
// ============================================================================

function toggleFurigana() {
    state.settings.furiganaVisible = !state.settings.furiganaVisible;
    if (state.settings.furiganaVisible) {
        elements.passageContent.classList.remove('hide-furigana');
        elements.furiganaStatus.textContent = 'ВКЛ';
        elements.btnToggleFurigana.classList.add('active');
    } else {
        elements.passageContent.classList.add('hide-furigana');
        elements.furiganaStatus.textContent = 'ВЫКЛ';
        elements.btnToggleFurigana.classList.remove('active');
    }
}

function toggleEvidence() {
    if (!state.pretestConfig.showHintsAndAnalysis) return;

    state.settings.evidenceVisible = !state.settings.evidenceVisible;
    if (state.settings.evidenceVisible) {
        elements.passageContent.classList.add('show-evidence');
        elements.evidenceStatus.textContent = 'ВКЛ';
        elements.btnToggleEvidence.classList.add('active');
    } else {
        elements.passageContent.classList.remove('show-evidence');
        elements.evidenceStatus.textContent = 'ВЫКЛ';
        elements.btnToggleEvidence.classList.remove('active');
    }
}

function locateEvidenceInText(spanId) {
    if (!state.pretestConfig.showHintsAndAnalysis) return;

    if (!state.settings.evidenceVisible) {
        toggleEvidence();
    }

    document.querySelectorAll('.evidence-active-pulse').forEach(el => {
        el.classList.remove('evidence-active-pulse');
    });

    const targetEl = document.getElementById(spanId);
    if (targetEl) {
        targetEl.classList.add('evidence-active-pulse');
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function toggleSupplementaryDrawer(type) {
    if (!state.pretestConfig.showHintsAndAnalysis) return;

    const isHidden = elements.supplementaryDrawer.classList.contains('hidden');
    const transSec = document.getElementById('drawer-translation-section');
    const vocabSec = document.getElementById('drawer-vocab-section');

    if (isHidden) {
        elements.supplementaryDrawer.classList.remove('hidden');
        if (type === 'translation') {
            transSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else if (type === 'vocab') {
            vocabSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    } else {
        elements.supplementaryDrawer.classList.add('hidden');
    }
}

// ============================================================================
// Yomichan-Style Interactive Popup Dictionary & Personal Notebook
// ============================================================================

const NOTEBOOK_STORAGE_KEY = 'dokkai_saved_words';

function speakJapanese(text) {
    if (!('speechSynthesis' in window)) return;
    try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ja-JP';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    } catch (e) {
        console.warn('Speech synthesis error', e);
    }
}

function getSavedWords() {
    if (Array.isArray(state.savedWords) && state.savedWords.length > 0) {
        return state.savedWords;
    }
    try {
        const stored = localStorage.getItem(NOTEBOOK_STORAGE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed) && parsed.length > 0) {
                state.savedWords = parsed;
                return state.savedWords;
            }
        }
    } catch (e) {
        console.warn('Failed to load saved words, using fallback []', e);
    }
    return Array.isArray(state.savedWords) ? state.savedWords : [];
}

async function saveWordsToStorage(words) {
    state.savedWords = words;
    try {
        localStorage.setItem(NOTEBOOK_STORAGE_KEY, JSON.stringify(words));
        updateNotebookBadge();
        if (window.DokkaiStorage) {
            for (const w of words) {
                if (w && w.word) {
                    await window.DokkaiStorage.saveWord(w, false);
                }
            }
        }
    } catch (e) {
        console.warn('Failed to save words to storage', e);
    }
}

function updateNotebookBadge() {
    const words = getSavedWords();
    const count = words.length;
    if (elements.headerSavedCount) {
        elements.headerSavedCount.textContent = count;
    }
}

function isWordSaved(wordText) {
    const words = getSavedWords();
    return words.some(w => w.word === wordText);
}

async function toggleSaveWord(wordData) {
    if (!wordData || !wordData.word) return;
    let words = getSavedWords();
    const existingIdx = words.findIndex(w => w.word === wordData.word);

    if (existingIdx >= 0) {
        const removed = words.splice(existingIdx, 1)[0];
        saveWordsToStorage(words);
        if (window.DokkaiStorage) {
            await window.DokkaiStorage.removeWord(wordData.word);
        }
        if (elements.popupBtnSave) {
            elements.popupBtnSave.classList.remove('is-saved');
            elements.popupBtnSaveText.textContent = 'В мой словарь';
        }
    } else {
        const newWord = {
            id: Date.now(),
            word: wordData.word,
            reading: wordData.reading || '',
            meaning: wordData.meaning || '',
            level: wordData.level || 'JLPT',
            mastered: false,
            date: new Date().toLocaleDateString()
        };
        words.unshift(newWord);
        saveWordsToStorage(words);
        if (window.DokkaiStorage) {
            await window.DokkaiStorage.saveWord(newWord, true);
        }
        if (elements.popupBtnSave) {
            elements.popupBtnSave.classList.add('is-saved');
            elements.popupBtnSaveText.textContent = '✓ В словаре';
        }
    }
    renderNotebookWords();
}

function showPopupDictionary(wordData, clientX, clientY) {
    state.activePopupWord = wordData;
    elements.popupWord.textContent = wordData.word;
    elements.popupReading.textContent = wordData.reading || '';
    elements.popupLevel.textContent = wordData.level || 'JLPT';
    elements.popupMeaning.textContent = wordData.meaning || 'Перевод не найден';

    const saved = isWordSaved(wordData.word);
    if (saved) {
        elements.popupBtnSave.classList.add('is-saved');
        elements.popupBtnSaveText.textContent = '✓ В словаре';
    } else {
        elements.popupBtnSave.classList.remove('is-saved');
        elements.popupBtnSaveText.textContent = 'В мой словарь';
    }

    elements.popupDictionaryCard.classList.remove('hidden');

    // Intelligent positioning
    const cardRect = elements.popupDictionaryCard.getBoundingClientRect();
    let top = clientY - cardRect.height - 12;
    let left = clientX - cardRect.width / 2;

    if (top < 10) {
        top = clientY + 24;
    }
    if (left < 10) {
        left = 10;
    }
    if (left + cardRect.width > window.innerWidth - 10) {
        left = window.innerWidth - cardRect.width - 10;
    }

    elements.popupDictionaryCard.style.top = `${top}px`;
    elements.popupDictionaryCard.style.left = `${left}px`;
}

function hidePopupDictionary() {
    if (elements.popupDictionaryCard) {
        elements.popupDictionaryCard.classList.add('hidden');
    }
    state.activePopupWord = null;
}

function lookupAndShowWord(query, clientX, clientY) {
    if (!state.popupDictEnabled) return;
    if (!query) return;

    // Clean word from rubies and punctuation
    let cleanQuery = query.replace(/[、。！？\s\t\n・「」『』（）]/g, '').trim();
    if (!cleanQuery || cleanQuery.length > 20) return;

    // 1. Check local text vocabulary if active
    if (state.activeText && state.activeText.vocabulary) {
        const localMatch = state.activeText.vocabulary.find(
            v => v.word === cleanQuery || cleanQuery.includes(v.word) || v.word.includes(cleanQuery)
        );
        if (localMatch) {
            showPopupDictionary({
                word: localMatch.word,
                reading: localMatch.furigana ? `[${localMatch.furigana}]` : '',
                meaning: localMatch.translation,
                level: state.activeText.level || 'JLPT'
            }, clientX, clientY);
            return;
        }
    }

    // 2. Fetch from backend dictionary API
    const lookupPromise = (window.DokkaiApi && window.DokkaiApi.lookupWord)
        ? window.DokkaiApi.lookupWord(cleanQuery)
        : fetch(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}`).then(res => {
            if (res.ok) return res.json();
            throw new Error('Not found');
        });

    lookupPromise
        .then(data => {
            showPopupDictionary({
                word: data.word,
                reading: data.reading ? `[${data.reading}]` : '',
                meaning: data.meaning,
                level: data.level || 'JLPT'
            }, clientX, clientY);
        })
        .catch(() => {
            // If unknown word, still allow saving or show kanji
            if (cleanQuery.length >= 1 && cleanQuery.length <= 8) {
                showPopupDictionary({
                    word: cleanQuery,
                    reading: '',
                    meaning: 'Слово из текста (сохраните для разбора)',
                    level: state.activeText ? state.activeText.level : 'JLPT'
                }, clientX, clientY);
            }
        });
}

function togglePopupDictStatus() {
    state.popupDictEnabled = !state.popupDictEnabled;
    if (elements.popupDictStatus) {
        elements.popupDictStatus.textContent = state.popupDictEnabled ? 'ВКЛ' : 'ВЫКЛ';
    }
    if (elements.btnTogglePopupDict) {
        elements.btnTogglePopupDict.classList.toggle('active', state.popupDictEnabled);
    }
    if (!state.popupDictEnabled) {
        hidePopupDictionary();
    }
}

// ============================================================================
// Main Tab Switching & Personal Notebook Logic
// ============================================================================

function switchMainTab(tabName, pushState = true) {
    state.activeTab = tabName;

    if (tabName === 'notebook') {
        stopTimer();
        state.currentView = 'notebook';
        elements.catalogView.classList.add('hidden');
        elements.exerciseView.classList.add('hidden');
        if (elements.importView) elements.importView.classList.add('hidden');
        elements.exerciseHeaderControls.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');
        elements.hardcoreNotice.classList.add('hidden');
        elements.notebookView.classList.remove('hidden');

        if (elements.btnTabCatalog) elements.btnTabCatalog.classList.remove('active');
        if (elements.btnTabNotebook) elements.btnTabNotebook.classList.add('active');
        if (elements.btnTabImport) elements.btnTabImport.classList.remove('active');

        if (pushState) {
            history.pushState({ view: 'notebook' }, '', '#notebook');
        }
        renderNotebookWords();
    } else if (tabName === 'import') {
        stopTimer();
        state.currentView = 'import';
        elements.catalogView.classList.add('hidden');
        elements.exerciseView.classList.add('hidden');
        elements.notebookView.classList.add('hidden');
        elements.exerciseHeaderControls.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');
        elements.hardcoreNotice.classList.add('hidden');
        if (elements.importView) elements.importView.classList.remove('hidden');

        if (elements.btnTabCatalog) elements.btnTabCatalog.classList.remove('active');
        if (elements.btnTabNotebook) elements.btnTabNotebook.classList.remove('active');
        if (elements.btnTabImport) elements.btnTabImport.classList.add('active');

        if (pushState) {
            history.pushState({ view: 'import' }, '', '#import');
        }
        fetchAndRenderDrafts();
    } else {
        returnToCatalog(pushState);
    }
}

function renderNotebookWords() {
    const allWords = getSavedWords();
    const safeWords = Array.isArray(allWords) ? allWords : [];
    const filter = state.notebookFilter || 'all';
    const query = (state.notebookSearchQuery || '').toLowerCase().trim();

    const countAll = safeWords.length;
    const countLearned = safeWords.filter(w => w && w.mastered).length;
    const countLearning = countAll - countLearned;

    if (elements.notebookCountAll) elements.notebookCountAll.textContent = countAll;
    if (elements.notebookCountLearning) elements.notebookCountLearning.textContent = countLearning;
    if (elements.notebookCountLearned) elements.notebookCountLearned.textContent = countLearned;
    if (elements.headerSavedCount) elements.headerSavedCount.textContent = countAll;
    if (elements.notebookStatsText) elements.notebookStatsText.textContent = `Всего сохранённых слов: ${countAll}`;

    // Filter words safely
    let filtered = safeWords;
    if (filter === 'learning') {
        filtered = filtered.filter(w => w && !w.mastered);
    } else if (filter === 'learned') {
        filtered = filtered.filter(w => w && w.mastered);
    }

    if (query) {
        filtered = filtered.filter(w =>
            (w.word && w.word.toLowerCase().includes(query)) ||
            (w.reading && w.reading.toLowerCase().includes(query)) ||
            (w.meaning && w.meaning.toLowerCase().includes(query))
        );
    }

    const container = elements.notebookWordsList;
    if (!container) return;

    if (!filtered || filtered.length === 0) {
        container.innerHTML = `
            <div class="notebook-empty-state">
                <div class="notebook-empty-icon">📖</div>
                <p>В словаре пока нет сохранённых слов.</p>
                <small>Выделяйте или кликайте на любые японские слова в текстах, чтобы посмотреть перевод и добавить их в свой персональный словарь.</small>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(w => {
        const wordText = escapeHtml(w.word || '');
        const readingText = escapeHtml(w.reading || '');
        const levelText = escapeHtml(w.level || 'JLPT');
        const meaningText = escapeHtml(w.meaning || '');
        const isMastered = Boolean(w.mastered);

        return `
        <div class="notebook-word-card ${isMastered ? 'is-mastered' : ''}" data-word="${wordText}">
            <div class="notebook-word-info">
                <div class="notebook-word-top">
                    <span class="notebook-word-jp">${wordText}</span>
                    ${readingText ? `<span class="notebook-word-reading">${readingText}</span>` : ''}
                    <span class="popup-level-tag">${levelText}</span>
                </div>
                <div class="notebook-word-meaning">${meaningText}</div>
            </div>
            <div class="notebook-word-actions">
                <button type="button" class="notebook-btn-icon btn-speak-saved" title="Прослушать" data-speak="${wordText}">🔊</button>
                <label class="switch" title="${isMastered ? 'Отметить как изучаемое' : 'Отметить как выученное'}" style="transform: scale(0.75);">
                    <input type="checkbox" class="cb-toggle-mastered" data-word="${wordText}" ${isMastered ? 'checked' : ''}>
                    <span class="slider round"></span>
                </label>
                <button type="button" class="notebook-btn-icon btn-delete-saved" title="Удалить" data-delete="${wordText}">🗑️</button>
            </div>
        </div>
        `;
    }).join('');
}

function clearAllSavedWords() {
    if (confirm('Вы уверены, что хотите полностью очистить свой словарь?')) {
        saveWordsToStorage([]);
        renderNotebookWords();
    }
}

function returnToCatalog(pushState = true) {
    stopTimer();
    state.currentView = 'catalog';
    state.activeTab = 'catalog';
    state.activeText = null;
    state.userAnswers = {};
    state.currentQuestionIndex = 0;
    state.isRetryMode = false;

    elements.exerciseView.classList.add('hidden');
    elements.exerciseHeaderControls.classList.add('hidden');
    elements.notebookView.classList.add('hidden');
    if (elements.importView) elements.importView.classList.add('hidden');
    elements.catalogView.classList.remove('hidden');
    elements.supplementaryDrawer.classList.add('hidden');
    elements.hardcoreNotice.classList.add('hidden');

    if (elements.btnTabCatalog) elements.btnTabCatalog.classList.add('active');
    if (elements.btnTabNotebook) elements.btnTabNotebook.classList.remove('active');
    if (elements.btnTabImport) elements.btnTabImport.classList.remove('active');

    closePretestModal();
    closeReportModal();

    if (pushState) {
        history.pushState({ view: 'catalog' }, '', window.location.pathname);
    }

    fetchAndRenderCatalog();
    checkAndPromptActiveSession();
}

// ============================================================================
// PDF Book Ingestion & Staging Management
// ============================================================================

let currentDraftsCache = [];

function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function handlePdfFileSelected(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Пожалуйста, выберите файл в формате .pdf');
        return;
    }
    state.selectedPdfFile = file;
    if (elements.dropzoneFileName) elements.dropzoneFileName.textContent = file.name;
    if (elements.dropzoneFileSize) elements.dropzoneFileSize.textContent = formatFileSize(file.size);
    if (elements.dropzonePrompt) elements.dropzonePrompt.classList.add('hidden');
    if (elements.dropzoneFileInfo) elements.dropzoneFileInfo.classList.remove('hidden');
}

function clearSelectedPdfFile() {
    state.selectedPdfFile = null;
    if (elements.pdfFileInput) elements.pdfFileInput.value = '';
    if (elements.dropzonePrompt) elements.dropzonePrompt.classList.remove('hidden');
    if (elements.dropzoneFileInfo) elements.dropzoneFileInfo.classList.add('hidden');
}

async function handlePdfUpload(e) {
    e.preventDefault();
    if (!state.selectedPdfFile) {
        alert('Пожалуйста, выберите или перетащите PDF файл книги.');
        return;
    }

    const formData = new FormData();
    formData.append('file', state.selectedPdfFile);
    formData.append('level', elements.importLevel ? elements.importLevel.value : 'N3');
    formData.append('category', elements.importCategory ? elements.importCategory.value : 'short');
    const titleVal = elements.importTitleOverride ? elements.importTitleOverride.value.trim() : '';
    if (titleVal) {
        formData.append('title_override', titleVal);
    }

    if (elements.btnStartUpload) elements.btnStartUpload.disabled = true;
    if (elements.uploadLoadingSpinner) elements.uploadLoadingSpinner.classList.remove('hidden');
    if (elements.uploadStatusText) elements.uploadStatusText.textContent = 'Распознавание книги: извлечение страниц, вопросов и ключей...';

    try {
        const resp = await fetch('/api/admin/upload-pdf', {
            method: 'POST',
            body: formData
        });

        const data = await resp.json();
        if (!resp.ok || !data.success) {
            throw new Error(data.error || data.detail || 'Не удалось распознать PDF');
        }

        clearSelectedPdfFile();
        if (elements.importTitleOverride) elements.importTitleOverride.value = '';

        await fetchAndRenderDrafts();

        const count = data.drafts ? data.drafts.length : 0;
        alert(`✓ Успешно! Извлечено заданий/текстов: ${count}. Они отображаются в песочнице черновиков ниже.`);
    } catch (err) {
        console.error('PDF upload error:', err);
        alert(`Ошибка при обработке PDF:\n${err.message}`);
    } finally {
        if (elements.btnStartUpload) elements.btnStartUpload.disabled = false;
        if (elements.uploadLoadingSpinner) elements.uploadLoadingSpinner.classList.add('hidden');
    }
}

async function fetchAndRenderDrafts() {
    try {
        const resp = await fetch('/api/admin/drafts');
        if (!resp.ok) return;
        const drafts = await resp.json();
        currentDraftsCache = Array.isArray(drafts) ? drafts : [];

        // Update badge counts
        const count = currentDraftsCache.length;
        if (elements.draftsCount) elements.draftsCount.textContent = count;
        if (elements.headerDraftsCount) {
            elements.headerDraftsCount.textContent = count;
            if (count > 0) {
                elements.headerDraftsCount.classList.remove('hidden');
            } else {
                elements.headerDraftsCount.classList.add('hidden');
            }
        }

        renderDraftsList(currentDraftsCache);
    } catch (err) {
        console.error('Failed to fetch drafts:', err);
    }
}

function renderDraftsList(drafts) {
    if (!elements.stagingDraftsList) return;

    if (!drafts || drafts.length === 0) {
        elements.stagingDraftsList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📭</span>
                <h3>Песочница черновиков пуста</h3>
                <p>Загрузите PDF книгу выше — распознанные тексты и вопросы появятся здесь перед публикацией.</p>
            </div>
        `;
        return;
    }

    elements.stagingDraftsList.innerHTML = drafts.map(draft => {
        const confidencePct = Math.round((draft.confidence || 0) * 100);
        const confColor = confidencePct >= 80 ? 'color-good' : (confidencePct >= 60 ? 'color-med' : 'color-low');
        const needsReviewBadge = draft.needs_review
            ? `<span class="badge-review-needed">⚠️ Требует проверки</span>`
            : `<span class="badge-review-ready">✓ Готов к публикации</span>`;

        const warningsHtml = (draft.needs_manual_review && draft.needs_manual_review.length > 0)
            ? `<div class="draft-warnings-box">
                <strong>Замечания системы:</strong>
                <ul>${draft.needs_manual_review.map(r => `<li>${r}</li>`).join('')}</ul>
               </div>`
            : '';

        const questionsHtml = (draft.questions || []).map((q, qIdx) => {
            const hasMatched = q.answer_matched;
            const matchStatus = hasMatched
                ? `<span class="match-badge match-ok">✓ Ответ найден в ключе</span>`
                : `<span class="match-badge match-missing">✗ Ответ не найден в ключе (выберите верный)</span>`;

            const optionsHtml = (q.options || []).map(opt => {
                const isChecked = opt.is_correct ? 'checked' : '';
                return `
                    <label class="draft-option-row">
                        <input type="radio" name="opt-correct-${draft.slug}-${qIdx}" 
                            value="${opt.option_number}" ${isChecked}
                            onchange="markDraftCorrectOption('${draft.slug}', ${qIdx}, ${opt.option_number})">
                        <span class="draft-opt-num">${opt.option_number}.</span>
                        <span class="draft-opt-text">${opt.text}</span>
                    </label>
                `;
            }).join('');

            return `
                <div class="draft-q-item">
                    <div class="draft-q-header">
                        <span class="draft-q-num">Вопрос ${q.question_number || (qIdx + 1)}:</span>
                        <span class="draft-q-prompt">${q.prompt}</span>
                        ${matchStatus}
                    </div>
                    <div class="draft-options-group">
                        ${optionsHtml}
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="staging-draft-card" id="card-${draft.slug}">
                <div class="staging-card-top">
                    <div class="staging-meta">
                        <span class="level-tag" data-lvl="${draft.level}">${draft.level}</span>
                        <span class="category-tag">${CATEGORY_NAMES[draft.category] || draft.category}</span>
                        <span class="confidence-pill ${confColor}">Точность: ${confidencePct}%</span>
                        ${needsReviewBadge}
                    </div>
                    <h3 class="staging-card-title">${draft.title}</h3>
                    <div class="staging-source-note">${draft.source_note || ''}</div>
                    ${warningsHtml}
                </div>

                <!-- Reading Passage Preview -->
                <div class="staging-passage-preview">
                    <details class="draft-details">
                        <summary class="draft-summary">
                            <span>📖 Текст для чтения (${(draft.body_html || '').replace(/<[^>]+>/g, '').length} симв.)</span>
                            <span class="details-cue">Развернуть / скрыть</span>
                        </summary>
                        <div class="draft-passage-body">
                            ${draft.body_html || ''}
                        </div>
                    </details>
                </div>

                <!-- Questions and Options Block -->
                <div class="staging-questions-block">
                    <h4 class="staging-block-title">❓ Вопросы и варианты (${(draft.questions || []).length}):</h4>
                    ${questionsHtml}
                </div>

                <!-- Actions Footer -->
                <div class="staging-actions-footer">
                    <div class="draft-footer-left">
                        <button type="button" class="btn btn-ghost btn-sm" onclick="saveDraft('${draft.slug}')">
                            💾 Сохранить изменения
                        </button>
                        <button type="button" class="btn btn-ghost btn-sm text-danger" onclick="deleteDraft('${draft.slug}')">
                            🗑 Удалить
                        </button>
                    </div>
                    <button type="button" class="btn btn-primary" onclick="publishDraft('${draft.slug}')">
                        🚀 Опубликовать в тренажёр →
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function markDraftCorrectOption(slug, qIdx, optNumber) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (!draft || !draft.questions || !draft.questions[qIdx]) return;
    const q = draft.questions[qIdx];
    q.options.forEach(opt => {
        opt.is_correct = (opt.option_number === optNumber);
    });
    q.answer_matched = true;
}

async function saveDraft(slug) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (!draft) return;

    try {
        const resp = await fetch(`/api/admin/drafts/${slug}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(draft)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Не удалось сохранить');
        alert('✓ Изменения черновика успешно сохранены!');
    } catch (err) {
        alert(`Ошибка при сохранении: ${err.message}`);
    }
}

async function publishDraft(slug) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (draft && draft.questions) {
        const missingAns = draft.questions.some(q => !q.options.some(o => o.is_correct));
        if (missingAns) {
            alert('Внимание: в одном из вопросов не выбран правильный ответ! Выберите правильный вариант (радиокнопкой) перед публикацией.');
            return;
        }
    }

    try {
        // Save current modifications first
        if (draft) {
            await fetch(`/api/admin/drafts/${slug}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(draft)
            });
        }

        const resp = await fetch(`/api/admin/drafts/${slug}/publish`, {
            method: 'POST'
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) {
            const errList = data.detail?.errors ? data.detail.errors.join('\n') : (data.detail || 'Ошибка');
            throw new Error(errList);
        }

        alert(`✓ Задание «${draft ? draft.title : slug}» успешно опубликовано и добавлено в каталог сайта!`);
        await fetchAndRenderDrafts();
        fetchAndRenderCatalog();
    } catch (err) {
        alert(`Не удалось опубликовать материал:\n${err.message}`);
    }
}

async function deleteDraft(slug) {
    if (!confirm('Вы уверены, что хотите удалить этот черновик?')) return;
    try {
        const resp = await fetch(`/api/admin/drafts/${slug}`, {
            method: 'DELETE'
        });
        if (!resp.ok) throw new Error('Ошибка удаления');
        await fetchAndRenderDrafts();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

// Global functions exposed to window for inline onclick attributes
window.markDraftCorrectOption = markDraftCorrectOption;
window.saveDraft = saveDraft;
window.publishDraft = publishDraft;
window.deleteDraft = deleteDraft;

function initEventListeners() {
    // Brand & abort buttons -> always cleanly return to catalog without exiting site
    elements.btnHome.addEventListener('click', () => returnToCatalog(true));
    elements.btnAbortExercise.addEventListener('click', () => returnToCatalog(true));
    elements.btnBackToCatalog.addEventListener('click', () => returnToCatalog(true));

    // Global Smartphone & Browser Back Button (popstate) Handler
    window.addEventListener('popstate', (e) => {
        // 1. If any modal is open, close it and stay on the current page
        if (elements.pretestModalBackdrop && !elements.pretestModalBackdrop.classList.contains('hidden')) {
            closePretestModal();
            return;
        }
        if (elements.reportModalBackdrop && !elements.reportModalBackdrop.classList.contains('hidden')) {
            closeReportModal();
            return;
        }
        if (elements.supplementaryDrawer && !elements.supplementaryDrawer.classList.contains('hidden')) {
            elements.supplementaryDrawer.classList.add('hidden');
            return;
        }

        // 2. If in exercise mode or analysis view, return to catalog without throwing user out
        if (state.currentView === 'exercise' || state.currentView === 'analysis') {
            returnToCatalog(false);
            return;
        }

        // 3. If in notebook or import view, return to catalog
        if (state.activeTab !== 'catalog') {
            switchMainTab('catalog', false);
            return;
        }

        // 4. If already on catalog, keep user on catalog
        history.pushState({ view: 'catalog' }, '', window.location.pathname);
    });

    // Reader tools (Font size & Typeface)
    elements.btnFontGothic.addEventListener('click', () => setReaderFont('gothic'));
    elements.btnFontMincho.addEventListener('click', () => setReaderFont('mincho'));
    elements.btnFontIncrease.addEventListener('click', () => adjustFontSize(2));
    elements.btnFontDecrease.addEventListener('click', () => adjustFontSize(-2));

    // Wizard navigation buttons
    elements.btnWizardNext.addEventListener('click', wizardGoNext);
    elements.btnWizardPrev.addEventListener('click', wizardGoPrev);
    elements.btnWizardSubmit.addEventListener('click', submitAnswers);

    // Pre-test modal events
    elements.modalBtnCancel.addEventListener('click', closePretestModal);
    elements.modalBtnClose.addEventListener('click', closePretestModal);
    elements.modalBtnStart.addEventListener('click', confirmPretestSettingsAndStart);
    elements.pretestToggleFurigana.addEventListener('change', updateModalSettingTags);
    elements.pretestToggleHints.addEventListener('change', updateModalSettingTags);
    if (elements.pretestToggleTimer) {
        elements.pretestToggleTimer.addEventListener('change', updateModalSettingTags);
    }
    if (elements.btnTimerMinus) {
        elements.btnTimerMinus.addEventListener('click', () => {
            let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
            if (cur > 1) {
                elements.modalTimerMinutes.textContent = cur - 1;
                updateModalSettingTags();
            }
        });
    }
    if (elements.btnTimerPlus) {
        elements.btnTimerPlus.addEventListener('click', () => {
            let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
            if (cur < 20) {
                elements.modalTimerMinutes.textContent = cur + 1;
                updateModalSettingTags();
            }
        });
    }
    elements.pretestModalBackdrop.addEventListener('click', (e) => {
        if (e.target === elements.pretestModalBackdrop) {
            closePretestModal();
        }
    });

    // Runtime Timer Buttons in Header & Alerts
    if (elements.btnTimerTogglePause) {
        elements.btnTimerTogglePause.addEventListener('click', toggleTimerPause);
    }
    if (elements.btnTimerAddMin) {
        elements.btnTimerAddMin.addEventListener('click', addTimerMinute);
    }
    if (elements.btnTimerDismiss) {
        elements.btnTimerDismiss.addEventListener('click', dismissTimer);
    }
    if (elements.btnEnableTimerRuntime) {
        elements.btnEnableTimerRuntime.addEventListener('click', enableTimerAtRuntime);
    }
    if (elements.btnDismissTimerAlert) {
        elements.btnDismissTimerAlert.addEventListener('click', () => {
            if (elements.timerAlertBanner) elements.timerAlertBanner.classList.add('hidden');
        });
    }

    // Continuous Stream Controls (Level, Category, Mode)
    if (elements.streamLevelPills) {
        elements.streamLevelPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.streamLevelPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.streamProfile.level = pill.dataset.level;
            fetchAndRenderStream();
        });
    }

    if (elements.streamCategoryPills) {
        elements.streamCategoryPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.streamCategoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.streamProfile.category = pill.dataset.category;
            fetchAndRenderSlots();
        });
    }

    if (elements.streamModePills) {
        elements.streamModePills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.streamProfile.solvedWhen = pill.dataset.solvedWhen || 'all_questions_answered';
        });
    }

    if (elements.btnRefreshSlots) {
        elements.btnRefreshSlots.addEventListener('click', () => {
            fetchAndRenderSlots();
        });
    }

    if (elements.solvedFilterPills) {
        elements.solvedFilterPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.mini-pill');
            if (!pill) return;
            elements.solvedFilterPills.querySelectorAll('.mini-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.solvedFilter = pill.dataset.solvedFilter || 'all';
            fetchAndRenderSolvedTasks();
        });
    }

    // Mobile Column Switcher
    if (elements.tabColActive) {
        elements.tabColActive.addEventListener('click', () => switchMobileStreamCol('active'));
    }
    if (elements.tabColSolved) {
        elements.tabColSolved.addEventListener('click', () => switchMobileStreamCol('solved'));
    }

    // Report Defect Modal Events
    if (elements.btnCloseReportModal) {
        elements.btnCloseReportModal.addEventListener('click', closeReportModal);
    }
    if (elements.btnCancelReport) {
        elements.btnCancelReport.addEventListener('click', closeReportModal);
    }
    if (elements.btnSubmitReport) {
        elements.btnSubmitReport.addEventListener('click', submitReportDefect);
    }
    if (elements.reportModalBackdrop) {
        elements.reportModalBackdrop.addEventListener('click', (e) => {
            if (e.target === elements.reportModalBackdrop) {
                closeReportModal();
            }
        });
    }

    // Filter pills (Legacy fallback if elements exist)
    if (elements.levelPills) {
        elements.levelPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.levelPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.filters.level = pill.dataset.level;
            fetchAndRenderCatalog();
        });
    }

    if (elements.categoryPills) {
        elements.categoryPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.categoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.filters.category = pill.dataset.category;
            fetchAndRenderCatalog();
        });
    }

    if (elements.sourcePills) {
        elements.sourcePills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.sourcePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.filters.source = pill.dataset.source;
            fetchAndRenderCatalog();
        });
    }

    // Analysis tools
    elements.btnToggleFurigana.addEventListener('click', toggleFurigana);
    elements.btnToggleEvidence.addEventListener('click', toggleEvidence);
    elements.btnToggleTranslation.addEventListener('click', () => toggleSupplementaryDrawer('translation'));
    elements.btnToggleVocab.addEventListener('click', () => toggleSupplementaryDrawer('vocab'));
    elements.btnCloseDrawer.addEventListener('click', () => elements.supplementaryDrawer.classList.add('hidden'));

    // Top Navigation Tabs (Тексты и тесты vs Мой словарь vs Импорт PDF)
    if (elements.btnTabCatalog) {
        elements.btnTabCatalog.addEventListener('click', () => switchMainTab('catalog'));
    }
    if (elements.btnTabNotebook) {
        elements.btnTabNotebook.addEventListener('click', () => switchMainTab('notebook'));
    }
    if (elements.btnTabImport) {
        elements.btnTabImport.addEventListener('click', () => switchMainTab('import'));
    }

    // PDF Import UI Events
    if (elements.formPdfUpload) {
        elements.formPdfUpload.addEventListener('submit', handlePdfUpload);
    }
    if (elements.btnRefreshDrafts) {
        elements.btnRefreshDrafts.addEventListener('click', fetchAndRenderDrafts);
    }
    if (elements.pdfDropzone && elements.pdfFileInput) {
        elements.pdfDropzone.addEventListener('click', (e) => {
            if (e.target.closest('#btn-clear-file')) return;
            elements.pdfFileInput.click();
        });
        elements.pdfFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handlePdfFileSelected(e.target.files[0]);
            }
        });
        elements.pdfDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            elements.pdfDropzone.classList.add('dragover');
        });
        elements.pdfDropzone.addEventListener('dragleave', () => {
            elements.pdfDropzone.classList.remove('dragover');
        });
        elements.pdfDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            elements.pdfDropzone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handlePdfFileSelected(e.dataTransfer.files[0]);
            }
        });
    }
    if (elements.btnClearFile) {
        elements.btnClearFile.addEventListener('click', (e) => {
            e.stopPropagation();
            clearSelectedPdfFile();
        });
    }

    if (elements.notebookSearchInput) {
        elements.notebookSearchInput.addEventListener('input', (e) => {
            state.notebookSearchQuery = e.target.value;
            renderNotebookWords();
        });
    }

    // Filter pills in Notebook
    const notebookFilterPills = document.querySelectorAll('.notebook-filter-pill');
    notebookFilterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            notebookFilterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.notebookFilter = pill.dataset.filter || 'all';
            renderNotebookWords();
        });
    });

    // Delegation for actions in saved words list
    if (elements.notebookWordsList) {
        elements.notebookWordsList.addEventListener('click', (e) => {
            const speakBtn = e.target.closest('.btn-speak-saved');
            if (speakBtn) {
                speakJapanese(speakBtn.dataset.speak);
                return;
            }
            const deleteBtn = e.target.closest('.btn-delete-saved');
            if (deleteBtn) {
                const wordToDelete = deleteBtn.dataset.delete;
                let words = getSavedWords();
                words = words.filter(w => w.word !== wordToDelete);
                saveWordsToStorage(words);
                renderNotebookWords();
                return;
            }
        });

        elements.notebookWordsList.addEventListener('change', (e) => {
            const cb = e.target.closest('.cb-toggle-mastered');
            if (cb) {
                const wordText = cb.dataset.word;
                let words = getSavedWords();
                const target = words.find(w => w.word === wordText);
                if (target) {
                    target.mastered = cb.checked;
                    saveWordsToStorage(words);
                    renderNotebookWords();
                }
            }
        });
    }

    if (elements.btnClearNotebook) {
        elements.btnClearNotebook.addEventListener('click', clearAllSavedWords);
    }

    // Reader Popup Dictionary Tool Button
    if (elements.btnTogglePopupDict) {
        elements.btnTogglePopupDict.addEventListener('click', togglePopupDictStatus);
    }

    // Floating Popup Controls
    if (elements.popupBtnClose) {
        elements.popupBtnClose.addEventListener('click', hidePopupDictionary);
    }
    if (elements.popupBtnAudio) {
        elements.popupBtnAudio.addEventListener('click', () => {
            if (state.activePopupWord && state.activePopupWord.word) {
                speakJapanese(state.activePopupWord.word);
            }
        });
    }
    if (elements.popupBtnSave) {
        elements.popupBtnSave.addEventListener('click', () => {
            toggleSaveWord(state.activePopupWord);
        });
    }

    // Selection & Click trigger on Passage text
    if (elements.passageContent) {
        elements.passageContent.addEventListener('mouseup', (e) => {
            if (!state.popupDictEnabled) return;
            const sel = window.getSelection();
            const text = sel ? sel.toString().trim() : '';
            if (text && text.length >= 1 && text.length <= 15) {
                const range = sel.getRangeAt(0);
                const rect = range.getBoundingClientRect();
                lookupAndShowWord(text, rect.left + rect.width / 2, rect.top);
            }
        });

        // Double click or click on Japanese words/rubies
        elements.passageContent.addEventListener('click', (e) => {
            if (!state.popupDictEnabled) return;
            const target = e.target;
            const rubyEl = target.closest('ruby');
            if (rubyEl) {
                // Get the kanji text without rt
                let kanjiText = '';
                rubyEl.childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        kanjiText += node.textContent.trim();
                    } else if (node.nodeName !== 'RT' && node.nodeName !== 'RP') {
                        kanjiText += node.textContent.trim();
                    }
                });
                if (kanjiText) {
                    const rect = rubyEl.getBoundingClientRect();
                    lookupAndShowWord(kanjiText, rect.left + rect.width / 2, rect.top);
                }
            }
        });
    }

    // Close popup dictionary when clicking outside
    document.addEventListener('mousedown', (e) => {
        if (!elements.popupDictionaryCard || elements.popupDictionaryCard.classList.contains('hidden')) return;
        if (!elements.popupDictionaryCard.contains(e.target) && !elements.passageContent.contains(e.target)) {
            hidePopupDictionary();
        }
    });

    // Sync Modal and Status triggers
    if (elements.btnSyncStatus) {
        elements.btnSyncStatus.addEventListener('click', openSyncModal);
    }
    if (elements.btnCloseSyncModal) {
        elements.btnCloseSyncModal.addEventListener('click', closeSyncModal);
    }
    if (elements.btnSyncModalDone) {
        elements.btnSyncModalDone.addEventListener('click', closeSyncModal);
    }
    if (elements.syncModalBackdrop) {
        elements.syncModalBackdrop.addEventListener('click', (e) => {
            if (e.target === elements.syncModalBackdrop) closeSyncModal();
        });
    }

    // Cloud Auth triggers
    if (elements.btnCloudSigninGoogle) {
        elements.btnCloudSigninGoogle.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            try {
                showSyncModalAlert('info', 'Подключение к Google...');
                await window.DokkaiCloudSync.signInGoogle();
            } catch (err) {
                showSyncModalAlert('error', err.message);
            }
        });
    }
    if (elements.btnCloudSigninAnon) {
        elements.btnCloudSigninAnon.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            try {
                showSyncModalAlert('info', 'Создание анонимного облачного профиля...');
                await window.DokkaiCloudSync.signInAnonymous();
            } catch (err) {
                showSyncModalAlert('error', err.message);
            }
        });
    }
    if (elements.btnCloudSignout) {
        elements.btnCloudSignout.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync) return;
            await window.DokkaiCloudSync.signOut();
            showSyncModalAlert('info', 'Вы вышли из облачного аккаунта. Локальные данные сохранены.');
        });
    }

    // Firebase Config custom save / clear
    if (elements.btnSaveFirebaseConfig) {
        elements.btnSaveFirebaseConfig.addEventListener('click', async () => {
            if (!window.DokkaiCloudSync || !elements.firebaseConfigInput) return;
            try {
                const parsed = JSON.parse(elements.firebaseConfigInput.value.trim());
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
    if (elements.btnClearFirebaseConfig) {
        elements.btnClearFirebaseConfig.addEventListener('click', () => {
            if (!window.DokkaiCloudSync) return;
            window.DokkaiCloudSync.clearFirebaseConfig();
            if (elements.firebaseConfigInput) elements.firebaseConfigInput.value = '';
            showSyncModalAlert('info', 'Конфигурация сброшена к настройкам по умолчанию.');
        });
    }

    // Backup Export & Import triggers
    if (elements.modalBtnExport) {
        elements.modalBtnExport.addEventListener('click', exportProgressJson);
    }
    if (elements.btnExportBackup) {
        elements.btnExportBackup.addEventListener('click', exportProgressJson);
    }
    if (elements.modalBtnImportTrigger) {
        elements.modalBtnImportTrigger.addEventListener('click', () => {
            if (elements.inputImportBackupFile) elements.inputImportBackupFile.click();
        });
    }
    if (elements.btnImportBackupTrigger) {
        elements.btnImportBackupTrigger.addEventListener('click', () => {
            if (elements.inputImportBackupFile) elements.inputImportBackupFile.click();
        });
    }
    if (elements.inputImportBackupFile) {
        elements.inputImportBackupFile.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleImportJsonFile(e.target.files[0]);
                e.target.value = '';
            }
        });
    }

    // Unfinished test banner triggers
    if (elements.btnResumeUnfinished) {
        elements.btnResumeUnfinished.addEventListener('click', async () => {
            if (!state.activeSession) return;
            const session = state.activeSession;
            await resumeActiveExercise(session);
        });
    }
    if (elements.btnDismissUnfinished) {
        elements.btnDismissUnfinished.addEventListener('click', async () => {
            if (elements.unfinishedTestBanner) {
                elements.unfinishedTestBanner.classList.add('hidden');
            }
            state.activeSession = null;
            if (window.DokkaiStorage) {
                await window.DokkaiStorage.clearActiveSession();
            }
        });
    }

    // Global keyboard shortcuts (Esc to close modals / popups)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hidePopupDictionary();
            closeNotebookModal();
            closePretestModal();
            closeSyncModal();
            closeReportModal();
        }
    });
}

// ============================================================================
// Cloud Sync & Backup UI & Handlers
// ============================================================================

function showSyncModalAlert(type, message) {
    if (!elements.syncModalAlert) return;
    elements.syncModalAlert.className = `sync-modal-alert alert-${type}`;
    elements.syncModalAlert.textContent = message;
    elements.syncModalAlert.classList.remove('hidden');

    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            if (elements.syncModalAlert) elements.syncModalAlert.classList.add('hidden');
        }, 5000);
    }
}

function openSyncModal() {
    if (elements.syncModalBackdrop) {
        elements.syncModalBackdrop.classList.remove('hidden');
        if (elements.syncModalAlert) elements.syncModalAlert.classList.add('hidden');
        if (window.DokkaiCloudSync && elements.firebaseConfigInput) {
            const cfg = window.DokkaiCloudSync.getStoredConfig();
            if (cfg) elements.firebaseConfigInput.value = JSON.stringify(cfg, null, 2);
        }
    }
}

function closeSyncModal() {
    if (elements.syncModalBackdrop) {
        elements.syncModalBackdrop.classList.add('hidden');
    }
}

function updateSyncStatusUI(status, extraInfo) {
    if (!elements.headerSyncDot || !elements.headerSyncLabel) return;
    const info = window.DokkaiCloudSync ? window.DokkaiCloudSync.getStatusInfo() : { text: 'На устройстве', class: 'status-local', icon: '📱' };

    elements.headerSyncDot.className = `sync-dot ${info.class}`;
    elements.headerSyncLabel.textContent = `${info.icon} ${info.text}`;

    if (elements.modalSyncDot) {
        elements.modalSyncDot.className = `sync-dot ${info.class}`;
    }
    if (elements.modalSyncTitle) {
        elements.modalSyncTitle.textContent = info.text;
    }
    if (elements.modalSyncDesc) {
        if (info.class === 'status-synced') {
            elements.modalSyncDesc.textContent = 'Все решённые задания, личный словарь и настройки синхронизированы с Google Firebase ($0 бесплатно).';
        } else if (info.class === 'status-syncing') {
            elements.modalSyncDesc.textContent = 'Идёт синхронизация данных с облаком...';
        } else if (info.class === 'status-offline') {
            elements.modalSyncDesc.textContent = 'Сеть недоступна. Все данные сохраняются на вашем устройстве (IndexedDB) и синхронизируются при включении интернета.';
        } else if (info.class === 'status-error') {
            elements.modalSyncDesc.textContent = extraInfo ? `Ошибка синхронизации: ${extraInfo}` : 'Ошибка соединения с облаком. Данные надёжно сохранены на устройстве.';
        } else {
            elements.modalSyncDesc.textContent = 'Все данные надёжно сохраняются на этом устройстве (IndexedDB). Они не пропадут при закрытии вкладки или перезапуске сервера Render.';
        }
    }
}

function updateSyncUserUI(user) {
    if (!elements.syncUserInfo || !elements.syncAuthActions) return;
    if (user) {
        elements.syncUserInfo.classList.remove('hidden');
        if (user.isAnonymous) {
            // Keep Google auth button visible so anonymous user can upgrade account
            elements.syncAuthActions.classList.remove('hidden');
            if (elements.btnCloudSigninAnon) elements.btnCloudSigninAnon.classList.add('hidden');
            if (elements.syncLinkGoogleHint) elements.syncLinkGoogleHint.classList.remove('hidden');
            if (elements.syncUserName) elements.syncUserName.textContent = 'Анонимный профиль';
            if (elements.syncUserEmail) elements.syncUserEmail.textContent = 'Облачный ID: ' + user.uid.slice(0, 10);
        } else {
            elements.syncAuthActions.classList.add('hidden');
            if (elements.syncLinkGoogleHint) elements.syncLinkGoogleHint.classList.add('hidden');
            if (elements.syncUserName) elements.syncUserName.textContent = user.displayName || 'Пользователь Google';
            if (elements.syncUserEmail) elements.syncUserEmail.textContent = user.email || '';
        }
    } else {
        elements.syncUserInfo.classList.add('hidden');
        elements.syncAuthActions.classList.remove('hidden');
        if (elements.btnCloudSigninAnon) elements.btnCloudSigninAnon.classList.remove('hidden');
        if (elements.syncLinkGoogleHint) elements.syncLinkGoogleHint.classList.add('hidden');
    }
}

async function exportProgressJson() {
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

async function handleImportJsonFile(file) {
    if (!file || !window.DokkaiStorage) return;
    try {
        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target.result;
            const res = await window.DokkaiStorage.importAllData(content);
            if (res.success) {
                showSyncModalAlert('success', `Успешно импортировано: ${res.solvedCount} решённых заданий, ${res.wordsCount} слов в словаре!`);
                state.savedWords = await window.DokkaiStorage.getAllWords();
                updateNotebookBadge();
                renderNotebookWords();
                fetchAndRenderSolvedTasks();
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

async function checkAndPromptActiveSession() {
    if (!window.DokkaiStorage) return;
    try {
        const session = await window.DokkaiStorage.getActiveSession();
        if (session && session.textId && session.title) {
            state.activeSession = session;
            if (elements.unfinishedTestBanner) {
                if (elements.unfinishedTaskTitle) {
                    elements.unfinishedTaskTitle.textContent = `Продолжить тест «${escapeHtml(session.title)}»?`;
                }
                if (elements.unfinishedTaskMeta) {
                    const qNum = (session.currentQuestionIndex || 0) + 1;
                    elements.unfinishedTaskMeta.textContent = `Вопрос ${qNum} • ${session.level || 'N5'}`;
                }
                elements.unfinishedTestBanner.classList.remove('hidden');
            }
        }
    } catch (e) {
        console.warn('[Dokkai] Active session check error:', e);
    }
}

async function resumeActiveExercise(session) {
    if (!session || !session.textId) return;
    if (elements.unfinishedTestBanner) {
        elements.unfinishedTestBanner.classList.add('hidden');
    }
    try {
        await startExercise(session.textId);
        state.userAnswers = session.userAnswers || {};
        state.currentQuestionIndex = session.currentQuestionIndex || 0;
        if (session.timer && session.timer.enabled) {
            state.timer.enabled = true;
            state.timer.totalSeconds = session.timer.totalSeconds || 180;
            state.timer.remainingSeconds = session.timer.remainingSeconds || 180;
            state.timer.secondsSpent = session.timer.secondsSpent || 0;
            if (elements.timerBox) elements.timerBox.classList.remove('hidden');
            if (elements.timerDisplay) elements.timerDisplay.textContent = formatTime(state.timer.remainingSeconds);
            if (!state.timer.intervalId) {
                startCountdownTimer(Math.ceil(state.timer.remainingSeconds / 60));
            }
        }
        renderWizard();
    } catch (err) {
        console.error('Failed to resume exercise', err);
        alert('Не удалось восстановить незавершённое задание.');
    }
}

async function initPersistenceAndSync() {
    if (!window.DokkaiStorage) return;

    // 1. Wait for DokkaiStorage
    await window.DokkaiStorage.initPromise;

    // 2. Load stored settings
    const storedUserSettings = await window.DokkaiStorage.getSettings('user_settings');
    if (storedUserSettings) {
        state.settings = { ...state.settings, ...storedUserSettings };
        if (state.settings.fontFamily) setReaderFont(state.settings.fontFamily);
        if (state.settings.fontSizePx) adjustFontSize(0);
    }

    const storedStreamProfile = await window.DokkaiStorage.getSettings('stream_profile');
    if (storedStreamProfile) {
        state.streamProfile = { ...state.streamProfile, ...storedStreamProfile };
        if (elements.streamLevelPills) {
            elements.streamLevelPills.querySelectorAll('.filter-pill').forEach(p => {
                p.classList.toggle('active', p.dataset.level === state.streamProfile.level);
            });
        }
        if (elements.streamCategoryPills) {
            elements.streamCategoryPills.querySelectorAll('.filter-pill').forEach(p => {
                p.classList.toggle('active', p.dataset.category === state.streamProfile.category);
            });
        }
    }

    const storedPretest = await window.DokkaiStorage.getSettings('pretest_config');
    if (storedPretest) {
        state.pretestConfig = { ...state.pretestConfig, ...storedPretest };
    }

    // 3. Load words into memory
    state.savedWords = await window.DokkaiStorage.getAllWords();
    updateNotebookBadge();

    // 4. Setup Cloud Sync
    if (window.DokkaiCloudSync) {
        window.DokkaiStorage.onSyncNeeded(() => {
            window.DokkaiCloudSync.scheduleAutoSync();
        });

        window.DokkaiCloudSync.onStatusChange((status, extra) => {
            updateSyncStatusUI(status, extra);
        });

        window.DokkaiCloudSync.onUserChange((user) => {
            updateSyncUserUI(user);
        });

        window.DokkaiCloudSync.onFeedback((type, message) => {
            showSyncModalAlert(type, message);
        });

        // Initialize Firebase asynchronously in background
        window.DokkaiCloudSync.init().catch(err => console.warn('[CloudSync] Init error:', err));
        updateSyncStatusUI();
    }

    // 5. Check if there is an in-progress test to recover
    await checkAndPromptActiveSession();

    // 6. Flush active session on page unload
    window.addEventListener('pagehide', () => saveCurrentActiveSession());
    window.addEventListener('beforeunload', () => saveCurrentActiveSession());
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            saveCurrentActiveSession();
        }
    });
}

// Startup
document.addEventListener('DOMContentLoaded', async () => {
    history.replaceState({ view: 'catalog' }, '', window.location.pathname);
    initEventListeners();
    try {
        await Promise.race([
            initPersistenceAndSync(),
            new Promise((_, reject) => setTimeout(() => reject(new Error('Persistence init timeout')), 2000))
        ]);
    } catch (err) {
        console.warn('[Dokkai] Persistence/Sync init non-blocking warning:', err);
    }
    fetchAndRenderCatalog();
    fetchAndRenderDrafts();
});
