/**
 * JLPT Dokkai Master - Analysis Feature Entry Point
 */

import {
  renderAnalysisView,
  renderAnalysisTabs,
  switchAnalysisTab,
  renderAnalysisActiveCard,
  toggleFurigana,
  toggleEvidence,
  locateEvidenceInText,
  toggleSupplementaryDrawer
} from './analysis_view.js';

import { submitAnswers } from './submit_flow.js';

export {
  renderAnalysisView,
  renderAnalysisTabs,
  switchAnalysisTab,
  renderAnalysisActiveCard,
  toggleFurigana,
  toggleEvidence,
  locateEvidenceInText,
  toggleSupplementaryDrawer,
  submitAnswers
};

const DokkaiAnalysis = {
  renderAnalysisView,
  renderAnalysisTabs,
  switchAnalysisTab,
  renderAnalysisActiveCard,
  toggleFurigana,
  toggleEvidence,
  locateEvidenceInText,
  toggleSupplementaryDrawer,
  submitAnswers
};

if (typeof window !== 'undefined') {
  window.DokkaiAnalysis = DokkaiAnalysis;
  // Shorthand bridges for inline event handlers and legacy calls during Step 5
  window.renderAnalysisView = (data) => renderAnalysisView(data, window.state, window.elements);
  window.renderAnalysisTabs = () => renderAnalysisTabs(window.state, window.elements);
  window.switchAnalysisTab = (idx) => switchAnalysisTab(idx, window.state, window.elements);
  window.renderAnalysisActiveCard = (q) => renderAnalysisActiveCard(q, window.state, window.elements);
  window.toggleFurigana = () => toggleFurigana(window.state, window.elements);
  window.toggleEvidence = () => toggleEvidence(window.state, window.elements);
  window.locateEvidenceInText = (spanId) => locateEvidenceInText(spanId, window.state, window.elements);
  window.toggleSupplementaryDrawer = (type) => toggleSupplementaryDrawer(type, window.state, window.elements);
  window.submitAnswers = (opts) => submitAnswers({
    state: window.state,
    elements: window.elements,
    handleSlotReplacement: window.handleSlotReplacement,
    fetchAndRenderSlots: window.fetchAndRenderSlots,
    fetchAndRenderSolvedTasks: window.fetchAndRenderSolvedTasks,
    ...opts
  });
}

export default DokkaiAnalysis;
