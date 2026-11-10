/**
 * JLPT Dokkai Master - Events & Action Delegation Facade
 */

import {
  registerAction,
  registerActions,
  dispatchAction,
  hasAction,
  initActionDelegation
} from './action_dispatcher.js';

import { initNavigationEvents } from './navigation_events.js';

export {
  registerAction,
  registerActions,
  dispatchAction,
  hasAction,
  initActionDelegation,
  initNavigationEvents
};

export const DokkaiEvents = {
  registerAction,
  registerActions,
  dispatchAction,
  hasAction,
  initActionDelegation,
  initNavigationEvents
};

// Global bridge for backward compatibility and classic scripts
if (typeof window !== 'undefined') {
  window.DokkaiEvents = DokkaiEvents;
}

