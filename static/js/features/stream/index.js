/**
 * JLPT Dokkai Master - Stream & Catalog Feature Barrel Export
 */

import {
  renderSlotCardHtml,
  fetchAndRenderSlots,
  handleSlotReplacement,
  switchMobileStreamCol
} from './stream_slots.js';

export {
  renderSlotCardHtml,
  fetchAndRenderSlots,
  handleSlotReplacement,
  switchMobileStreamCol
};

if (typeof window !== 'undefined') {
  window.DokkaiStream = {
    renderSlotCardHtml,
    fetchAndRenderSlots,
    handleSlotReplacement,
    switchMobileStreamCol
  };

  // Direct bridges for backward compatibility until Step 6 event delegation
  window.fetchAndRenderSlots = (isExplicitRefresh) => fetchAndRenderSlots(isExplicitRefresh);
  window.handleSlotReplacement = (solvedTextId, replacement) => handleSlotReplacement(solvedTextId, replacement);
  window.switchMobileStreamCol = (col) => switchMobileStreamCol(col, window.elements);
}
