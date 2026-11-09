/**
 * JLPT Dokkai Master - Stream, Catalog & Solved Tasks Event Listeners
 */

export function initStreamEvents({ state, elements, actions }) {
  if (window.DokkaiEvents) {
    window.DokkaiEvents.registerActions({
      'filter-level': (el, e, ds) => {
        if (elements.streamLevelPills) {
          elements.streamLevelPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        }
        el.classList.add('active');
        state.streamProfile.level = ds.level || el.dataset.level;
        actions.fetchAndRenderStream();
      },
      'filter-category': (el, e, ds) => {
        if (elements.streamCategoryPills) {
          elements.streamCategoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        }
        el.classList.add('active');
        state.streamProfile.category = ds.category || el.dataset.category;
        actions.fetchAndRenderSlots();
      },
      'filter-solved-when': (el, e, ds) => {
        if (elements.streamModePills) {
          elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        }
        el.classList.add('active');
        state.streamProfile.solvedWhen = ds.solvedWhen || el.dataset.solvedWhen || 'all_questions_answered';
        try {
          localStorage.setItem('dokkai_stream_solved_when', state.streamProfile.solvedWhen);
        } catch (err) { }
      },
      'refresh-slots': () => actions.fetchAndRenderSlots(),
      'filter-solved': (el, e, ds) => {
        if (elements.solvedFilterPills) {
          elements.solvedFilterPills.querySelectorAll('.mini-pill').forEach(p => p.classList.remove('active'));
        }
        el.classList.add('active');
        state.solvedFilter = ds.solvedFilter || el.dataset.solvedFilter || 'all';
        actions.fetchAndRenderSolvedTasks();
      },
      'switch-mobile-stream-col': (el, e, ds) => {
        actions.switchMobileStreamCol(ds.col || el.dataset.col || 'active');
      },
      'open-pretest': (el, e, ds) => {
        if (e && e.stopPropagation) e.stopPropagation();
        const textId = Number(ds.textId || el.dataset.textId);
        if (textId) actions.openPretestModal(textId);
      },
      'review-solved': (el, e, ds) => {
        const textId = Number(ds.textId || el.dataset.textId);
        if (textId) actions.reviewSolvedTask(textId);
      },
      'retry-solved': (el, e, ds) => {
        const textId = Number(ds.textId || el.dataset.textId);
        if (textId) actions.retrySolvedTask(textId);
      }
    });
  }

  // Restore saved solvedWhen setting from localStorage
  if (elements.streamModePills) {
    try {
      const savedSolvedWhen = localStorage.getItem('dokkai_stream_solved_when');
      if (savedSolvedWhen) {
        state.streamProfile.solvedWhen = savedSolvedWhen;
        const targetPill = elements.streamModePills.querySelector(`[data-solved-when="${savedSolvedWhen}"]`);
        if (targetPill) {
          elements.streamModePills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
          targetPill.classList.add('active');
        }
      }
    } catch (err) { }
  }
}
