/**
 * JLPT Dokkai Master - Navigation, Popstate & Global Escape Event Listeners
 */

export function initNavigationEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'return-to-catalog': () => actions.returnToCatalog(true),
      'switch-main-tab': (el, e, ds) => actions.switchMainTab(ds.tab || 'catalog'),
      'open-sync-modal': () => actions.openSyncModal(),
      'escape': () => {
        if (actions.hidePopupDictionary) actions.hidePopupDictionary();
        if (actions.closeNotebookModal) actions.closeNotebookModal();
        if (actions.closePretestModal) actions.closePretestModal();
        if (actions.closeSyncModal) actions.closeSyncModal();
        if (actions.closeReportModal) actions.closeReportModal();
      }
    });
  }

  // Global Smartphone & Browser Back Button (popstate) Handler
  // Safe to call multiple times with idempotent check
  if (!window._dokkaiPopstateInitialized) {
    window._dokkaiPopstateInitialized = true;
    window.addEventListener('popstate', (e) => {
      // 1. If any modal is open, close it and stay on the current page
      if (elements.pretestModalBackdrop && !elements.pretestModalBackdrop.classList.contains('hidden')) {
        actions.closePretestModal();
        return;
      }
      if (elements.reportModalBackdrop && !elements.reportModalBackdrop.classList.contains('hidden')) {
        actions.closeReportModal();
        return;
      }
      if (elements.supplementaryDrawer && !elements.supplementaryDrawer.classList.contains('hidden')) {
        elements.supplementaryDrawer.classList.add('hidden');
        return;
      }

      // 2. If in exercise mode or analysis view, return to catalog without throwing user out
      if (state.currentView === 'exercise' || state.currentView === 'analysis') {
        actions.returnToCatalog(false);
        return;
      }

      // 3. If in notebook or import view, return to catalog
      if (state.activeTab !== 'catalog') {
        actions.switchMainTab('catalog', false);
        return;
      }

      // 4. If already on catalog, keep user on catalog
      history.pushState({ view: 'catalog' }, '', window.location.pathname);
    });
  }
}
