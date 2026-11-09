/**
 * JLPT Dokkai Master - Personal Vocabulary Notebook Storage
 * Manages saving, deleting, and syncing notebook words between LocalStorage and DokkaiStorage (IndexedDB).
 */

import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

export const NOTEBOOK_STORAGE_KEY = 'dokkai_saved_words';

export function getSavedWords(state = storeState) {
    const currentState = state;
    if (currentState && Array.isArray(currentState.savedWords) && currentState.savedWords.length > 0) {
        return currentState.savedWords;
    }
    if (typeof localStorage !== 'undefined') {
        try {
            const stored = localStorage.getItem(NOTEBOOK_STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    if (currentState) {
                        currentState.savedWords = parsed;
                    }
                    return parsed;
                }
            }
        } catch (e) {
            console.warn('Failed to load saved words, using fallback []', e);
        }
    }
    return (currentState && Array.isArray(currentState.savedWords)) ? currentState.savedWords : [];
}

export async function saveWordsToStorage(words, state = storeState, elements = domElements) {
    const currentState = state;
    const currentElements = elements;

    if (currentState) {
        currentState.savedWords = words;
    }
    try {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem(NOTEBOOK_STORAGE_KEY, JSON.stringify(words));
        }
        updateNotebookBadge(currentElements, currentState);
        if (typeof window !== 'undefined' && window.DokkaiStorage) {
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

export function updateNotebookBadge(elements = domElements, state = storeState) {
    const currentElements = elements;
    const words = getSavedWords(state);
    const count = words.length;
    if (currentElements && currentElements.headerSavedCount) {
        currentElements.headerSavedCount.textContent = count;
    }
}

export function isWordSaved(wordText, state = storeState) {
    const words = getSavedWords(state);
    return words.some(w => w && w.word === wordText);
}

export async function toggleSaveWord(wordData, state = storeState, elements = domElements, onUpdate) {
    if (!wordData || !wordData.word) return;
    const currentState = state;
    const currentElements = elements;

    let words = getSavedWords(currentState);
    const existingIdx = words.findIndex(w => w && w.word === wordData.word);

    if (existingIdx >= 0) {
        words.splice(existingIdx, 1);
        await saveWordsToStorage(words, currentState, currentElements);
        if (typeof window !== 'undefined' && window.DokkaiStorage) {
            await window.DokkaiStorage.removeWord(wordData.word);
        }
        if (currentElements && currentElements.popupBtnSave) {
            currentElements.popupBtnSave.classList.remove('is-saved');
            if (currentElements.popupBtnSaveText) {
                currentElements.popupBtnSaveText.textContent = 'В мой словарь';
            }
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
        await saveWordsToStorage(words, currentState, currentElements);
        if (typeof window !== 'undefined' && window.DokkaiStorage) {
            await window.DokkaiStorage.saveWord(newWord, true);
        }
        if (currentElements && currentElements.popupBtnSave) {
            currentElements.popupBtnSave.classList.add('is-saved');
            if (currentElements.popupBtnSaveText) {
                currentElements.popupBtnSaveText.textContent = '✓ В словаре';
            }
        }
    }

    if (typeof onUpdate === 'function') {
        onUpdate();
    } else if (typeof window !== 'undefined' && typeof window.renderNotebookWords === 'function') {
        window.renderNotebookWords();
    }
}

export async function clearAllSavedWords(state = storeState, elements = domElements, onUpdate) {
    const currentState = state;
    const currentElements = elements;

    if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
        if (!window.confirm('Вы уверены, что хотите полностью очистить свой словарь?')) {
            return;
        }
    }
    await saveWordsToStorage([], currentState, currentElements);
    if (typeof onUpdate === 'function') {
        onUpdate();
    } else if (typeof window !== 'undefined' && typeof window.renderNotebookWords === 'function') {
        window.renderNotebookWords();
    }
}

