/**
 * JLPT Dokkai Master - Report Defect Modal Feature Module
 */

import { localizeServerMessage } from '../../i18n/server_messages.js';
import { t, setI18nText } from '../../i18n/index.js';
import { reportTextIssue } from '../../api/texts.js';
import { getUserId } from '../../utils/user.js';
import { state as storeState } from '../../state/store.js';
import { elements as domElements } from '../../state/elements.js';

/**
 * Open report defect modal for a specific text.
 * @param {number|string} textId
 * @param {string} title
 * @param {Object} context - { state, elements }
 */
export function openReportModal(textId, title, context = {}) {
  const state = context.state || storeState;
  const elements = context.elements || domElements;

  if (state) state.reportingTextId = textId;
  if (typeof history !== 'undefined' && history.pushState) {
    history.pushState({ modal: 'report', textId }, '', '#report');
  }

  if (elements?.reportModalTaskTitle) {
    elements.reportModalTaskTitle.textContent = title || t('report.taskFallback', { id: textId });
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
  const state = context.state || storeState;
  const elements = context.elements || domElements;

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
  const state = context.state || storeState;
  const elements = context.elements || domElements;
  const userId = (typeof context.getUserId === 'function') ? context.getUserId() : getUserId();

  if (!state?.reportingTextId) return;
  const reason = elements?.reportReasonSelect ? elements.reportReasonSelect.value : 'Опечатка';
  const details = elements?.reportDetailsTextarea ? elements.reportDetailsTextarea.value.trim() : '';

  try {
    if (elements?.btnSubmitReport) {
      elements.btnSubmitReport.disabled = true;
      setI18nText(elements.btnSubmitReport, 'report.sending');
    }

    const resData = await reportTextIssue(state.reportingTextId, {
      reason,
      details,
      user_id: userId
    });

    closeReportModal(context);
    alert(resData?.message ? localizeServerMessage(resData.message) : t('report.thanks'));

    if (typeof context.onRefreshSlots === 'function') {
      context.onRefreshSlots();
    } else if (typeof window !== 'undefined' && typeof window.fetchAndRenderSlots === 'function') {
      window.fetchAndRenderSlots();
    }
  } catch (e) {
    console.error(e);
    alert(t('report.failed'));
  } finally {
    if (elements?.btnSubmitReport) {
      elements.btnSubmitReport.disabled = false;
      setI18nText(elements.btnSubmitReport, 'report.submit');
    }
  }
}
