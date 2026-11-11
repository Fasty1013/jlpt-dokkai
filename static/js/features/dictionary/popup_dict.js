/**
 * JLPT Dokkai Master - Interactive Popup Dictionary
 * Yomichan-style inline hover/selection/click dictionary with intelligent viewport positioning.
 */
import { t, getLang } from '../../i18n/index.js';
import { isWordSaved } from '../notebook/notebook_storage.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * One-line note under the meaning: where it comes from / why it is not in the UI language.
 * Empty for Russian (the historical behaviour is unchanged).
 */
function describeMeaningSource(wordData) {
    if (getLang() === 'ru') return '';
    if (wordData.meaningLang === 'ru') return t('popup.noteRussianOnly');
    if (wordData.fallback && wordData.meaningLang === 'en') return t('popup.noteEnglishFallback');
    if (wordData.source === 'jmdict') return t('popup.noteJmdict');
    if (wordData.source === 'manual') return t('popup.noteManual');
    return '';
}

export function showPopupDictionary(wordData, clientX, clientY, elements = domElements, state = storeState) {
    if (!wordData || !wordData.word) return;
    const currentElements = elements;
    const currentState = state;

    if (currentState) {
        currentState.activePopupWord = wordData;
    }

    if (!currentElements || !currentElements.popupDictionaryCard) return;

    if (currentElements.popupWord) currentElements.popupWord.textContent = wordData.word;
    if (currentElements.popupReading) currentElements.popupReading.textContent = wordData.reading || '';
    if (currentElements.popupLevel) currentElements.popupLevel.textContent = wordData.level || 'JLPT';
    if (currentElements.popupMeaning) {
        currentElements.popupMeaning.textContent = wordData.meaning || (wordData.noMeaningKey ? t(wordData.noMeaningKey) : t('popup.notFound'));
    }
    if (currentElements.popupMeaningNote) {
        const note = describeMeaningSource(wordData);
        currentElements.popupMeaningNote.textContent = note;
        currentElements.popupMeaningNote.classList.toggle('hidden', !note);
    }

    const saved = isWordSaved(wordData.word, currentState);
    if (currentElements.popupBtnSave) {
        if (saved) {
            currentElements.popupBtnSave.classList.add('is-saved');
            if (currentElements.popupBtnSaveText) currentElements.popupBtnSaveText.textContent = t('popup.saved');
        } else {
            currentElements.popupBtnSave.classList.remove('is-saved');
            if (currentElements.popupBtnSaveText) currentElements.popupBtnSaveText.textContent = t('popup.save');
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

export function hidePopupDictionary(elements = domElements, state = storeState) {
    const currentElements = elements;
    const currentState = state;

    if (currentElements && currentElements.popupDictionaryCard) {
        currentElements.popupDictionaryCard.classList.add('hidden');
    }
    if (currentState) {
        currentState.activePopupWord = null;
    }
}

export function lookupAndShowWord(query, clientX, clientY, elements = domElements, state = storeState) {
    const currentElements = elements;
    const currentState = state;

    if (currentState && !currentState.popupDictEnabled) return;
    if (!query) return;

    // Clean word from rubies and punctuation
    const cleanQuery = query.replace(/[、。！？\s\t\n・「」『』（）]/g, '').trim();
    if (!cleanQuery || cleanQuery.length > 20) return;

    // 1. Check local text vocabulary if active (Russian translations; Russian UI only - see 1b)
    if (getLang() === 'ru' && currentState && currentState.activeText && currentState.activeText.vocabulary) {
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

    // 1b. Non-Russian UI: the local vocabulary holds Russian translations only, so ask the server for
    //     the selected language (manual glossary / JMdict). Local data still supplies the reading in context.
    const uiLang = getLang();
    if (uiLang !== 'ru') {
        const localMatch = (currentState && currentState.activeText && currentState.activeText.vocabulary)
            ? currentState.activeText.vocabulary.find(v => v.word === cleanQuery || cleanQuery.includes(v.word) || v.word.includes(cleanQuery))
            : null;
        const level = (currentState && currentState.activeText && currentState.activeText.level) || 'JLPT';
        const request = (typeof window !== 'undefined' && window.DokkaiApi && window.DokkaiApi.lookupWord)
            ? window.DokkaiApi.lookupWord(cleanQuery, uiLang)
            : fetch(`/api/dictionary/lookup?q=${encodeURIComponent(cleanQuery)}&lang=${encodeURIComponent(uiLang)}`).then(res => {
                if (res.ok) return res.json();
                throw new Error('Not found');
            });
        request
            .then(data => {
                const reading = data.reading || (localMatch && localMatch.furigana) || '';
                showPopupDictionary({
                    word: data.word,
                    reading: reading ? `[${reading}]` : '',
                    meaning: data.meaning,
                    noMeaningKey: uiLang === 'ja' && !data.meaning ? 'popup.noJapaneseDefinition' : undefined,
                    meaningLang: data.lang,
                    source: data.source,
                    fallback: Boolean(data.fallback),
                    level: data.level || level
                }, clientX, clientY, currentElements, currentState);
            })
            .catch(() => {
                if (localMatch) {
                    // honest fallback: the only translation we have is the Russian one, and it is labelled as such
                    showPopupDictionary({
                        word: localMatch.word,
                        reading: localMatch.furigana ? `[${localMatch.furigana}]` : '',
                        meaning: localMatch.translation,
                        meaningLang: 'ru',
                        fallback: true,
                        level
                    }, clientX, clientY, currentElements, currentState);
                } else if (cleanQuery.length >= 1 && cleanQuery.length <= 8) {
                    showPopupDictionary({ word: cleanQuery, reading: '', meaning: t('popup.unknownWord'), level }, clientX, clientY, currentElements, currentState);
                }
            });
        return;
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
                    meaning: t('popup.unknownWord'),
                    level: (currentState && currentState.activeText) ? currentState.activeText.level : 'JLPT'
                }, clientX, clientY, currentElements, currentState);
            }
        });
}

export function togglePopupDictStatus(elements = domElements, state = storeState) {
    const currentElements = elements;
    const currentState = state;

    if (currentState) {
        currentState.popupDictEnabled = !currentState.popupDictEnabled;
        if (currentElements) {
            if (currentElements.popupDictStatus) {
                currentElements.popupDictStatus.textContent = currentState.popupDictEnabled ? t('common.on') : t('common.off');
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

