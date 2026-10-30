/**
 * JLPT Dokkai Master - Frontend Application Logic (Vanilla JS ES6+)
 * Supports Step-by-Step Question Wizard & Tabbed Post-Submit Analysis
 */

// ============================================================================
// Application State & LocalStorage Configuration
// ============================================================================

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
        showHintsAndAnalysis: true
    };
}

function saveStoredConfig(config) {
    try {
        localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(config));
    } catch (e) {
        console.warn('Failed to save pretest config to localStorage', e);
    }
}

const state = {
    currentView: 'catalog', // 'catalog' | 'exercise' | 'analysis'
    filters: {
        level: '',
        category: '',
        source: '' // '' | 'nhk' | 'exam'
    },
    activeText: null,        // Loaded TextReadSchema or TextAnalysisSchema
    pendingTextId: null,     // Selected text awaiting modal confirmation
    pendingTextData: null,
    
    // Step-by-Step Wizard State
    currentQuestionIndex: 0, // 0-based index of the active question
    userAnswers: {},         // questionId -> selectedOptionId
    
    timer: {
        seconds: 0,
        intervalId: null
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
    notebookFilter: 'all', // 'all' | 'learning' | 'learned'
    notebookSearchQuery: ''
};

// ============================================================================
// DOM Elements Cache
// ============================================================================

const elements = {
    // Top Bar
    btnHome: document.getElementById('btn-home'),
    exerciseHeaderControls: document.getElementById('exercise-header-controls'),
    headerLevelTag: document.getElementById('header-level-tag'),
    headerCategoryTag: document.getElementById('header-category-tag'),
    headerExamBadge: document.getElementById('header-exam-badge'),
    timerDisplay: document.getElementById('timer-display'),
    timerTarget: document.getElementById('timer-target'),
    btnAbortExercise: document.getElementById('btn-abort-exercise'),
    btnOpenNotebook: document.getElementById('btn-open-notebook'),
    headerSavedCount: document.getElementById('header-saved-count'),

    // Views
    catalogView: document.getElementById('catalog-view'),
    exerciseView: document.getElementById('exercise-view'),

    // Catalog
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
    modalTextTitle: document.getElementById('modal-text-title'),
    modalTimeEstimate: document.getElementById('modal-time-estimate'),
    pretestToggleFurigana: document.getElementById('pretest-toggle-furigana'),
    pretestToggleHints: document.getElementById('pretest-toggle-hints'),
    modalBtnCancel: document.getElementById('modal-btn-cancel'),
    modalBtnClose: document.getElementById('modal-btn-close'),
    modalBtnStart: document.getElementById('modal-btn-start'),
    tagFurigana: document.getElementById('tag-furigana'),
    tagHints: document.getElementById('tag-hints')
};

// ============================================================================
// Translations & Label Helpers
// ============================================================================

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
// Timer Functions
// ============================================================================

function startTimer() {
    stopTimer();
    state.timer.seconds = 0;
    elements.timerDisplay.textContent = '00:00';
    state.timer.intervalId = setInterval(() => {
        state.timer.seconds += 1;
        elements.timerDisplay.textContent = formatTime(state.timer.seconds);
    }, 1000);
}

function stopTimer() {
    if (state.timer.intervalId) {
        clearInterval(state.timer.intervalId);
        state.timer.intervalId = null;
    }
}

// ============================================================================
// Reader Customization (Font Size & Typeface)
// ============================================================================

function setReaderFont(typeface) {
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
}

function adjustFontSize(delta) {
    const newSize = Math.max(16, Math.min(28, state.settings.fontSizePx + delta));
    state.settings.fontSizePx = newSize;
    elements.passageContent.style.fontSize = `${newSize}px`;
}

// ============================================================================
// Catalog Loading & Rendering
// ============================================================================

let cachedCatalogTexts = [];

async function fetchAndRenderCatalog() {
    elements.catalogGrid.innerHTML = '<div class="loading-spinner">Загрузка каталога текстов...</div>';

    const params = new URLSearchParams();
    if (state.filters.level) params.append('level', state.filters.level);
    if (state.filters.category) params.append('category', state.filters.category);

    try {
        const response = await fetch(`/api/texts?${params.toString()}`);
        if (!response.ok) throw new Error('Ошибка загрузки каталога');
        const texts = await response.json();
        cachedCatalogTexts = texts;

        let filteredTexts = texts;
        if (state.filters.source === 'nhk') {
            filteredTexts = filteredTexts.filter(t => t.is_nhk === true);
        } else if (state.filters.source === 'exam') {
            filteredTexts = filteredTexts.filter(t => t.is_nhk === false);
        }

        if (filteredTexts.length === 0) {
            elements.catalogGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: #fff; border-radius: 12px; border: 1px solid var(--washi-border);">
                    <p style="font-size: 1.1rem; color: var(--sumi-600);">По выбранным фильтрам текстов пока нет.</p>
                </div>
            `;
            return;
        }

        elements.catalogGrid.innerHTML = filteredTexts.map(text => `
            <div class="catalog-card">
                <div class="card-top">
                    <div class="card-meta">
                        <span class="level-tag" data-lvl="${text.level}">${text.level}</span>
                        <span class="category-tag">${CATEGORY_NAMES[text.category] || text.category}</span>
                        ${text.is_nhk ? `<span class="nhk-badge">NHK WORLD</span>` : ''}
                        ${text.source_exam ? `<span class="exam-archive-badge">📜 ${text.source_exam}</span>` : ''}
                    </div>
                    <h3 class="card-title">${text.title}</h3>
                    <div class="card-specs">
                        <span class="card-spec-item">⏱️ ${text.recommended_time_min} мин</span>
                        <span class="card-spec-item">❓ ${text.question_count} вопр.</span>
                    </div>
                </div>
                <div class="card-bottom">
                    <button class="btn btn-primary btn-full" onclick="openPretestModal(${text.id})">
                        Начать решение →
                    </button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
        elements.catalogGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--vermilion);">
                Не удалось подключиться к серверу. Пожалуйста, обновите страницу.
            </div>
        `;
    }
}

// ============================================================================
// Pre-Test Settings Modal Logic
// ============================================================================

function openPretestModal(textId) {
    state.pendingTextId = textId;
    const textInfo = cachedCatalogTexts.find(t => t.id === textId);

    if (textInfo) {
        elements.modalTextTitle.textContent = textInfo.title;
        elements.modalTimeEstimate.textContent = textInfo.recommended_time_min;
    } else {
        elements.modalTextTitle.textContent = 'Текст задания';
    }

    elements.pretestToggleFurigana.checked = state.pretestConfig.showFurigana;
    elements.pretestToggleHints.checked = state.pretestConfig.showHintsAndAnalysis;
    updateModalSettingTags();

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
}

function confirmPretestSettingsAndStart() {
    const showFurigana = elements.pretestToggleFurigana.checked;
    const showHints = elements.pretestToggleHints.checked;

    state.pretestConfig.showFurigana = showFurigana;
    state.pretestConfig.showHintsAndAnalysis = showHints;
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
        const response = await fetch(`/api/texts/${textId}`);
        if (!response.ok) throw new Error('Не удалось загрузить задание');

        const textData = await response.json();
        state.activeText = textData;
        state.userAnswers = {};
        state.currentQuestionIndex = 0;
        state.currentView = 'exercise';

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

        elements.timerTarget.textContent = `(Реком.: ${textData.recommended_time_min} мин)`;

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

        // Reset and start stopwatch
        startTimer();

    } catch (err) {
        console.error(err);
        alert('Ошибка при загрузке текста задания.');
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

    // Navigation buttons state
    elements.btnWizardPrev.disabled = (currentQIdx === 0);

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
}

function wizardGoNext() {
    const totalQ = state.activeText.questions.length;
    if (state.currentQuestionIndex < totalQ - 1) {
        state.currentQuestionIndex += 1;
        renderWizard();
    }
}

function wizardGoPrev() {
    if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
        renderWizard();
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
    const timeSpent = state.timer.seconds;

    const answersPayload = Object.entries(state.userAnswers).map(([qId, optId]) => ({
        question_id: parseInt(qId, 10),
        selected_option_id: parseInt(optId, 10)
    }));

    try {
        elements.btnWizardSubmit.disabled = true;
        elements.btnWizardSubmit.textContent = 'Проверка ответов...';

        const response = await fetch(`/api/texts/${state.activeText.id}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                answers: answersPayload,
                time_spent_sec: timeSpent
            })
        });

        if (!response.ok) throw new Error('Ошибка сервера при проверке ответов');

        const analysisData = await response.json();
        state.activeText = analysisData;
        state.currentView = 'analysis';
        state.analysisActiveTabIdx = 0;

        renderAnalysisView(analysisData);

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
    elements.bannerResultMeta.textContent = `Затрачено: ${spentTimeFormatted} | Рекомендовано: ${data.recommended_time_min} мин`;

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
                        explanationBoxHtml = `
                            <div class="option-explanation-box ${expClass}">
                                ${opt.option_explanation}
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
    try {
        const stored = localStorage.getItem(NOTEBOOK_STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (e) {
        console.warn('Failed to load saved words', e);
        return [];
    }
}

function saveWordsToStorage(words) {
    try {
        localStorage.setItem(NOTEBOOK_STORAGE_KEY, JSON.stringify(words));
        updateNotebookBadge();
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

function toggleSaveWord(wordData) {
    if (!wordData || !wordData.word) return;
    let words = getSavedWords();
    const existingIdx = words.findIndex(w => w.word === wordData.word);

    if (existingIdx >= 0) {
        words.splice(existingIdx, 1);
        saveWordsToStorage(words);
        if (elements.popupBtnSave) {
            elements.popupBtnSave.classList.remove('is-saved');
            elements.popupBtnSaveText.textContent = 'В мой словарь';
        }
    } else {
        words.unshift({
            id: Date.now(),
            word: wordData.word,
            reading: wordData.reading || '',
            meaning: wordData.meaning || '',
            level: wordData.level || 'JLPT',
            mastered: false,
            date: new Date().toLocaleDateString()
        });
        saveWordsToStorage(words);
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
    fetch(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}`)
        .then(res => {
            if (res.ok) return res.json();
            throw new Error('Not found');
        })
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

// Personal Notebook UI Handlers
function openNotebookModal() {
    renderNotebookWords();
    elements.savedWordsModalBackdrop.classList.remove('hidden');
}

function closeNotebookModal() {
    elements.savedWordsModalBackdrop.classList.add('hidden');
}

function renderNotebookWords() {
    const allWords = getSavedWords();
    const filter = state.notebookFilter;
    const query = (state.notebookSearchQuery || '').toLowerCase().trim();

    const countAll = allWords.length;
    const countLearned = allWords.filter(w => w.mastered).length;
    const countLearning = countAll - countLearned;

    if (elements.notebookCountAll) elements.notebookCountAll.textContent = countAll;
    if (elements.notebookCountLearning) elements.notebookCountLearning.textContent = countLearning;
    if (elements.notebookCountLearned) elements.notebookCountLearned.textContent = countLearned;
    if (elements.notebookStatsText) elements.notebookStatsText.textContent = `Всего сохранённых слов: ${countAll}`;

    // Filter words
    let filtered = allWords;
    if (filter === 'learning') {
        filtered = filtered.filter(w => !w.mastered);
    } else if (filter === 'learned') {
        filtered = filtered.filter(w => w.mastered);
    }

    if (query) {
        filtered = filtered.filter(w => 
            w.word.toLowerCase().includes(query) ||
            (w.reading && w.reading.toLowerCase().includes(query)) ||
            (w.meaning && w.meaning.toLowerCase().includes(query))
        );
    }

    if (filtered.length === 0) {
        elements.notebookWordsList.innerHTML = `
            <div class="notebook-empty-state">
                <div class="notebook-empty-icon">📖</div>
                <p>В этой категории пока нет слов.</p>
                <small>Выделяйте любые слова в текстах для мгновенного перевода и добавления в словарь.</small>
            </div>
        `;
        return;
    }

    elements.notebookWordsList.innerHTML = filtered.map(w => `
        <div class="notebook-word-card ${w.mastered ? 'is-mastered' : ''}" data-word="${escapeHtml(w.word)}">
            <div class="notebook-word-info">
                <div class="notebook-word-top">
                    <span class="notebook-word-jp">${escapeHtml(w.word)}</span>
                    ${w.reading ? `<span class="notebook-word-reading">${escapeHtml(w.reading)}</span>` : ''}
                    <span class="popup-level-tag">${escapeHtml(w.level || 'JLPT')}</span>
                </div>
                <div class="notebook-word-meaning">${escapeHtml(w.meaning)}</div>
            </div>
            <div class="notebook-word-actions">
                <button class="notebook-btn-icon btn-speak-saved" title="Прослушать" data-speak="${escapeHtml(w.word)}">🔊</button>
                <label class="switch" title="${w.mastered ? 'Отметить как изучаемое' : 'Отметить как выученное'}" style="transform: scale(0.75);">
                    <input type="checkbox" class="cb-toggle-mastered" data-word="${escapeHtml(w.word)}" ${w.mastered ? 'checked' : ''}>
                    <span class="slider round"></span>
                </label>
                <button class="notebook-btn-icon btn-delete-saved" title="Удалить" data-delete="${escapeHtml(w.word)}">🗑️</button>
            </div>
        </div>
    `).join('');
}

function clearAllSavedWords() {
    if (confirm('Вы уверены, что хотите полностью очистить свой словарь?')) {
        saveWordsToStorage([]);
        renderNotebookWords();
    }
}

function returnToCatalog() {
    stopTimer();
    state.currentView = 'catalog';
    state.activeText = null;
    state.userAnswers = {};
    state.currentQuestionIndex = 0;

    elements.exerciseView.classList.add('hidden');
    elements.exerciseHeaderControls.classList.add('hidden');
    elements.catalogView.classList.remove('hidden');
    elements.supplementaryDrawer.classList.add('hidden');
    elements.hardcoreNotice.classList.add('hidden');

    fetchAndRenderCatalog();
}

// ============================================================================
// Event Listeners & Initialization
// ============================================================================

function initEventListeners() {
    // Brand & abort buttons
    elements.btnHome.addEventListener('click', returnToCatalog);
    elements.btnAbortExercise.addEventListener('click', () => {
        if (confirm('Прервать текущее решение и вернуться в каталог?')) {
            returnToCatalog();
        }
    });
    elements.btnBackToCatalog.addEventListener('click', returnToCatalog);

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
    elements.pretestModalBackdrop.addEventListener('click', (e) => {
        if (e.target === elements.pretestModalBackdrop) {
            closePretestModal();
        }
    });

    // Filter pills
    elements.levelPills.addEventListener('click', (e) => {
        const pill = e.target.closest('.filter-pill');
        if (!pill) return;
        elements.levelPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.filters.level = pill.dataset.level;
        fetchAndRenderCatalog();
    });

    elements.categoryPills.addEventListener('click', (e) => {
        const pill = e.target.closest('.filter-pill');
        if (!pill) return;
        elements.categoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.filters.category = pill.dataset.category;
        fetchAndRenderCatalog();
    });

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

    // Interactive Yomichan Dictionary & Saved Words Notebook
    if (elements.btnOpenNotebook) {
        elements.btnOpenNotebook.addEventListener('click', openNotebookModal);
    }
    if (elements.btnCloseNotebook) {
        elements.btnCloseNotebook.addEventListener('click', closeNotebookModal);
    }
    if (elements.savedWordsModalBackdrop) {
        elements.savedWordsModalBackdrop.addEventListener('click', (e) => {
            if (e.target === elements.savedWordsModalBackdrop) {
                closeNotebookModal();
            }
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

    // Global keyboard shortcuts (Esc to close modals / popups)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hidePopupDictionary();
            closeNotebookModal();
            closePretestModal();
        }
    });
}

// Startup
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    updateNotebookBadge();
    fetchAndRenderCatalog();
});
