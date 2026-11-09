/**
 * JLPT Dokkai Master - State & DOM Elements Barrel Export
 */

import { state } from './store.js';
import { elements, initElementsCache } from './elements.js';

export {
    state,
    elements,
    initElementsCache
};

if (typeof window !== 'undefined') {
    window.DokkaiState = {
        state,
        elements,
        initElementsCache
    };
    window.state = state;
    window.elements = elements;
}

