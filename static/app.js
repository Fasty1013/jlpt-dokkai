/**
 * JLPT Dokkai Master - Frontend Application Logic (Vanilla JS ES6+)
 * Supports Step-by-Step Question Wizard & Tabbed Post-Submit Analysis
 */

// ============================================================================
// Application State & LocalStorage Configuration
// ============================================================================

// ============================================================================
// Core Utility Delegates (Single Source of Truth: static/js/utils/)
// ============================================================================

if (typeof window !== 'undefined' && (!window.DokkaiUtils || !window.DokkaiUtils.getUserId)) {
    console.error('[Dokkai] Критическая ошибка: модуль DokkaiUtils не загружен.');
    if (typeof document !== 'undefined' && document.body) {
        const errBanner = document.createElement('div');
        errBanner.className = 'module-load-error-banner';
        errBanner.style.cssText = 'background: #fee2e2; color: #991b1b; padding: 12px 16px; margin: 12px; border: 1px solid #f87171; border-radius: 8px; font-weight: 600; text-align: center;';
        errBanner.textContent = 'Ошибка: компонент DokkaiUtils не загрузился. Пожалуйста, обновите страницу.';
        document.body.prepend(errBanner);
    }
}

const escapeHtml = (str) => {
    if (window.DokkaiUtils?.escapeHtml) return window.DokkaiUtils.escapeHtml(str);
    console.error('[Dokkai] DokkaiUtils.escapeHtml недоступен');
    throw new Error('[Dokkai] DokkaiUtils.escapeHtml недоступен');
};
const getUserId = () => {
    if (window.DokkaiUtils?.getUserId) return window.DokkaiUtils.getUserId();
    console.error('[Dokkai] DokkaiUtils.getUserId недоступен');
    throw new Error('[Dokkai] DokkaiUtils.getUserId недоступен');
};
const formatTime = (totalSeconds) => {
    if (window.DokkaiUtils?.formatTime) return window.DokkaiUtils.formatTime(totalSeconds);
    console.error('[Dokkai] DokkaiUtils.formatTime недоступен');
    throw new Error('[Dokkai] DokkaiUtils.formatTime недоступен');
};
const formatFileSize = (bytes) => {
    if (window.DokkaiUtils?.formatFileSize) return window.DokkaiUtils.formatFileSize(bytes);
    console.error('[Dokkai] DokkaiUtils.formatFileSize недоступен');
    throw new Error('[Dokkai] DokkaiUtils.formatFileSize недоступен');
};

const CONFIG_STORAGE_KEY = 'dokkai_pretest_config';

function loadStoredConfig() {
    return window.DokkaiFormatting.loadStoredConfig();
}

function saveStoredConfig(config) {
    return window.DokkaiFormatting.saveStoredConfig(config);
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

// ============================================================================
// Timer Functions (Delegated to static/js/features/timer/)
// ============================================================================

function stopTimer() {
    window.DokkaiTimer.stopTimer(state.timer);
}

function startUntimedMode() {
    window.DokkaiTimer.startUntimedMode(state.timer, elements);
}

function startCountdownTimer(minutes) {
    window.DokkaiTimer.startCountdownTimer(minutes, state.timer, elements);
}

function toggleTimerPause() {
    window.DokkaiTimer.toggleTimerPause(state.timer, elements);
}

function addTimerMinute() {
    window.DokkaiTimer.addTimerMinute(state.timer, elements);
}

function dismissTimer() {
    window.DokkaiTimer.dismissTimer(state.timer, elements);
}

function enableTimerAtRuntime() {
    const recMin = (state.activeText && state.activeText.recommended_time_min) ? state.activeText.recommended_time_min : 3;
    window.DokkaiTimer.enableTimerAtRuntime(recMin, state.timer, elements);
}

// ============================================================================
// Reader Customization (Delegated to static/js/features/settings/)
// ============================================================================

function saveUserSettings() {
    window.DokkaiSettings.saveUserSettings(state.settings);
}

function setReaderFont(typeface) {
    window.DokkaiSettings.setReaderFont(typeface, state.settings, elements);
}

function adjustFontSize(delta) {
    return window.DokkaiSettings.adjustFontSize(delta, state.settings, elements);
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
    await window.DokkaiStream.fetchAndRenderSlots(isExplicitRefresh, { state, elements, getUserId });
    cachedCatalogTexts = window.cachedCatalogTexts || [];
}

async function fetchAndRenderSolvedTasks() {
    await window.DokkaiSolved.fetchAndRenderSolvedTasks({ state, elements, getUserId });
}

async function reviewSolvedTask(textId) {
    await window.DokkaiSolved.reviewSolvedTask(textId, { state, getUserId, onRenderAnalysis: renderAnalysisView });
}

async function retrySolvedTask(textId) {
    await window.DokkaiSolved.retrySolvedTask(textId, { state, getUserId, onOpenPretest: openPretestModal });
}

function handleSlotReplacement(solvedTextId, replacement) {
    window.DokkaiStream.handleSlotReplacement(solvedTextId, replacement, fetchAndRenderSlots);
}

function openReportModal(textId, title) {
    window.DokkaiSolved.openReportModal(textId, title, { state, elements });
}

function closeReportModal() {
    window.DokkaiSolved.closeReportModal({ state, elements });
}

async function submitReportDefect() {
    await window.DokkaiSolved.submitReportDefect({ state, elements, getUserId, onRefreshSlots: fetchAndRenderSlots });
}

function switchMobileStreamCol(col) {
    window.DokkaiStream.switchMobileStreamCol(col, elements);
}

window.reviewSolvedTask = reviewSolvedTask;
window.retrySolvedTask = retrySolvedTask;
window.openReportModal = openReportModal;

// ============================================================================
// Pre-Test Settings Modal Logic (Delegated to static/js/features/pretest/)
// ============================================================================

function openPretestModal(textId) {
    window.DokkaiPretest.openPretestModal(textId, {
        state,
        elements,
        getTextInfo: id => cachedCatalogTexts.find(t => String(t.id) === String(id))
    });
}

function closePretestModal() {
    window.DokkaiPretest.closePretestModal({ state, elements });
}

function updateModalSettingTags() {
    window.DokkaiPretest.updateModalSettingTags(elements);
}

function confirmPretestSettingsAndStart() {
    window.DokkaiPretest.confirmPretestSettingsAndStart({ state, elements, onStart: startExercise });
}

// ============================================================================
// Exercise (Strict Anti-Cheat Reading Mode & Step-by-Step Wizard)
// ============================================================================

async function startExercise(textId) {
    if (window.DokkaiExercise && window.DokkaiExercise.startExercise) {
        return window.DokkaiExercise.startExercise(textId, {
            state,
            elements,
            startCountdownTimer,
            startUntimedMode,
            returnToCatalog
        });
    }
    throw new Error('DokkaiExercise feature module is not loaded');
}

function renderWizard() {
    if (window.DokkaiExercise && window.DokkaiExercise.renderWizard) {
        return window.DokkaiExercise.renderWizard(state, elements);
    }
}

function saveCurrentActiveSession() {
    if (window.DokkaiExercise && window.DokkaiExercise.saveCurrentActiveSession) {
        return window.DokkaiExercise.saveCurrentActiveSession(state);
    }
}

function handleOptionSelect(questionId, optionId) {
    if (window.DokkaiExercise && window.DokkaiExercise.handleOptionSelect) {
        return window.DokkaiExercise.handleOptionSelect(questionId, optionId, state, elements);
    }
}

function wizardGoNext() {
    if (window.DokkaiExercise && window.DokkaiExercise.wizardGoNext) {
        return window.DokkaiExercise.wizardGoNext(state, elements);
    }
}

function wizardGoPrev() {
    if (window.DokkaiExercise && window.DokkaiExercise.wizardGoPrev) {
        return window.DokkaiExercise.wizardGoPrev(state, elements, returnToCatalog);
    }
}

// ============================================================================
// Submission & Analysis Mode (Post-Submit Flow with Tabbed Analysis)
// ============================================================================

async function submitAnswers() {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.submitAnswers) {
        return window.DokkaiAnalysis.submitAnswers({
            state,
            elements,
            handleSlotReplacement,
            fetchAndRenderSlots,
            fetchAndRenderSolvedTasks,
            stopTimer,
            getUserId,
            renderWizard
        });
    }
    throw new Error('DokkaiAnalysis feature module is not loaded');
}

function renderAnalysisView(data) {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.renderAnalysisView) {
        return window.DokkaiAnalysis.renderAnalysisView(data, state, elements);
    }
}

function renderAnalysisTabs() {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.renderAnalysisTabs) {
        return window.DokkaiAnalysis.renderAnalysisTabs(state, elements);
    }
}

function switchAnalysisTab(idx) {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.switchAnalysisTab) {
        return window.DokkaiAnalysis.switchAnalysisTab(idx, state, elements);
    }
}

function renderAnalysisActiveCard(q) {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.renderAnalysisActiveCard) {
        return window.DokkaiAnalysis.renderAnalysisActiveCard(q, state, elements);
    }
}

function toggleFurigana() {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.toggleFurigana) {
        return window.DokkaiAnalysis.toggleFurigana(state, elements);
    }
}

function toggleEvidence() {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.toggleEvidence) {
        return window.DokkaiAnalysis.toggleEvidence(state, elements);
    }
}

function locateEvidenceInText(spanId) {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.locateEvidenceInText) {
        return window.DokkaiAnalysis.locateEvidenceInText(spanId, state, elements);
    }
}

function toggleSupplementaryDrawer(type) {
    if (window.DokkaiAnalysis && window.DokkaiAnalysis.toggleSupplementaryDrawer) {
        return window.DokkaiAnalysis.toggleSupplementaryDrawer(type, state, elements);
    }
}

// ============================================================================
// Yomichan-Style Interactive Popup Dictionary & Personal Notebook
// ============================================================================

const NOTEBOOK_STORAGE_KEY = 'dokkai_saved_words';

function speakJapanese(text) {
    if (window.DokkaiSpeech && window.DokkaiSpeech.speakJapanese) {
        return window.DokkaiSpeech.speakJapanese(text);
    }
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
        try {
            const savedSolvedWhen = localStorage.getItem('dokkai_stream_solved_when');
            if (savedSolvedWhen) {
                state.streamProfile.solvedWhen = savedSolvedWhen;
                const targetPill = elements.streamModePills.querySelector(`[data-solved-when="${savedSolvedWhen}"]`);
                if (targetPill) {
                    elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                    targetPill.classList.add('active');
                }
            }
        } catch (err) {}

        elements.streamModePills.addEventListener('click', (e) => {
            const pill = e.target.closest('.filter-pill');
            if (!pill) return;
            elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.streamProfile.solvedWhen = pill.dataset.solvedWhen || 'all_questions_answered';
            try {
                localStorage.setItem('dokkai_stream_solved_when', state.streamProfile.solvedWhen);
            } catch (err) {}
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
