/**
 * JLPT Dokkai Master - Central DOM Elements Cache
 * Provides direct access to cached DOM elements across modules.
 */

export const elements = {};

export function initElementsCache(rootDoc = (typeof document !== 'undefined' ? document : null)) {
    if (!rootDoc) return elements;

    // Top Bar & Navigation Tabs
    elements.btnHome = rootDoc.getElementById('btn-home');
    elements.headerNav = rootDoc.getElementById('header-nav');
    elements.btnTabCatalog = rootDoc.getElementById('btn-tab-catalog');
    elements.btnTabNotebook = rootDoc.getElementById('btn-tab-notebook');
    elements.btnTabImport = rootDoc.getElementById('btn-tab-import');
    elements.exerciseHeaderControls = rootDoc.getElementById('exercise-header-controls');
    elements.headerLevelTag = rootDoc.getElementById('header-level-tag');
    elements.headerCategoryTag = rootDoc.getElementById('header-category-tag');
    elements.headerExamBadge = rootDoc.getElementById('header-exam-badge');
    elements.btnAbortExercise = rootDoc.getElementById('btn-abort-exercise');
    elements.headerSavedCount = rootDoc.getElementById('header-saved-count');
    elements.headerDraftsCount = rootDoc.getElementById('header-drafts-count');

    // Timer Elements in Header
    elements.timerBox = rootDoc.getElementById('timer-box');
    elements.timerDisplay = rootDoc.getElementById('timer-display');
    elements.timerDot = rootDoc.getElementById('timer-dot');
    elements.btnTimerTogglePause = rootDoc.getElementById('btn-timer-toggle-pause');
    elements.btnTimerAddMin = rootDoc.getElementById('btn-timer-add-min');
    elements.btnTimerDismiss = rootDoc.getElementById('btn-timer-dismiss');
    elements.btnEnableTimerRuntime = rootDoc.getElementById('btn-enable-timer-runtime');
    elements.timerAlertBanner = rootDoc.getElementById('timer-alert-banner');
    elements.btnDismissTimerAlert = rootDoc.getElementById('btn-dismiss-timer-alert');

    // Views
    elements.catalogView = rootDoc.getElementById('catalog-view');
    elements.exerciseView = rootDoc.getElementById('exercise-view');
    elements.notebookView = rootDoc.getElementById('notebook-view');
    elements.importView = rootDoc.getElementById('import-view');

    // PDF Import Elements
    elements.formPdfUpload = rootDoc.getElementById('form-pdf-upload');
    elements.pdfDropzone = rootDoc.getElementById('pdf-dropzone');
    elements.pdfFileInput = rootDoc.getElementById('pdf-file-input');
    elements.dropzonePrompt = rootDoc.getElementById('dropzone-prompt');
    elements.dropzoneFileInfo = rootDoc.getElementById('dropzone-file-info');
    elements.dropzoneFileName = rootDoc.getElementById('dropzone-file-name');
    elements.dropzoneFileSize = rootDoc.getElementById('dropzone-file-size');
    elements.btnClearFile = rootDoc.getElementById('btn-clear-file');
    elements.importLevel = rootDoc.getElementById('import-level');
    elements.importCategory = rootDoc.getElementById('import-category');
    elements.importTitleOverride = rootDoc.getElementById('import-title-override');
    elements.btnStartUpload = rootDoc.getElementById('btn-start-upload');
    elements.uploadLoadingSpinner = rootDoc.getElementById('upload-loading-spinner');
    elements.uploadStatusText = rootDoc.getElementById('upload-status-text');
    elements.stagingDraftsList = rootDoc.getElementById('staging-drafts-list');
    elements.draftsCount = rootDoc.getElementById('drafts-count');
    elements.btnRefreshDrafts = rootDoc.getElementById('btn-refresh-drafts');

    // Continuous Stream Elements
    elements.activeSlotsList = rootDoc.getElementById('active-slots-list');
    elements.solvedTasksList = rootDoc.getElementById('solved-tasks-list');
    elements.streamLevelPills = rootDoc.getElementById('stream-level-pills');
    elements.streamCategoryPills = rootDoc.getElementById('stream-category-pills');
    elements.streamModePills = rootDoc.getElementById('stream-mode-pills');
    elements.btnRefreshSlots = rootDoc.getElementById('btn-refresh-slots');
    elements.solvedFilterPills = rootDoc.getElementById('solved-filter-pills');
    elements.solvedArchiveTotal = rootDoc.getElementById('solved-archive-total');
    elements.mobileActiveCount = rootDoc.getElementById('mobile-active-count');
    elements.mobileSolvedCount = rootDoc.getElementById('mobile-solved-count');
    elements.streamMobileTabs = rootDoc.getElementById('stream-mobile-tabs');
    elements.tabColActive = rootDoc.getElementById('tab-col-active');
    elements.tabColSolved = rootDoc.getElementById('tab-col-solved');
    elements.colActiveSlots = rootDoc.getElementById('col-active-slots');
    elements.colSolvedArchive = rootDoc.getElementById('col-solved-archive');

    // Report Defect Modal Elements
    elements.reportModalBackdrop = rootDoc.getElementById('report-modal-backdrop');
    elements.reportModalTaskTitle = rootDoc.getElementById('report-modal-task-title');
    elements.btnCloseReportModal = rootDoc.getElementById('btn-close-report-modal');
    elements.btnCancelReport = rootDoc.getElementById('btn-cancel-report');
    elements.btnSubmitReport = rootDoc.getElementById('btn-submit-report');
    elements.reportReasonSelect = rootDoc.getElementById('report-reason-select');
    elements.reportDetailsTextarea = rootDoc.getElementById('report-details-textarea');

    // Catalog Legacy Fallback (if needed)
    elements.catalogGrid = rootDoc.getElementById('catalog-grid');
    elements.levelPills = rootDoc.getElementById('level-filter-pills');
    elements.categoryPills = rootDoc.getElementById('category-filter-pills');
    elements.sourcePills = rootDoc.getElementById('source-filter-pills');

    // Exercise Left Pane (Passage & Reader tools)
    elements.passageTitle = rootDoc.getElementById('passage-title');
    elements.passageLevel = rootDoc.getElementById('passage-level');
    elements.passageCategory = rootDoc.getElementById('passage-category');
    elements.passageExamBadge = rootDoc.getElementById('passage-exam-badge');
    elements.passageTime = rootDoc.getElementById('passage-time');
    elements.passageContent = rootDoc.getElementById('passage-content');
    elements.btnFontGothic = rootDoc.getElementById('btn-font-gothic');
    elements.btnFontMincho = rootDoc.getElementById('btn-font-mincho');
    elements.btnFontIncrease = rootDoc.getElementById('btn-font-increase');
    elements.btnFontDecrease = rootDoc.getElementById('btn-font-decrease');
    elements.btnTogglePopupDict = rootDoc.getElementById('btn-toggle-popup-dict');
    elements.popupDictStatus = rootDoc.getElementById('popup-dict-status');

    // Yomichan Floating Card
    elements.popupDictionaryCard = rootDoc.getElementById('popup-Dictionary-card') || rootDoc.getElementById('popup-dictionary-card');
    elements.popupWord = rootDoc.getElementById('popup-word');
    elements.popupReading = rootDoc.getElementById('popup-reading');
    elements.popupLevel = rootDoc.getElementById('popup-level');
    elements.popupMeaning = rootDoc.getElementById('popup-meaning');
    elements.popupBtnAudio = rootDoc.getElementById('popup-btn-audio');
    elements.popupBtnClose = rootDoc.getElementById('popup-btn-close');
    elements.popupBtnSave = rootDoc.getElementById('popup-btn-save');
    elements.popupBtnSaveText = rootDoc.getElementById('popup-btn-save-text');

    // Notebook Modal
    elements.savedWordsModalBackdrop = rootDoc.getElementById('saved-words-modal-backdrop');
    elements.btnCloseNotebook = rootDoc.getElementById('btn-close-notebook');
    elements.notebookSearchInput = rootDoc.getElementById('notebook-search-input');
    elements.notebookWordsList = rootDoc.getElementById('notebook-words-list');
    elements.notebookCountAll = rootDoc.getElementById('notebook-count-all');
    elements.notebookCountLearning = rootDoc.getElementById('notebook-count-learning');
    elements.notebookCountLearned = rootDoc.getElementById('notebook-count-learned');
    elements.notebookStatsText = rootDoc.getElementById('notebook-stats-text');
    elements.btnClearNotebook = rootDoc.getElementById('btn-clear-notebook');

    // Wizard Controls (Right Pane)
    elements.wizardHeader = rootDoc.getElementById('wizard-header');
    elements.wizardStepLabel = rootDoc.getElementById('wizard-step-label');
    elements.wizardTrack = rootDoc.getElementById('wizard-track');
    elements.answeredCount = rootDoc.getElementById('answered-count');
    elements.totalQuestionsCount = rootDoc.getElementById('total-questions-count');
    elements.wizardCardArea = rootDoc.getElementById('wizard-card-area');
    elements.wizardNavBar = rootDoc.getElementById('wizard-nav-bar');
    elements.btnWizardPrev = rootDoc.getElementById('btn-wizard-prev');
    elements.btnWizardNext = rootDoc.getElementById('btn-wizard-next');
    elements.btnWizardSubmit = rootDoc.getElementById('btn-wizard-submit');

    // Analysis Post-Submit Tabbed View
    elements.analysisBanner = rootDoc.getElementById('analysis-banner');
    elements.scoreText = rootDoc.getElementById('score-text');
    elements.scorePercent = rootDoc.getElementById('score-percent');
    elements.bannerResultTitle = rootDoc.getElementById('banner-result-title');
    elements.bannerResultMeta = rootDoc.getElementById('banner-result-meta');
    elements.studyToolsBar = rootDoc.getElementById('study-tools-bar');
    elements.hardcoreNotice = rootDoc.getElementById('hardcore-notice');
    elements.btnToggleFurigana = rootDoc.getElementById('btn-toggle-furigana');
    elements.furiganaStatus = rootDoc.getElementById('furigana-status');
    elements.btnToggleEvidence = rootDoc.getElementById('btn-toggle-evidence');
    elements.evidenceStatus = rootDoc.getElementById('evidence-status');
    elements.btnToggleTranslation = rootDoc.getElementById('btn-toggle-translation');
    elements.btnToggleVocab = rootDoc.getElementById('btn-toggle-vocab');
    elements.vocabCountBadge = rootDoc.getElementById('vocab-count-badge');
    elements.btnBackToCatalog = rootDoc.getElementById('btn-back-to-catalog');
    elements.analysisQAContainer = rootDoc.getElementById('analysis-qa-container');
    elements.analysisTabs = rootDoc.getElementById('analysis-tabs');
    elements.analysisActiveCard = rootDoc.getElementById('analysis-active-card');

    // Supplementary Drawer
    elements.supplementaryDrawer = rootDoc.getElementById('supplementary-drawer');
    elements.drawerTitle = rootDoc.getElementById('drawer-title');
    elements.btnCloseDrawer = rootDoc.getElementById('btn-close-drawer');
    elements.translationText = rootDoc.getElementById('translation-text');
    elements.vocabList = rootDoc.getElementById('vocab-list');

    // Pre-test Modal
    elements.pretestModalBackdrop = rootDoc.getElementById('pretest-modal-backdrop');
    elements.modalBody = rootDoc.querySelector('#pretest-modal-backdrop .modal-body');
    elements.modalTextTitle = rootDoc.getElementById('modal-text-title');
    elements.modalTimeEstimate = rootDoc.getElementById('modal-time-estimate');
    elements.pretestToggleFurigana = rootDoc.getElementById('pretest-toggle-furigana');
    elements.pretestToggleHints = rootDoc.getElementById('pretest-toggle-hints');
    elements.pretestToggleTimer = rootDoc.getElementById('pretest-toggle-timer');
    elements.timerDurationSelector = rootDoc.getElementById('timer-duration-selector');
    elements.modalTimerMinutes = rootDoc.getElementById('modal-timer-minutes');
    elements.btnTimerMinus = rootDoc.getElementById('btn-timer-minus');
    elements.btnTimerPlus = rootDoc.getElementById('btn-timer-plus');
    elements.tagFurigana = rootDoc.getElementById('tag-furigana');
    elements.tagHints = rootDoc.getElementById('tag-hints');
    elements.tagTimer = rootDoc.getElementById('tag-timer');
    elements.modalBtnCancel = rootDoc.getElementById('modal-btn-cancel');
    elements.modalBtnClose = rootDoc.getElementById('modal-btn-close');
    elements.modalBtnStart = rootDoc.getElementById('modal-btn-start');

    // Sync Status & Unfinished Test Banner
    elements.btnSyncStatus = rootDoc.getElementById('btn-sync-status');
    elements.headerSyncDot = rootDoc.getElementById('header-sync-dot');
    elements.headerSyncLabel = rootDoc.getElementById('header-sync-label');
    elements.unfinishedTestBanner = rootDoc.getElementById('unfinished-test-banner');
    elements.unfinishedTaskTitle = rootDoc.getElementById('unfinished-task-title');
    elements.unfinishedTaskMeta = rootDoc.getElementById('unfinished-task-meta');
    elements.btnResumeUnfinished = rootDoc.getElementById('btn-resume-unfinished');
    elements.btnDismissUnfinished = rootDoc.getElementById('btn-dismiss-unfinished');

    // Cloud Sync Modal
    elements.syncModalBackdrop = rootDoc.getElementById('sync-modal-backdrop');
    elements.syncModalAlert = rootDoc.getElementById('sync-modal-alert');
    elements.btnCloseSyncModal = rootDoc.getElementById('btn-close-sync-modal');
    elements.btnSyncModalDone = rootDoc.getElementById('btn-sync-modal-done');
    elements.modalSyncDot = rootDoc.getElementById('modal-sync-dot');
    elements.modalSyncTitle = rootDoc.getElementById('modal-sync-title');
    elements.modalSyncDesc = rootDoc.getElementById('modal-sync-desc');
    elements.syncUserInfo = rootDoc.getElementById('sync-user-info');
    elements.syncUserAvatar = rootDoc.getElementById('sync-user-avatar');
    elements.syncUserName = rootDoc.getElementById('sync-user-name');
    elements.syncUserEmail = rootDoc.getElementById('sync-user-email');
    elements.syncLinkGoogleHint = rootDoc.getElementById('sync-link-google-hint');
    elements.btnCloudSignout = rootDoc.getElementById('btn-cloud-signout');
    elements.syncAuthActions = rootDoc.getElementById('sync-auth-actions');
    elements.btnCloudSigninGoogle = rootDoc.getElementById('btn-cloud-signin-google');
    elements.btnCloudSigninAnon = rootDoc.getElementById('btn-cloud-signin-anon');
    elements.modalBtnExport = rootDoc.getElementById('modal-btn-export');
    elements.modalBtnImportTrigger = rootDoc.getElementById('modal-btn-import-trigger');
    elements.firebaseConfigInput = rootDoc.getElementById('firebase-config-input');
    elements.btnSaveFirebaseConfig = rootDoc.getElementById('btn-save-firebase-config');
    elements.btnClearFirebaseConfig = rootDoc.getElementById('btn-clear-firebase-config');

    // Notebook Backup
    elements.btnExportBackup = rootDoc.getElementById('btn-export-backup');
    elements.btnImportBackupTrigger = rootDoc.getElementById('btn-import-backup-trigger');
    elements.inputImportBackupFile = rootDoc.getElementById('input-import-backup-file');

    return elements;
}

if (typeof document !== 'undefined') {
    initElementsCache(document);
}

if (typeof window !== 'undefined') {
    window.DokkaiElements = { elements, initElementsCache };
    window.elements = elements;
}

