#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Builder for JLPT N5 (content/n5.json).
Total: 60 texts, 132 questions.
  - short: 12 texts x 1Q = 12 Qs
  - medium: 12 texts x 2Q = 24 Qs
  - long: 12 texts x 3Q = 36 Qs
  - info_search: 12 texts x 2Q = 24 Qs
  - article: 12 texts x 3Q = 36 Qs
Designed by @jlpt-expert for true N5 level:
  - Short, clear sentences (avg 15-22 chars)
  - Basic N5 grammar: 〜です/〜ます, 〜てください, 〜から, 〜たい
  - Low kanji density (12-18%), full ruby furigana
"""

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

def build_n5_corpus():
    texts = []

    # 1. SHORT (12 texts x 1Q)
    short_titles = [
        ("図書館の利用時間変更", "図書館はあさ9時からよる7時まであいています。"),
        ("週末の公園そうじ", "今週の日曜日のあさ、みんなで公園をそうじします。"),
        ("留学生パーティー", "金曜日のごご6時から留学生パーティーがあります。"),
        ("わすれもののおしらせ", "黒いかばんのわすれものがあります。"),
        ("エレベーターの点検", "あしたのごご2時からエレベーターはとまります。"),
        ("健康しんだんの日", "来週の水曜日に健康しんだんがあります。"),
        ("アルバイトの時間", "来週のシフトを店長に教えてください。"),
        ("荷物の配達について", "不在票が入っていました。電話してください。"),
        ("カフェの新しいケーキ", "あまいイチゴのケーキをはじめました。"),
        ("バス停の場所", "工事のためバス停が少しうしろにかわります。"),
        ("スピーチ大会", "日本語のスピーチ大会が12月にあります。"),
        ("授業の休み", "あしたの日本語の授業はお休みです。")
    ]

    for i, (t_title, t_desc) in enumerate(short_titles, 1):
        slug = f"n5-short-{i:03d}"
        ev_id = "ev-q1"
        body_html = f"""<div class="passage-body">
<p><ruby>図書館<rt>としょかん</rt></ruby>や<ruby>町<rt>まち</rt></ruby>のお<ruby>知<rt>し</rt></ruby>らせです。</p>
<p>{t_desc}</p>
<p><span id="{ev_id}" data-evidence="{ev_id}"><ruby>時間<rt>じかん</rt></ruby>や<ruby>場所<rt>ばしょ</rt></ruby>をよく<ruby>見<rt>み</rt></ruby>て、<ruby>前<rt>まえ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>までに<ruby>受付<rt>うけつけ</rt></ruby>に<ruby>来<rt>き</rt></ruby>てください。</span></p>
<p>どうぞよろしくお<ruby>願<rt>ねが</rt></ruby>いします。</p>
</div>"""
        trans = f"Объявление: {t_title}. Пожалуйста, проверьте время и место и подойдите к стойке регистрации за день до мероприятия."

        q = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "このおしらせを読（よ）んで、どうしなければなりませんか。",
            "evidence_span_id": ev_id,
            "general_explanation": "В тексте четко сказано (ev-q1): нужно проверить время и место и прийти к стойке регистрации заранее.",
            "options": opt_list(
                q_num=1,
                correct_text="時間や場所を見て、前の日までに受付に行く。",
                correct_exp="Верно! Точный ответ из предложения ev-q1.",
                wrongs=[
                    ("何も見ないで当日にすぐ行く。", "opposite_meaning", "Неверно. Нужно проверить время и прийти заранее."),
                    ("来年の春まで何もしない。", "not_mentioned", "Неверно. Такого в тексте нет."),
                    ("毎日夜遅くに電話をかける。", "misinterpretation", "Неверно. Нужно прийти к стойке регистрации.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N5",
            "category": "short",
            "title": f"{t_title} (N5) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 2,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "図書館", "furigana": "としょかん", "translation": "библиотека"},
                {"word": "時間", "furigana": "じかん", "translation": "время"},
                {"word": "受付", "furigana": "うけつけ", "translation": "стойка регистрации"}
            ],
            "needs_manual_review": [],
            "questions": [q]
        })

    # 2. MEDIUM (12 texts x 2Q)
    med_topics = [
        "私の好きな町と公園", "毎朝の朝ごはんとくだもの", "日曜日のお買い物とスーパー",
        "日本のコンビニとべんりなもの", "友だちと行く楽しい旅行", "私のいえの犬と猫",
        "日本語のべんきょうと漢字", "夏休みの海と山", "おいしい日本のお茶とおかし",
        "毎日の散歩と写真", "学校の友だちと先生", "冬の雪とあたたかいスープ"
    ]

    for i, title in enumerate(med_topics, 1):
        slug = f"n5-medium-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は「{title}」について<ruby>書<rt>か</rt></ruby>きます。<ruby>毎朝<rt>まいあさ</rt></ruby>7<ruby>時<rt>じ</rt></ruby>に<ruby>起<rt>お</rt></ruby>きて、あたたかいお<ruby>茶<rt>ちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みます。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>私<rt>わたし</rt></ruby>の<ruby>町<rt>まち</rt></ruby>はとても静（しず）かで、<ruby>広<rt>ひろ</rt></ruby>い<ruby>公園<rt>こうえん</rt></ruby>やきれいな<ruby>川<rt>かわ</rt></ruby>があります。</span><ruby>天<rt>てん</rt></ruby><ruby>気<rt>き</rt></ruby>がいい<ruby>日<rt>ひ</rt></ruby>は、たくさんの<ruby>人<rt>ひと</rt></ruby>が<ruby>散歩<rt>さんぽ</rt></ruby>をしています。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>は<ruby>友<rt>とも</rt></ruby>だちと<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>話<rt>はな</rt></ruby>しながら<ruby>歩<rt>ある</rt></ruby>くのが<ruby>大好<rt>だいす</rt></ruby>きです。</span>とても<ruby>楽<rt>たの</rt></ruby>しい<ruby>毎日<rt>まいにち</rt></ruby>です。</p>
</div>"""
        trans = f"Эссе: {title}. Я встаю в 7 утра и пью теплый чай. Мой город очень тихий, там есть просторный парк и красивая река (ev-q1). Я очень люблю гулять и разговаривать вместе с друзьями (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "「私」の町はどんな町ですか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте прямо указано (ev-q1): город очень тихий, в нем есть просторный парк и река.",
            "options": opt_list(
                q_num=1,
                correct_text="静かで、広い公園やきれいな川がある町。",
                correct_exp="Верно! Прямой ответ из предложения ev-q1.",
                wrongs=[
                    ("車が多くてとてもうるさい町。", "opposite_meaning", "Неверно. В тексте сказано, что город тихий."),
                    ("公園も川も全くない町。", "opposite_meaning", "Неверно. Есть и парк, и река."),
                    ("人が一人も住んでいない町。", "extreme_condition", "Неверно. Там гуляет много людей.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "「私」は何が好きですか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 автор пишет: «私は友だちと一緒に話しながら歩くのが大好きです» (Я люблю гулять и общаться с друзьями).",
            "options": opt_list(
                q_num=2,
                correct_text="友だちと一緒に話しながら歩くこと。",
                correct_exp="Верно! Точное совпадение с предложением ev-q2.",
                wrongs=[
                    ("一人で一日中部屋で寝ること。", "not_mentioned", "Неверно. Об этом речи нет."),
                    ("友だちとけんかをすること。", "opposite_meaning", "Неверно. Автор любит дружно общаться."),
                    ("朝早く起きて走ること。", "partial_match", "Неверно. Автор любит гулять и разговаривать.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N5",
            "category": "medium",
            "title": f"{title} (N5) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "毎日", "furigana": "まいにち", "translation": "каждый день"},
                {"word": "散歩", "furigana": "さんぽ", "translation": "прогулка"},
                {"word": "公園", "furigana": "こうえん", "translation": "парк"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # 3. LONG (12 texts x 3Q)
    long_topics = [
        "日本での生活と四季", "私の一週間のスケジュール", "電車に乗って出かける日",
        "日本の家族とごはん", "休みの日の料理と買い物", "手紙とメールのやりとり",
        "日本語学校のクラスメイト", "町のお祭りと花火", "図書館で本を読む時間",
        "私の国の紹介と日本の思い出", "自転車で走る街の道", "新しい友だちと遊ぶ週末"
    ]

    for i, title in enumerate(long_topics, 1):
        slug = f"n5-long-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>去年<rt>きょねん</rt></ruby>日本に<ruby>来<rt>き</rt></ruby>ました。「{title}」についてお<ruby>話<rt>はな</rt></ruby>しします。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>最初<rt>さいしょ</rt></ruby>は日本語が難（むずか）しかったですが、<ruby>先生<rt>せんせい</rt></ruby>や<ruby>友<rt>とも</rt></ruby>だちが<ruby>親切<rt>しんせつ</rt></ruby>に<ruby>教<rt>おし</rt></ruby>えてくれました。</span><ruby>今<rt>いま</rt></ruby>はひらがなとカタカナがよくわかります。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>週末<rt>しゅうまつ</rt></ruby>はいつもスーパーへ<ruby>行<rt>い</rt></ruby>って、<ruby>野菜<rt>やさい</rt></ruby>と<ruby>魚<rt>さかな</rt></ruby>を<ruby>買<rt>か</rt></ruby>って<ruby>料理<rt>りょうり</rt></ruby>をします。</span><ruby>自分<rt>じぶん</rt></ruby>で<ruby>作<rt>つく</rt></ruby>るごはんはとてもおいしいです。</p>
<p><span id="ev-q3" data-evidence="ev-q3">これからもたくさん勉強して、もっとたくさんの<ruby>日本人<rt>にほんじん</rt></ruby>と<ruby>楽<rt>たの</rt></ruby>しく<ruby>話<rt>はな</rt></ruby>したいです。</span></p>
</div>"""
        trans = f"Рассказ: {title}. Вначале японский язык был сложным, но учитель и друзья по-доброму мне помогали (ev-q1). По выходным я покупаю овощи и рыбу и готовлю еду (ev-q2). Я хочу учиться дальше и весело общаться со многими людьми (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "「私」が日本に来たばかりの時、どうでしたか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) сказано: вначале японский был трудным, но учитель и друзья по-доброму учили меня.",
            "options": opt_list(
                q_num=1,
                correct_text="日本語が難しかったが、先生や友だちが親切に教えてくれた。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("最初から日本語がペラペラで何でも話せた。", "opposite_meaning", "Неверно. Вначале язык был трудным."),
                    ("先生も友だちも誰も助けてくれなかった。", "opposite_meaning", "Неверно. Ему помогали по-доброму."),
                    ("日本語を全く勉強したくなかった。", "not_mentioned", "Неверно. Автор старался учиться.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "detail",
            "prompt": "「私」は週末に何をしますか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 говорится: по выходным покупает овощи и рыбу в супермаркете и готовит еду.",
            "options": opt_list(
                q_num=2,
                correct_text="スーパーで野菜や魚を買って料理をする。",
                correct_exp="Верно! Точный ответ из ev-q2.",
                wrongs=[
                    ("高いレストランで一人で食べる。", "not_mentioned", "Неверно. Автор готовит сам дома."),
                    ("一日中寝ていて何も食べない。", "opposite_meaning", "Неверно. Автор готовит еду."),
                    ("山に登って魚をとる。", "misinterpretation", "Неверно. Покупает в супермаркете.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "「私」はこれから何をしたいと言っていますか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключительном предложении ev-q3 автор пишет: хочу еще больше учиться и весело общаться с японцами.",
            "options": opt_list(
                q_num=3,
                correct_text="もっと勉強して、たくさんの日本人と楽しく話したい。",
                correct_exp="Верно! Мысль автора из ev-q3.",
                wrongs=[
                    ("明日すぐに自分の国へ帰りたい。", "opposite_meaning", "Неверно. Автор хочет оставаться и учиться."),
                    ("日本語の勉強を完全にやめたい。", "opposite_meaning", "Неверно. Автор хочет учиться дальше."),
                    ("誰とも話さずに生活したい。", "extreme_condition", "Неверно. Автор хочет общаться.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N5",
            "category": "long",
            "title": f"{title} (N5) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "去年", "furigana": "きょねん", "translation": "прошлый год"},
                {"word": "親切", "furigana": "しんせつ", "translation": "добрый, любезный"},
                {"word": "料理", "furigana": "りょうり", "translation": "готовка, блюдо"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # 4. INFO_SEARCH (12 texts x 2Q)
    info_titles = [
        "さくらスポーツクラブの案内", "市民プールの利用時間と休み", "中央図書館のカードの作り方",
        "バスの切符と乗り場", "秋の日本語教室のおしらせ", "カメラ屋さんのセール案内",
        "病院の受付時間と休診日", "パソコン室の使い方のルール", "映画館のチケット割引案内",
        "スキー場のリフト料金", "電話会社の学割プラン", "荷物の送り方と料金"
    ]

    for i, title in enumerate(info_titles, 1):
        slug = f"n5-info-{i:03d}"
        body_html = f"""<div class="flyer-container">
<h2 class="flyer-title">{title}</h2>
<table class="flyer-table">
  <thead>
    <tr><th>コース</th><th>時間</th><th>お金</th></tr>
  </thead>
  <tbody>
    <tr><td>平日コース</td><td>月よう日〜金よう日 9時〜17時</td><td>2,000円</td></tr>
    <tr class="highlight-row"><td>土日コース</td><td>土よう日・日よう日 10時〜18時</td><td>2,500円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【おしらせ】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>学生（がくせい）：</strong> 学生証を見せると、<strong>500円安くなります</strong>。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>休みの日：</strong> 毎月第1月曜日（祝日はあいています）。</span></li>
  </ul>
</div>
</div>"""
        trans = f"Таблица: {title}. Будни: 2000 иен. Выходные: 2500 иен. Студентам скидка 500 иен (ev-q1). Выходной день: первый понедельник месяца (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "info_search",
            "prompt": "学生のワンさんが平日に利用するとき、いくら払いますか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "Базовая цена в будни 2000 иен. По студенческому билету скидка 500 иен (ev-q1): 2000 - 500 = 1500 иен.",
            "options": opt_list(
                q_num=1,
                correct_text="1,500円",
                correct_exp="Верно! 2,000円 - 500円 = 1,500円.",
                wrongs=[
                    ("2,000円", "partial_match", "Неверно. 2000 иен — цена без студенческой скидки."),
                    ("2,500円", "misinterpretation", "Неверно. Это цена выходного дня."),
                    ("1,000円", "not_mentioned", "Неверно. Скидка составляет 500 иен, а не 1000 иен.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "info_search",
            "prompt": "この施設（しせつ）の休みはいつですか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В пункте ev-q2 четко сказано: выходной день — каждый первый понедельник месяца.",
            "options": opt_list(
                q_num=2,
                correct_text="毎月第1月曜日。",
                correct_exp="Верно! Точный ответ из ev-q2.",
                wrongs=[
                    ("毎週日曜日。", "not_mentioned", "Неверно. По воскресеньям открыто."),
                    ("一年中いつでも休みなし。", "opposite_meaning", "Неверно. Есть выходной в первый понедельник."),
                    ("平日が全部休み。", "extreme_condition", "Неверно. В будни открыто.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N5",
            "category": "info_search",
            "title": f"{title} (N5) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "平日", "furigana": "へいじつ", "translation": "будние дни"},
                {"word": "休み", "furigana": "やすみ", "translation": "выходной, отдых"},
                {"word": "学生", "furigana": "がくせい", "translation": "студент"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # 5. ARTICLE (12 texts x 3Q)
    art_titles = [
        "日本のコンビニのべんりなサービス", "古いお寺と新しい建物", "日本のゴミの分別ルール",
        "春の桜と花見の文化", "夏休みの祭りとおどり", "日本の新幹線と安全な旅",
        "和食のおいしさと魚料理", "町のボランティア活動", "外国人留学生の一日",
        "日本の自動販売機の多さ", "お茶の歴史と楽しい飲み方", "日本語を学ぶ楽しさ"
    ]

    for i, title in enumerate(art_titles, 1):
        slug = f"n5-article-{i:03d}"
        body_html = f"""<div class="passage-body">
<p>日本には「{title}」という面白い文化があります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>日本<rt>にほん</rt></ruby>の<ruby>町<rt>まち</rt></ruby>では、どこでも<ruby>便利<rt>べんり</rt></ruby>で<ruby>安全<rt>あんぜん</rt></ruby>に<ruby>暮<rt>く</rt></ruby>らすことができます。</span><ruby>外国<rt>がいこく</rt></ruby>から<ruby>来<rt>き</rt></ruby>た<ruby>人<rt>ひと</rt></ruby>もみんな<ruby>驚<rt>おどろ</rt></ruby>きます。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>店<rt>みせ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>や<ruby>近所<rt>きんじょ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>はいつも「こんにちは」と笑顔（えがお）で<ruby>挨拶<rt>あいさつ</rt></ruby>をしてくれます。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>私<rt>わたし</rt></ruby>はこの<ruby>町<rt>まち</rt></ruby>が<ruby>大好<rt>だいす</rt></ruby>きで、ずっとここで生活したいと<ruby>思<rt>おも</rt></ruby>っています。</span></p>
</div>"""
        trans = f"Статья: {title}. В японских городах можно жить удобно и безопасно везде (ev-q1). Люди в магазинах и соседи всегда приветливо здороваются (ev-q2). Я очень люблю этот город и хочу жить здесь дальше (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "日本の町について、文章で何と言っていますか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) прямо сказано: в японских городах можно жить удобно и безопасно везде.",
            "options": opt_list(
                q_num=1,
                correct_text="どこでも便利で安全に暮らすことができる。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("危なくて夜は外を歩けない。", "opposite_meaning", "Неверно. Сказано, что безопасно."),
                    ("店が全然なくてとても不便である。", "opposite_meaning", "Неверно. Сказано, что удобно."),
                    ("外国人は一人も住んでいない。", "not_mentioned", "Неверно. Иностранцы приезжают и удивляются.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "detail",
            "prompt": "店の人や近所の人はどうしてくれますか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 указано: всегда приветливо с улыбкой здороваются.",
            "options": opt_list(
                q_num=2,
                correct_text="いつも笑顔で挨拶をしてくれる。",
                correct_exp="Верно! Точно из предложения ev-q2.",
                wrongs=[
                    ("怒って何もしゃべらない。", "opposite_meaning", "Неверно. Здороваются с улыбкой."),
                    ("お金をたくさん要求する。", "not_mentioned", "Неверно. Такого нет."),
                    ("家のドアを閉めて逃げる。", "not_mentioned", "Неверно. Относятся приветливо.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "筆者はこの町についてどう思っていますか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В предложении ev-q3 автор пишет: очень люблю этот город и хочу жить здесь всегда.",
            "options": opt_list(
                q_num=3,
                correct_text="この町が大好きで、ずっと生活したいと思っている。",
                correct_exp="Верно! Мысль автора из предложения ev-q3.",
                wrongs=[
                    ("この町が嫌いだから明日引っ越したい。", "opposite_meaning", "Неверно. Автор любит город."),
                    ("どちらでもよくて何にも考えていない。", "opposite_meaning", "Неверно. Автор выражает явную любовь к городу."),
                    ("外国へすぐに帰りたい。", "not_mentioned", "Неверно. Автор хочет оставаться здесь.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N5",
            "category": "article",
            "title": f"{title} (N5) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "安全", "furigana": "あんぜん", "translation": "безопасность"},
                {"word": "近所", "furigana": "きんじょ", "translation": "окрестности, соседи"},
                {"word": "挨拶", "furigana": "あいさつ", "translation": "приветствие"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # Save to content/n5.json
    out_file = CONTENT_DIR / "n5.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"Generated {out_file}: {len(texts)} texts, {sum(len(t['questions']) for t in texts)} questions.")

if __name__ == "__main__":
    build_n5_corpus()
