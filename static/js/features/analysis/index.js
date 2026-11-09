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
import { initAnalysisEvents } from './analysis_events.js';

export {
  renderAnalysisView,
  renderAnalysisTabs,
  switchAnalysisTab,
  renderAnalysisActiveCard,
  toggleFurigana,
  toggleEvidence,
  locateEvidenceInText,
  toggleSupplementaryDrawer,
  submitAnswers,
  initAnalysisEvents
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
  submitAnswers,
  initEvents: initAnalysisEvents
};

if (typeof window !== 'undefined') {
  window.DokkaiAnalysis = DokkaiAnalysis;
  // Rendering utilities for view lifecycle
  window.renderAnalysisView = (data) => renderAnalysisView(data, window.state, window.elements);
  window.renderAnalysisTabs = () => renderAnalysisTabs(window.state, window.elements);
  window.renderAnalysisActiveCard = (q) => renderAnalysisActiveCard(q, window.state, window.elements);
}

export default DokkaiAnalysis;

