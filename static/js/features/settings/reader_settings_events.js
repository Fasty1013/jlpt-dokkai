/**
 * JLPT Dokkai Master - Reader Settings Event Listeners
 */

export function initReaderSettingsEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'set-reader-font': (el, e, ds) => actions.setReaderFont(ds.font || el.dataset.font),
      'adjust-font-size': (el, e, ds) => actions.adjustFontSize(parseInt(ds.delta || el.dataset.delta, 10) || 0),
      'toggle-popup-dict': () => actions.togglePopupDictStatus()
    });
  }
}
