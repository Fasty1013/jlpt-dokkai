/**
 * JLPT Dokkai Master - Dictionary Feature Entry Point
 */
import {
    showPopupDictionary,
    hidePopupDictionary,
    lookupAndShowWord,
    togglePopupDictStatus
} from './popup_dict.js';

export {
    showPopupDictionary,
    hidePopupDictionary,
    lookupAndShowWord,
    togglePopupDictStatus
};

if (typeof window !== 'undefined') {
    window.DokkaiDictionary = {
        showPopupDictionary,
        hidePopupDictionary,
        lookupAndShowWord,
        togglePopupDictStatus
    };

    window.showPopupDictionary = (wordData, clientX, clientY) => showPopupDictionary(wordData, clientX, clientY, window.elements, window.state);
    window.hidePopupDictionary = () => hidePopupDictionary(window.elements, window.state);
    window.lookupAndShowWord = (query, clientX, clientY) => lookupAndShowWord(query, clientX, clientY, window.elements, window.state);
    window.togglePopupDictStatus = () => togglePopupDictStatus(window.elements, window.state);
}

