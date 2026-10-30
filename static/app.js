/**
 * JLPT Dokkai Master - Frontend Application Logic (Vanilla JS ES6+)
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
    }
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

    // Exercise Right Pane (Questions)
    answeredCount: document.getElementById('answered-count'),
    totalQuestionsCount: document.getElementById('total-questions-count'),
    questionsForm: document.getElementById('questions-form'),
    questionsList: document.getElementById('questions-list'),
    btnSubmitAnswers: document.getElementById('btn-submit-answers'),
    submitActionBar: document.getElementById('submit-action-bar'),

    // Analysis Post-Submit Banner & Tools
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
// Pre-Test Settings Modal Logic (Feature 2)
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

    // Load current config into toggle checkboxes
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
// Exercise (Strict Anti-Cheat Reading Mode)
// ============================================================================

async function startExercise(textId) {
    try {
        const response = await fetch(`/api/texts/${textId}`);
        if (!response.ok) throw new Error('Не удалось загрузить задание');

        const textData = await response.json();
        state.activeText = textData;
        state.userAnswers = {};
        state.currentView = 'exercise';

        // Switch Views
        elements.catalogView.classList.add('hidden');
        elements.exerciseView.classList.remove('hidden');
        elements.exerciseHeaderControls.classList.remove('hidden');
        elements.analysisBanner.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');
        elements.submitActionBar.classList.remove('hidden');

        // Apply pre-test settings to Header
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

        // Apply pre-test Furigana setting
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

        // Show/Hide Hardcore Notice
        if (!state.pretestConfig.showHintsAndAnalysis) {
            elements.hardcoreNotice.classList.remove('hidden');
        } else {
            elements.hardcoreNotice.classList.add('hidden');
        }

        // Render Questions (Strict Reading Mode: No answers leaked!)
        renderQuestionsForReading(textData.questions);

        // Reset and start stopwatch
        startTimer();

    } catch (err) {
        console.error(err);
        alert('Ошибка при загрузке текста задания.');
    }
}

function renderQuestionsForReading(questions) {
    elements.totalQuestionsCount.textContent = questions.length;
    elements.answeredCount.textContent = '0';
    elements.btnSubmitAnswers.disabled = true;

    elements.questionsList.innerHTML = questions.map((q) => `
        <div class="question-card" id="card-q-${q.id}">
            <div class="question-top">
                <span class="question-num-badge">№${q.question_number}</span>
                <p class="question-prompt">${q.question_text}</p>
            </div>
            <div class="options-group">
                ${q.options.map(opt => `
                    <div class="option-item" id="opt-item-${opt.id}">
                        <label class="option-label" for="radio-opt-${opt.id}">
                            <input 
                                type="radio" 
                                id="radio-opt-${opt.id}" 
                                name="question_${q.id}" 
                                value="${opt.id}" 
                                class="option-radio"
                                onchange="handleOptionSelect(${q.id}, ${opt.id})"
                            >
                            <span class="option-text">${opt.option_number}. ${opt.option_text}</span>
                        </label>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function handleOptionSelect(questionId, optionId) {
    state.userAnswers[questionId] = optionId;

    // Highlight selected option visually
    const qCard = document.getElementById(`card-q-${questionId}`);
    if (qCard) {
        qCard.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
        const optItem = document.getElementById(`opt-item-${optionId}`);
        if (optItem) optItem.classList.add('selected');
    }

    // Update answered count
    const totalQuestions = state.activeText.questions.length;
    const answeredCount = Object.keys(state.userAnswers).length;
    elements.answeredCount.textContent = answeredCount;

    // Enable submit if and only if all questions are answered
    if (answeredCount === totalQuestions) {
        elements.btnSubmitAnswers.disabled = false;
        elements.btnSubmitAnswers.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
        elements.btnSubmitAnswers.disabled = true;
    }
}

// ============================================================================
// Submission & Analysis Mode (Post-Submit Flow)
// ============================================================================

async function submitAnswers(e) {
    e.preventDefault();

    const totalQuestions = state.activeText.questions.length;
    const answeredCount = Object.keys(state.userAnswers).length;

    if (answeredCount < totalQuestions) {
        alert('Пожалуйста, ответьте на все вопросы перед отправкой!');
        return;
    }

    // Stop stopwatch
    stopTimer();
    const timeSpent = state.timer.seconds;

    // Prepare payload
    const answersPayload = Object.entries(state.userAnswers).map(([qId, optId]) => ({
        question_id: parseInt(qId, 10),
        selected_option_id: parseInt(optId, 10)
    }));

    try {
        elements.btnSubmitAnswers.disabled = true;
        elements.btnSubmitAnswers.textContent = 'Проверка ответов...';

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

        // Render analysis respecting pre-test configurations
        renderAnalysisView(analysisData);

    } catch (err) {
        console.error(err);
        alert('Не удалось отправить ответы на проверку.');
        elements.btnSubmitAnswers.disabled = false;
        elements.btnSubmitAnswers.textContent = 'Проверить ответы';
    }
}

function renderAnalysisView(data) {
    // Hide submit button bar
    elements.submitActionBar.classList.add('hidden');

    // Show Analysis Banner
    elements.analysisBanner.classList.remove('hidden');
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
        // Normal interactive analysis tools enabled
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
        // Hardcore Mode: Disable evidence, hide translation & vocabulary tools
        state.settings.evidenceVisible = false;
        elements.passageContent.classList.remove('show-evidence');
        elements.btnToggleEvidence.classList.add('hidden');
        elements.btnToggleTranslation.classList.add('hidden');
        elements.btnToggleVocab.classList.add('hidden');
        elements.supplementaryDrawer.classList.add('hidden');
    }

    // Render Questions Breakdown
    elements.questionsList.innerHTML = data.questions.map(q => {
        return `
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

                        // If hints are enabled, show detailed option explanation
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

                <!-- General question analysis & Evidence locator (Only if hints enabled) -->
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
    }).join('');

    // Smoothly scroll to top of right pane to see results
    document.querySelector('.split-pane-right').scrollTo({ top: 0, behavior: 'smooth' });
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

function returnToCatalog() {
    stopTimer();
    state.currentView = 'catalog';
    state.activeText = null;
    state.userAnswers = {};

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

    // Form submission
    elements.questionsForm.addEventListener('submit', submitAnswers);

    // Analysis tools
    elements.btnToggleFurigana.addEventListener('click', toggleFurigana);
    elements.btnToggleEvidence.addEventListener('click', toggleEvidence);
    elements.btnToggleTranslation.addEventListener('click', () => toggleSupplementaryDrawer('translation'));
    elements.btnToggleVocab.addEventListener('click', () => toggleSupplementaryDrawer('vocab'));
    elements.btnCloseDrawer.addEventListener('click', () => elements.supplementaryDrawer.classList.add('hidden'));
}

// Startup
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    fetchAndRenderCatalog();
});
