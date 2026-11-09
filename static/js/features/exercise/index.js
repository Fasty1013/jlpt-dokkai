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
import { initExerciseEvents } from './exercise_events.js';

export {
  saveCurrentActiveSession,
  renderWizard,
  handleOptionSelect,
  wizardGoNext,
  wizardGoPrev,
  startExercise,
  initExerciseEvents
};

const DokkaiExercise = {
  saveCurrentActiveSession,
  renderWizard,
  handleOptionSelect,
  wizardGoNext,
  wizardGoPrev,
  startExercise,
  initEvents: initExerciseEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiExercise = DokkaiExercise;
  // Shorthand bridges for inline event handlers and legacy calls during Step 5
  window.handleOptionSelect = (qid, oid) => handleOptionSelect(qid, oid);
  window.wizardGoNext = () => wizardGoNext();
  window.wizardGoPrev = () => wizardGoPrev();
  window.renderWizard = () => renderWizard();
  window.startExercise = (textId, opts) => startExercise(textId, opts);
}

export default DokkaiExercise;
