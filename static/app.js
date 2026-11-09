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

// State and DOM elements are managed centrally by static/js/state/
const state = (typeof window !== 'undefined' && window.DokkaiState)
    ? window.DokkaiState.state
    : (typeof window !== 'undefined' && window.state ? window.state : {});

const elements = (typeof window !== 'undefined' && window.DokkaiState)
    ? window.DokkaiState.elements
    : (typeof window !== 'undefined' && window.elements ? window.elements : {});

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
    // Feature Event Inits (Step 6d Modular Event Decomposition)
    // ------------------------------------------------------------------------
    if (window.DokkaiEvents && window.DokkaiEvents.initNavigationEvents) {
        window.DokkaiEvents.initNavigationEvents({
            state,
            elements,
            actions: {
                returnToCatalog,
                switchMainTab,
                openSyncModal,
                hidePopupDictionary,
                closeNotebookModal: () => {
                    // Parity with main: on main, closeNotebookModal() was an undeclared reference that threw ReferenceError.
                    // Scheduled for clean fix in Part III (Step 11).
                    throw new ReferenceError('closeNotebookModal is not defined');
                },
                closePretestModal,
                closeSyncModal,
                closeReportModal
            }
        });
    }

    if (window.DokkaiStream && window.DokkaiStream.initEvents) {
        window.DokkaiStream.initEvents({
            state,
            elements,
            actions: {
                fetchAndRenderStream,
                fetchAndRenderSlots,
                fetchAndRenderSolvedTasks,
                openPretestModal,
                reviewSolvedTask,
                retrySolvedTask,
                switchMobileStreamCol
            }
        });
    }

    if (window.DokkaiPretest && window.DokkaiPretest.initEvents) {
        window.DokkaiPretest.initEvents({
            state,
            elements,
            actions: {
                closePretestModal,
                confirmPretestSettingsAndStart,
                updateModalSettingTags
            }
        });
    }

    if (window.DokkaiTimer && window.DokkaiTimer.initEvents) {
        window.DokkaiTimer.initEvents({
            state,
            elements,
            actions: {
                toggleTimerPause,
                addTimerMinute,
                dismissTimer,
                enableTimerAtRuntime
            }
        });
    }

    if (window.DokkaiSettings && window.DokkaiSettings.initEvents) {
        window.DokkaiSettings.initEvents({
            state,
            elements,
            actions: {
                setReaderFont,
                adjustFontSize,
                togglePopupDictStatus
            }
        });
    }

    if (window.DokkaiExercise && window.DokkaiExercise.initEvents) {
        window.DokkaiExercise.initEvents({
            state,
            elements,
            actions: {
                wizardGoPrev,
                wizardGoNext,
                submitAnswers,
                handleOptionSelect,
                resumeActiveExercise
            }
        });
    }

    if (window.DokkaiAnalysis && window.DokkaiAnalysis.initEvents) {
        window.DokkaiAnalysis.initEvents({
            state,
            elements,
            actions: {
                toggleFurigana,
                toggleEvidence,
                toggleSupplementaryDrawer,
                switchAnalysisTab,
                locateEvidenceInText
            }
        });
    }

    if (window.DokkaiDictionary && window.DokkaiDictionary.initEvents) {
        window.DokkaiDictionary.initEvents({
            state,
            elements,
            actions: {
                hidePopupDictionary,
                speakJapanese,
                toggleSaveWord,
                lookupAndShowWord
            }
        });
    }

    if (window.DokkaiNotebook && window.DokkaiNotebook.initEvents) {
        window.DokkaiNotebook.initEvents({
            state,
            elements,
            actions: {
                renderNotebookWords,
                exportProgressJson,
                clearAllSavedWords,
                speakJapanese,
                getSavedWords,
                saveWordsToStorage
            }
        });
    }

    if (window.DokkaiPdfImport && window.DokkaiPdfImport.initEvents) {
        window.DokkaiPdfImport.initEvents({
            state,
            elements,
            actions: {
                clearSelectedPdfFile: window.clearSelectedPdfFile,
                fetchAndRenderDrafts: window.fetchAndRenderDrafts
            }
        });
    }

    if (window.DokkaiSyncUI && window.DokkaiSyncUI.initEvents) {
        window.DokkaiSyncUI.initEvents({
            state,
            elements,
            actions: {
                closeSyncModal,
                exportProgressJson
            }
        });
    }

    if (window.DokkaiSolved && window.DokkaiSolved.initEvents) {
        window.DokkaiSolved.initEvents({
            state,
            elements,
            actions: {
                openReportModal,
                closeReportModal,
                submitReportDefect
            }
        });
    }

    if (window.DokkaiEvents && window.DokkaiEvents.initActionDelegation) {
        window.DokkaiEvents.initActionDelegation();
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
