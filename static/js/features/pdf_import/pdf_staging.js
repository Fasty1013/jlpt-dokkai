/**
 * JLPT Dokkai Master - PDF Ingestion & Staging Management
 * Client-side interface for PDF book upload, preview of extracted exercises,
 * question/option correction, and publishing into active catalog.
 * Note: Never commits user PDFs to git. Server-side /api/admin/* endpoints remain untouched.
 */

import { CATEGORY_NAMES } from '../../constants/labels.js';
import { formatFileSize } from '../../utils/index.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

let currentDraftsCache = [];

function getElements() {
    return domElements || {};
}

function getState() {
    return storeState || {};
}

export function getCurrentDraftsCache() {
    return currentDraftsCache;
}

export function setCurrentDraftsCache(drafts) {
    currentDraftsCache = Array.isArray(drafts) ? drafts : [];
}

/**
 * Handle selection of PDF file via input or drag-and-drop.
 * @param {File} file 
 */
export function handlePdfFileSelected(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Пожалуйста, выберите файл в формате .pdf');
        return;
    }
    const state = getState();
    state.selectedPdfFile = file;
    const els = getElements();
    if (els.dropzoneFileName) els.dropzoneFileName.textContent = file.name;
    if (els.dropzoneFileSize) els.dropzoneFileSize.textContent = formatFileSize(file.size);
    if (els.dropzonePrompt) els.dropzonePrompt.classList.add('hidden');
    if (els.dropzoneFileInfo) els.dropzoneFileInfo.classList.remove('hidden');
}

/**
 * Clear currently selected PDF file and reset dropzone state.
 */
export function clearSelectedPdfFile() {
    const state = getState();
    state.selectedPdfFile = null;
    const els = getElements();
    if (els.pdfFileInput) els.pdfFileInput.value = '';
    if (els.dropzonePrompt) els.dropzonePrompt.classList.remove('hidden');
    if (els.dropzoneFileInfo) els.dropzoneFileInfo.classList.add('hidden');
}

/**
 * Upload selected PDF file to server for OCR & exercise extraction.
 * @param {Event} e 
 */
export async function handlePdfUpload(e) {
    if (e && e.preventDefault) e.preventDefault();
    const state = getState();
    if (!state.selectedPdfFile) {
        alert('Пожалуйста, выберите или перетащите PDF файл книги.');
        return;
    }

    const els = getElements();
    const formData = new FormData();
    formData.append('file', state.selectedPdfFile);
    formData.append('level', els.importLevel ? els.importLevel.value : 'N3');
    formData.append('category', els.importCategory ? els.importCategory.value : 'short');
    const titleVal = els.importTitleOverride ? els.importTitleOverride.value.trim() : '';
    if (titleVal) {
        formData.append('title_override', titleVal);
    }

    if (els.btnStartUpload) els.btnStartUpload.disabled = true;
    if (els.uploadLoadingSpinner) els.uploadLoadingSpinner.classList.remove('hidden');
    if (els.uploadStatusText) els.uploadStatusText.textContent = 'Распознавание книги: извлечение страниц, вопросов и ключей...';

    try {
        const resp = await fetch('/api/admin/upload-pdf', {
            method: 'POST',
            body: formData
        });

        const data = await resp.json();
        if (!resp.ok || !data.success) {
            throw new Error(data.error || data.detail || 'Не удалось распознать PDF');
        }

        clearSelectedPdfFile();
        if (els.importTitleOverride) els.importTitleOverride.value = '';

        await fetchAndRenderDrafts();

        const count = data.drafts ? data.drafts.length : 0;
        alert(`✓ Успешно! Извлечено заданий/текстов: ${count}. Они отображаются в песочнице черновиков ниже.`);
    } catch (err) {
        console.error('PDF upload error:', err);
        alert(`Ошибка при обработке PDF:\n${err.message}`);
    } finally {
        if (els.btnStartUpload) els.btnStartUpload.disabled = false;
        if (els.uploadLoadingSpinner) els.uploadLoadingSpinner.classList.add('hidden');
    }
}

/**
 * Fetch list of current staging drafts from backend and update badges/list.
 */
export async function fetchAndRenderDrafts() {
    const els = getElements();
    try {
        const resp = await fetch('/api/admin/drafts');
        if (!resp.ok) return;
        const drafts = await resp.json();
        currentDraftsCache = Array.isArray(drafts) ? drafts : [];

        // Update badge counts
        const count = currentDraftsCache.length;
        if (els.draftsCount) els.draftsCount.textContent = count;
        if (els.headerDraftsCount) {
            els.headerDraftsCount.textContent = count;
            if (count > 0) {
                els.headerDraftsCount.classList.remove('hidden');
            } else {
                els.headerDraftsCount.classList.add('hidden');
            }
        }

        renderDraftsList(currentDraftsCache);
    } catch (err) {
        console.error('Failed to fetch drafts:', err);
    }
}

/**
 * Render the list of draft cards in the staging area.
 * @param {Array} drafts 
 */
export function renderDraftsList(drafts) {
    const els = getElements();
    if (!els.stagingDraftsList) return;

    if (!drafts || drafts.length === 0) {
        els.stagingDraftsList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📭</span>
                <h3>Песочница черновиков пуста</h3>
                <p>Загрузите PDF книгу выше — распознанные тексты и вопросы появятся здесь перед публикацией.</p>
            </div>
        `;
        return;
    }

    els.stagingDraftsList.innerHTML = drafts.map(draft => {
        const confidencePct = Math.round((draft.confidence || 0) * 100);
        const confColor = confidencePct >= 80 ? 'color-good' : (confidencePct >= 60 ? 'color-med' : 'color-low');
        const needsReviewBadge = draft.needs_review
            ? `<span class="badge-review-needed">⚠️ Требует проверки</span>`
            : `<span class="badge-review-ready">✓ Готов к публикации</span>`;

        const warningsHtml = (draft.needs_manual_review && draft.needs_manual_review.length > 0)
            ? `<div class="draft-warnings-box">
                <strong>Замечания системы:</strong>
                <ul>${draft.needs_manual_review.map(r => `<li>${r}</li>`).join('')}</ul>
               </div>`
            : '';

        const questionsHtml = (draft.questions || []).map((q, qIdx) => {
            const hasMatched = q.answer_matched;
            const matchStatus = hasMatched
                ? `<span class="match-badge match-ok">✓ Ответ найден в ключе</span>`
                : `<span class="match-badge match-missing">✗ Ответ не найден в ключе (выберите верный)</span>`;

            const optionsHtml = (q.options || []).map(opt => {
                const isChecked = opt.is_correct ? 'checked' : '';
                return `
                    <label class="draft-option-row">
                        <input type="radio" name="opt-correct-${draft.slug}-${qIdx}" 
                            value="${opt.option_number}" ${isChecked}
                            data-action="mark-draft-option"
                            data-slug="${escapeHtml(draft.slug)}"
                            data-question-index="${qIdx}"
                            data-option-number="${opt.option_number}">
                        <span class="draft-opt-num">${opt.option_number}.</span>
                        <span class="draft-opt-text">${opt.text}</span>
                    </label>
                `;
            }).join('');

            return `
                <div class="draft-q-item">
                    <div class="draft-q-header">
                        <span class="draft-q-num">Вопрос ${q.question_number || (qIdx + 1)}:</span>
                        <span class="draft-q-prompt">${q.prompt}</span>
                        ${matchStatus}
                    </div>
                    <div class="draft-options-group">
                        ${optionsHtml}
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="staging-draft-card" id="card-${draft.slug}">
                <div class="staging-card-top">
                    <div class="staging-meta">
                        <span class="level-tag" data-lvl="${draft.level}">${draft.level}</span>
                        <span class="category-tag">${CATEGORY_NAMES[draft.category] || draft.category}</span>
                        <span class="confidence-pill ${confColor}">Точность: ${confidencePct}%</span>
                        ${needsReviewBadge}
                    </div>
                    <h3 class="staging-card-title">${draft.title}</h3>
                    <div class="staging-source-note">${draft.source_note || ''}</div>
                    ${warningsHtml}
                </div>

                <!-- Reading Passage Preview -->
                <div class="staging-passage-preview">
                    <details class="draft-details">
                        <summary class="draft-summary">
                            <span>📖 Текст для чтения (${(draft.body_html || '').replace(/<[^>]+>/g, '').length} симв.)</span>
                            <span class="details-cue">Развернуть / скрыть</span>
                        </summary>
                        <div class="draft-passage-body">
                            ${draft.body_html || ''}
                        </div>
                    </details>
                </div>

                <!-- Questions and Options Block -->
                <div class="staging-questions-block">
                    <h4 class="staging-block-title">❓ Вопросы и варианты (${(draft.questions || []).length}):</h4>
                    ${questionsHtml}
                </div>

                <!-- Actions Footer -->
                <div class="staging-actions-footer">
                    <div class="draft-footer-left">
                        <button type="button" class="btn btn-ghost btn-sm" data-action="save-draft" data-slug="${escapeHtml(draft.slug)}">
                            💾 Сохранить изменения
                        </button>
                        <button type="button" class="btn btn-ghost btn-sm text-danger" data-action="delete-draft" data-slug="${escapeHtml(draft.slug)}">
                            🗑 Удалить
                        </button>
                    </div>
                    <button type="button" class="btn btn-primary" data-action="publish-draft" data-slug="${escapeHtml(draft.slug)}">
                        🚀 Опубликовать в тренажёр →
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Mark a specific option as correct for a draft question.
 * @param {string} slug 
 * @param {number} qIdx 
 * @param {number} optNumber 
 */
export function markDraftCorrectOption(slug, qIdx, optNumber) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (!draft || !draft.questions || !draft.questions[qIdx]) return;
    const q = draft.questions[qIdx];
    q.options.forEach(opt => {
        opt.is_correct = (opt.option_number === optNumber);
    });
    q.answer_matched = true;
}

/**
 * Save draft edits to server.
 * @param {string} slug 
 */
export async function saveDraft(slug) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (!draft) return;

    try {
        const resp = await fetch(`/api/admin/drafts/${slug}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(draft)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Не удалось сохранить');
        alert('✓ Изменения черновика успешно сохранены!');
    } catch (err) {
        alert(`Ошибка при сохранении: ${err.message}`);
    }
}

/**
 * Validate and publish draft into active task catalog.
 * @param {string} slug 
 */
export async function publishDraft(slug) {
    const draft = currentDraftsCache.find(d => d.slug === slug);
    if (draft && draft.questions) {
        const missingAns = draft.questions.some(q => !q.options.some(o => o.is_correct));
        if (missingAns) {
            alert('Внимание: в одном из вопросов не выбран правильный ответ! Выберите правильный вариант (радиокнопкой) перед публикацией.');
            return;
        }
    }

    try {
        // Save current modifications first
        if (draft) {
            await fetch(`/api/admin/drafts/${slug}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(draft)
            });
        }

        const resp = await fetch(`/api/admin/drafts/${slug}/publish`, {
            method: 'POST'
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) {
            const errList = data.detail?.errors ? data.detail.errors.join('\n') : (data.detail || 'Ошибка');
            throw new Error(errList);
        }

        alert(`✓ Задание «${draft ? draft.title : slug}» успешно опубликовано и добавлено в каталог сайта!`);
        await fetchAndRenderDrafts();
        if (window.fetchAndRenderCatalog) {
            window.fetchAndRenderCatalog();
        }
    } catch (err) {
        alert(`Не удалось опубликовать материал:\n${err.message}`);
    }
}

/**
 * Delete draft from staging area after confirmation.
 * @param {string} slug 
 */
export async function deleteDraft(slug) {
    if (!confirm('Вы уверены, что хотите удалить этот черновик?')) return;
    try {
        const resp = await fetch(`/api/admin/drafts/${slug}`, {
            method: 'DELETE'
        });
        if (!resp.ok) throw new Error('Ошибка удаления');
        await fetchAndRenderDrafts();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

/**
 * Bind event listeners for PDF Dropzone, file upload form and drafts refresh.
 */
let isPdfImportUIInitialized = false;

export function initPdfImportUI() {
    if (isPdfImportUIInitialized) return;
    isPdfImportUIInitialized = true;

    const els = getElements();

    if (els.btnRefreshDrafts) {
        els.btnRefreshDrafts.addEventListener('click', fetchAndRenderDrafts);
    }
    if (els.pdfDropzone && els.pdfFileInput) {
        els.pdfDropzone.addEventListener('click', (e) => {
            if (e.target.closest('#btn-clear-file')) return;
            els.pdfFileInput.click();
        });
        els.pdfFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handlePdfFileSelected(e.target.files[0]);
            }
        });
        els.pdfDropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            els.pdfDropzone.classList.add('dragover');
        });
        els.pdfDropzone.addEventListener('dragleave', () => {
            els.pdfDropzone.classList.remove('dragover');
        });
        els.pdfDropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            els.pdfDropzone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handlePdfFileSelected(e.dataTransfer.files[0]);
            }
        });
    }
    if (els.btnClearFile) {
        els.btnClearFile.addEventListener('click', (e) => {
            e.stopPropagation();
            clearSelectedPdfFile();
        });
    }
    if (els.formPdfUpload) {
        els.formPdfUpload.addEventListener('submit', handlePdfUpload);
    }
}

