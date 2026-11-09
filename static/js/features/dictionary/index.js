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
}

