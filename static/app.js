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
    if (window.DokkaiNotebook && window.DokkaiNotebook.getSavedWords) {
        return window.DokkaiNotebook.getSavedWords(state);
    }
    return Array.isArray(state.savedWords) ? state.savedWords : [];
}

async function saveWordsToStorage(words) {
    if (window.DokkaiNotebook && window.DokkaiNotebook.saveWordsToStorage) {
        return window.DokkaiNotebook.saveWordsToStorage(words, state, elements);
    }
    state.savedWords = words;
}

function updateNotebookBadge() {
    if (window.DokkaiNotebook && window.DokkaiNotebook.updateNotebookBadge) {
        return window.DokkaiNotebook.updateNotebookBadge(elements, state);
    }
}

function isWordSaved(wordText) {
    if (window.DokkaiNotebook && window.DokkaiNotebook.isWordSaved) {
        return window.DokkaiNotebook.isWordSaved(wordText, state);
    }
    return false;
}

async function toggleSaveWord(wordData) {
    if (window.DokkaiNotebook && window.DokkaiNotebook.toggleSaveWord) {
        return window.DokkaiNotebook.toggleSaveWord(wordData, state, elements, renderNotebookWords);
    }
}

function showPopupDictionary(wordData, clientX, clientY) {
    if (window.DokkaiDictionary && window.DokkaiDictionary.showPopupDictionary) {
        return window.DokkaiDictionary.showPopupDictionary(wordData, clientX, clientY, elements, state);
    }
}

function hidePopupDictionary() {
    if (window.DokkaiDictionary && window.DokkaiDictionary.hidePopupDictionary) {
        return window.DokkaiDictionary.hidePopupDictionary(elements, state);
    }
    if (elements.popupDictionaryCard) {
        elements.popupDictionaryCard.classList.add('hidden');
    }
    state.activePopupWord = null;
}

function lookupAndShowWord(query, clientX, clientY) {
    if (window.DokkaiDictionary && window.DokkaiDictionary.lookupAndShowWord) {
        return window.DokkaiDictionary.lookupAndShowWord(query, clientX, clientY, elements, state);
    }
}

function togglePopupDictStatus() {
    if (window.DokkaiDictionary && window.DokkaiDictionary.togglePopupDictStatus) {
        return window.DokkaiDictionary.togglePopupDictStatus(elements, state);
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
    if (window.DokkaiNotebook && window.DokkaiNotebook.renderNotebookWords) {
        return window.DokkaiNotebook.renderNotebookWords(elements, state);
    }
}

function clearAllSavedWords() {
    if (window.DokkaiNotebook && window.DokkaiNotebook.clearAllSavedWords) {
        return window.DokkaiNotebook.clearAllSavedWords(state, elements, renderNotebookWords);
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
// PDF Book Ingestion & Staging Management (Extracted to features/pdf_import/)
// ============================================================================

function initEventListeners() {
    // ------------------------------------------------------------------------
    // Central Declarative Action Delegation (Step 6a)
    // ------------------------------------------------------------------------
    if (window.DokkaiEvents) {
        window.DokkaiEvents.registerActions({
            // Brand & Navigation
            'return-to-catalog': () => returnToCatalog(true),
            'switch-main-tab': (el, e, ds) => switchMainTab(ds.tab || 'catalog'),
            'open-sync-modal': () => openSyncModal(),

            // Reader tools (Font size & Typeface)
            'set-reader-font': (el, e, ds) => setReaderFont(ds.font || el.dataset.font),
            'adjust-font-size': (el, e, ds) => adjustFontSize(parseInt(ds.delta || el.dataset.delta, 10) || 0),
            'toggle-popup-dict': () => togglePopupDictStatus(),

            // Wizard navigation buttons
            'wizard-prev': () => wizardGoPrev(),
            'wizard-next': () => wizardGoNext(),
            'wizard-submit': () => submitAnswers(),

            // Pre-test modal events
            'close-pretest-modal': () => closePretestModal(),
            'start-exercise': () => confirmPretestSettingsAndStart(),
            'timer-duration-minus': () => {
                let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
                if (cur > 1) {
                    elements.modalTimerMinutes.textContent = cur - 1;
                    updateModalSettingTags();
                }
            },
            'timer-duration-plus': () => {
                let cur = parseInt(elements.modalTimerMinutes.textContent, 10) || 3;
                if (cur < 20) {
                    elements.modalTimerMinutes.textContent = cur + 1;
                    updateModalSettingTags();
                }
            },

            // Runtime Timer Buttons in Header & Alerts
            'toggle-timer-pause': () => toggleTimerPause(),
            'add-timer-minute': () => addTimerMinute(),
            'dismiss-timer': () => dismissTimer(),
            'enable-timer-runtime': () => enableTimerAtRuntime(),
            'dismiss-timer-alert': () => {
                if (elements.timerAlertBanner) elements.timerAlertBanner.classList.add('hidden');
            },

            // Continuous Stream Controls (Level, Category, Mode)
            'filter-level': (el, e, ds) => {
                if (elements.streamLevelPills) {
                    elements.streamLevelPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                }
                el.classList.add('active');
                state.streamProfile.level = ds.level || el.dataset.level;
                fetchAndRenderStream();
            },
            'filter-category': (el, e, ds) => {
                if (elements.streamCategoryPills) {
                    elements.streamCategoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                }
                el.classList.add('active');
                state.streamProfile.category = ds.category || el.dataset.category;
                fetchAndRenderSlots();
            },
            'filter-solved-when': (el, e, ds) => {
                if (elements.streamModePills) {
                    elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
                }
                el.classList.add('active');
                state.streamProfile.solvedWhen = ds.solvedWhen || el.dataset.solvedWhen || 'all_questions_answered';
                try {
                    localStorage.setItem('dokkai_stream_solved_when', state.streamProfile.solvedWhen);
                } catch (err) { }
            },
            'refresh-slots': () => fetchAndRenderSlots(),
            'filter-solved': (el, e, ds) => {
                if (elements.solvedFilterPills) {
                    elements.solvedFilterPills.querySelectorAll('.mini-pill').forEach(p => p.classList.remove('active'));
                }
                el.classList.add('active');
                state.solvedFilter = ds.solvedFilter || el.dataset.solvedFilter || 'all';
                fetchAndRenderSolvedTasks();
            },
            'switch-mobile-stream-col': (el, e, ds) => {
                switchMobileStreamCol(ds.col || el.dataset.col || 'active');
            },

            // Report Defect Modal Events
            'close-report-modal': () => closeReportModal(),
            'submit-report': () => submitReportDefect(),

            // Analysis tools
            'toggle-furigana': () => toggleFurigana(),
            'toggle-evidence': () => toggleEvidence(),
            'toggle-translation': () => toggleSupplementaryDrawer('translation'),
            'toggle-vocab': () => toggleSupplementaryDrawer('vocab'),
            'close-drawer': () => {
                if (elements.supplementaryDrawer) elements.supplementaryDrawer.classList.add('hidden');
            },

            // Unfinished test banner triggers
            'resume-unfinished': async () => {
                if (!state.activeSession) return;
                await resumeActiveExercise(state.activeSession);
            },
            'dismiss-unfinished': async () => {
                if (elements.unfinishedTestBanner) {
                    elements.unfinishedTestBanner.classList.add('hidden');
                }
                state.activeSession = null;
                if (window.DokkaiStorage) {
                    await window.DokkaiStorage.clearActiveSession();
                }
            },

            // Notebook actions
            'filter-notebook': (el, e, ds) => {
                const notebookFilterPills = document.querySelectorAll('.notebook-filter-pill');
                notebookFilterPills.forEach(p => p.classList.remove('active'));
                el.classList.add('active');
                state.notebookFilter = ds.filter || el.dataset.filter || 'all';
                renderNotebookWords();
            },
            'export-notebook-backup': () => exportProgressJson(),
            'import-notebook-backup-trigger': () => {
                const fileInput = document.getElementById('input-import-backup-file');
                if (fileInput) fileInput.click();
            },
            'clear-notebook': () => clearAllSavedWords(),

            // PDF Import Actions
            'clear-pdf-file': () => {
                if (window.clearSelectedPdfFile) window.clearSelectedPdfFile();
            },
            'refresh-pdf-drafts': () => {
                if (window.fetchAndRenderDrafts) window.fetchAndRenderDrafts();
            },

            // Floating Popup Dictionary Controls
            'dict-close': () => hidePopupDictionary(),
            'dict-play-audio': () => {
                if (state.activePopupWord && state.activePopupWord.word) {
                    speakJapanese(state.activePopupWord.word);
                }
            },
            'dict-save-word': () => {
                toggleSaveWord(state.activePopupWord);
            },

            // Cloud Sync Modal Actions
            'close-sync-modal': () => closeSyncModal(),
            'cloud-signout': () => {
                if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleCloudSignout) {
                    window.DokkaiSyncUI.handleCloudSignout();
                }
            },
            'cloud-signin-google': () => {
                if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleGoogleSignIn) {
                    window.DokkaiSyncUI.handleGoogleSignIn();
                }
            },
            'cloud-signin-anon': () => {
                if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleAnonymousSignIn) {
                    window.DokkaiSyncUI.handleAnonymousSignIn();
                }
            },
            'export-sync-backup': () => exportProgressJson(),
            'import-sync-backup-trigger': () => {
                const fileInput = document.getElementById('input-import-backup-file');
                if (fileInput) fileInput.click();
            },
            'save-firebase-config': () => {
                if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleSaveCustomFirebaseConfig) {
                    window.DokkaiSyncUI.handleSaveCustomFirebaseConfig();
                }
            },
            'clear-firebase-config': () => {
                if (window.DokkaiSyncUI && window.DokkaiSyncUI.handleClearCustomFirebaseConfig) {
                    window.DokkaiSyncUI.handleClearCustomFirebaseConfig();
                }
            },

            // Escape key
            'escape': () => {
                hidePopupDictionary();
                closeNotebookModal();
                closePretestModal();
                closeSyncModal();
                closeReportModal();
            }
        });

        window.DokkaiEvents.initActionDelegation();
    }

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

    // Pre-test modal setting change handlers
    if (elements.pretestToggleFurigana) {
        elements.pretestToggleFurigana.addEventListener('change', updateModalSettingTags);
    }
    if (elements.pretestToggleHints) {
        elements.pretestToggleHints.addEventListener('change', updateModalSettingTags);
    }
    if (elements.pretestToggleTimer) {
        elements.pretestToggleTimer.addEventListener('change', updateModalSettingTags);
    }
    if (elements.pretestModalBackdrop) {
        elements.pretestModalBackdrop.addEventListener('click', (e) => {
            if (e.target === elements.pretestModalBackdrop) {
                closePretestModal();
            }
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
        } catch (err) { }
    }

    if (elements.reportModalBackdrop) {
        elements.reportModalBackdrop.addEventListener('click', (e) => {
            if (e.target === elements.reportModalBackdrop) {
                closeReportModal();
            }
        });
    }

    // PDF Import UI Events (delegated to features/pdf_import/)
    if (window.initPdfImportUI) {
        window.initPdfImportUI();
    }

    if (elements.notebookSearchInput) {
        elements.notebookSearchInput.addEventListener('input', (e) => {
            state.notebookSearchQuery = e.target.value;
            renderNotebookWords();
        });
    }

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

    // Sync Modal and Cloud Auth triggers (delegated to features/sync_ui/)
    if (window.initSyncModalUI) {
        window.initSyncModalUI();
    }
}

// ============================================================================
// Cloud Sync & Backup UI & Handlers (Extracted to features/sync_ui/)
// ============================================================================

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
