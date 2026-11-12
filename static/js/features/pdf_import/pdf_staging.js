/**
 * JLPT Dokkai Master - PDF Ingestion & Staging Management
 * Client-side interface for PDF book upload, preview of extracted exercises,
 * question/option correction, and publishing into active catalog.
 * Note: Never commits user PDFs to git. /api/admin/* requires the admin key (ADMIN_TOKEN) in production;
 * adminFetch() sends it when it is stored in this browser (set on the /admin page).
 */

import { t } from '../../i18n/index.js';
import { localizeServerMessage } from '../../i18n/server_messages.js';
import { adminFetch } from '../../api/admin_token.js';
import { getCategoryName } from '../../constants/labels.js';
import { formatFileSize, escapeHtml } from '../../utils/index.js';
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
        alert(t('pdf.needPdf'));
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
        alert(t('pdf.needFile'));
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
    if (els.uploadStatusText) els.uploadStatusText.textContent = t('pdf.recognizing');

    try {
        const resp = await adminFetch('/api/admin/upload-pdf', {
            method: 'POST',
            body: formData
        });

        const data = await resp.json();
        if (!resp.ok || !data.success) {
            throw new Error(data.error || localizeServerMessage(data.detail) || t('pdf.recognizeFailed'));
        }

        clearSelectedPdfFile();
        if (els.importTitleOverride) els.importTitleOverride.value = '';

        await fetchAndRenderDrafts();

        const count = data.drafts ? data.drafts.length : 0;
        alert(t('pdf.success', { count }));
    } catch (err) {
        console.error('PDF upload error:', err);
        alert(t('pdf.processError', { message: err.message }));
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
        const resp = await adminFetch('/api/admin/drafts');
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
                <h3>${t('pdf.emptyTitle')}</h3>
                <p>${t('pdf.emptyDesc')}</p>
            </div>
        `;
        return;
    }

    els.stagingDraftsList.innerHTML = drafts.map(draft => {
        const confidencePct = Math.round((draft.confidence || 0) * 100);
        const confColor = confidencePct >= 80 ? 'color-good' : (confidencePct >= 60 ? 'color-med' : 'color-low');
        const needsReviewBadge = draft.needs_review
            ? `<span class="badge-review-needed">${t('pdf.needsReview')}</span>`
            : `<span class="badge-review-ready">${t('pdf.ready')}</span>`;

        const warningsHtml = (draft.needs_manual_review && draft.needs_manual_review.length > 0)
            ? `<div class="draft-warnings-box">
                <strong>${t('pdf.warnings')}</strong>
                <ul>${draft.needs_manual_review.map(r => `<li>${r}</li>`).join('')}</ul>
               </div>`
            : '';

        const questionsHtml = (draft.questions || []).map((q, qIdx) => {
            const hasMatched = q.answer_matched;
            const matchStatus = hasMatched
                ? `<span class="match-badge match-ok">${t('pdf.answerFound')}</span>`
                : `<span class="match-badge match-missing">${t('pdf.answerMissing')}</span>`;

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
                        <span class="draft-q-num">${t('pdf.questionNum', { n: q.question_number || (qIdx + 1) })}</span>
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
                        <span class="category-tag">${getCategoryName(draft.category) || draft.category}</span>
                        <span class="confidence-pill ${confColor}">${t('pdf.accuracy', { pct: confidencePct })}</span>
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
                            <span>${t('pdf.passageSummary', { n: (draft.body_html || '').replace(/<[^>]+>/g, '').length })}</span>
                            <span class="details-cue">${t('pdf.expandCollapse')}</span>
                        </summary>
                        <div class="draft-passage-body">
                            ${draft.body_html || ''}
                        </div>
                    </details>
                </div>

                <!-- Questions and Options Block -->
                <div class="staging-questions-block">
                    <h4 class="staging-block-title">${t('pdf.questionsBlock', { n: (draft.questions || []).length })}</h4>
                    ${questionsHtml}
                </div>

                <!-- Actions Footer -->
                <div class="staging-actions-footer">
                    <div class="draft-footer-left">
                        <button type="button" class="btn btn-ghost btn-sm" data-action="save-draft" data-slug="${escapeHtml(draft.slug)}">
                            ${t('pdf.save')}
                        </button>
                        <button type="button" class="btn btn-ghost btn-sm text-danger" data-action="delete-draft" data-slug="${escapeHtml(draft.slug)}">
                            ${t('pdf.delete')}
                        </button>
                    </div>
                    <button type="button" class="btn btn-primary" data-action="publish-draft" data-slug="${escapeHtml(draft.slug)}">
                        ${t('pdf.publish')}
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
        const resp = await adminFetch(`/api/admin/drafts/${slug}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(draft)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(localizeServerMessage(data.detail) || t('pdf.saveFailed'));
        alert(t('pdf.saved'));
    } catch (err) {
        alert(t('pdf.saveError', { message: err.message }));
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
            alert(t('pdf.needCorrect'));
            return;
        }
    }

    try {
        // Save current modifications first
        if (draft) {
            await adminFetch(`/api/admin/drafts/${slug}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(draft)
            });
        }

        const resp = await adminFetch(`/api/admin/drafts/${slug}/publish`, {
            method: 'POST'
        });
        const data = await resp.json();
        if (!resp.ok || !data.success) {
            const errList = localizeServerMessage(data.detail)?.errors ? localizeServerMessage(data.detail).errors.join('\n') : (localizeServerMessage(data.detail) || t('pdf.errorGeneric'));
            throw new Error(errList);
        }

        alert(t('pdf.published', { title: draft ? draft.title : slug }));
        await fetchAndRenderDrafts();
        if (window.fetchAndRenderCatalog) {
            window.fetchAndRenderCatalog();
        }
    } catch (err) {
        alert(t('pdf.publishError', { message: err.message }));
    }
}

/**
 * Delete draft from staging area after confirmation.
 * @param {string} slug 
 */
export async function deleteDraft(slug) {
    if (!confirm(t('pdf.confirmDelete'))) return;
    try {
        const resp = await adminFetch(`/api/admin/drafts/${slug}`, {
            method: 'DELETE'
        });
        if (!resp.ok) throw new Error(t('pdf.deleteFailed'));
        await fetchAndRenderDrafts();
    } catch (err) {
        alert(t('pdf.errorPrefix', { message: err.message }));
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

