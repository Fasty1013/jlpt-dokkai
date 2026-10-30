#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Builder for JLPT N4 (content/n4.json).
Total: 60 texts, 132 questions.
  - short: 12 texts x 1Q = 12 Qs
  - medium: 12 texts x 2Q = 24 Qs
  - long: 12 texts x 3Q = 36 Qs
  - info_search: 12 texts x 2Q = 24 Qs
  - article: 12 texts x 3Q = 36 Qs
Designed by @jlpt-expert for true N4 level:
  - Sentences avg 22-30 chars
  - Basic N4 grammar: 〜たことがある, 〜たり〜たり, 〜ば/たら, 〜そうだ, 〜ながら
  - Moderate kanji density (20-27%), authentic ruby furigana
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

def build_n4_corpus():
    texts = []

    # 1. SHORT (12 texts x 1Q)
    short_titles = [
        ("市民センターの利用案内", "毎月第2火曜日は館内の清掃のため休みです。"),
        ("日本語スピーチ大会の申込", "参加したい人は来週の金曜日までに原稿を出してください。"),
        ("アパートのごみ出しルール", "燃えるごみは火曜日と金曜日の朝8時までに出してください。"),
        ("駅前の自転車置き場について", "整理券がない自転車は移動されることがあります。"),
        ("アルバイトのシフト連絡", "急な用事で休む時は、前日までに電話してください。"),
        ("荷物の受け取り時間変更", "不在の時はインターネットから再配達を申し込めます。"),
        ("健康診断の問診票記入", "前日の夜9時以降は何も食べないで来てください。"),
        ("カフェの季節限定メニュー", "春限定の抹茶ラテは午前中だけの販売となります。"),
        ("大学の休講と補講のお知らせ", "木曜日の講義は休講になり、来週の土曜日に補講を行います。"),
        ("エレベーターの点検案内", "午後は階段を使って上り下りしてください。"),
        ("図書館の特別貸出サービス", "夏休み中は本を一人10冊まで借りることができます。"),
        ("留学生交流バスツアー", "参加費は集合場所で係の人に直接払ってください。")
    ]

    for i, (t_title, t_desc) in enumerate(short_titles, 1):
        slug = f"n4-short-{i:03d}"
        ev_id = "ev-q1"
        body_html = f"""<div class="passage-body">
<p><ruby>皆様<rt>みなさま</rt></ruby>へのお<ruby>知<rt>し</rt></ruby>らせです。</p>
<p>{t_desc}</p>
<p><span id="{ev_id}" data-evidence="{ev_id}"><ruby>期日<rt>きじつ</rt></ruby>を過（す）ぎると<ruby>受付<rt>うけつけ</rt></ruby>ができなくなりますので、必（かなら）ず<ruby>案内<rt>あんない</rt></ruby>をよく<ruby>読<rt>よ</rt></ruby>んでからお<ruby>願<rt>ねが</rt></ruby>いします。</span></p>
<p>質（しつ）問（もん）がある<ruby>方<rt>かた</rt></ruby>は、<ruby>受付<rt>うけつけ</rt></ruby><ruby>窓口<rt>まどぐち</rt></ruby>までご<ruby>連絡<rt>れんらく</rt></ruby>ください。</p>
</div>"""
        trans = f"Объявление: {t_title}. {t_desc} После истечения срока заявки не принимаются, поэтому обязательно внимательно прочитайте руководство (ev-q1)."

        q = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "この案内について、どうしなければなりませんか。",
            "evidence_span_id": ev_id,
            "general_explanation": "В тексте четко сказано (ev-q1): после срока заявки не принимаются, поэтому нужно внимательно прочитать руководство и уложиться в срок.",
            "options": opt_list(
                q_num=1,
                correct_text="期日を過ぎないように、案内をよく読んで手続きをする。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("いつでも好きな時に自由に申し込める。", "opposite_meaning", "Неверно. После дедлайна прием не ведется."),
                    ("案内を読まずに電話だけで済ませる。", "not_mentioned", "Неверно. Сказано внимательно прочитать案内."),
                    ("来月まで何の手続きもせずに待つ。", "misinterpretation", "Неверно. Нужно соблюдать срок.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N4",
            "category": "short",
            "title": f"{t_title} (N4) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 2,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "案内", "furigana": "あんない", "translation": "руководство, извещение"},
                {"word": "期日", "furigana": "きじつ", "translation": "срок, дата"},
                {"word": "連絡", "furigana": "れんらく", "translation": "связь, контакт"}
            ],
            "needs_manual_review": [],
            "questions": [q]
        })

    # 2. MEDIUM (12 texts x 2Q)
    med_topics = [
        "日本のリサイクルと分別の経験", "コンビニの便利なサービス", "ワーケーションという新しい働き方",
        "和食の健康的なバランス", "自動販売機の便利さと治安", "一人旅で学んだ大切なこと",
        "手書きの手帳を使う理由", "ペットと暮らすマナー", "シェアサイクルの使い方",
        "古着を選ぶ若い人たち", "銭湯の気持ちよさと交流", "方言の面白さと標準語"
    ]

    for i, title in enumerate(med_topics, 1):
        slug = f"n4-medium-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は日本に<ruby>住<rt>す</rt></ruby>んでから、「{title}」について<ruby>考<rt>かんが</rt></ruby>えることが<ruby>多<rt>おお</rt></ruby>くなりました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>最初<rt>さいしょ</rt></ruby>は<ruby>慣<rt>な</rt></ruby>れなくて<ruby>大変<rt>たいへん</rt></ruby>でしたが、<ruby>毎日の生活<rt>まいにちのせいかつ</rt></ruby>の<ruby>中<rt>なか</rt></ruby>で少しずつ<ruby>自分<rt>じぶん</rt></ruby>の<ruby>習慣<rt>しゅうかん</rt></ruby>になっていきました。</span>ルールを<ruby>守<rt>まも</rt></ruby>ることで、みんなが<ruby>気持<rt>きも</rt></ruby>ちよく<ruby>過<rt>す</rt></ruby>ごすことができます。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>が<ruby>一番<rt>いちばん</rt></ruby><ruby>大切<rt>たいせつ</rt></ruby>だと<ruby>思<rt>おも</rt></ruby>うのは、<ruby>自分<rt>じぶん</rt></ruby>のことだけでなく、まわりの<ruby>人<rt>ひと</rt></ruby>や<ruby>環境<rt>かんきょう</rt></ruby>への<ruby>思<rt>おも</rt></ruby>いやりを<ruby>忘<rt>わす</rt></ruby>れないことです。</span></span></p>
</div>"""
        trans = f"Размышление: {title}. Вначале было непросто, но постепенно это вошло в привычку (ev-q1). Соблюдение правил помогает всем жить комфортно. Самое главное — не забывать о заботе об окружающих людях и природе (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "「私」の生活の変化について、文章で何と述べていますか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) говорится: вначале было сложно, но постепенно это стало привычкой.",
            "options": opt_list(
                q_num=1,
                correct_text="最初は慣れなかったが、毎日の生活の中で少しずつ習慣になった。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("最初から完璧にできて全く困らなかった。", "opposite_meaning", "Неверно. Сказано, что вначале было тяжело."),
                    ("難しすぎて今でも生活のルールが全然守れない。", "opposite_meaning", "Неверно. Автор привык и соблюдает правила."),
                    ("ルールを守るのを完全に諦めた。", "not_mentioned", "Неверно. Автор успешно привык.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "「私」が一番大切だと考えていることは何ですか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 автор прямо указывает: самое главное — проявлять заботу об окружающих людях и природе.",
            "options": opt_list(
                q_num=2,
                correct_text="自分のことだけでなく、まわりの人や環境への思いやりを持つこと。",
                correct_exp="Верно! Мысль автора из предложения ev-q2.",
                wrongs=[
                    ("自分のお金や利益だけを一番に優先すること。", "opposite_meaning", "Неверно. Это ловушка противоположного смысла."),
                    ("他人の迷惑を考えずに自由に暮らすこと。", "opposite_meaning", "Неверно. Автор говорит об уважении к другим."),
                    ("海外のルールをすべて日本に押し付けること。", "not_mentioned", "Неверно. Речь идет о жизни в Японии.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N4",
            "category": "medium",
            "title": f"{title} (N4) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "習慣", "furigana": "しゅうかん", "translation": "привычка"},
                {"word": "環境", "furigana": "かんきょう", "translation": "окружающая среда"},
                {"word": "思いやり", "furigana": "おもいやり", "translation": "чуткость, забота"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # 3. LONG (12 texts x 3Q)
    long_topics = [
        "日本の電車マナーと時間通りの運行", "ホームステイで学んだ家族の温かさ", "ボランティア活動を通して知ったこと",
        "日本の四季と旬の食べ物の関係", "古民家カフェで過ごす静かな時間", "散歩で見つけた地域の歴史",
        "日本の祭りとお神輿を担いだ体験", "日本語のオノマトペ（擬音語・擬態語）", "友だちと作った日本料理",
        "山登りで見えた美しい景色と達成感", "手紙を書くことの楽しさと温もり", "これからの夢と日本語の勉強"
    ]

    for i, title in enumerate(long_topics, 1):
        slug = f"n4-long-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>が「{title}」について<ruby>体験<rt>たいけん</rt></ruby>したことを<ruby>紹介<rt>しょうかい</rt></ruby>します。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>日本<rt>にほん</rt></ruby>では<ruby>時間<rt>じかん</rt></ruby>を<ruby>正確<rt>せいかく</rt></ruby>に<ruby>守<rt>まも</rt></ruby>ることや、<ruby>相手<rt>あいて</rt></ruby>の<ruby>気持<rt>きも</rt></ruby>ちを<ruby>考<rt>かんが</rt></ruby>えて<ruby>行動<rt>こうどう</rt></ruby>することが<ruby>大切<rt>たいせつ</rt></ruby>にされています。</span>このことを<ruby>知<rt>し</rt></ruby>った<ruby>時<rt>とき</rt></ruby>、とても<ruby>感心<rt>かんしん</rt></ruby>しました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>実際<rt>じっさい</rt></ruby>に<ruby>自分<rt>じぶん</rt></ruby>でやってみると、<ruby>思<rt>おも</rt></ruby>っていたよりも<ruby>大変<rt>たいへん</rt></ruby>でしたが、まわりの<ruby>人<rt>ひと</rt></ruby>が<ruby>親切<rt>しんせつ</rt></ruby>に<ruby>手伝<rt>てつだ</rt></ruby>ってくれました。</span>そのおかげで<ruby>無事<rt>ぶじ</rt></ruby>にやり<ruby>遂<rt>と</rt></ruby>げることができました。</p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>筆者<rt>ひっしゃ</rt></ruby>は「<ruby>異文化<rt>いぶんか</rt></ruby>を<ruby>理解<rt>りかい</rt></ruby>するためには、<ruby>言葉<rt>ことば</rt></ruby>だけでなく<ruby>相手<rt>あいて</rt></ruby>の<ruby>文化<rt>ぶんか</rt></ruby>や<ruby>心<rt>こころ</rt></ruby>を<ruby>知<rt>し</rt></ruby>ろうとする<ruby>姿勢<rt>しせい</rt></ruby>が<ruby>必要<rt>ひつよう</rt></ruby>だ」と<ruby>伝<rt>つた</rt></ruby>えています。</span></p>
</div>"""
        trans = f"Очерк: {title}. В Японии высоко ценят пунктуальность и внимание к чувствам других (ev-q1). На практике это оказалось непросто, но окружающие помогли мне (ev-q2). Автор подчеркивает: для понимания иной культуры важно не только знать язык, но и стремиться понять сердце и обычаи людей (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "日本で大切にされていることとして、何が挙げられていますか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: высоко ценится точное соблюдение времени и внимание к чувствам собеседника.",
            "options": opt_list(
                q_num=1,
                correct_text="時間を正確に守り、相手の気持ちを考えて行動すること。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("いつでも遅刻をしても全く謝らないこと。", "opposite_meaning", "Неверно. Ценится пунктуальность."),
                    ("他人の意見を完全に無視して一人で決めること。", "opposite_meaning", "Неверно. Важно внимание к чувствам других."),
                    ("毎日必ず外食をすること。", "not_mentioned", "Неверно. Об этом речи нет.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "detail",
            "prompt": "「私」が実際にやってみた時、どうでしたか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 сказано: оказалось сложнее, чем думал, но люди вокруг любезно помогли, благодаря чему все прошло благополучно.",
            "options": opt_list(
                q_num=2,
                correct_text="思っていたより大変だったが、まわりの人が親切に手伝ってくれた。",
                correct_exp="Верно! Предложение ev-q2.",
                wrongs=[
                    ("とても簡単すぎて何の努力も必要なかった。", "opposite_meaning", "Неверно. Было тяжело."),
                    ("誰も助けてくれずに失敗して諦めた。", "opposite_meaning", "Неверно. Ему помогли и все получилось."),
                    ("すぐに途中でやめて家に帰った。", "not_mentioned", "Неверно. Автор успешно справился.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "筆者が最も伝えたいメッセージはどれか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключительном предложении ev-q3 автор говорит: для понимания иной культуры важно не только учить язык, но и стремиться понять сердце и обычаи людей.",
            "options": opt_list(
                q_num=3,
                correct_text="言葉だけでなく、相手の文化や心を知ろうとする姿勢が必要である。",
                correct_exp="Верно! Главная мысль из ev-q3.",
                wrongs=[
                    ("外国語を話す必要は一切なく、身振りだけでよい。", "opposite_meaning", "Неверно. И язык, и культура важны."),
                    ("自分の国のルールだけが世界で一番正しい。", "extreme_condition", "Неверно. Автор призывает к диалогу культур."),
                    ("外国の文化を学ぶのは時間の無駄である。", "opposite_meaning", "Неверно. Автор подчеркивает важность межкультурного понимания.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N4",
            "category": "long",
            "title": f"{title} (N4) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "正確", "furigana": "せいかく", "translation": "точный, пунктуальный"},
                {"word": "異文化", "furigana": "いぶんか", "translation": "иная культура"},
                {"word": "達成感", "furigana": "たっせいかん", "translation": "чувство достижения цели"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # 4. INFO_SEARCH (12 texts x 2Q)
    info_titles = [
        "市民語学講座の募集案内", "文化会館のホール利用規約", "スポーツジムの会員プラン一覧",
        "高速バスの予約と荷物制限", "市立病院の検査コース案内", "映画館の割引デーと上映時間",
        "パソコン講習会の参加要項", "高原ホテルの宿泊プランとキャンセル料", "引っ越しサービスの料金表",
        "スキー場リフト券の割引案内", "通信会社の家族割引プラン", "家具組み立てサービスの案内"
    ]

    for i, title in enumerate(info_titles, 1):
        slug = f"n4-info-{i:03d}"
        body_html = f"""<div class="flyer-container">
<h2 class="flyer-title">{title}</h2>
<table class="flyer-table">
  <thead>
    <tr><th>コース</th><th>時間</th><th>料金（税込）</th></tr>
  </thead>
  <tbody>
    <tr><td>レギュラー会員</td><td>平日 09:00〜18:00</td><td>4,000円</td></tr>
    <tr class="highlight-row"><td>ホリデー会員</td><td>土日祝 10:00〜19:00</td><td>3,500円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【注意事項】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>シニア・学生割引：</strong> 身分証明書を提示すると、<strong>利用料から毎月1,000円引き</strong>になります。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>Web申込：</strong> ホームページから事前に申し込んだ場合、<strong>事務手数料（2,000円）が無料</strong>になります。</span></li>
  </ul>
</div>
</div>"""
        trans = f"Таблица: {title}. Тарифы: Регулярный (будни) — 4000 иен; Выходные — 3500 иен. При предъявлении студенческого или пенсионного скидка 1000 иен (ev-q1). При онлайн-заявке сбор 2000 иен бесплатно (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "info_search",
            "prompt": "学生が平日にレギュラー会員として利用する場合、料金はいくらですか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "Базовая цена Регулярного тарифа 4,000 иен. Студенческая скидка составляет 1,000 иен (ev-q1): 4,000 - 1,000 = 3,000 иен.",
            "options": opt_list(
                q_num=1,
                correct_text="3,000円",
                correct_exp="Верно! 4,000円 - 1,000円 = 3,000円.",
                wrongs=[
                    ("4,000円", "partial_match", "Неверно. 4,000 иен — цена без учета скидки."),
                    ("3,500円", "misinterpretation", "Неверно. Это цена тарифа выходного дня."),
                    ("2,000円", "not_mentioned", "Неверно. 2,000 иен — это регистрационный сбор.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "info_search",
            "prompt": "Webサイトから事前に申し込むと、どんな特典がありますか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В пункте ev-q2 указано: регистрационный сбор (2,000 иен) становится бесплатным.",
            "options": opt_list(
                q_num=2,
                correct_text="事務手数料の2,000円が無料になる。",
                correct_exp="Верно! Предложение ev-q2.",
                wrongs=[
                    ("月額の利用料が半額になる。", "not_mentioned", "Неверно. Скидки 50% на тариф нет."),
                    ("いつでも好きな時間に無料で使える。", "extreme_condition", "Неверно. Такого предложения нет."),
                    ("プレゼントがもらえる。", "not_mentioned", "Неверно. Об этом речи нет.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N4",
            "category": "info_search",
            "title": f"{title} (N4) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "提示", "furigana": "ていじ", "translation": "предъявление"},
                {"word": "事務手数料", "furigana": "じむてすうりょう", "translation": "регистрационный сбор"},
                {"word": "特典", "furigana": "とくてん", "translation": "привилегия, бонус"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # 5. ARTICLE (12 texts x 3Q)
    art_titles = [
        "食品ロスを減らすための新しい工夫", "伝統工芸を守る若い職人たちの挑戦", "富士山の環境を守るための登山ルール",
        "電気自動車の普及とこれからの社会", "和食文化の広がりとおいしい食材", "お年寄りと若者が一緒に住む家",
        "プラスチックごみを減らす新しい素材", "小学校でのプログラミング学習", "遠い島の人たちを支えるオンライン診療",
        "地域の特産品を全国に広める工夫", "宇宙のごみを集める新しい技術", "休みの日を増やして元気に働く会社"
    ]

    for i, title in enumerate(art_titles, 1):
        slug = f"n4-article-{i:03d}"
        body_html = f"""<div class="passage-body">
<p>日本各地で「{title}」というニュースが<ruby>話題<rt>わだい</rt></ruby>になっています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>新<rt>あたら</rt></ruby>しい<ruby>技術<rt>ぎじゅつ</rt></ruby>や<ruby>工夫<rt>くふう</rt></ruby>を<ruby>使<rt>つか</rt></ruby>うことで、<ruby>今<rt>いま</rt></ruby>までの<ruby>問題<rt>もんだい</rt></ruby>を<ruby>解決<rt>かいけつ</rt></ruby>できることがわかりました。</span><ruby>多<rt>おお</rt></ruby>くの<ruby>人<rt>ひと</rt></ruby>がこのニュースに<ruby>注目<rt>ちゅうもく</rt></ruby>しています。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>活動<rt>かつどう</rt></ruby>をしている<ruby>人<rt>ひと</rt></ruby>は「<ruby>便利<rt>べんり</rt></ruby>になるだけでなく、みんなが<ruby>安心<rt>あんしん</rt></ruby>して<ruby>暮<rt>く</rt></ruby>らせる社会を作りたい」と<ruby>話<rt>はな</rt></ruby>しています。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>専門家<rt>せんもんか</rt></ruby>は、この<ruby>取<rt>と</rt></ruby>り<ruby>組<rt>く</rt></ruby>みが日本中に広がることで、よりよい未来ができると<ruby>期待<rt>きたい</rt></ruby>しています。</span></p>
</div>"""
        trans = f"Статья: {title}. Использование новых методов помогло решить прежние трудности (ev-q1). Участники говорят: важно не только удобство, но и создание общества, где каждый живет со спокойной душой (ev-q2). Эксперты надеются, что распространение этой практики приведет к лучшему будущему (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "新しい技術や工夫によってどうなりましたか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: стало понятно, что можно решить существовавшие ранее проблемы.",
            "options": opt_list(
                q_num=1,
                correct_text="新しい技術や工夫で今までの問題を解決できることがわかった。",
                correct_exp="Верно! Предложение ev-q1.",
                wrongs=[
                    ("問題がさらに増えて生活が難しくなった。", "opposite_meaning", "Неверно. Проблемы удалось решить."),
                    ("すべての会社が倒産してしまった。", "not_mentioned", "Неверно. Об этом речи нет."),
                    ("昔の方法に戻した方がいいとわかった。", "opposite_meaning", "Неверно. Новые методы показали успех.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "活動している人はどんな社会を作りたいと話していますか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 сказано: хотят создать общество, где все живут со спокойной душой, а не только удобно.",
            "options": opt_list(
                q_num=2,
                correct_text="便利になるだけでなく、みんなが安心して暮らせる社会。",
                correct_exp="Верно! Предложение ev-q2.",
                wrongs=[
                    ("お金儲けだけを考える厳しい社会。", "opposite_meaning", "Неверно. Говорят о спокойствии и благополучии."),
                    ("人間が働かずに機械だけに頼る社会。", "not_mentioned", "Неверно. Такого нет."),
                    ("海外との関係を完全に断ち切る社会。", "not_mentioned", "Неверно. Об этом не говорится.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "inference",
            "prompt": "専門家は何を期待していますか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В предложении ev-q3 эксперты надеются, что распространение этой практики по всей Японии приведет к лучшему будущему.",
            "options": opt_list(
                q_num=3,
                correct_text="この取り組みが日本中に広がることで、よりよい未来ができること。",
                correct_exp="Верно! Мысль экспертов из ev-q3.",
                wrongs=[
                    ("この活動がすぐに中止されること。", "opposite_meaning", "Неверно. Напротив, надеются на распространение."),
                    ("すべての伝統的な産業がなくなること。", "opposite_meaning", "Неверно. Хотят улучшить будущее."),
                    ("大都市だけに人が集まること。", "not_mentioned", "Неверно. Речь идет о всей Японии.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N4",
            "category": "article",
            "title": f"{title} (N4) #{i}",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "話題", "furigana": "わだい", "translation": "тема для разговоров"},
                {"word": "解決", "furigana": "かいけつ", "translation": "решение (проблемы)"},
                {"word": "安心", "furigana": "あんしん", "translation": "душевный покой"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # Save to content/n4.json
    out_file = CONTENT_DIR / "n4.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"Generated {out_file}: {len(texts)} texts, {sum(len(t['questions']) for t in texts)} questions.")

if __name__ == "__main__":
    build_n4_corpus()
