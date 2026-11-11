/**
 * JLPT Dokkai Master - Sideways scrolling for one-line rows with a mouse.
 *
 * The header tabs (and the other one-line rows) scroll horizontally when they do not fit.
 * Touch devices swipe natively; this module adds the same for a mouse:
 *   - vertical wheel over a row scrolls it sideways (only while it can still scroll that way);
 *   - press-and-drag with the primary button scrolls it, and the click that ends a drag is swallowed.
 * Listeners are delegated on `document`, so rows rendered later work too.
 */

const ROW_SELECTOR = [
  '.header-nav',
  '.pill-selectors',
  '.study-tools-bar',
  '.reader-tools',
  '.analysis-tabs',
  '.exercise-header-controls'
].join(',');

const DRAG_THRESHOLD_PX = 5;
const NO_DRAG_TARGETS = 'select, input, textarea';

function overflows(row) {
  return row.scrollWidth - row.clientWidth > 1;
}

function onWheel(event) {
  if (event.ctrlKey || event.defaultPrevented || event.deltaMode !== 0) return;
  const row = event.target instanceof Element ? event.target.closest(ROW_SELECTOR) : null;
  if (!row || !overflows(row)) return;
  // Native horizontal gestures (trackpads, shift+wheel) already work.
  if (Math.abs(event.deltaX) >= Math.abs(event.deltaY)) return;
  const max = row.scrollWidth - row.clientWidth;
  const next = Math.min(max, Math.max(0, row.scrollLeft + event.deltaY));
  if (next === row.scrollLeft) return; // at the edge: let the page scroll
  row.scrollLeft = next;
  event.preventDefault();
}

let drag = null;

function onPointerDown(event) {
  if (event.pointerType !== 'mouse' || event.button !== 0) return;
  const target = event.target instanceof Element ? event.target : null;
  const row = target && target.closest(ROW_SELECTOR);
  if (!row || !overflows(row) || target.closest(NO_DRAG_TARGETS)) return;
  drag = { row, startX: event.clientX, startScroll: row.scrollLeft, moved: false, snap: row.style.scrollSnapType };
}

function onPointerMove(event) {
  if (!drag) return;
  const dx = event.clientX - drag.startX;
  if (!drag.moved) {
    if (Math.abs(dx) < DRAG_THRESHOLD_PX) return;
    drag.moved = true;
    drag.row.style.scrollSnapType = 'none'; // snapping would fight the drag
    drag.row.style.cursor = 'grabbing';
    drag.row.style.userSelect = 'none';
  }
  drag.row.scrollLeft = drag.startScroll - dx;
}

function endDrag() {
  if (!drag) return;
  const { row, moved, snap } = drag;
  drag = null;
  if (!moved) return;
  row.style.scrollSnapType = snap;
  row.style.cursor = '';
  row.style.userSelect = '';
  // The button release after a drag must not activate the tab under the pointer.
  const swallow = (e) => { e.stopPropagation(); e.preventDefault(); };
  document.addEventListener('click', swallow, { capture: true, once: true });
  setTimeout(() => document.removeEventListener('click', swallow, { capture: true }), 0);
}

let initialized = false;

export function initSwipeRows() {
  if (initialized || typeof document === 'undefined') return;
  initialized = true;
  document.addEventListener('wheel', onWheel, { passive: false });
  document.addEventListener('pointerdown', onPointerDown);
  document.addEventListener('pointermove', onPointerMove);
  document.addEventListener('pointerup', endDrag);
  document.addEventListener('pointercancel', endDrag);
}
