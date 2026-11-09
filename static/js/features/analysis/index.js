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
  // Rendering utilities for view lifecycle
  window.renderAnalysisView = (data) => renderAnalysisView(data, window.state, window.elements);
  window.renderAnalysisTabs = () => renderAnalysisTabs(window.state, window.elements);
  window.renderAnalysisActiveCard = (q) => renderAnalysisActiveCard(q, window.state, window.elements);
}

export default DokkaiAnalysis;

