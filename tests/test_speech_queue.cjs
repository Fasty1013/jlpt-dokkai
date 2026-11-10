/**
 * Step 11c: unit checks for static/js/features/speech/speech.js (no browser, fake speechSynthesis).
 * Usage: node tests/test_speech_queue.cjs
 */
const path = require('path');
const { pathToFileURL } = require('url');

let failed = 0;
const eq = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${ok ? '' : `\n   got:  ${JSON.stringify(got)}\n   want: ${JSON.stringify(want)}`}`);
  if (!ok) failed++;
};

(async () => {
  const url = pathToFileURL(path.join(__dirname, '..', 'static', 'js', 'features', 'speech', 'speech.js')).href;

  // --- fake browser environment -------------------------------------------------
  const spoken = [];
  let cancelled = 0;
  let voices = [];
  const listeners = {};
  global.window = {
    speechSynthesis: {
      speak: (u) => spoken.push(u),
      cancel: () => { cancelled++; },
      getVoices: () => voices,
      addEventListener: (t, fn) => { listeners[t] = fn; },
      removeEventListener: (t) => { delete listeners[t]; }
    },
    SpeechSynthesisUtterance: function (text) { this.text = text; }
  };
  global.SpeechSynthesisUtterance = global.window.SpeechSynthesisUtterance;

  const S = await import(url);

  // --- toSpeakableText ----------------------------------------------------------
  eq('rt removed', S.toSpeakableText('<ruby>漢字<rt>かんじ</rt></ruby>を読む'), '漢字を読む');
  eq('rp+rt removed', S.toSpeakableText('<ruby>日本<rp>(</rp><rt>にほん</rt><rp>)</rp></ruby>'), '日本');
  eq('plain text untouched', S.toSpeakableText('先生'), '先生');
  eq('tags and entities', S.toSpeakableText('<p>A&amp;B</p><p>こんにちは</p>'), 'A&B\nこんにちは');
  eq('non-string', S.toSpeakableText(null), '');

  // --- splitIntoSentences -------------------------------------------------------
  eq('split by 。！？', S.splitIntoSentences('本日、お荷物をお届けにまいりました。留守でした！よろしく？'), ['本日、お荷物をお届けにまいりました。', '留守でした！', 'よろしく？']);
  eq('split by newline', S.splitIntoSentences('一行目\n二行目'), ['一行目', '二行目']);
  const long = ('あ'.repeat(50) + '、').repeat(5) + '終わり。';
  const chunks = S.splitIntoSentences(long);
  eq('long sentence chunked <=120 and lossless', [chunks.every((c) => c.length <= 120), chunks.join('')], [true, long]);

  // --- speakJapanese: queue, voice wait, GC refs --------------------------------
  await S.speakJapanese('<ruby>今日<rt>きょう</rt></ruby>は晴れです。明日は雨です。');
  eq('no voices: waits then speaks after timeout, 2 utterances', spoken.map((u) => u.text), ['今日は晴れです。', '明日は雨です。']);
  eq('lang/rate set', [spoken[0].lang, spoken[0].rate], ['ja-JP', 0.9]);
  eq('no ja voice -> default voice (none set)', spoken[0].voice, undefined);

  spoken.length = 0;
  voices = [{ lang: 'en-US', name: 'en' }, { lang: 'ja-JP', name: 'Kyoko' }];
  await S.speakJapanese('先生');
  eq('ja-JP voice picked when available', spoken[0].voice && spoken[0].voice.name, 'Kyoko');

  // voiceschanged arrives while waiting
  spoken.length = 0;
  voices = [];
  const p = S.speakJapanese('学校');
  voices = [{ lang: 'ja-JP', name: 'Late' }];
  listeners.voiceschanged && listeners.voiceschanged();
  await p;
  eq('voiceschanged unblocks the wait and voice is used', spoken[0] && spoken[0].voice && spoken[0].voice.name, 'Late');

  // a newer request replaces one that is still waiting for voices
  spoken.length = 0;
  voices = [];
  const first = S.speakJapanese('最初');
  voices = [{ lang: 'ja-JP', name: 'V' }];
  const second = S.speakJapanese('二番目');
  await Promise.all([first, second]);
  eq('stale request dropped, only latest spoken', spoken.map((u) => u.text), ['二番目']);

  eq('cancel() called for each request', cancelled > 0, true);
  S.stopSpeaking();

  console.log(failed ? `\n${failed} FAILED` : '\nALL PASSED');
  process.exit(failed ? 1 : 0);
})();
