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

    window.getSavedWords = () => getSavedWords();
    window.saveWordsToStorage = (words) => saveWordsToStorage(words);
    window.updateNotebookBadge = () => updateNotebookBadge();
    window.isWordSaved = (wordText) => isWordSaved(wordText);
    window.renderNotebookWords = () => renderNotebookWords();
}

