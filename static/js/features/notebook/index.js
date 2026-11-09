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

export {
    NOTEBOOK_STORAGE_KEY,
    getSavedWords,
    saveWordsToStorage,
    updateNotebookBadge,
    isWordSaved,
    toggleSaveWord,
    clearAllSavedWords,
    renderNotebookWords
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
        renderNotebookWords
    };

    window.getSavedWords = () => getSavedWords(window.state);
    window.saveWordsToStorage = (words) => saveWordsToStorage(words, window.state, window.elements);
    window.updateNotebookBadge = () => updateNotebookBadge(window.elements, window.state);
    window.isWordSaved = (wordText) => isWordSaved(wordText, window.state);
    window.renderNotebookWords = () => renderNotebookWords(window.elements, window.state);
}

