/**
 * JLPT Dokkai Master - Central Action Dispatcher & Event Delegation
 * Replaces inline event handlers and static addEventListener bindings
 * with declarative [data-action] attributes and a single unified root listener.
 */

const actionHandlers = new Map();
let isDelegationInitialized = false;

/**
 * Register an action handler for a specific data-action attribute value.
 * @param {string} actionName - The value of data-action (e.g. 'return-to-catalog')
 * @param {Function} handler - Callback (element, event, dataset) => void
 */
export function registerAction(actionName, handler) {
  if (typeof handler !== 'function') {
    throw new TypeError(`Handler for action "${actionName}" must be a function.`);
  }
  actionHandlers.set(actionName, handler);
}

/**
 * Register multiple action handlers at once.
 * @param {Object.<string, Function>} handlersMap
 */
export function registerActions(handlersMap) {
  for (const [actionName, handler] of Object.entries(handlersMap)) {
    registerAction(actionName, handler);
  }
}

/**
 * Manually dispatch an action programmatically.
 * @param {string} actionName
 * @param {HTMLElement|null} element
 * @param {Event|null} originalEvent
 */
export function dispatchAction(actionName, element = null, originalEvent = null) {
  const handler = actionHandlers.get(actionName);
  if (handler) {
    const dataset = element ? { ...element.dataset } : {};
    return handler(element, originalEvent, dataset);
  } else {
    console.warn(`[Dokkai Actions] No handler registered for action: "${actionName}"`);
  }
}

/**
 * Check if an action has a registered handler.
 * @param {string} actionName
 * @returns {boolean}
 */
export function hasAction(actionName) {
  return actionHandlers.has(actionName);
}

/**
 * Initialize root delegated event listeners for click and keyboard.
 * Safe to call multiple times (idempotent).
 * @param {HTMLElement|Document} rootEl - Defaults to document
 */
export function initActionDelegation(rootEl = document) {
  if (isDelegationInitialized) return;
  isDelegationInitialized = true;

  // Root click delegation
  rootEl.addEventListener('click', (event) => {
    const actionEl = event.target.closest('[data-action]');
    if (!actionEl) return;

    // Disabled elements cannot trigger actions
    if (actionEl.disabled || actionEl.getAttribute('aria-disabled') === 'true') {
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    const action = actionEl.dataset.action;
    if (!action) return;

    // Dispatch the action with element and event context
    const handler = actionHandlers.get(action);
    if (handler) {
      handler(actionEl, event, actionEl.dataset);
    } else {
      console.warn(`[Dokkai Actions] Unhandled action: "${action}" on element:`, actionEl);
    }
  });

  // Root change delegation (for radios, checkboxes, selects with data-action)
  rootEl.addEventListener('change', (event) => {
    const actionEl = event.target.closest('[data-action]');
    if (!actionEl) return;

    if (actionEl.disabled || actionEl.getAttribute('aria-disabled') === 'true') {
      event.preventDefault();
      return;
    }

    const action = actionEl.dataset.action;
    if (!action) return;

    const handler = actionHandlers.get(action);
    if (handler) {
      handler(actionEl, event, actionEl.dataset);
    }
  });

  // Keyboard navigation & accessibility delegation
  rootEl.addEventListener('keydown', (event) => {
    // Escape key: global dismissal of open modals/drawers
    if (event.key === 'Escape') {
      const escapeHandler = actionHandlers.get('escape');
      if (escapeHandler) {
        escapeHandler(null, event, {});
      }
      return;
    }

    // Enter / Space activation for non-button interactive elements with [data-action]
    if (event.key === 'Enter' || event.key === ' ') {
      const target = event.target;
      if (target && target.matches && target.matches('[data-action]:not(button):not(input):not(select):not(textarea)')) {
        event.preventDefault();
        target.click();
      }
    }
  });
}

