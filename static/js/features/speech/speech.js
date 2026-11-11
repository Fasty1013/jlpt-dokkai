/**
 * JLPT Dokkai Master - Web Speech API Feature (Step 11c)
 * Japanese text-to-speech with graceful degradation:
 *  - furigana (<rt>/<rp>) and any other markup is removed before synthesis, so readings are not spoken twice;
 *  - long text is split into sentences (。！？ and line breaks) and spoken as a queue;
 *  - utterances are kept referenced until the queue ends (Chromium/Android garbage-collect
 *    unreferenced utterances and drop their events, which cuts speech off);
 *  - waits for ja-JP voices (speechSynthesis.onvoiceschanged) instead of falling back to the default voice.
 */

const MAX_CHUNK_CHARS = 120;     // Chromium silently stops long utterances (~15 s)
const VOICES_TIMEOUT_MS = 1500;  // do not wait for voices forever

// Strong references to the utterances of the running queue (GC protection).
let activeQueue = [];
let queueToken = 0;

const ENTITIES = { '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'" };

/** Plain speakable text: drops <rt>/<rp> (with content), all other tags, decodes basic entities. */
export function toSpeakableText(input) {
    if (typeof input !== 'string') return '';
    let text = input
        .replace(/<rt\b[^>]*>[\s\S]*?<\/rt>/gi, '')
        .replace(/<rp\b[^>]*>[\s\S]*?<\/rp>/gi, '')
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/(p|div|li|h[1-6])>/gi, '\n')
        .replace(/<[^>]+>/g, '');
    text = text.replace(/&(?:nbsp|amp|lt|gt|quot|#39);/g, (m) => ENTITIES[m]);
    return text.replace(/[ \t 　]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim();
}

/** Split into sentences at 。！？!? and line breaks; over-long sentences are cut at 、 / commas. */
export function splitIntoSentences(text) {
    if (!text) return [];
    const parts = text.match(/[^。！？!?\n]+[。！？!?]*|[。！？!?]+/g) || [];
    const sentences = [];
    for (const raw of parts) {
        const part = raw.trim();
        if (!part || /^[。！？!?]+$/.test(part)) continue;
        if (part.length <= MAX_CHUNK_CHARS) {
            sentences.push(part);
            continue;
        }
        let buf = '';
        for (const piece of part.match(/[^、，,]+[、，,]?/g) || [part]) {
            if (buf && (buf + piece).length > MAX_CHUNK_CHARS) {
                sentences.push(buf);
                buf = '';
            }
            buf += piece;
        }
        if (buf) sentences.push(buf);
    }
    return sentences;
}

function getVoicesSafe(synth) {
    try {
        return synth.getVoices() || [];
    } catch (e) {
        return [];
    }
}

function pickJapaneseVoice(voices) {
    const ja = voices.filter((v) => /^ja([-_]|$)/i.test(v.lang || ''));
    return ja.find((v) => /^ja[-_]JP$/i.test(v.lang)) || ja[0] || null;
}

/** Resolves with the voice list as soon as it is non-empty (or after a timeout with whatever exists). */
function waitForVoices(synth) {
    const now = getVoicesSafe(synth);
    if (now.length > 0) return Promise.resolve(now);
    return new Promise((resolve) => {
        let done = false;
        const finish = () => {
            if (done) return;
            done = true;
            clearTimeout(timer);
            if (typeof synth.removeEventListener === 'function') synth.removeEventListener('voiceschanged', onChange);
            resolve(getVoicesSafe(synth));
        };
        const onChange = () => {
            if (getVoicesSafe(synth).length > 0) finish();
        };
        const timer = setTimeout(finish, VOICES_TIMEOUT_MS);
        if (typeof synth.addEventListener === 'function') synth.addEventListener('voiceschanged', onChange);
        else synth.onvoiceschanged = onChange;
    });
}

function enqueue(synth, sentences, voice, token) {
    activeQueue = sentences.map((sentence, index) => {
        const utterance = new window.SpeechSynthesisUtterance(sentence);
        utterance.lang = 'ja-JP';
        utterance.rate = 0.9;
        if (voice) utterance.voice = voice;
        const release = () => {
            if (token !== queueToken) return;
            if (index === sentences.length - 1) activeQueue = [];
        };
        utterance.onend = release;
        utterance.onerror = release;
        return utterance;
    });
    // The array above holds the references; the engine plays them in order.
    activeQueue.forEach((u) => synth.speak(u));
}

export function stopSpeaking() {
    queueToken++;
    activeQueue = [];
    try {
        if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel();
    } catch (e) {
        console.warn('Speech synthesis error', e);
    }
}

/**
 * Speak Japanese text (plain text or ruby HTML). Cancels any previous speech.
 * Returns a promise that resolves when the queue has been handed to the engine.
 */
export async function speakJapanese(text) {
    if (!text || typeof text !== 'string') return;
    if (typeof window === 'undefined' || !('speechSynthesis' in window) || typeof window.SpeechSynthesisUtterance === 'undefined') {
        return;
    }
    try {
        const synth = window.speechSynthesis;
        const sentences = splitIntoSentences(toSpeakableText(text));
        if (sentences.length === 0) return;

        stopSpeaking();
        const token = queueToken;

        let voices = getVoicesSafe(synth);
        if (voices.length === 0) {
            voices = await waitForVoices(synth);
            if (token !== queueToken) return; // a newer request replaced this one while waiting
        }
        enqueue(synth, sentences, pickJapaneseVoice(voices), token);
    } catch (e) {
        console.warn('Speech synthesis error', e);
    }
}
