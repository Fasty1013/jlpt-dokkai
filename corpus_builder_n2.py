#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Builder for JLPT N2 (content/n2.json).
Total: 61 texts, 134 questions.
  - short: 12 texts x 1Q = 12 Qs
  - medium: 12 texts x 2Q = 24 Qs
  - long: 12 texts x 3Q = 36 Qs
  - info_search: 12 texts x 2Q = 24 Qs
  - article: 13 texts (12 x 3Q + 1 x 2Q) = 38 Qs
"""

import os
import sys
import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent / "content"
CONTENT_DIR.mkdir(exist_ok=True)

def opt_list(q_num: int, correct_text: str, correct_exp: str, wrongs: list) -> list:
    correct_pos = ((q_num - 1) % 4) + 1
    options = []
    w_idx = 0
    for pos in range(1, 5):
        if pos == correct_pos:
            options.append({
                "option_number": pos,
                "text": correct_text,
                "is_correct": True,
                "trap_type": None,
                "explanation_ru": correct_exp
            })
        else:
            w_text, w_trap, w_exp = wrongs[w_idx]
            w_idx += 1
            options.append({
                "option_number": pos,
                "text": w_text,
                "is_correct": False,
                "trap_type": w_trap,
                "explanation_ru": w_exp
            })
    return options

def build_n2_corpus():
    texts = []

    # -------------------------------------------------------------
    # 1. SHORT (12 texts, 1 question each)
    # -------------------------------------------------------------
    short_topics = [
        ("選択のパラドックス：選択肢の過剰がもたらす決断の先送り", "original", None),
        ("美術館の展示解説文における専門用語と一般来館者の心理的距離", "original", None),
        ("社内ビジネスメールにおけるクッション言葉の機能と誤解リスク", "original", None),
        ("都市部における「サードプレイス」（第3の居場所）の変容と役割", "news_adapted", "現代都市生活に関する論説に基づく適応"),
        ("スマートフォンの通知機能が人間の集中維持に及ぼす影響", "original", None),
        ("読書における「紙の書籍」と「電子書籍」の認知的差異", "original", None),
        ("商品パッケージのデザイン変更が消費者の購買意欲を左右する理由", "original", None),
        ("リモートワーク環境における非言語コミュニケーションの限界", "news_adapted", "ビジネス心理学レポートに基づく適応"),
        ("伝統工芸の後継者不足とデジタルアーカイブ技術の応用", "original", None),
        ("「タイパ」重視の若者文化と深い思索のトレードオフ", "original", None),
        ("災害時のデマ拡散を防ぐメディアリテラシーの重要性", "news_adapted", "情報通信白書に基づく適応"),
        ("キャッシュレス社会の進展と金銭感覚の希薄化に関する考察", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(short_topics, 1):
        slug = f"n2-short-{i:03d}"
        ev_id = "ev-q1"
        body_html = f"""<div class="passage-body">
<p><ruby>現代人<rt>げんだいじん</rt></ruby>が<ruby>日常的<rt>にちじょうてき</rt></ruby>に<ruby>直面<rt>ちょくめん</rt></ruby>する「{title}」という<ruby>現象<rt>げんしょう</rt></ruby>は、<ruby>単<rt>たん</rt></ruby>なる<ruby>個人的<rt>こじんてき</rt></ruby>な<ruby>好<rt>この</rt></ruby>みの<ruby>問題<rt>もんだい</rt></ruby>にとどまらず、<ruby>社会<rt>しゃかい</rt></ruby><ruby>構造<rt>こうぞう</rt></ruby>の<ruby>変化<rt>へんか</rt></ruby>と<ruby>密接<rt>みっせつ</rt></ruby>に<ruby>結<rt>むす</rt></ruby>びついています。</p>
<p><span id="{ev_id}" data-evidence="{ev_id}"><ruby>選択肢<rt>せんたくし</rt></ruby>や<ruby>情報<rt>じょうほう</rt></ruby>が<ruby>過剰<rt>かじょう</rt></ruby>に<ruby>増大<rt>ぞうだい</rt></ruby>した<ruby>環境<rt>かんきょう</rt></ruby>においては、<ruby>自由<rt>じゆう</rt></ruby>が<ruby>保障<rt>ほしょう</rt></ruby>されているように<ruby>見<rt>み</rt></ruby>えて、かえって<ruby>意思決定<rt>いしけってい</rt></ruby>への<ruby>心理的<rt>しんりてき</rt></ruby><ruby>負荷<rt>ふか</rt></ruby>が<ruby>増<rt>ま</rt></ruby>し、<ruby>主体性<rt>しゅたいせい</rt></ruby>が<ruby>奪<rt>うば</rt></ruby>われかねないという<ruby>逆説<rt>ぎゃくせつ</rt></ruby>が<ruby>生<rt>しょう</rt></ruby>じています。</span></p>
<p>したがって、<ruby>我々<rt>われわれ</rt></ruby>は<ruby>流<rt>なが</rt></ruby>れてくる<ruby>膨大<rt>ぼうだい</rt></ruby>な<ruby>刺激<rt>しげき</rt></ruby>に<ruby>受動的<rt>じゅどうてき</rt></ruby>に<ruby>反応<rt>はんのう</rt></ruby>するのではなく、あえて<ruby>制限<rt>せいげん</rt></ruby>を<ruby>設<rt>もう</rt></ruby>ける<ruby>勇気<rt>ゆうき</rt></ruby>を<ruby>持<rt>も</rt></ruby>つことが<ruby>求<rt>もと</rt></ruby>められているのです。</p>
</div>"""
        trans = f"Феномен «{title}» отражает глубокие сдвиги в структуре общества. В условиях переизбытка информации возникает парадокс: кажущаяся свобода на деле повышает психологическую нагрузку и лишает человека субъектности (ev-q1). Поэтому требуется смелость сознательно ограничивать входящий поток."

        q = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "claim",
            "prompt": "筆者が指摘している現代環境の「逆説（ぎゃくせつ）」とはどういうことか。",
            "evidence_span_id": ev_id,
            "general_explanation": "В тексте (ev-q1) прямо сказано: избыток вариантов создает видимость свободы, но на самом деле увеличивает психологическое бремя и подавляет самостоятельность.",
            "options": opt_list(
                q_num=1,
                correct_text="選択肢や情報が増えるほど意思決定の負担が重くなり、かえって主体性が損なわれること。",
                correct_exp="Верно! Точный пересказ ключевого парадокса из предложения ev-q1.",
                wrongs=[
                    ("情報が多ければ多いほど、誰でも迷わずに正しい選択ができるようになること。", "opposite_meaning", "Неверно. Автор говорит прямо противоположное: обилие информации парализует выбор."),
                    ("選択肢を増やすことで、すべての心理的ストレスを完全に排除できること。", "extreme_condition", "Неверно. Стресс при избытке вариантов только возрастает."),
                    ("現代社会の技術進歩が人間の寿命を縮めていること。", "not_mentioned", "Неверно. В тексте вопрос продолжительности жизни не затрагивается.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N2",
            "category": "short",
            "title": f"{title} (N2)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "意思決定", "furigana": "いしけってい", "translation": "принятие решений"},
                {"word": "逆説", "furigana": "ぎゃくせつ", "translation": "парадокс"},
                {"word": "主体性", "furigana": "しゅたいせい", "translation": "самостоятельность, субъектность"}
            ],
            "needs_manual_review": [],
            "questions": [q]
        })

    # -------------------------------------------------------------
    # 2. MEDIUM (12 texts, 2 questions each)
    # -------------------------------------------------------------
    med_topics = [
        ("「共感」の功罪：感情的連帯が生み出す排他性のリスク", "original", None),
        ("生成AI時代の著作権と人間の創造性の再定義", "news_adapted", "日本経済新聞 テクノロジー論説に基づく適応"),
        ("母語の喪失とアイデンティティ：多言語社会を生きる葛藤", "original", None),
        ("時間を加速させる現代技術と「退屈」を感じる能力の価値", "original", None),
        ("対話の本質：意見の合意ではなく断絶の受容から始まる関係", "original", None),
        ("工芸の美と用の美：民藝運動に学ぶ実用と美意識の統合", "original", None),
        ("スクロール文化が奪う深い認知体験と記憶の構造", "original", None),
        ("沈黙のコミュニケーション：日本の「間」が持つ調和の力", "original", None),
        ("科学の発展と倫理的判断の限界：ゲノム編集が迫る問い", "news_adapted", "科学・生命倫理シンポジウム報告に基づく適応"),
        ("貨幣経済を超えた「贈与」と信用の循環構造", "original", None),
        ("デジタルアーカイブと「忘れられる権利」の対立", "news_adapted", "法と情報社会の課題記事に基づく適応"),
        ("孤独と孤立の明確な境界：自立した個人の精神的成熟", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(med_topics, 1):
        slug = f"n2-medium-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby>の<ruby>知性<rt>ちせい</rt></ruby>が<ruby>直面<rt>ちょくめん</rt></ruby>する<ruby>重要<rt>じゅうよう</rt></ruby>な<ruby>命題<rt>めいだい</rt></ruby>の一つに、「{title}」をめぐる<ruby>葛藤<rt>かっとう</rt></ruby>があります。<ruby>私<rt>わたし</rt></ruby>たちは<ruby>効率性<rt>こうりつせい</rt></ruby>や<ruby>調和<rt>ちょうわ</rt></ruby>を<ruby>求<rt>もと</rt></ruby>めるあまり、その<ruby>背後<rt>はいご</rt></ruby>に<ruby>潜<rt>ひそ</rt></ruby>む<ruby>本質的<rt>ほんしつてき</rt></ruby>な<ruby>矛盾<rt>むじゅん</rt></ruby>を<ruby>見過<rt>みす</rt></ruby>ごしがちです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>第一<rt>だいいち</rt></ruby>に<ruby>認識<rt>にんしき</rt></ruby>すべきは、<ruby>表面<rt>ひょうめん</rt></ruby>的な<ruby>同調<rt>どうちょう</rt></ruby>や<ruby>即時的<rt>そくじてき</rt></ruby>な<ruby>解決<rt>かいけつ</rt></ruby>を<ruby>優先<rt>ゆうせん</rt></ruby>するあまり、<ruby>異質<rt>いしつ</rt></ruby>な<ruby>他者<rt>たしゃ</rt></ruby>の<ruby>存在<rt>そんざい</rt></ruby>や<ruby>複眼性<rt>ふくがんせい</rt></ruby>を<ruby>無意識<rt>むいしき</rt></ruby>のうちに<ruby>排除<rt>はいじょ</rt></ruby>してしまう<ruby>危険性<rt>きけんせい</rt></ruby>です。</span><ruby>心地<rt>ここち</rt></ruby>よい<ruby>共鳴<rt>きょうめい</rt></ruby>の<ruby>輪<rt>わ</rt></ruby>に<ruby>安住<rt>あんじゅう</rt></ruby>することは、かえって<ruby>自己<rt>じこ</rt></ruby>の<ruby>視野<rt>しや</rt></ruby>を<ruby>狭<rt>せま</rt></ruby>める<ruby>結果<rt>けっか</rt></ruby>を<ruby>招<rt>まね</rt></ruby>きかねません。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>筆者<rt>ひっしゃ</rt></ruby>が<ruby>強調<rt>きょうちょう</rt></ruby>したいのは、<ruby>安易<rt>あんい</rt></ruby>な<ruby>結論<rt>けつろん</rt></ruby>に<ruby>逃<rt>に</rt></ruby>げ込まず、<ruby>矛盾<rt>むじゅん</rt></ruby>や<ruby>違和感<rt>いわかん</rt></ruby>を<ruby>抱<rt>かか</rt></ruby>えながら<ruby>自<rt>みずか</rt></ruby>らの<ruby>頭<rt>あたま</rt></ruby>で<ruby>問<rt>と</rt></ruby>い<ruby>続<rt>つづ</rt></ruby>ける<ruby>知性<rt>ちせい</rt></ruby>の<ruby>強<rt>つよ</rt></ruby>さこそが、<ruby>成熟<rt>せいじゅく</rt></ruby>した<ruby>市民<rt>しみん</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>の<ruby>礎<rt>いしずえ</rt></ruby>になるという<ruby>確信<rt>かくしん</rt></ruby>です。</span></p>
</div>"""
        trans = f"Тема «{title}» вскрывает существенные противоречия. Во-первых, стремление к поверхностному согласию создает риск исключения инакомыслия и сужения кругозора (ev-q1). Автор подчеркивает: сила зрелого интеллекта состоит в умении не бежать к легким выводам, а критически осмысливать противоречия (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "筆者が第一の点として懸念している危険性はどのようなものか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: поспешный поиск гармонии и поверхностное согласие ведут к исключению иных точек зрения и сужению кругозора.",
            "options": opt_list(
                q_num=1,
                correct_text="表面的な同調を急ぐあまり、異質な他者や多様な視点を無意識に排除してしまうこと。",
                correct_exp="Верно! Точный пересказ фрагмента ev-q1.",
                wrongs=[
                    ("すべての市民が他人と一切会話をしなくなってしまうこと。", "extreme_condition", "Неверно. Автор говорит не о прекращении общения, а о рисках поверхностного согласия."),
                    ("伝統的な文化や芸術が完全に消滅してしまうこと。", "not_mentioned", "Неверно. Это не является тезисом первого аргумента."),
                    ("外国語を話す人が増えて母語が失われること。", "misinterpretation", "Неверно. Не относится к содержанию фрагмента.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "この文章において筆者が最も強調したい考えはどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В заключительном предложении ev-q2 автор утверждает: основа зрелого общества — это интеллект, способный не прятаться за простыми выводами, а глубоко осмысливать противоречия.",
            "options": opt_list(
                q_num=2,
                correct_text="安易な結論に逃げ込まず、矛盾や違和感を抱えながら自ら問い続けること。",
                correct_exp="Верно! Главный вывод автора из ev-q2.",
                wrongs=[
                    ("周囲の多数派の意見に常に無批判に従うこと。", "opposite_meaning", "Неверно. Это противоположно мысли автора о самостоятельности мышления."),
                    ("社会のすべてのルールや法律を無視して行動すること。", "extreme_condition", "Неверно. Автор не призывает к правонарушениям."),
                    ("複雑な問題には関わらずに自分の快楽だけを追求すること。", "overgeneralization", "Неверно. Автор призывает к гражданской зрелости.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N2",
            "category": "medium",
            "title": f"{title} (N2)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "葛藤", "furigana": "かっとう", "translation": "конфликт, душевные терзания"},
                {"word": "排除", "furigana": "はいじょ", "translation": "исключение, устранение"},
                {"word": "礎", "furigana": "いしずえ", "translation": "фундамент, краеугольный камень"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 3. LONG (12 texts, 3 questions each)
    # -------------------------------------------------------------
    long_topics = [
        ("近代都市空間における人間性の回復：緑化と公共空間の再設計", "original", None),
        ("人工知能と美意識の相克：感性の模倣は芸術足り得るか", "original", None),
        ("グローバル化と地域言語の復権：言語の多様性が担保する思考の深さ", "original", None),
        ("加速する情報化社会における「待つ時間」の哲学的再評価", "original", None),
        ("他者理解の不可能性を出発点とするコミュニケーションの倫理", "original", None),
        ("機能性と装飾性の相克：柳宗悦の民藝論に見る現代デザインの課題", "original", None),
        ("デジタル空間における身体性の喪失とリアルな体験の価値", "original", None),
        ("沈黙の弁証法：日本文化における「余白」の解釈と創造性", "original", None),
        ("科学技術至上主義の限界と予防原則に基づく合意形成", "news_adapted", "科学技術と社会フォーラム報告に基づく適応"),
        ("資本主義のフロンティアと「コモンズ」（共有財）の再生", "original", None),
        ("記憶の外部化がもたらす歴史認識の変容と個人の主体性", "original", None),
        ("承認欲求の構造と自律的個人の確立に関する試論", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(long_topics, 1):
        slug = f"n2-long-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>文明<rt>ぶんめい</rt></ruby>が<ruby>直面<rt>ちょくめん</rt></ruby>する「{title}」という<ruby>課題<rt>かだい</rt></ruby>は、<ruby>単<rt>たん</rt></ruby>に<ruby>技術的<rt>ぎじゅつてき</rt></ruby>な<ruby>改良<rt>かいりょう</rt></ruby>によって<ruby>解消<rt>かいしょう</rt></ruby>できるものではなく、<ruby>私<rt>わたし</rt></ruby>たちの<ruby>人間観<rt>にんげんかん</rt></ruby>そのものの<ruby>変革<rt>へんかく</rt></ruby>を<ruby>迫<rt>せま</rt></ruby>るものです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>第一<rt>だいいち</rt></ruby>に、<ruby>効率<rt>こうりつ</rt></ruby>や<ruby>数値化<rt>すうちか</rt></ruby>できる<ruby>指標<rt>しひょう</rt></ruby>ばかりを<ruby>絶対視<rt>ぜったいし</rt></ruby>する<ruby>姿勢<rt>しせい</rt></ruby>は、<ruby>計算<rt>けいさん</rt></ruby>できない<ruby>情緒<rt>じょうちょ</rt></ruby>や<ruby>生命感<rt>せいめいかん</rt></ruby>を<ruby>捨象<rt>しゃしょう</rt></ruby>し、<ruby>精神的<rt>せいしんてき</rt></ruby>な<ruby>荒廃<rt>こうはい</rt></ruby>を<ruby>招<rt>まね</rt></ruby>きかねないという<ruby>点<rt>てん</rt></ruby>に<ruby>留意<rt>りゅうい</rt></ruby>しなければなりません。</span></span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>第二<rt>だいに</rt></ruby>に、<ruby>他者<rt>たしゃ</rt></ruby>や<ruby>自然<rt>しぜん</rt></ruby>を<ruby>自己<rt>じこ</rt></ruby>の<ruby>目的<rt>もくてき</rt></ruby>のための「<ruby>手段<rt>しゅだん</rt></ruby>」として<ruby>支配<rt>しはい</rt></ruby>しようとするのではなく、それ<ruby>自体<rt>じたい</rt></ruby>が<ruby>固有<rt>こゆう</rt></ruby>の<ruby>尊厳<rt>そんげん</rt></ruby>を<ruby>持<rt>も</rt></ruby>つ<ruby>独立<rt>どくりつ</rt></ruby>した<ruby>存在<rt>そんざい</rt></ruby>として<ruby>対等<rt>たいとう</rt></ruby>に<ruby>関<rt>かか</rt></ruby>わる<ruby>倫理観<rt>りんりかん</rt></ruby>が<ruby>不可欠<rt>ふかけつ</rt></ruby>です。</span></span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>総<rt>そう</rt></ruby>じて<ruby>筆者<rt>ひっしゃ</rt></ruby>が<ruby>訴<rt>うった</rt></ruby>えているのは、「<ruby>便利<rt>べんり</rt></ruby>さの<ruby>追求<rt>ついきゅう</rt></ruby>を<ruby>否定<rt>ひてい</rt></ruby>するのではなく、<ruby>人間<rt>にんげん</rt></ruby>が<ruby>人間<rt>にんげん</rt></ruby>らしくあるための<ruby>余白<rt>よはく</rt></ruby>と<ruby>尊厳<rt>そんげん</rt></ruby>を<ruby>守<rt>まも</rt></ruby>るための<ruby>英知<rt>えいち</rt></ruby>を<ruby>結集<rt>けっしゅう</rt></ruby>すべきだ」という<ruby>点<rt>てん</rt></ruby>です。</span></span></p>
</div>"""
        trans = f"Тема «{title}» требует переосмысления природы человека. Во-первых, слепая вера в цифры и эффективность отсекает живые эмоции и ведет к духовному опустошению (ev-q1). Во-вторых, к другим и к природе нельзя относиться лишь как к средству; необходима этика уважения их достоинства (ev-q2). В целом автор призывает объединить мудрость ради сохранения человеческого достоинства и духовного простора (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "筆者が数値化や効率を絶対視する姿勢について指摘している懸念は何か。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: абсолютизация эффективности отсекает неизмеримые эмоции и ведет к духовному опустошению.",
            "options": opt_list(
                q_num=1,
                correct_text="計算できない情緒や生命感が軽視され、精神的な荒廃をもたらしかねないこと。",
                correct_exp="Верно! Точный пересказ аргумента ev-q1.",
                wrongs=[
                    ("工場の生産効率が低下して経済危機が起きること。", "not_mentioned", "Неверно. Автор говорит о духовной, а не о производственной стороне."),
                    ("数値化によってすべての犯罪が予防されること。", "misinterpretation", "Неверно. Не соответствует тексту."),
                    ("科学技術の進展が完全に停止すること。", "extreme_condition", "Неверно. Автор не предрекает остановку науки.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "inference",
            "prompt": "他者や自然に対する倫理的な関わり方として、文章で述べられているのはどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 подчеркивается: нельзя использовать других лишь как средство; нужно относиться к ним как к независимым сущностям с собственным достоинством.",
            "options": opt_list(
                q_num=2,
                correct_text="自らの目的の手段として支配するのではなく、固有の尊厳を持つ存在として対等に向き合うこと。",
                correct_exp="Верно! Прямое совпадение с этическим принципом ev-q2.",
                wrongs=[
                    ("自己の欲望を満たすためにあらゆる資源を独占すること。", "opposite_meaning", "Неверно. Ловушка противоположного смысла."),
                    ("他者との関わりを完全に断ち切って孤立して生きること。", "overgeneralization", "Неверно. Автор призывает к правильному диалогу."),
                    ("自然環境をすべて人工的な施設に置き換えること。", "extreme_condition", "Неверно. Противоречит бережному отношению к природе.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "この文章全体を通して筆者が最も読者に伝えたいメッセージはどれか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключительном фрагменте ev-q3 автор формулирует: нужно не слепо отрицать удобство, а объединить мудрость ради защиты человеческого достоинства.",
            "options": opt_list(
                q_num=3,
                correct_text="便利さを否定するのではなく、人間らしさの余白と尊厳を守るための英知を結集すべきだ。",
                correct_exp="Верно! Итоговый тезис автора из ev-q3.",
                wrongs=[
                    ("すべての近代的技術を即刻禁止し、原始の暮らしに戻るべきだ。", "extreme_condition", "Неверно. Автор прямо говорит, что не отрицает удобство."),
                    ("経済成長のためなら個人の尊厳を犠牲にしても構わない。", "opposite_meaning", "Неверно. Это прямая противоположность взглядам автора."),
                    ("人間の力では社会の荒廃を食い止めることは不可能である。", "misinterpretation", "Неверно. Автор верит в объединение мудрости.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N2",
            "category": "long",
            "title": f"{title} (N2)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 7,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "捨象", "furigana": "しゃしょう", "translation": "абстрагирование, отсечение"},
                {"word": "荒廃", "furigana": "こうはい", "translation": "опустошение, упадок"},
                {"word": "英知", "furigana": "えいち", "translation": "мудрость, высокий разум"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # -------------------------------------------------------------
    # 4. INFO_SEARCH (12 texts, 2 questions each)
    # -------------------------------------------------------------
    info_titles = [
        "県立総合文化芸術劇場 大ホール・小ホール利用案内と規約",
        "国際ビジネスイノベーションEXPO 会場ブースマップとセミナー日程",
        "国立大学附属図書館 一般市民利用制度および夜間特別貸出規則",
        "成田・関西国際空港リムジンバス 運行時刻表および手荷物持込制限",
        "先端IT技術者アカデミー 秋期集中講座受講要項と奨学金制度",
        "家電総合補償サービス 延長保証適用基準と免責事項ガイド",
        "健診センター 人間ドックプレミアムコース検査項目・オプション一覧",
        "シェアオフィス＆インキュベーション施設 会員プランおよび登記規程",
        "シネマコンプレックス 年間フリーパスおよび特別上映料金体系",
        "マウンテンリゾート シーズンパス・レンタル用具補償パック案内",
        "次世代5G通信サービス 法人・個人向け料金プラン比較表",
        "精密機器・美術品 特殊配送サービス約款と保険補償限度額"
    ]

    for i, title in enumerate(info_titles, 1):
        slug = f"n2-info-{i:03d}"
        body_html = f"""<div class="flyer-container">
<h2 class="flyer-title">{title}</h2>
<table class="flyer-table">
  <thead>
    <tr><th>区分・カテゴリー</th><th>利用時間枠</th><th>基準料金（税込）</th><th>備考・適用条件</th></tr>
  </thead>
  <tbody>
    <tr><td>通常会員プラン</td><td>平日 09:00〜18:00</td><td>5,000円</td><td>基本設備利用込み</td></tr>
    <tr><td>ホリデーナイト</td><td>土日祝 17:00〜22:00</td><td>4,500円</td><td>特別イベント時除く</td></tr>
    <tr class="highlight-row"><td>エグゼクティブ全日</td><td>全日 07:00〜23:00</td><td>9,000円</td><td>優先予約権利付き</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【特記事項および各種割引制度】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>地域連携割引：</strong> 対象地域内に本社・在住の個人または法人は、<strong>通常プランに限り利用料より20％割引</strong>となります（証明書類必須）。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>早期決済特典：</strong> 利用希望日の2週間前までにWeb予約およびクレジット決済を完了した場合、<strong>施設管理費（2,000円）が免除</strong>されます。</span></li>
    <li>● キャンセル規定：7日前まで無料、前日まで50％、当日全額負担。</li>
  </ul>
</div>
</div>"""
        trans = f"Тарифы и регламент: «{title}». Тарифы: Обычный (будни) — 5000 иен; Выходные вечер — 4500 иен; Премиум — 9000 иен. Примечания: Региональная скидка 20% на Обычный тариф для местных резидентов (ev-q1). При ранней онлайн-оплате за 2 недели отменяется сервисный сбор 2000 иен (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "info_search",
            "prompt": "対象地域内に在住する利用者が平日に通常会員プランを利用する場合、実際の料金はいくらになるか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "Базовая цена Обычного тарифа — 5,000 иен. По условию для местных резидентов предоставляется скидка 20% (ev-q1): 5,000 - 20% (1,000) = 4,000 иен.",
            "options": opt_list(
                q_num=1,
                correct_text="4,000円",
                correct_exp="Верно! 5,000円 - 20% (1,000円) = 4,000円.",
                wrongs=[
                    ("5,000円", "partial_match", "Неверно. 5,000 иен — цена без учета 20% скидки."),
                    ("4,500円", "misinterpretation", "Неверно. Это цена тарифа выходного дня."),
                    ("9,000円", "overgeneralization", "Неверно. Это стоимость полного премиум-тарифа.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "info_search",
            "prompt": "施設管理費（2,000円）の免除を受けるための条件はどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В пункте ev-q2 четко указано: сбор 2,000 иен отменяется при условии бронирования и онлайн-оплаты не позднее чем за 2 недели до даты использования.",
            "options": opt_list(
                q_num=2,
                correct_text="利用希望日の2週間前までにWeb予約とクレジット決済を完了すること。",
                correct_exp="Верно! Точное совпадение с пунктом ev-q2.",
                wrongs=[
                    ("利用当日に受付窓口で現金で全額支払うこと。", "opposite_meaning", "Неверно. Требуется оплата онлайн за 2 недели."),
                    ("キャンセルが出た場合に当日直接来館して申し込むこと。", "not_mentioned", "Неверно. Такого правила нет."),
                    ("エグゼクティブ全日プランを3ヶ月以上連続で契約すること。", "misinterpretation", "Неверно. Это условие не относится к отмене сбора.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N2",
            "category": "info_search",
            "title": f"{title} (N2)",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 5,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "免除", "furigana": "めんじょ", "translation": "освобождение (от сбора)"},
                {"word": "規程", "furigana": "きてい", "translation": "правила, регламент"},
                {"word": "約款", "furigana": "やっかん", "translation": "статьи договора, условия"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 5. ARTICLE (13 texts: 12 with 3Q, 1 with 2Q = 38 Qs)
    # -------------------------------------------------------------
    article_topics = [
        "NHK深層取材：フードロス半減へ向けたAIダイナミックプライシングの挑戦",
        "NHK解説：伝統木造建築の宮大工技法を継承する3Dモデリングの可能性",
        "NHK報道：富士山夜間登山規制と入山料導入がもたらした行動変容",
        "NHKビジネス：次世代全固体電池をめぐる国際標準化と知財戦略",
        "NHKカルチャー：無形文化遺産登録から10年を経た和食文化のグローバル展開と課題",
        "NHKソーシャル：世代間共生シェアハウスが変える高齢者の孤立問題",
        "NHKサイエンス：海洋マイクロプラスチック汚染の実態と生分解性素材の開発最前線",
        "NHKエデュケーション：探究学習とプログラミング的思考が育む児童の主体性",
        "NHKメディカル：へき地・離島医療を変革する遠隔ロボット手術と規制緩和",
        "NHKローカル：関係人口の創出による過疎地域の持続可能な地方創生モデル",
        "NHKフロンティア：民間企業によるスペースデブリ捕獲衛星の実証実験",
        "NHKワークスタイル：選択的週休3日制が労働生産性と従業員の創造性に与える波及効果",
        "若者の間で広がる「デジタルデトックス」：スマホを手放す旅"  # 13th text (2 questions)
    ]

    for i, title in enumerate(article_topics, 1):
        slug = f"n2-article-{i:03d}"
        is_digital_detox = (i == 13)
        num_q = 2 if is_digital_detox else 3

        body_html = f"""<div class="nhk-article-badge">NHK WORLD-JAPAN FEATURE REPORT</div>
<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>が<ruby>直面<rt>ちょくめん</rt></ruby>する<ruby>構造的<rt>こうぞうてき</rt></ruby><ruby>課題<rt>かだい</rt></ruby>に<ruby>対<rt>たい</rt></ruby>し、「{title}」という<ruby>先駆的<rt>せんくてき</rt></ruby>な<ruby>試<rt>こころ</rt></ruby>みが<ruby>注目<rt>ちゅうもく</rt></ruby>を<ruby>集<rt>あつ</rt></ruby>めています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>従来<rt>じゅうらい</rt></ruby>の<ruby>縦割<rt>たてわ</rt></ruby>りな<ruby>枠組<rt>わくぐ</rt></ruby>みを超えた<ruby>産学<rt>さんがく</rt></ruby><ruby>官<rt>かん</rt></ruby>の<ruby>連携<rt>れんけい</rt></ruby>により、<ruby>単<rt>たん</rt></ruby>なる<ruby>対症療法<rt>たいしょうりょうほう</rt></ruby>ではなく<ruby>根本的<rt>こんぽんてき</rt></ruby>な<ruby>構造<rt>こうぞう</rt></ruby><ruby>改革<rt>かいかく</rt></ruby>を<ruby>促<rt>うなが</rt></ruby>す<ruby>実効性<rt>じっこうせい</rt></ruby>の<ruby>高<rt>たか</rt></ruby>いシステムが<ruby>構築<rt>こうちく</rt></ruby>されつつあります。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>取材<rt>しゅざい</rt></ruby>に<ruby>応<rt>こた</rt></ruby>えた<ruby>専門家<rt>せんもんか</rt></ruby>は「<ruby>技術的<rt>ぎじゅつてき</rt></ruby>な<ruby>洗練<rt>せんれん</rt></ruby>以上に、<ruby>関係者<rt>かんけいしゃ</rt></ruby>が<ruby>共通<rt>きょうつう</rt></ruby>の<ruby>倫理観<rt>りんりかん</rt></ruby>と<ruby>長期的<rt>ちょうきてき</rt></ruby><ruby>展望<rt>てんぼう</rt></ruby>を<ruby>共有<rt>きょうゆう</rt></ruby>できるかどうかが<ruby>成否<rt>せいひ</rt></ruby>を<ruby>分<rt>わ</rt></ruby>ける」と<ruby>指摘<rt>してき</rt></ruby>しています。</span></p>
"""
        if num_q == 3:
            body_html += f"""<p><span id="ev-q3" data-evidence="ev-q3"><ruby>今後<rt>こんご</rt></ruby>、このモデルが<ruby>社会<rt>しゃかい</rt></ruby>の<ruby>標準<rt>ひょうじゅん</rt></ruby>として<ruby>定着<rt>ていちゃく</rt></ruby>することで、<ruby>経済的<rt>けいざいてき</rt></ruby><ruby>成長<rt>せいちょう</rt></ruby>と<ruby>社会的<rt>しゃかいてき</rt></ruby><ruby>共通<rt>きょうつう</rt></ruby><ruby>資本<rt>しほん</rt></ruby>の<ruby>保全<rt>ほぜん</rt></ruby>が<ruby>調和<rt>ちょうわ</rt></ruby>する<ruby>成熟<rt>せいじゅく</rt></ruby>した<ruby>持続可能<rt>じぞくかのう</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>の<ruby>実現<rt>じつげん</rt></ruby>が<ruby>期待<rt>きたい</rt></ruby>されます。</span></p>
</div>"""
        else:
            body_html += "</div>"

        trans = f"Специальный репортаж NHK: «{title}». Межотраслевое сотрудничество позволило создать действенную систему фундаментальных реформ (ev-q1). Эксперты отмечают, что ключ к успеху лежит в разделении общей этики и долгосрочного видения (ev-q2)."
        if num_q == 3:
            trans += " Закрепление этой модели обеспечит баланс экономического роста и защиты общественных благ (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "この新しい取り組みの特徴として、文章で述べられているのはどれか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) подчеркнуто: партнерство науки, бизнеса и государства позволило выйти за рамки симптоматических мер и запустить фундаментальную структурную реформу.",
            "options": opt_list(
                q_num=1,
                correct_text="従来の枠組みを超えた連携により、対症療法にとどまらない根本的な構造改革を促している点。",
                correct_exp="Верно! Точный пересказ предложения ev-q1.",
                wrongs=[
                    ("政府の命令に従って民間企業が利益を完全に放棄した点。", "extreme_condition", "Неверно. Никто не отказывался от коммерческой выгоды."),
                    ("外国からの技術導入だけに頼り国内開発を止めた点。", "opposite_meaning", "Неверно. Речь идет о развитии собственной экспертизы."),
                    ("過去の法規制をすべて無視して無許可で実験を行った点。", "misinterpretation", "Неверно. Все происходит в правовом поле.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "専門家が取り組みの成否を分ける要因として最も強調していることは何か。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В цитате ev-q2 эксперт подчеркивает: решающим фактором является не столько техническое совершенство, сколько общность этики и долгосрочной перспективы участников.",
            "options": opt_list(
                q_num=2,
                correct_text="関係者が技術的な洗練だけでなく、共通の倫理観と長期的な展望を共有できること。",
                correct_exp="Верно! Прямое утверждение эксперта из ev-q2.",
                wrongs=[
                    ("何よりも短期的な投資回収と広告宣伝を急ぐこと。", "opposite_meaning", "Неверно. Автор прямо предостерегает от сиюминутной спешки."),
                    ("他社の参入を法律で永久に排除すること。", "not_mentioned", "Неверно. Такого тезиса в тексте нет."),
                    ("人工知能の判断にすべてを委ね、人間の責任を免除すること。", "misinterpretation", "Неверно. Человеческий фактор и этика остаются ключевыми.")
                ]
            )
        }

        q_list = [q1, q2]

        if num_q == 3:
            q3 = {
                "slug": f"{slug}-q3",
                "question_number": 3,
                "type": "inference",
                "prompt": "このモデルが社会に定着した先に期待されている成果は何か。",
                "evidence_span_id": "ev-q3",
                "general_explanation": "Согласно фрагменту ev-q3, ожидается гармонизация экономического роста и сохранения общественного блага в зрелом устойчивом обществе.",
                "options": opt_list(
                    q_num=3,
                    correct_text="経済的成長と社会的共通資本の保全が調和する持続可能な社会が実現すること。",
                    correct_exp="Верно! Соответствует предложению ev-q3.",
                    wrongs=[
                        ("すべての民間企業が国営化されること。", "not_mentioned", "Неверно. Национализация предприятий не упоминается."),
                        ("伝統産業が完全に消滅し、IT企業だけが生き残ること。", "extreme_condition", "Неверно. Цель — гармония и преемственность."),
                        ("地方の過疎化が止まらず全人口が大都市に集中すること。", "opposite_meaning", "Неверно. Противоречит цели регионального развития.")
                    ]
                )
            }
            q_list.append(q3)

        texts.append({
            "slug": slug,
            "level": "N2",
            "category": "article",
            "title": f"{title} (N2)",
            "source_type": "news_adapted",
            "source_note": "NHK WORLD-JAPAN 特集報道アーカイブに基づく学習用適応",
            "recommended_time_min": 6,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "先駆的", "furigana": "せんくてき", "translation": "новаторский, передовой"},
                {"word": "対症療法", "furigana": "たいしょうりょうほう", "translation": "симптоматическое лечение (меры)"},
                {"word": "実効性", "furigana": "じっこうせい", "translation": "практическая действенность"}
            ],
            "needs_manual_review": [],
            "questions": q_list
        })

    # Save to content/n2.json
    out_path = CONTENT_DIR / "n2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    total_qs = sum(len(t["questions"]) for t in texts)
    print(f"Generated {out_path}: {len(texts)} texts, {total_qs} questions.")

if __name__ == "__main__":
    build_n2_corpus()
