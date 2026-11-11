/**
 * JLPT Dokkai Master - Domain Labels & Categorization Constants
 * Display texts live in the i18n dictionaries (keys trap.<type> and category.<key>).
 */
import { t } from '../i18n/index.js';

const TRAP_TYPES = [
    'overgeneralization',
    'opposite_meaning',
    'not_mentioned',
    'partial_match',
    'extreme_condition',
    'subject_swap',
    'fact_opinion_confusion',
    'temporal_mismatch',
    'misinterpretation'
];

const CATEGORY_KEYS = ['short', 'medium', 'long', 'info_search', 'article'];

/** Localized trap label, or undefined for an unknown trap type. */
export function getTrapLabel(type) {
    return TRAP_TYPES.includes(type) ? t(`trap.${type}`) : undefined;
}

/** Localized category name, or undefined for an unknown category. */
export function getCategoryName(category) {
    return CATEGORY_KEYS.includes(category) ? t(`category.${category}`) : undefined;
}
