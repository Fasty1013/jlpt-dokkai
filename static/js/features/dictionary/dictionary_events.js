/**
 * JLPT Dokkai Master - Popup Dictionary Event Listeners
 */

export function initDictionaryEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'dict-close': () => actions.hidePopupDictionary(),
      'dict-play-audio': () => {
        if (state.activePopupWord && state.activePopupWord.word) {
          actions.speakJapanese(state.activePopupWord.word);
        }
      },
      'dict-save-word': () => {
        actions.toggleSaveWord(state.activePopupWord);
      }
    });
  }

  // Selection & Click trigger on Passage text (idempotent guard)
  if (elements.passageContent && !elements.passageContent._dokkaiDictBound) {
    elements.passageContent._dokkaiDictBound = true;

    elements.passageContent.addEventListener('mouseup', (e) => {
      if (!state.popupDictEnabled) return;
      const sel = window.getSelection();
      const text = sel ? sel.toString().trim() : '';
      if (text && text.length >= 1 && text.length <= 15) {
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        actions.lookupAndShowWord(text, rect.left + rect.width / 2, rect.top);
      }
    });

    elements.passageContent.addEventListener('click', (e) => {
      if (!state.popupDictEnabled) return;
      const target = e.target;
      const rubyEl = target.closest('ruby');
      if (rubyEl) {
        let kanjiText = '';
        rubyEl.childNodes.forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) {
            kanjiText += node.textContent.trim();
          } else if (node.nodeName !== 'RT' && node.nodeName !== 'RP') {
            kanjiText += node.textContent.trim();
          }
        });
        if (kanjiText) {
          const rect = rubyEl.getBoundingClientRect();
          actions.lookupAndShowWord(kanjiText, rect.left + rect.width / 2, rect.top);
        }
      }
    });
  }

  // Close popup dictionary when clicking outside (idempotent guard)
  if (!window._dokkaiDictOutsideBound) {
    window._dokkaiDictOutsideBound = true;
    document.addEventListener('mousedown', (e) => {
      if (!elements.popupDictionaryCard || elements.popupDictionaryCard.classList.contains('hidden')) return;
      if (!elements.popupDictionaryCard.contains(e.target) && !elements.passageContent.contains(e.target)) {
        actions.hidePopupDictionary();
      }
    });
  }
}
