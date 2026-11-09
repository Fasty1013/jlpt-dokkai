/**
 * JLPT Dokkai Master - Central Application State Store
 * Single source of truth for runtime application state.
 */

import { loadStoredConfig } from '../features/formatting/config.js';

export const state = {
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

if (typeof window !== 'undefined') {
    window.DokkaiStore = { state };
    window.state = state;
}

