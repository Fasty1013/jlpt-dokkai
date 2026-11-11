/**
 * JLPT Dokkai Master - Personal Vocabulary Notebook View
 * Renders saved words list, statistics counters, and filter partitions.
 */
import { t } from '../../i18n/index.js';
import { escapeHtml } from '../../utils/dom.js';
import { getSavedWords } from './notebook_storage.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

export function renderNotebookWords(elements = domElements, state = storeState) {
    const currentElements = elements;
    const currentState = state;

    const allWords = getSavedWords(currentState);
    const safeWords = Array.isArray(allWords) ? allWords : [];
    const filter = (currentState && currentState.notebookFilter) || 'all';
    const query = (currentState && currentState.notebookSearchQuery) ? currentState.notebookSearchQuery.toLowerCase().trim() : '';

    const countAll = safeWords.length;
    const countLearned = safeWords.filter(w => w && w.mastered).length;
    const countLearning = countAll - countLearned;

    if (currentElements) {
        if (currentElements.notebookCountAll) currentElements.notebookCountAll.textContent = countAll;
        if (currentElements.notebookCountLearning) currentElements.notebookCountLearning.textContent = countLearning;
        if (currentElements.notebookCountLearned) currentElements.notebookCountLearned.textContent = countLearned;
        if (currentElements.headerSavedCount) currentElements.headerSavedCount.textContent = countAll;
        if (currentElements.notebookStatsText) currentElements.notebookStatsText.textContent = t('notebook.statsTotal', { n: countAll });
    }

    // Filter words safely
    let filtered = safeWords;
    if (filter === 'learning') {
        filtered = filtered.filter(w => w && !w.mastered);
    } else if (filter === 'learned') {
        filtered = filtered.filter(w => w && w.mastered);
    }

    if (query) {
        filtered = filtered.filter(w =>
            (w.word && w.word.toLowerCase().includes(query)) ||
            (w.reading && w.reading.toLowerCase().includes(query)) ||
            (w.meaning && w.meaning.toLowerCase().includes(query))
        );
    }

    const container = currentElements ? currentElements.notebookWordsList : null;
    if (!container) return;

    if (!filtered || filtered.length === 0) {
        container.innerHTML = `
            <div class="notebook-empty-state">
                <div class="notebook-empty-icon">📖</div>
                <p>${t('notebook.empty')}</p>
                <small>${t('notebook.emptyHint')}</small>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(w => {
        const wordText = escapeHtml(w.word || '');
        const readingText = escapeHtml(w.reading || '');
        const levelText = escapeHtml(w.level || 'JLPT');
        const meaningText = escapeHtml(w.meaning || '');
        const isMastered = Boolean(w.mastered);

        return `
        <div class="notebook-word-card ${isMastered ? 'is-mastered' : ''}" data-word="${wordText}">
            <div class="notebook-word-info">
                <div class="notebook-word-top">
                    <span class="notebook-word-jp" lang="ja">${wordText}</span>
                    ${readingText ? `<span class="notebook-word-reading">${readingText}</span>` : ''}
                    <span class="popup-level-tag">${levelText}</span>
                </div>
                <div class="notebook-word-meaning">${meaningText}</div>
            </div>
            <div class="notebook-word-actions">
                <button type="button" class="notebook-btn-icon btn-speak-saved" title="${t('notebook.listen')}" data-action="notebook-speak-word" data-word="${wordText}">🔊</button>
                <label class="switch" title="${isMastered ? t('notebook.markLearning') : t('notebook.markLearned')}" style="transform: scale(0.75);">
                    <input type="checkbox" class="cb-toggle-mastered" data-action="notebook-toggle-mastered" data-word="${wordText}" ${isMastered ? 'checked' : ''}>
                    <span class="slider round"></span>
                </label>
                <button type="button" class="notebook-btn-icon btn-delete-saved" title="${t('notebook.delete')}" data-action="notebook-delete-word" data-word="${wordText}">🗑️</button>
            </div>
        </div>
        `;
    }).join('');
}

