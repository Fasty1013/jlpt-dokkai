/**
 * JLPT Dokkai Master - Analysis View & Verification Tools Event Listeners
 */

export function initAnalysisEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'toggle-furigana': () => actions.toggleFurigana(),
      'toggle-evidence': () => actions.toggleEvidence(),
      'toggle-translation': () => actions.toggleSupplementaryDrawer('translation'),
      'toggle-vocab': () => actions.toggleSupplementaryDrawer('vocab'),
      'close-drawer': () => {
        if (elements.supplementaryDrawer) elements.supplementaryDrawer.classList.add('hidden');
      },
      'switch-analysis-tab': (el, e, ds) => {
        const idx = Number(ds.tabIndex || el.dataset.tabIndex);
        if (!isNaN(idx)) actions.switchAnalysisTab(idx);
      },
      'locate-evidence': (el, e, ds) => {
        const spanId = ds.spanId || el.dataset.spanId;
        if (spanId) actions.locateEvidenceInText(spanId);
      }
    });
  }
}
