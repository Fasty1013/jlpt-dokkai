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

export {
  registerAction,
  registerActions,
  dispatchAction,
  hasAction,
  initActionDelegation
};

export const DokkaiEvents = {
  registerAction,
  registerActions,
  dispatchAction,
  hasAction,
  initActionDelegation
};

// Global bridge for backward compatibility and classic scripts
if (typeof window !== 'undefined') {
  window.DokkaiEvents = DokkaiEvents;
}

