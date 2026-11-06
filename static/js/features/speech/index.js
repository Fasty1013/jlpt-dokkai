/**
 * JLPT Dokkai Master - Speech Feature Entry Point
 */
import { speakJapanese } from './speech.js';

export { speakJapanese };

if (typeof window !== 'undefined') {
    window.speakJapanese = speakJapanese;
    window.DokkaiSpeech = {
        speakJapanese
    };
}

