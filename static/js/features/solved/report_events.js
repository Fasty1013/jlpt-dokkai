/**
 * JLPT Dokkai Master - Defect Reporting & Report Modal Event Listeners
 */

export function initReportEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'open-report': (el, e, ds) => {
        const textId = Number(ds.textId || el.dataset.textId);
        const title = ds.taskTitle || el.dataset.taskTitle || '';
        if (textId) actions.openReportModal(textId, title);
      },
      'close-report-modal': () => actions.closeReportModal(),
      'submit-report': () => actions.submitReportDefect()
    });
  }

  // Backdrop click listener (idempotent guard)
  if (elements.reportModalBackdrop && !elements.reportModalBackdrop._dokkaiBound) {
    elements.reportModalBackdrop._dokkaiBound = true;
    elements.reportModalBackdrop.addEventListener('click', (e) => {
      if (e.target === elements.reportModalBackdrop) {
        actions.closeReportModal();
      }
    });
  }
}
