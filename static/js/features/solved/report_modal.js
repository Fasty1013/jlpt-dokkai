/**
 * JLPT Dokkai Master - Report Defect Modal Feature Module
 */

import { reportTextIssue } from '../../api/texts.js';

/**
 * Open report defect modal for a specific text.
 * @param {number|string} textId
 * @param {string} title
 * @param {Object} context - { state, elements }
 */
export function openReportModal(textId, title, context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const elements = context.elements || (typeof window !== 'undefined' ? window.elements : null);

  if (state) state.reportingTextId = textId;
  if (typeof history !== 'undefined' && history.pushState) {
    history.pushState({ modal: 'report', textId }, '', '#report');
  }

  if (elements?.reportModalTaskTitle) {
    elements.reportModalTaskTitle.textContent = title || `Задание #${textId}`;
  }
  if (elements?.reportDetailsTextarea) {
    elements.reportDetailsTextarea.value = '';
  }
  if (elements?.reportModalBackdrop) {
    elements.reportModalBackdrop.classList.remove('hidden');
  }
}

/**
 * Close report defect modal.
 * @param {Object} context - { state, elements }
 */
export function closeReportModal(context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const elements = context.elements || (typeof window !== 'undefined' ? window.elements : null);

  if (state) state.reportingTextId = null;
  if (elements?.reportModalBackdrop) {
    elements.reportModalBackdrop.classList.add('hidden');
  }
}

/**
 * Submit defect report.
 * @param {Object} context - { state, elements, getUserId, onRefreshSlots }
 */
export async function submitReportDefect(context = {}) {
  const state = context.state || (typeof window !== 'undefined' ? window.state : null);
  const elements = context.elements || (typeof window !== 'undefined' ? window.elements : null);
  const getUserId = context.getUserId || (typeof window !== 'undefined' ? window.getUserId : () => 'guest');

  if (!state?.reportingTextId) return;
  const reason = elements?.reportReasonSelect ? elements.reportReasonSelect.value : 'Опечатка';
  const details = elements?.reportDetailsTextarea ? elements.reportDetailsTextarea.value.trim() : '';

  try {
    if (elements?.btnSubmitReport) {
      elements.btnSubmitReport.disabled = true;
      elements.btnSubmitReport.textContent = 'Отправка...';
    }

    const resData = await reportTextIssue(state.reportingTextId, {
      reason,
      details,
      user_id: getUserId()
    });

    closeReportModal(context);
    alert(resData?.message || 'Жалоба принята. Спасибо за помощь!');

    if (typeof context.onRefreshSlots === 'function') {
      context.onRefreshSlots();
    } else if (typeof window !== 'undefined' && typeof window.fetchAndRenderSlots === 'function') {
      window.fetchAndRenderSlots();
    }
  } catch (e) {
    console.error(e);
    alert('Не удалось отправить замечание.');
  } finally {
    if (elements?.btnSubmitReport) {
      elements.btnSubmitReport.disabled = false;
      elements.btnSubmitReport.textContent = 'Отправить замечание';
    }
  }
}
