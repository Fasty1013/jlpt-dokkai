/**
 * JLPT Dokkai Master - Dictionary Feature Entry Point
 */
import {
    showPopupDictionary,
    hidePopupDictionary,
    lookupAndShowWord,
    togglePopupDictStatus
} from './popup_dict.js';

import { initDictionaryEvents } from './dictionary_events.js';

export {
    showPopupDictionary,
    hidePopupDictionary,
    lookupAndShowWord,
    togglePopupDictStatus,
    initDictionaryEvents
};

if (typeof window !== 'undefined') {
    window.DokkaiDictionary = {
        showPopupDictionary,
        hidePopupDictionary,
        lookupAndShowWord,
        togglePopupDictStatus,
        initEvents: initDictionaryEvents
    };
}

