/**
 * JLPT Dokkai Master - Math & Scoring Utilities
 */

export function calculateScorePercent(correctCount, totalQuestions) {
    if (!totalQuestions || totalQuestions <= 0) return 0;
    return Math.round((Number(correctCount) / Number(totalQuestions)) * 100);
}
