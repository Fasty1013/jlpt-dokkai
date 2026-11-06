/**
 * JLPT Dokkai Master - Interactive Popup Dictionary
 * Yomichan-style inline hover/selection/click dictionary with intelligent viewport positioning.
 */
import { isWordSaved } from '../notebook/notebook_storage.js';

export function showPopupDictionary(wordData, clientX, clientY, elements, state) {
    if (!wordData || !wordData.word) return;
    const currentElements = elements || (typeof window !== 'undefined' ? window.elements : null);
    const currentState = state || (typeof window !== 'undefined' ? window.state : null);

    if (currentState) {
        currentState.activePopupWord = wordData;
    }

    if (!currentElements || !currentElements.popupDictionaryCard) return;

    if (currentElements.popupWord) currentElements.popupWord.textContent = wordData.word;
    if (currentElements.popupReading) currentElements.popupReading.textContent = wordData.reading || '';
    if (currentElements.popupLevel) currentElements.popupLevel.textContent = wordData.level || 'JLPT';
    if (currentElements.popupMeaning) currentElements.popupMeaning.textContent = wordData.meaning || 'Перевод не найден';

    const saved = isWordSaved(wordData.word, currentState);
    if (currentElements.popupBtnSave) {
        if (saved) {
            currentElements.popupBtnSave.classList.add('is-saved');
            if (currentElements.popupBtnSaveText) currentElements.popupBtnSaveText.textContent = '✓ В словаре';
        } else {
            currentElements.popupBtnSave.classList.remove('is-saved');
            if (currentElements.popupBtnSaveText) currentElements.popupBtnSaveText.textContent = 'В мой словарь';
        }
    }

    currentElements.popupDictionaryCard.classList.remove('hidden');

    // Intelligent positioning
    const cardRect = currentElements.popupDictionaryCard.getBoundingClientRect();
    let top = clientY - cardRect.height - 12;
    let left = clientX - cardRect.width / 2;

    if (top < 10) {
        top = clientY + 24;
    }
    if (left < 10) {
        left = 10;
    }
    const winWidth = typeof window !== 'undefined' ? window.innerWidth : 1024;
    if (left + cardRect.width > winWidth - 10) {
        left = winWidth - cardRect.width - 10;
    }

    currentElements.popupDictionaryCard.style.top = `${top}px`;
    currentElements.popupDictionaryCard.style.left = `${left}px`;
}

export function hidePopupDictionary(elements, state) {
    const currentElements = elements || (typeof window !== 'undefined' ? window.elements : null);
    const currentState = state || (typeof window !== 'undefined' ? window.state : null);

    if (currentElements && currentElements.popupDictionaryCard) {
        currentElements.popupDictionaryCard.classList.add('hidden');
    }
    if (currentState) {
        currentState.activePopupWord = null;
    }
}

export function lookupAndShowWord(query, clientX, clientY, elements, state) {
    const currentElements = elements || (typeof window !== 'undefined' ? window.elements : null);
    const currentState = state || (typeof window !== 'undefined' ? window.state : null);

    if (currentState && !currentState.popupDictEnabled) return;
    if (!query) return;

    // Clean word from rubies and punctuation
    const cleanQuery = query.replace(/[、。！？\s\t\n・「」『』（）]/g, '').trim();
    if (!cleanQuery || cleanQuery.length > 20) return;

    // 1. Check local text vocabulary if active
    if (currentState && currentState.activeText && currentState.activeText.vocabulary) {
        const localMatch = currentState.activeText.vocabulary.find(
            v => v.word === cleanQuery || cleanQuery.includes(v.word) || v.word.includes(cleanQuery)
        );
        if (localMatch) {
            showPopupDictionary({
                word: localMatch.word,
                reading: localMatch.furigana ? `[${localMatch.furigana}]` : '',
                meaning: localMatch.translation,
                level: currentState.activeText.level || 'JLPT'
            }, clientX, clientY, currentElements, currentState);
            return;
        }
    }

    // 2. Fetch from backend dictionary API
    const lookupPromise = (typeof window !== 'undefined' && window.DokkaiApi && window.DokkaiApi.lookupWord)
        ? window.DokkaiApi.lookupWord(cleanQuery)
        : fetch(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}`).then(res => {
            if (res.ok) return res.json();
            throw new Error('Not found');
        });

    lookupPromise
        .then(data => {
            showPopupDictionary({
                word: data.word,
                reading: data.reading ? `[${data.reading}]` : '',
                meaning: data.meaning,
                level: data.level || 'JLPT'
            }, clientX, clientY, currentElements, currentState);
        })
        .catch(() => {
            // If unknown word, still allow saving or show kanji
            if (cleanQuery.length >= 1 && cleanQuery.length <= 8) {
                showPopupDictionary({
                    word: cleanQuery,
                    reading: '',
                    meaning: 'Слово из текста (сохраните для разбора)',
                    level: (currentState && currentState.activeText) ? currentState.activeText.level : 'JLPT'
                }, clientX, clientY, currentElements, currentState);
            }
        });
}

export function togglePopupDictStatus(elements, state) {
    const currentElements = elements || (typeof window !== 'undefined' ? window.elements : null);
    const currentState = state || (typeof window !== 'undefined' ? window.state : null);

    if (currentState) {
        currentState.popupDictEnabled = !currentState.popupDictEnabled;
        if (currentElements) {
            if (currentElements.popupDictStatus) {
                currentElements.popupDictStatus.textContent = currentState.popupDictEnabled ? 'ВКЛ' : 'ВЫКЛ';
            }
            if (currentElements.btnTogglePopupDict) {
                currentElements.btnTogglePopupDict.classList.toggle('active', currentState.popupDictEnabled);
            }
        }
        if (!currentState.popupDictEnabled) {
            hidePopupDictionary(currentElements, currentState);
        }
    }
}

