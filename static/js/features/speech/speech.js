/**
 * JLPT Dokkai Master - Web Speech API Feature
 * Handles Japanese text-to-speech pronunciation with graceful degradation.
 */

export function speakJapanese(text) {
    if (!text || typeof text !== 'string') return;
    if (typeof window === 'undefined' || !('speechSynthesis' in window) || typeof window.SpeechSynthesisUtterance === 'undefined') {
        return;
    }
    try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ja-JP';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    } catch (e) {
        console.warn('Speech synthesis error', e);
    }
}

