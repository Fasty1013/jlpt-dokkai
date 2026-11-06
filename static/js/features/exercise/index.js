/**
 * JLPT Dokkai Master - Exercise Feature Entry Point
 */

import {
  saveCurrentActiveSession,
  renderWizard,
  handleOptionSelect,
  wizardGoNext,
  wizardGoPrev
} from './wizard.js';

import { startExercise } from './exercise_view.js';

export {
  saveCurrentActiveSession,
  renderWizard,
  handleOptionSelect,
  wizardGoNext,
  wizardGoPrev,
  startExercise
};

const DokkaiExercise = {
  saveCurrentActiveSession,
  renderWizard,
  handleOptionSelect,
  wizardGoNext,
  wizardGoPrev,
  startExercise
};

if (typeof window !== 'undefined') {
  window.DokkaiExercise = DokkaiExercise;
  // Shorthand bridges for inline event handlers and legacy calls during Step 5
  window.handleOptionSelect = (qid, oid) => handleOptionSelect(qid, oid, window.state, window.elements);
  window.wizardGoNext = () => wizardGoNext(window.state, window.elements);
  window.wizardGoPrev = () => wizardGoPrev(window.state, window.elements, window.returnToCatalog);
  window.renderWizard = () => renderWizard(window.state, window.elements);
  window.startExercise = (textId, opts) => startExercise(textId, opts);
}

export default DokkaiExercise;
