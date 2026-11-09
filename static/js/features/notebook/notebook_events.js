/**
 * JLPT Dokkai Master - Notebook & Personal Vocabulary Event Listeners
 */

export function initNotebookEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'filter-notebook': (el, e, ds) => {
        const notebookFilterPills = document.querySelectorAll('.notebook-filter-pill');
        notebookFilterPills.forEach(p => p.classList.remove('active'));
        el.classList.add('active');
        state.notebookFilter = ds.filter || el.dataset.filter || 'all';
        actions.renderNotebookWords();
      },
      'export-notebook-backup': () => actions.exportProgressJson(),
      'import-notebook-backup-trigger': () => {
        const fileInput = document.getElementById('input-import-backup-file');
        if (fileInput) fileInput.click();
      },
      'clear-notebook': () => actions.clearAllSavedWords(),
      'notebook-speak-word': (el, e, ds) => {
        const word = ds.word || el.dataset.word;
        if (word && actions.speakJapanese) actions.speakJapanese(word);
      },
      'notebook-delete-word': (el, e, ds) => {
        const wordToDelete = ds.word || el.dataset.word;
        if (wordToDelete && actions.getSavedWords && actions.saveWordsToStorage) {
          let words = actions.getSavedWords();
          words = words.filter(w => w.word !== wordToDelete);
          actions.saveWordsToStorage(words);
          actions.renderNotebookWords();
        }
      },
      'notebook-toggle-mastered': (el, e, ds) => {
        const wordText = ds.word || el.dataset.word;
        if (wordText && actions.getSavedWords && actions.saveWordsToStorage) {
          let words = actions.getSavedWords();
          const target = words.find(w => w.word === wordText);
          if (target) {
            target.mastered = el.checked;
            actions.saveWordsToStorage(words);
            actions.renderNotebookWords();
          }
        }
      }
    });
  }

  // Notebook Search Input listener (idempotent guard)
  if (elements.notebookSearchInput && !elements.notebookSearchInput._dokkaiBound) {
    elements.notebookSearchInput._dokkaiBound = true;
    elements.notebookSearchInput.addEventListener('input', (e) => {
      state.notebookSearchQuery = e.target.value;
      actions.renderNotebookWords();
    });
  }
}
