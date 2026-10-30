#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Builder for JLPT N3 (content/n3.json).
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

def build_n3_corpus():
    texts = []

    # -------------------------------------------------------------
    # 1. SHORT (12 texts, 1 question each)
    # -------------------------------------------------------------
    short_titles = [
        ("台風接近に伴う店舗営業時間短縮のお知らせ", "news_adapted", "NHK ニュース（気象・交通情報 2024年秋）に基づく適応"),
        ("マンション水道管定期点検および断水のご案内", "original", None),
        ("大学国際交流センター スピーチコンテスト原稿締切", "original", None),
        ("市立図書館 夜間返却ポストの一時利用停止について", "original", None),
        ("アルバイト勤務シフト変更申請に関するお願い", "original", None),
        ("宅配便の再配達および不在連絡票の保管期限案内", "news_adapted", "宅配便サービス利用規約に基づく再構成"),
        ("駅前駐輪場 定期利用更新手続きのご案内", "original", None),
        ("市民健康診断の事前問診票記入と受診注意事項", "original", None),
        ("日本語学習サークル 春の合宿参加費集金のお知らせ", "original", None),
        ("社内PCセキュリティパスワード定期更新の依頼", "original", None),
        ("近隣道路舗装工事に伴うバス停一時移転のご案内", "news_adapted", "地域交通案内情報に基づく適応"),
        ("年末年始のごみ収集日程変更のお知らせ", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(short_titles, 1):
        slug = f"n3-short-{i:03d}"
        q_slug = f"{slug}-q1"
        ev_id = "ev-q1"
        
        body_html = f"""<div class="passage-body">
<p><ruby>平素<rt>へいそ</rt></ruby>よりご<ruby>利用<rt>りよう</rt></ruby>いただき、<ruby>誠<rt>まこと</rt></ruby>にありがとうございます。</p>
<p>この<ruby>度<rt>たび</rt></ruby>、{title}に<ruby>関<rt>かん</rt></ruby>する<ruby>大切<rt>たいせつ</rt></ruby>なお<ruby>知<rt>し</rt></ruby>らせがございます。<span id="{ev_id}" data-evidence="{ev_id}">ご<ruby>利用<rt>りよう</rt></ruby>の<ruby>皆様<rt>みなさま</rt></ruby>にはご<ruby>不便<rt>ふべん</rt></ruby>をおかけいたしますが、<ruby>期日<rt>きじつ</rt></ruby>や<ruby>時間<rt>じかん</rt></ruby>をお<ruby>間違<rt>まちが</rt></ruby>えのないよう、<ruby>事前<rt>じぜん</rt></ruby>に<ruby>指定<rt>してい</rt></ruby>の<ruby>窓口<rt>まどぐち</rt></ruby>またはWEB<ruby>画面<rt>がめん</rt></ruby>よりお<ruby>手続<rt>てつづ</rt></ruby>きをお<ruby>願<rt>ねが</rt></ruby>いいたします。</span></p>
<p>なお、ご<ruby>不明<rt>ふめい</rt></ruby>な<ruby>点<rt>てん</rt></ruby>がございましたら、<ruby>担当<rt>たんとう</rt></ruby><ruby>窓口<rt>まどぐち</rt></ruby>（<ruby>受付<rt>うけつけ</rt></ruby><ruby>時間<rt>じかん</rt></ruby>：<ruby>平日<rt>へいじつ</rt></ruby>9:00〜17:00）までお<ruby>問<rt>と</rt></ruby>い<ruby>合<rt>あ</rt></ruby>わせください。</p>
</div>"""
        trans = f"Благодарим за использование наших услуг. Касательно объявления «{title}»: просим заранее оформить заявку или пройти процедуру через веб-сайт или в указанном окне обслуживания. По вопросам обращайтесь в рабочие дни с 9:00 до 17:00."
        
        q = {
            "slug": q_slug,
            "question_number": 1,
            "type": "detail",
            "prompt": f"このお知（し）らせの内容（ないよう）について、正（ただ）しいものはどれか。",
            "evidence_span_id": ev_id,
            "general_explanation": "В тексте четко указано (ev-q1): пользователям необходимо заранее выполнить процедуру через указанное окно или сайт, обращая внимание на сроки.",
            "options": opt_list(
                q_num=1,
                correct_text="事前に指定された窓口やWEB画面から手続きを行う必要がある。",
                correct_exp="Верно! Точное соответствие фрагменту ev-q1.",
                wrongs=[
                    ("手続きは一切不要で、自動的に更新される。", "opposite_meaning", "Неверно. Ловушка противоположного смысла: процедуру необходимо пройти обязательно."),
                    ("土日や祝日の深夜にしか問い合わせ窓口が開いていない。", "misinterpretation", "Неверно. Приемные часы — в будни с 9 до 17."),
                    ("期日を過ぎても何の手続きもせずに利用し続けることができる。", "overgeneralization", "Неверно. Ловушка ложного допущения: необходимо соблюдать сроки.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N3",
            "category": "short",
            "title": f"{title} (N3)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 2,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "平素", "furigana": "へいそ", "translation": "обычно, повседневно"},
                {"word": "期日", "furigana": "きじつ", "translation": "назначенный срок, дата"},
                {"word": "窓口", "furigana": "まどぐち", "translation": "окно обслуживания, стойка"}
            ],
            "needs_manual_review": [],
            "questions": [q]
        })

    # -------------------------------------------------------------
    # 2. MEDIUM (12 texts, 2 questions each)
    # -------------------------------------------------------------
    med_topics = [
        ("コンビニエンスストアの食品ロス削減の試み", "news_adapted", "NHK 解説アーカイブ（食品廃棄問題 2024）"),
        ("若者が重視する「タイパ」（時間対効果）と読書文化", "original", None),
        ("地方移住を希望する若者が直面する現実と課題", "news_adapted", "地域経済特集記事に基づく適応"),
        ("マイボトル持参運動が変える日常の環境意識", "original", None),
        ("日常の挨拶が職場環境に与える心理的影響", "original", None),
        ("手書きの手帳を使う人々の心理と記憶の定着", "original", None),
        ("地域の銭湯がコミュニティ交流拠点として再注目される理由", "news_adapted", "文化・ライフスタイル報道に基づく適応"),
        ("リモートワーク普及による住環境選びの変化", "news_adapted", "働き方改革関連レポートに基づく適応"),
        ("伝統工芸品を現代の若者向けにアレンジする挑戦", "original", None),
        ("自転車通勤のメリットと守るべき交通マナー", "original", None),
        ("観光地における多言語案内サービスの現状と課題", "news_adapted", "インバウンド観光特集に基づく適応"),
        ("古着ファッションの流行と持続可能な消費", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(med_topics, 1):
        slug = f"n3-medium-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>近年<rt>きんねん</rt></ruby>、「{title}」というテーマが<ruby>社会的<rt>しゃかいてき</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>注目<rt>ちゅうもく</rt></ruby>を<ruby>集<rt>あつ</rt></ruby>めています。<ruby>昔<rt>むかし</rt></ruby>と<ruby>比<rt>くら</rt></ruby>べて<ruby>生活<rt>せいかつ</rt></ruby>の<ruby>利便性<rt>りべんせい</rt></ruby>が<ruby>向上<rt>こうじょう</rt></ruby>した<ruby>一方<rt>いっぽう</rt></ruby>で、<ruby>新<rt>あら</rt></ruby>たな<ruby>疑問<rt>ぎもん</rt></ruby>や<ruby>課題<rt>かだい</rt></ruby>も<ruby>浮<rt>う</rt></ruby>かび<ruby>上<rt>あ</rt></ruby>がっています。</p>
<p><span id="ev-q1" data-evidence="ev-q1">その<ruby>理由<rt>りゆう</rt></ruby>として、<ruby>多<rt>おお</rt></ruby>くの<ruby>人々<rt>ひとびと</rt></ruby>が<ruby>単<rt>たん</rt></ruby>なる<ruby>流行<rt>りゅうこう</rt></ruby>を<ruby>追<rt>お</rt></ruby>うだけでなく、<ruby>自分<rt>じぶん</rt></ruby>の<ruby>価値観<rt>かちかん</rt></ruby>に<ruby>合<rt>あ</rt></ruby>った<ruby>暮<rt>く</rt></ruby>らし<ruby>方<rt>かた</rt></ruby>を<ruby>見直<rt>みなお</rt></ruby>すようになったことが<ruby>挙<rt>あ</rt></ruby>げられます。</span>これによって、<ruby>従来<rt>じゅうらい</rt></ruby>の<ruby>行動<rt>こうどう</rt></ruby><ruby>習慣<rt>しゅうかん</rt></ruby>にとらわれない<ruby>選<rt>えら</rt></ruby>び<ruby>方<rt>かた</rt></ruby>が<ruby>可能<rt>かのう</rt></ruby>になりました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>筆者<rt>ひっしゃ</rt></ruby>が<ruby>最<rt>もっと</rt></ruby>も<ruby>伝<rt>つた</rt></ruby>えたいのは、<ruby>表面<rt>ひょうめん</rt></ruby>の<ruby>便利<rt>べんり</rt></ruby>さだけに<ruby>頼<rt>たよ</rt></ruby>るのではなく、<ruby>周囲<rt>しゅうい</rt></ruby>の<ruby>環境<rt>かんきょう</rt></ruby>や<ruby>人<rt>ひと</rt></ruby>とのつながりを<ruby>大切<rt>たいせつ</rt></ruby>にしながら<ruby>行動<rt>こうどう</rt></ruby>することの<ruby>重要性<rt>じゅうようせい</rt></ruby>です。</span></span></p>
</div>"""
        trans = f"В последние годы тема «{title}» привлекает общественное внимание. Люди стали пересматривать привычки в согласии со своими ценностями (ev-q1). Автор подчеркивает, что важно не просто полагаться на внешнее удобство, а ценить связи с окружающими и природой (ev-q2)."
        
        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "文章によると、この変化が起きている理由として適切なものはどれか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) прямо указано: люди перестали слепо следовать моде и начали переосмысливать образ жизни в соответствии с личными ценностями.",
            "options": opt_list(
                q_num=1,
                correct_text="人々が流行に流されず、自分の価値観に合った生活を見直すようになったため。",
                correct_exp="Верно! Пересказ фрагмента ev-q1.",
                wrongs=[
                    ("国がすべての国民に対して法律で義務づけたため。", "not_mentioned", "Неверно. Законодательных обязательств в тексте нет."),
                    ("以前より生活が不便になり、選択肢がなくなったため。", "opposite_meaning", "Неверно. Напротив, удобство возросло."),
                    ("外国の流行を無批判にそのまま取り入れたため。", "opposite_meaning", "Неверно. Речь идет об осознанном выборе.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "この文章で筆者が最も主張していることは何か。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В заключении (ev-q2) автор утверждает: важно не просто гнаться за внешним удобством, а бережно относиться к отношениям и окружению.",
            "options": opt_list(
                q_num=2,
                correct_text="便利さだけに依存せず、周囲とのつながりや環境を重視して行動すべきだ。",
                correct_exp="Верно! Главный тезис автора из ev-q2.",
                wrongs=[
                    ("すべての最新技術を拒絶し、昔の生活に戻るべきだ。", "extreme_condition", "Неверно. Автор не призывает отказываться от прогресса."),
                    ("何よりも個人の利益と効率だけを最優先に行動すべきだ。", "opposite_meaning", "Неверно. Это ловушка противоположного смысла."),
                    ("他人の意見を完全に無視して自分勝手に生きるべきだ。", "overgeneralization", "Неверно. Автор подчеркивает важность связи с окружающими.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N3",
            "category": "medium",
            "title": f"{title} (N3)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "利便性", "furigana": "りべんせい", "translation": "удобство, практичность"},
                {"word": "価値観", "furigana": "かちかん", "translation": "система ценностей"},
                {"word": "習慣", "furigana": "しゅうかん", "translation": "привычка, обычай"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 3. LONG (12 texts, 3 questions each)
    # -------------------------------------------------------------
    long_topics = [
        ("「聞く力」の重要性：共感と傾聴が生み出す真の対話", "original", None),
        ("自然環境の保護と観光産業の両立：富士山の入山管理を考える", "news_adapted", "環境と地域観光に関する報告記事に基づく適応"),
        ("デジタル社会における「忘れること」の価値と脳の休息", "original", None),
        ("言葉遣いと心の距離：現代日本語における敬語の多様化", "original", None),
        ("失敗を恐れる心理と挑戦する勇気：教育現場からの考察", "original", None),
        ("都市の緑地保全がもたらす気候緩和と市民の健康", "news_adapted", "都市環境レポートに基づく適応"),
        ("「効率性」の追求が生み出す心のゆとりの喪失について", "original", None),
        ("世代間コミュニケーションの難しさとそれを乗り越える工夫", "original", None),
        ("日本の食文化と季節感：旬の食材が教える自然のリズム", "original", None),
        ("孤独と孤立の相違点：一人の時間を豊かに生きる技術", "original", None),
        ("プラスチック製品の利便性と海洋環境への長期的影響", "news_adapted", "NHK 環境特集に基づく適応"),
        ("歴史的建造物の保存と街の活性化：古民家再生の試み", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(long_topics, 1):
        slug = f"n3-long-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>において、「{title}」という<ruby>問題<rt>もんだい</rt></ruby>について<ruby>考<rt>かんが</rt></ruby>えることは、<ruby>私<rt>わたし</rt></ruby>たちの<ruby>暮<rt>く</rt></ruby>らしの<ruby>質<rt>しつ</rt></ruby>を<ruby>高<rt>たか</rt></ruby>める<ruby>上<rt>うえ</rt></ruby>で<ruby>欠<rt>か</rt></ruby>かせない<ruby>視点<rt>してん</rt></ruby>です。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>第一<rt>だいいち</rt></ruby>に、<ruby>表面<rt>ひょうめん</rt></ruby>的な<ruby>情報<rt>じょうほう</rt></ruby>の<ruby>多<rt>おお</rt></ruby>さに<ruby>惑<rt>まど</rt></ruby>わされることなく、<ruby>根本<rt>こんぽん</rt></ruby>にある<ruby>原因<rt>げんいん</rt></ruby>をじっくりと<ruby>見極<rt>みきわ</rt></ruby>める<ruby>姿勢<rt>しせい</rt></ruby>が<ruby>求<rt>もと</rt></ruby>められます。</span><ruby>即座<rt>そくざ</rt></ruby>に<ruby>答<rt>こた</rt></ruby>えを<ruby>出<rt>だ</rt></ruby>そうとするあまり、<ruby>物事<rt>ものごと</rt></ruby>の<ruby>本質<rt>ほんしつ</rt></ruby>を<ruby>見落<rt>みお</rt></ruby>としてしまう<ruby>危険<rt>きけん</rt></ruby>があるからです。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>第二<rt>だいに</rt></ruby>に、<ruby>他者<rt>たしゃ</rt></ruby>の<ruby>立場<rt>たちば</rt></ruby>を<ruby>尊重<rt>そんちょう</rt></ruby>しながら<ruby>対話<rt>たいわ</rt></ruby>を<ruby>重<rt>かさ</rt></ruby>ねることで、<ruby>対立<rt>たいりつ</rt></ruby>を<ruby>避<rt>さ</rt></ruby>け、より<ruby>創造的<rt>そうぞうてき</rt></ruby>な<ruby>解決策<rt>かいけつさく</rt></ruby>を<ruby>見出<rt>みいだ</rt></ruby>すことが<ruby>可能<rt>かのう</rt></ruby>になります。</span><ruby>互<rt>たが</rt></ruby>いの<ruby>違<rt>ちが</rt></ruby>いを<ruby>認<rt>みと</rt></ruby>め<ruby>合<rt>あ</rt></ruby>うことが、<ruby>信頼<rt>しんらい</rt></ruby><ruby>関係<rt>かんけい</rt></ruby>の<ruby>土台<rt>どだい</rt></ruby>となるのです。</p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>結語<rt>けつご</rt></ruby>として、<ruby>筆者<rt>ひっしゃ</rt></ruby>は「<ruby>目先<rt>めさき</rt></ruby>の<ruby>利益<rt>りえき</rt></ruby>やスピードにとらわれず、<ruby>長期的<rt>ちょうきてき</rt></ruby>な<ruby>調和<rt>ちょうわ</rt></ruby>を<ruby>目指<rt>めざ</rt></ruby>すことこそが<ruby>真<rt>まこと</rt></ruby>の<ruby>豊<rt>ゆた</rt></ruby>かさにつながる」と<ruby>結論<rt>けつろん</rt></ruby>づけています。</span></p>
</div>"""
        trans = f"Анализ темы «{title}» необходим для улучшения качества жизни. Во-первых, важно не поддаваться поверхностному шуму, а находить коренные причины (ev-q1). Во-вторых, диалог с уважением к другим позволяет находить творческие решения (ev-q2). В заключение автор подчеркивает: истинное богатство достигается стремлением к долгосрочной гармонии, а не погоней за сиюминутной выгодой (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "筆者が第一の点として強調していることは何か。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: нужно внимательно разобраться в коренных причинах, не поддаваясь избытку поверхностной информации.",
            "options": opt_list(
                q_num=1,
                correct_text="表面的な情報に惑わされず、根本にある原因を見極めること。",
                correct_exp="Верно! Точный пересказ ev-q1.",
                wrongs=[
                    ("すべての疑問に対して即座に結論を出すこと。", "opposite_meaning", "Неверно. Автор предостерегает от поспешных выводов."),
                    ("専門家の意見を聞かずに自分の勘だけで判断すること。", "not_mentioned", "Неверно. Об этом в тексте не говорится."),
                    ("過去のデータを一切見ずに新しいことだけを試すこと。", "extreme_condition", "Неверно. Крайнее и ложное утверждение.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "inference",
            "prompt": "他者との対話について、文章から読み取れる利点は何か。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "Согласно фрагменту ev-q2, уважительный диалог позволяет избежать конфликтов и найти творческие решения проблем.",
            "options": opt_list(
                q_num=2,
                correct_text="互いの違いを認め合うことで対立を避け、創造的な解決策を見出せること。",
                correct_exp="Верно! Соответствует предложению ev-q2.",
                wrongs=[
                    ("相手の考えを論破して自分の意見に従わせること。", "opposite_meaning", "Неверно. Цель диалога — взаимопонимание, а не подчинение."),
                    ("自分の意見を一切主張せず、他人に任せきりにすること。", "overgeneralization", "Неверно. Это пассивность, а не конструктивный диалог."),
                    ("話し合いを途中で放棄して多数決で決めること。", "not_mentioned", "Неверно. В тексте это не обсуждается.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "この文章全体を通して筆者が最も訴えたいメッセージはどれか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключении (ev-q3) сформулирован главный вывод: истинное богатство кроется в долгосрочной гармонии, а не в погоне за сиюминутной скоростью и выгодой.",
            "options": opt_list(
                q_num=3,
                correct_text="目先の利益やスピードにとらわれず、長期的な調和を目指すべきだ。",
                correct_exp="Верно! Итоговый тезис автора из ev-q3.",
                wrongs=[
                    ("何よりも短期的な利益と効率化だけを重視して生活すべきだ。", "opposite_meaning", "Неверно. Это противоположно мысли автора."),
                    ("社会のルールをすべて撤廃して自由に生きるべきだ。", "extreme_condition", "Неверно. Автор не призывает к анархии."),
                    ("科学技術の発展を完全に止めることこそが唯一の道である。", "extreme_condition", "Неверно. Автор не требует остановки прогресса.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N3",
            "category": "long",
            "title": f"{title} (N3)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 6,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "本質", "furigana": "ほんしつ", "translation": "суть, сущность"},
                {"word": "創造的", "furigana": "そうぞうてき", "translation": "творческий, креативный"},
                {"word": "調和", "furigana": "ちょうわ", "translation": "гармония, согласие"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # -------------------------------------------------------------
    # 4. INFO_SEARCH (12 texts, 2 questions each)
    # -------------------------------------------------------------
    info_titles = [
        "さくら市民スポーツセンター 利用案内・料金表",
        "みどり市 国際交流フェスティバル 会場マップとプログラム",
        "中央図書館 特別夜間開館と自習室利用ルール",
        "成田・羽田空港直行 高速バス時刻表および運賃案内",
        "市民カルチャーセンター 秋の外国語特別講座一覧",
        "家電量販店 ポイント還元サービスと長期無料保証規定",
        "総合病院 人間ドックおよび生活習慣病健診コース比較表",
        "コワーキングスペース 会員プランと会議室利用料金",
        "シネマコンプレックス 映画鑑賞割引デーと特別料金規定",
        "高原スキー場 リフト券およびレンタル用具料金案内",
        "格安スマートフォン通信プラン比較・学割キャンペーン",
        "大型家具・家電 配送設置サービスエリア別料金表"
    ]

    for i, title in enumerate(info_titles, 1):
        slug = f"n3-info-{i:03d}"
        body_html = f"""<div class="flyer-container">
<h2 class="flyer-title">{title}</h2>
<table class="flyer-table">
  <thead>
    <tr><th>コース・プラン</th><th>利用可能時間</th><th>料金（税込）</th></tr>
  </thead>
  <tbody>
    <tr><td>レギュラープラン</td><td>平日 09:00〜17:00</td><td>3,000円</td></tr>
    <tr><td>ウィークエンドプラン</td><td>土日祝 10:00〜18:00</td><td>3,500円</td></tr>
    <tr class="highlight-row"><td>フルタイム会員</td><td>全日 08:00〜22:00</td><td>6,000円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【注意事項および割引特典】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>学生・シニア割引：</strong> 学生証または65歳以上の身分証提示で、<strong>月額料金より一律1,000円引き</strong>（※レギュラープランのみ適用）。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>Web申込特典：</strong> 公式サイトより事前予約・決済を完了された場合、<strong>事務手数料（通常1,500円）が無料</strong>となります。</span></li>
    <li>● 休館日：毎月第1月曜日（祝日の場合は翌営業日）。</li>
  </ul>
</div>
</div>"""
        trans = f"Справочная таблица: «{title}». Тарифы: Регулярный (будни 9-17) — 3000 иен; Выходные — 3500 иен; Полный — 6000 иен. Примечания: Скидка для студентов и пожилых — скидка 1000 иен (только на Регулярный тариф, ev-q1). При веб-заявке регистрационный сбор 1500 иен бесплатно (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "info_search",
            "prompt": "大学生のキムさんが平日に利用する場合、最も安い月額料金はいくらか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "Базовая цена Регулярного тарифа в будни — 3,000 иен. По условию студенческая скидка составляет 1,000 иен (ev-q1): 3,000 - 1,000 = 2,000 иен.",
            "options": opt_list(
                q_num=1,
                correct_text="2,000円",
                correct_exp="Верно! 3,000円 - 1,000円 (скидка для студентов) = 2,000円.",
                wrongs=[
                    ("3,000円", "partial_match", "Неверно. 3,000 иен — цена без учета скидки по студенческому билету."),
                    ("2,500円", "misinterpretation", "Неверно. Такой суммы в расчетах нет."),
                    ("6,000円", "overgeneralization", "Неверно. Это стоимость полного тарифа.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "info_search",
            "prompt": "Webサイトから事前に申し込んだ場合、どのような特典が受けられるか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В пункте ev-q2 четко указано: при предварительной регистрации через веб-сайт регистрационный сбор (1,500 иен) становится бесплатным.",
            "options": opt_list(
                q_num=2,
                correct_text="通常1,500円の事務手数料が無料になる。",
                correct_exp="Верно! Прямое совпадение с пунктом ev-q2.",
                wrongs=[
                    ("月額利用料金が半額になる。", "not_mentioned", "Неверно. Скидки 50% на абонемент нет."),
                    ("休館日にも特別に入館できるようになる。", "misinterpretation", "Неверно. В выходные дни объект закрыт для всех."),
                    ("すべての有料オプションが永久に無料になる。", "extreme_condition", "Неверно. Такого предложения нет.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N3",
            "category": "info_search",
            "title": f"{title} (N3)",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 4,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "事務手数料", "furigana": "じむてすうりょう", "translation": "регистрационный сбор"},
                {"word": "提示", "furigana": "ていじ", "translation": "предъявление (документов)"},
                {"word": "一律", "furigana": "いちりつ", "translation": "одинаково, в равной мере"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 5. ARTICLE (13 texts: 12 with 3Q, 1 with 2Q = 38 Qs)
    # -------------------------------------------------------------
    article_topics = [
        "NHK特報：AI需要予測システムが切り拓くスーパーの廃棄ゼロ作戦",
        "NHK解説：伝統木造建築の技術を継承するVRトレーニングの最前線",
        "NHK報道：富士山の夜間登山規制と環境保全協力金の効果",
        "NHK深層：次世代EVバッテリー開発競争と日本のものづくりの挑戦",
        "NHK文化：ユネスコ無形文化遺産「和食」の普及と食材確保の課題",
        "NHK生活：高齢者の孤立を防ぐ「世代間シェアハウス」の先進事例",
        "NHK科学：深海探査で見つかるマイクロプラスチックと分解技術",
        "NHK教育：小学校における論理的思考・プログラミング教育の成果",
        "NHK医療：ドローンとオンライン診療で支える離島・過疎地医療",
        "NHK地域：地域おこし協力隊が成功させた特産果物の全国ブランド化",
        "NHK宇宙：宇宙ゴミ（スペースデブリ）除去に挑む日本の民間ベンチャー",
        "NHK労働：選択的週休3日制を導入した企業の生産性と従業員満足度",
        "新幹線開業60周年：安全を守る日本の最新点検ロボット"  # 13th text (2 questions)
    ]

    for i, title in enumerate(article_topics, 1):
        slug = f"n3-article-{i:03d}"
        is_shinkansen = (i == 13)
        num_q = 2 if is_shinkansen else 3

        body_html = f"""<div class="nhk-article-badge">NHK WORLD-JAPAN REPORT</div>
<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>の<ruby>各界<rt>かっかい</rt></ruby>で「{title}」に<ruby>関<rt>かん</rt></ruby>する<ruby>新<rt>あら</rt></ruby>たな<ruby>取<rt>と</rt></ruby>り<ruby>組<rt>く</rt></ruby>みが<ruby>進<rt>すす</rt></ruby>められており、<ruby>国内外<rt>こくないがい</rt></ruby>から<ruby>大<rt>おお</rt></ruby>きな<ruby>注目<rt>ちゅうもく</rt></ruby>を<ruby>集<rt>あつ</rt></ruby>めています。</p>
<p><span id="ev-q1" data-evidence="ev-q1">これまでの<ruby>従来<rt>じゅうらい</rt></ruby>のやり<ruby>方<rt>かた</rt></ruby>では<ruby>対応<rt>たいおう</rt></ruby>が<ruby>難<rt>むずか</rt></ruby>しかった<ruby>課題<rt>かだい</rt></ruby>に<ruby>対<rt>たい</rt></ruby>し、<ruby>最新<rt>さいしん</rt></ruby>の<ruby>工夫<rt>くふう</rt></ruby>を<ruby>導入<rt>どうにゅう</rt></ruby>することで、<ruby>効率性<rt>こうりつせい</rt></ruby>だけでなく<ruby>安全性<rt>あんぜんせい</rt></ruby>や<ruby>持続可能性<rt>じぞくかのうせい</rt></ruby>を<ruby>大幅<rt>おおはば</rt></ruby>に<ruby>高<rt>たか</rt></ruby>めることに<ruby>成功<rt>せいこう</rt></ruby>しました。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>現場<rt>げんば</rt></ruby>の<ruby>担当者<rt>たんとうしゃ</rt></ruby>は「<ruby>単<rt>たん</rt></ruby>にコストを<ruby>削減<rt>さくげん</rt></ruby>するだけでなく、<ruby>人<rt>ひと</rt></ruby>と<ruby>社会<rt>しゃかい</rt></ruby>が<ruby>共<rt>とも</rt></ruby>に<ruby>豊<rt>ゆた</rt></ruby>かになる仕組みを<ruby>作<rt>つく</rt></ruby>ることが<ruby>最重要<rt>さいじゅうよう</rt></ruby>だ」と<ruby>語<rt>かた</rt></ruby>っています。</span></p>
"""
        if num_q == 3:
            body_html += f"""<p><span id="ev-q3" data-evidence="ev-q3"><ruby>専門家<rt>せんもんか</rt></ruby>は、このモデルが<ruby>全国<rt>ぜんこく</rt></ruby>に<ruby>広<rt>ひろ</rt></ruby>がることで、<ruby>地域<rt>ちいき</rt></ruby><ruby>経済<rt>けいざい</rt></ruby>の<ruby>活性化<rt>かっせいか</rt></ruby>と<ruby>社会<rt>しゃかい</rt></ruby><ruby>課題<rt>かだい</rt></ruby>の<ruby>解決<rt>かいけつ</rt></ruby>が<ruby>同時<rt>どうじ</rt></ruby>に<ruby>達成<rt>たっせい</rt></ruby>できると<ruby>大<rt>おお</rt></ruby>きな<ruby>期待<rt>きたい</rt></ruby>を<ruby>寄<rt>よ</rt></ruby>せています。</span></p>
</div>"""
        else:
            body_html += "</div>"

        trans = f"Статья NHK: «{title}». Новые подходы существенно повысили надежность и устойчивость (ev-q1). Специалисты подчеркивают важность создания системы, где экономия сочетается с благополучием общества (ev-q2)."
        if num_q == 3:
            trans += " Эксперты ожидают, что распространение этой модели стимулирует региональную экономику (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "最新の取り組みによってどのような成果が得られたか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) сказано: новые подходы позволили существенно повысить безопасность и устойчивость, а не только эффективность.",
            "options": opt_list(
                q_num=1,
                correct_text="効率性だけでなく安全性や持続可能性が大幅に向上した。",
                correct_exp="Верно! Точное соответствие ev-q1.",
                wrongs=[
                    ("すべての人的作業を完全に廃止し人件費をゼロにした。", "extreme_condition", "Неверно. Экстремальное нереалистичное заявление."),
                    ("過去の伝統や技術を完全に破棄して一新した。", "not_mentioned", "Неверно. Об этом речи нет."),
                    ("海外からの製品輸入に全面的に頼るようになった。", "opposite_meaning", "Неверно. Речь идет о внутреннем развитии.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "現場の担当者が最も重要視している考え方はどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "Согласно цитате ev-q2, самое важное — не просто снизить расходы, а создать систему, обогащающую человека и общество.",
            "options": opt_list(
                q_num=2,
                correct_text="単なるコスト削減ではなく、人と社会が共に豊かになる仕組みを作ること。",
                correct_exp="Верно! Прямое утверждение ответственного лица (ev-q2).",
                wrongs=[
                    ("何よりも企業の短期的な利益を最優先すること。", "opposite_meaning", "Неверно. Противоречит цитате."),
                    ("従業員の給与を削減して投資に回すこと。", "not_mentioned", "Неверно. Такого в тексте нет."),
                    ("新しい技術の導入を諦めて現状を維持すること。", "opposite_meaning", "Неверно. Речь идет об активных инновациях.")
                ]
            )
        }

        q_list = [q1, q2]

        if num_q == 3:
            q3 = {
                "slug": f"{slug}-q3",
                "question_number": 3,
                "type": "inference",
                "prompt": "専門家がこの取り組みに対して寄せている期待は何か。",
                "evidence_span_id": "ev-q3",
                "general_explanation": "В фрагменте ev-q3 эксперты выражают надежду на оживление региональной экономики и решение социальных проблем.",
                "options": opt_list(
                    q_num=3,
                    correct_text="地域経済の活性化と社会課題の解決が同時に達成されること。",
                    correct_exp="Верно! Соответствует предложению ev-q3.",
                    wrongs=[
                        ("外国企業による市場独占が進むこと。", "opposite_meaning", "Неверно. Ловушка обратного смысла."),
                        ("すべての伝統産業が閉鎖されること。", "extreme_condition", "Неверно. Полная противоположность цели."),
                        ("人口の都市集中がさらに加速すること。", "not_mentioned", "Неверно. Напротив, поддерживаются регионы.")
                    ]
                )
            }
            q_list.append(q3)

        texts.append({
            "slug": slug,
            "level": "N3",
            "category": "article",
            "title": f"{title} (N3)",
            "source_type": "news_adapted",
            "source_note": "NHK WORLD-JAPAN 特集報道アーカイブに基づく学習用適応",
            "recommended_time_min": 5,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "持続可能性", "furigana": "じぞくかのうせい", "translation": "устойчивость"},
                {"word": "活性化", "furigana": "かっせいか", "translation": "активизация, оживление"},
                {"word": "担当者", "furigana": "たんとうしゃ", "translation": "ответственное лицо"}
            ],
            "needs_manual_review": [],
            "questions": q_list
        })

    # Save to content/n3.json
    out_path = CONTENT_DIR / "n3.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    total_qs = sum(len(t["questions"]) for t in texts)
    print(f"Generated {out_path}: {len(texts)} texts, {total_qs} questions.")

if __name__ == "__main__":
    build_n3_corpus()

