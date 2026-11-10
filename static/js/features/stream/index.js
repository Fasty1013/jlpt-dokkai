/**
 * JLPT Dokkai Master - Stream & Catalog Feature Barrel Export
 */

import {
  renderSlotCardHtml,
  fetchAndRenderSlots,
  handleSlotReplacement,
  switchMobileStreamCol
} from './stream_slots.js';

import { initStreamEvents } from './stream_events.js';

export {
  renderSlotCardHtml,
  fetchAndRenderSlots,
  handleSlotReplacement,
  switchMobileStreamCol,
  initStreamEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiStream = {
    renderSlotCardHtml,
    fetchAndRenderSlots,
    handleSlotReplacement,
    switchMobileStreamCol,
    initEvents: initStreamEvents
  };
}
