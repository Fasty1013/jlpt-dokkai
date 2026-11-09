/**
 * JLPT Dokkai Master - Notebook Feature Entry Point
 */
import {
    NOTEBOOK_STORAGE_KEY,
    getSavedWords,
    saveWordsToStorage,
    updateNotebookBadge,
    isWordSaved,
    toggleSaveWord,
    clearAllSavedWords
} from './notebook_storage.js';
import { renderNotebookWords } from './notebook_view.js';
import { initNotebookEvents } from './notebook_events.js';

export {
    NOTEBOOK_STORAGE_KEY,
    getSavedWords,
    saveWordsToStorage,
    updateNotebookBadge,
    isWordSaved,
    toggleSaveWord,
    clearAllSavedWords,
    renderNotebookWords,
    initNotebookEvents
};

if (typeof window !== 'undefined') {
    window.DokkaiNotebook = {
        NOTEBOOK_STORAGE_KEY,
        getSavedWords,
        saveWordsToStorage,
        updateNotebookBadge,
        isWordSaved,
        toggleSaveWord,
        clearAllSavedWords,
        renderNotebookWords,
        initEvents: initNotebookEvents
    };

    window.getSavedWords = () => getSavedWords(window.state);
    window.saveWordsToStorage = (words) => saveWordsToStorage(words, window.state, window.elements);
    window.updateNotebookBadge = () => updateNotebookBadge(window.elements, window.state);
    window.isWordSaved = (wordText) => isWordSaved(wordText, window.state);
    window.renderNotebookWords = () => renderNotebookWords(window.elements, window.state);
}

