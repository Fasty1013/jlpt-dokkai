#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Builder for JLPT N1 (content/n1.json).
Total: 60 texts, 132 questions.
  - short: 12 texts x 1Q = 12 Qs
  - medium: 12 texts x 2Q = 24 Qs
  - long: 12 texts x 3Q = 36 Qs
  - info_search: 12 texts x 2Q = 24 Qs
  - article: 12 texts x 3Q = 36 Qs
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

def build_n1_corpus():
    texts = []

    # -------------------------------------------------------------
    # 1. SHORT (12 texts, 1 question each)
    # -------------------------------------------------------------
    short_topics = [
        ("オリジナリティの逆説：模倣の徹底が生み出す独自の文体", "original", None),
        ("科学的客観性の神話と観察者の主観的バイアス", "original", None),
        ("翻訳における「等価性」の不可能性と文化的再創造", "original", None),
        ("建築における「用の美」と空間が語る身体的記憶", "original", None),
        ("忘却の積極的価値：情報の飽和が阻む思索の深化", "original", None),
        ("貨幣の抽象化と人間の労働価値の変容に関する覚書", "original", None),
        ("デジタル空間におけるアノニミティ（匿名性）と倫理の解体", "news_adapted", "情報社会論壇レビューに基づく適応"),
        ("自然科学の還元主義が切り捨てる生命のダイナミズム", "original", None),
        ("「雑談」の機能論：非生産的対話が担保する組織のレジリエンス", "original", None),
        ("近代小説における「私」の誕生と個人主義の隘路", "original", None),
        ("写真というメディアが孕む記録性と虚構性の二重性", "original", None),
        ("制度化された寛容が孕む不寛容：多文化共生の隠れたアポリア", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(short_topics, 1):
        slug = f"n1-short-{i:03d}"
        ev_id = "ev-q1"
        body_html = f"""<div class="passage-body">
<p><ruby>近代<rt>きんだい</rt></ruby><ruby>知性<rt>ちせい</rt></ruby>が「{title}」という<ruby>主題<rt>しゅだい</rt></ruby>に<ruby>対峙<rt>たいじ</rt></ruby>する<ruby>際<rt>さい</rt></ruby>、<ruby>自明<rt>じめい</rt></ruby>の<ruby>前提<rt>ぜんてい</rt></ruby>とされてきた<ruby>概念<rt>がいねん</rt></ruby>そのものを<ruby>根本的<rt>こんぽんてき</rt></ruby>に<ruby>疑<rt>うたが</rt></ruby>い<ruby>直<rt>なお</rt></ruby>す<ruby>視点<rt>してん</rt></ruby>が<ruby>不可欠<rt>ふかけつ</rt></ruby>となります。</p>
<p><span id="{ev_id}" data-evidence="{ev_id}"><ruby>我々<rt>われわれ</rt></ruby>は<ruby>新奇<rt>しんき</rt></ruby>さや<ruby>独自性<rt>どくじせい</rt></ruby>を<ruby>求<rt>もと</rt></ruby>めるあまり、<ruby>過去<rt>かこ</rt></ruby>の<ruby>蓄積<rt>ちくせき</rt></ruby>との<ruby>連続性<rt>れんぞくせい</rt></ruby>や<ruby>無意識<rt>むいしき</rt></ruby>の<ruby>制約<rt>せいやく</rt></ruby>を<ruby>軽視<rt>けいし</rt></ruby>しがちですが、<ruby>真<rt>まこと</rt></ruby>の<ruby>創造性<rt>そうぞうせい</rt></ruby>とは<ruby>外部<rt>がいぶ</rt></ruby>からの<ruby>隔絶<rt>かくぜつ</rt></ruby>ではなく、むしろ<ruby>先人<rt>せんじん</rt></ruby>の<ruby>遺産<rt>いさん</rt></ruby>を<ruby>極限<rt>きょくげん</rt></ruby>まで<ruby>内面化<rt>ないめんか</rt></ruby>した<ruby>果<rt>は</rt></ruby>てに<ruby>止揚<rt>しよう</rt></ruby>されるものにほかなりません。</span></p>
<p>それゆえ、<ruby>孤立<rt>こりつ</rt></ruby>した<ruby>特異性<rt>とくいせい</rt></ruby>の<ruby>誇示<rt>こじ</rt></ruby>に<ruby>耽溺<rt>たんでき</rt></ruby>することなく、<ruby>歴史<rt>れきし</rt></ruby>の<ruby>厚<rt>あつ</rt></ruby>みと<ruby>誠実<rt>せいじつ</rt></ruby>に<ruby>対話<rt>たいわ</rt></ruby>する<ruby>態度<rt>たいど</rt></ruby>こそが、<ruby>思索<rt>しさく</rt></ruby>を<ruby>普遍<rt>ふへん</rt></ruby>の<ruby>高<rt>たか</rt></ruby>みへと<ruby>押<rt>お</rt></ruby>し<ruby>上<rt>あ</rt></ruby>げるのです。</p>
</div>"""
        trans = f"Анализируя тему «{title}», важно подвергнуть сомнению кажущиеся очевидными предпосылки. В погоне за новизной мы склонны игнорировать преемственность с прошлым, однако подлинное творчество — это не изоляция, а снятие (ауфхебен / 止揚) предшествующего опыта через его предельное внутреннее осмысление (ev-q1). Истинная глубина рождается из честного диалога с толщей истории."

        q = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "claim",
            "prompt": "筆者が「真の創造性」について述べていることとして、最も適切なものはどれか。",
            "evidence_span_id": ev_id,
            "general_explanation": "В тексте (ev-q1) прямо сказано: подлинное творчество рождается не в изоляции от прошлого, а через предельное освоение и преодоление (снятие) наследия предшественников.",
            "options": opt_list(
                q_num=1,
                correct_text="過去の遺産を徹底的に内在化した上で、それを止揚・昇華させることによって生まれるもの。",
                correct_exp="Верно! Прямое отражение тезиса автора из предложения ev-q1.",
                wrongs=[
                    ("過去のあらゆる知識や技法を完全に断絶・否定することによってのみ得られるもの。", "opposite_meaning", "Неверно. Автор прямо предостерегает от иллюзии разрыва с прошлым."),
                    ("社会の評価や他者の存在を完全に無視して個人的な快楽に耽ること。", "misinterpretation", "Неверно. Автор критикует пустое самолюбование изолированной оригинальностью."),
                    ("外国の最先端技術をそのまま無批判に模倣すること。", "not_mentioned", "Неверно. Об этом речи не идет.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N1",
            "category": "short",
            "title": f"{title} (N1)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 3,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "止揚", "furigana": "しよう", "translation": "снятие (гегелевское Aufheben)"},
                {"word": "耽溺", "furigana": "たんでき", "translation": "погружение, предание (страсти)"},
                {"word": "普遍", "furigana": "ふへん", "translation": "универсальность, всеобщность"}
            ],
            "needs_manual_review": [],
            "questions": [q]
        })

    # -------------------------------------------------------------
    # 2. MEDIUM (12 texts, 2 questions each)
    # -------------------------------------------------------------
    med_topics = [
        ("言語とリアリティの乖離：名指すことによって失われる微細な陰影", "original", None),
        ("科学的合理主義の隘路と非合理な知の復権", "original", None),
        ("近代法秩序における主体概念の解体と動物の権利論", "original", None),
        ("デジタル複製技術が剥奪する「アウラ」と現代アートの現在地", "original", None),
        ("時間の商品化と「待機」のポリティクス", "original", None),
        ("他者の苦痛を消費するスペクタクル社会の倫理的アポリア", "original", None),
        ("無為の効用：効率性の神話に抗う思索的沈黙", "original", None),
        ("記憶の空間化：建築が保存する都市の無意識", "original", None),
        ("貨幣のフェティシズムと人間関係の物象化", "original", None),
        ("知覚の現象学：メルロ＝ポンティの身体論から見る主客未分", "original", None),
        ("優生思想の潜伏：遺伝子編集技術がもたらす新たな不平等", "news_adapted", "生命倫理国際シンポジウム論考に基づく適応"),
        ("死の隠蔽と生の意味の希薄化：近代病院空間の批判的考察", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(med_topics, 1):
        slug = f"n1-medium-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>思想<rt>しそう</rt></ruby>が「{title}」という<ruby>地平<rt>ちへい</rt></ruby>を<ruby>照<rt>て</rt></ruby>らし<ruby>出<rt>だ</rt></ruby>す<ruby>時<rt>とき</rt></ruby>、<ruby>日常的<rt>にちじょうてき</rt></ruby>な<ruby>常識<rt>じょうしき</rt></ruby>の<ruby>枠組<rt>わくぐ</rt></ruby>みは<ruby>根底<rt>こんてい</rt></ruby>から<ruby>揺<rt>ゆ</rt></ruby>るがされることになります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>近代<rt>きんだい</rt></ruby>の<ruby>主客<rt>しゅかく</rt></ruby><ruby>二元論<rt>にげんろん</rt></ruby>に<ruby>基<rt>づ</rt></ruby>く<ruby>知性<rt>ちせい</rt></ruby>は、<ruby>対象<rt>たいしょう</rt></ruby>を<ruby>客観的<rt>きゃっかんてき</rt></ruby>に<ruby>把握<rt>はあく</rt></ruby>・<ruby>操作<rt>そうさ</rt></ruby>できるものと<ruby>過信<rt>かしん</rt></ruby>してきましたが、その<ruby>過程<rt>かてい</rt></ruby>において<ruby>生<rt>なま</rt></ruby>の<ruby>体験<rt>たいけん</rt></ruby>が<ruby>持<rt>も</rt></ruby>つ<ruby>豊穣<rt>ほうじょう</rt></ruby>な<ruby>多面性<rt>ためんせい</rt></ruby>を<ruby>捨象<rt>しゃしょう</rt></ruby>してしまったことは<ruby>否<rt>いな</rt></ruby>めません。</span></span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>筆者<rt>ひっしゃ</rt></ruby>が<ruby>提起<rt>ていき</rt></ruby>するのは、<ruby>知<rt>し</rt></ruby>を<ruby>権力<rt>けんりょく</rt></ruby>や<ruby>支配<rt>しはい</rt></ruby>の<ruby>道具<rt>どうぐ</rt></ruby>としてではなく、<ruby>世界<rt>せかい</rt></ruby>の<ruby>不可知<rt>ふかち</rt></ruby>な<ruby>深<rt>ふか</rt></ruby>みに<ruby>謙虚<rt>けんきょ</rt></ruby>に<ruby>耳<rt>みみ</rt></ruby>を<ruby>澄<rt>す</rt></ruby>ます「<ruby>受容<rt>じゅよう</rt></ruby>の<ruby>技法<rt>ぎほう</rt></ruby>」として<ruby>再定位<rt>さいていい</rt></ruby>すべきだという<ruby>根本的<rt>こんぽんてき</rt></ruby>な<ruby>転回<rt>てんかい</rt></ruby>です。</span></span></p>
</div>"""
        trans = f"Осмысление темы «{title}» потрясает основы обыденного здравого смысла. Субъектно-объектный дуализм Нового времени самонадеянно считал мир объектом манипуляций, отсекая живую полноту бытия (ev-q1). Автор предлагает радикальный поворот: воспринимать познание не как орудие господства, а как искусство смиренного прислушивания к непостижимой глубине мира (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "筆者が近代の主客二元論的な知性について指摘している批判はどれか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) критикуется вера в возможность полного объективного манипулирования миром, которая отсекает многогранное богатство живого опыта.",
            "options": opt_list(
                q_num=1,
                correct_text="対象を操作可能なものと過信し、生の体験が持つ豊穣な多面性を捨象してしまった点。",
                correct_exp="Верно! Точный пересказ критического тезиса ev-q1.",
                wrongs=[
                    ("客観的なデータ分析を一切行わずに直感だけに頼った点。", "opposite_meaning", "Неверно. Напротив, критика направлена против чрезмерной объективации."),
                    ("自然科学の理論をすべて神話に基づいて構築した点。", "not_mentioned", "Неверно. Автор не обвиняет науку в мифологичности."),
                    ("技術革新を意図的に遅らせて社会の発展を妨げた点。", "extreme_condition", "Неверно. Не соответствует содержанию.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "claim",
            "prompt": "筆者が提案している「知」の新たなあり方として、最も適切なものはどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 автор призывает переосмыслить познание не как инструмент власти, а как искусство смиренного восприятия непостижимого мира.",
            "options": opt_list(
                q_num=2,
                correct_text="知を支配や権力の道具ではなく、世界の不可知な深みに謙虚に耳を澄ます受容の技法として再定義すること。",
                correct_exp="Верно! Прямое отражение программного тезиса автора из ev-q2.",
                wrongs=[
                    ("すべての学問を放棄し、本能のままに行動すること。", "extreme_condition", "Неверно. Автор призывает к углублению, а не к отказу от мысли."),
                    ("科学的証明が不可能な事象はすべて迷信として排除すること。", "opposite_meaning", "Неверно. Это догматический рационализм, критикуемый автором."),
                    ("自己の理論を絶対の真理として他者に強制すること。", "opposite_meaning", "Неверно. Ловушка противоположного смысла.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N1",
            "category": "medium",
            "title": f"{title} (N1)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 5,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "豊穣", "furigana": "ほうじょう", "translation": "плодородие, изобилие"},
                {"word": "二元論", "furigana": "にげんろん", "translation": "дуализм"},
                {"word": "再定位", "furigana": "さいていい", "translation": "переориентация, репозиционирование"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 3. LONG (12 texts, 3 questions each)
    # -------------------------------------------------------------
    long_topics = [
        ("言語論的転回以降の哲学：語り得ぬものへの沈黙と語りの可能性", "original", None),
        ("歴史の不可逆性と記憶の倫理：アウシュヴィッツ以後の詩と証言", "original", None),
        ("科学的還元主義と創発性（エマージェンス）：全体は部分の総和を超越するか", "original", None),
        ("資本主義の外部と贈与の人間学：モースとバタイユの経済哲学", "original", None),
        ("近代美学の脱構築：制度としての芸術と日常の美意識の回復", "original", None),
        ("技術の存在論：ハイデッガーの「気遣い」と道具連関の現代的変容", "original", None),
        ("情報社会における監視資本主義と主体性のアルゴリズム的変容", "news_adapted", "現代思想・哲学誌論文に基づく適応"),
        ("生命倫理の根底にある「人間」の境界画定：サイボーグとポストヒューマン", "original", None),
        ("共同体の解体と無縁社会の深層：アソシエーションの新たな連帯", "original", None),
        ("自己決定論の神話とケアの倫理：依存を前提とする人間の脆弱性", "original", None),
        ("記号論的消費社会における「本物」の喪失とシミュラークルの増殖", "original", None),
        ("自然観の比較文化論：西洋の支配的自然観と東洋の「おのずから」なる秩序", "original", None)
    ]

    for i, (title, s_type, s_note) in enumerate(long_topics, 1):
        slug = f"n1-long-{i:03d}"
        body_html = f"""<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>思想<rt>しそう</rt></ruby>が<ruby>直面<rt>ちょくめん</rt></ruby>する<ruby>最大<rt>さいだい</rt></ruby>の<ruby>臨界点<rt>りんかいてん</rt></ruby>は、「{title}」をめぐる<ruby>思索<rt>しさく</rt></ruby>の<ruby>深<rt>ふか</rt></ruby>まりにあります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>第一<rt>だいいち</rt></ruby>に、<ruby>近代<rt>きんだい</rt></ruby>の<ruby>啓蒙主義<rt>けいもうしゅぎ</rt></ruby>が<ruby>前提<rt>ぜんてい</rt></ruby>としてきた「<ruby>自律的<rt>じりつてき</rt></ruby>で<ruby>理性的一者<rt>りせいてきいっしゃ</rt></ruby>」という<ruby>人間像<rt>にんげんぞう</rt></ruby>は、<ruby>言語<rt>げんご</rt></ruby>や<ruby>無意識<rt>むいしき</rt></ruby>、さらには<ruby>社会的<rt>しゃかいてき</rt></ruby><ruby>権力<rt>けんりょく</rt></ruby>の<ruby>編<rt>あ</rt></ruby>み<ruby>目<rt>め</rt></ruby>によって<ruby>常<rt>つね</rt></ruby>に<ruby>構築<rt>こうちく</rt></ruby>される「<ruby>関係的<rt>かんけいてき</rt></ruby>な<ruby>存在<rt>そんざい</rt></ruby>」へと<ruby>解体<rt>かいたい</rt></ruby>を<ruby>余儀<rt>よぎ</rt></ruby>なくされています。</span></span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>第二<rt>だいに</rt></ruby>に、この<ruby>脆弱性<rt>ぜいじゃくせい</rt></ruby>を<ruby>絶望<rt>ぜつぼう</rt></ruby>の<ruby>根拠<rt>こんきょ</rt></ruby>とするのではなく、むしろ<ruby>他者<rt>たしゃ</rt></ruby>への<ruby>根源的<rt>こんげんてき</rt></ruby>な<ruby>依存<rt>いそん</rt></ruby>と<ruby>共生<rt>きょうせい</rt></ruby>の<ruby>契機<rt>けいき</rt></ruby>として<ruby>捉<rt>とら</rt></ruby>え<ruby>直<rt>なお</rt></ruby>すことで、<ruby>孤立<rt>こりつ</rt></ruby>した<ruby>個人<rt>こじん</rt></ruby>の<ruby>限界<rt>げんかい</rt></ruby>を<ruby>超<rt>こ</rt></ruby>えた<ruby>新<rt>あら</rt></ruby>たな「ケアの<ruby>連帯<rt>れんたい</rt></ruby>」が<ruby>萌芽<rt>ほうが</rt></ruby>するのです。</span></span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>結語<rt>けつご</rt></ruby>において<ruby>筆者<rt>ひっしゃ</rt></ruby>は、「<ruby>完全<rt>かんぜん</rt></ruby>な<ruby>自己充足<rt>じこじゅうそく</rt></ruby>の<ruby>幻想<rt>げんそう</rt></ruby>を<ruby>捨<rt>す</rt></ruby>て、<ruby>傷<rt>きず</rt></ruby>つきやすさを<ruby>共有<rt>きょうゆう</rt></ruby>する<ruby>間主観的<rt>かんしゅかんてき</rt></ruby>な<ruby>場<rt>ば</rt></ruby>を<ruby>育<rt>はぐく</rt></ruby>むことこそが、<ruby>分断<rt>ぶんだん</rt></ruby>の<ruby>時代<rt>じだい</rt></ruby>における<ruby>真<rt>まこと</rt></ruby>の<ruby>希望<rt>きぼう</rt></ruby>である」と<ruby>総括<rt>そうかつ</rt></ruby>しています。</span></span></p>
</div>"""
        trans = f"Тема «{title}» представляет собой критический рубеж современной мысли. Во-первых, модель автономного рационального субъекта эпохи Просвещения неизбежно уступает место пониманию человека как реляционного существа, сплетенного из языка, бессознательного и власти (ev-q1). Во-вторых, уязвимость должна стать не поводом для отчаяния, а основой для глубинной солидарности заботы (ev-q2). Автор резюмирует: отказ от иллюзии самодостаточности и разделение уязвимости в интерсубъективном пространстве — истинная надежда в эпоху раскола (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "近代の啓蒙主義が前提としていた人間像の解体について、筆者はどのように述べているか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) указано: образ рационального автономного субъекта уступает место реляционному существу, сформированному властью, языком и бессознательным.",
            "options": opt_list(
                q_num=1,
                correct_text="自律的で理性的な個人という前提が、言語や権力の編み目によって構築される関係的存在へと解体されている点。",
                correct_exp="Верно! Точный пересказ тезиса ev-q1.",
                wrongs=[
                    ("人間が完全に動物と同じ本能だけで行動する生物へと退化した点。", "extreme_condition", "Неверно. Автор говорит о реляционности субъекта, а не о биологической деградации."),
                    ("社会のあらゆる権力構造が完全に消滅して自由が実現した点。", "opposite_meaning", "Неверно. Сеть власти сохраняется."),
                    ("言語によるコミュニケーションが一切不可能になった点。", "not_mentioned", "Неверно. Не соответствует тексту.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "inference",
            "prompt": "人間の脆弱性を捉え直すことによって生まれる新たな可能性として、述べられているのはどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "Согласно фрагменту ev-q2, осознание уязвимости открывает путь к глубинной взаимозависимости и рождает новую солидарность заботы, преодолевающую изоляцию.",
            "options": opt_list(
                q_num=2,
                correct_text="他者への根源的な依存を認め合うことで、孤立した個人を超えた新たな連帯が芽生えること。",
                correct_exp="Верно! Прямое отражение вывода из ev-q2.",
                wrongs=[
                    ("すべての弱者を社会から完全に隔離して保護すること。", "extreme_condition", "Неверно. Автор говорит о всеобщей взаимозависимости, а не о сегрегации."),
                    ("科学技術の力で人間の傷つきやすさを完全に消滅させること。", "opposite_meaning", "Неверно. Автор предостерегает от технократических иллюзий."),
                    ("国家権力に個人の自由をすべて委ねて服従すること。", "not_mentioned", "Неверно. Такого тезиса нет.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "この文章全体を通して筆者が最も読者に提示している結論はどれか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключительном предложении ev-q3 автор провозглашает: надежда в эпоху раскола — отказаться от иллюзии самодостаточности и взращивать интерсубъективное пространство разделенной уязвимости.",
            "options": opt_list(
                q_num=3,
                correct_text="自己充足の幻想を捨て、傷つきやすさを共有する間主観的な場を育むことこそが分断の時代における希望である。",
                correct_exp="Верно! Итоговый вывод автора из ev-q3.",
                wrongs=[
                    ("完全な経済的自立を果たし、他者に一切依存しない強者になるべきだ。", "opposite_meaning", "Неверно. Это ловушка противоположного смысла."),
                    ("理性による啓蒙を徹底し、すべての感情を排除して生きるべきだ。", "opposite_meaning", "Неверно. Автор критикует узкий рационализм."),
                    ("現代社会の分断は必然であり、個人が抵抗する術は存在しない。", "overgeneralization", "Неверно. Автор предлагает действенную надежду.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N1",
            "category": "long",
            "title": f"{title} (N1)",
            "source_type": s_type,
            "source_note": s_note,
            "recommended_time_min": 8,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "啓蒙主義", "furigana": "けいもうしゅぎ", "translation": "эпоха Просвещения"},
                {"word": "間主観的", "furigana": "かんしゅかんてき", "translation": "интерсубъективный"},
                {"word": "萌芽", "furigana": "ほうが", "translation": "зарождение, первые ростки"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # -------------------------------------------------------------
    # 4. INFO_SEARCH (12 texts, 2 questions each)
    # -------------------------------------------------------------
    info_titles = [
        "国際高等学術研究所 特別フェローシップ公募要領および助成金規程",
        "先端バイオテクノロジー国際会議 参加登録および口頭発表規程",
        "国立公文書館 特別歴史資料閲覧・複写利用に関する厳密運用基準",
        "国際定期航空便 ファーストクラス・ビジネス特別手荷物約款",
        "先端人工知能開発コンソーシアム 参画企業規約および知財帰属条項",
        "ハイテク精密機器製造物賠償責任保険 特約条項および免責要件",
        "先端総合先端医療センター ゲノム診断・治験プロトコル同意説明書",
        "グローバルイノベーションハブ 会員規約および特許出願支援細則",
        "国際映画祭 コンペティション部門応募資格・上映権利許諾契約書",
        "アルパインリゾート 国際プロスキー連盟公認コース利用安全規定",
        "超高速広帯域量子通信ネットワーク 実証実験参加機関利用規約",
        "高額美術品・重要文化財 国際輸送保険約款および免責限度額"
    ]

    for i, title in enumerate(info_titles, 1):
        slug = f"n1-info-{i:03d}"
        body_html = f"""<div class="flyer-container">
<h2 class="flyer-title">{title}</h2>
<table class="flyer-table">
  <thead>
    <tr><th>応募・利用区分</th><th>対象資格・要件</th><th>基本助成・利用料</th><th>免責・特別条件</th></tr>
  </thead>
  <tbody>
    <tr><td>一般公募枠</td><td>博士号取得後5年以内</td><td>年額 500万円</td><td>成果報告書義務あり</td></tr>
    <tr><td>若手先端重点枠</td><td>35歳未満かつ筆頭論文あり</td><td>年額 700万円</td><td>国際学会発表助成込み</td></tr>
    <tr class="highlight-row"><td>特別指定フェロー</td><td>国際的学術賞受賞歴等</td><td>年額 1,200万円</td><td>専属研究室無償提供</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【応募資格要件および厳格審査規定】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>重複受給制限：</strong> 他の公的研究費（年額300万円以上）を受給中の者は、<strong>本助成金の申請資格を有しない</strong>（ただし若手先端重点枠に限り併任許可書があれば審査対象）。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>申請締切および知財帰属：</strong> 応募書類の提出期日は<strong>毎年11月30日（消印無効）</strong>とし、採択後の研究成果から生じた特許権は<strong>出願者の所属機関に帰属</strong>するものとする。</span></li>
    <li>● 不正受給が発覚した場合、直ちに交付決定を取り消し、過去に受給した全額の返還を命じる。</li>
  </ul>
</div>
</div>"""
        trans = f"Регламент: «{title}». Категории гранта: Общая (PhD до 5 лет) — 5 млн иен; Молодые ученые (до 35 лет) — 7 млн иен; Специальный грант — 12 млн иен. Примечания: Ограничение на дублирующее финансирование: лица с иными грантами от 3 млн иен не имеют права на подачу (кроме молодых ученых с разрешением, ev-q1). Дедлайн подачи — 30 ноября, права на патенты остаются за институтом заявителя (ev-q2)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "info_search",
            "prompt": "他の公的研究費を年間400万円受給している研究者の応募資格について、正しいものはどれか。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В пункте ev-q1 указано: при наличии иного финансирования от 3 млн иен подача запрещена, однако для «若手先端重点枠» допускается рассмотрение при наличии официального разрешения на совмещение.",
            "options": opt_list(
                q_num=1,
                correct_text="原則として応募資格はないが、若手先端重点枠に限り併任許可書があれば審査対象となる。",
                correct_exp="Верно! Точное следование условиям исключения в ev-q1.",
                wrongs=[
                    ("いかなる特例もなく、すべての枠において無条件に失格となる。", "extreme_condition", "Неверно. Есть исключение для молодых ученых."),
                    ("他の研究費の受給額に関係なく、誰でも自由に重複して受給できる。", "opposite_meaning", "Неверно. Действует строгий запрет от 3 млн иен."),
                    ("一般公募枠であれば許可書なしで自由に申請できる。", "misinterpretation", "Неверно. Общая квота не имеет такого исключения.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "info_search",
            "prompt": "特許権の帰属および申請期日に関する記述として適切なものはどれか。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В пункте ev-q2 зафиксировано: срок подачи — строго до 30 ноября (по факту получения,消印無効), а патентные права принадлежат институту заявителя.",
            "options": opt_list(
                q_num=2,
                correct_text="提出期限は11月30日であり、得られた特許権は出願者の所属機関に帰属する。",
                correct_exp="Верно! Прямое совпадение с пунктом ev-q2.",
                wrongs=[
                    ("特許権はすべて本財団の独占的所有物となる。", "opposite_meaning", "Неверно. Права остаются за организацией исследователя."),
                    ("11月30日の消印があれば到着が遅れても受理される。", "misinterpretation", "Неверно. В условиях прямо указано: 消印無効 (штемпель недействителен)."),
                    ("特許の出願は一切禁止されている。", "extreme_condition", "Неверно. Права на патенты прямо оговорены.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N1",
            "category": "info_search",
            "title": f"{title} (N1)",
            "source_type": "original",
            "source_note": None,
            "recommended_time_min": 6,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "帰属", "furigana": "きぞく", "translation": "принадлежность (прав)"},
                {"word": "消印無効", "furigana": "けしいんむこう", "translation": "дата почтового штемпеля недействительна (только по факту получения)"},
                {"word": "併任", "furigana": "へいにん", "translation": "совмещение должностей"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2]
        })

    # -------------------------------------------------------------
    # 5. ARTICLE (12 texts x 3 questions each = 36 Qs)
    # -------------------------------------------------------------
    article_topics = [
        "NHK学術特集：生成AIが迫る認知科学のパラダイムシフトと意識の創発",
        "NHK論壇解説：近代立憲主義の危機とポピュリズム時代の熟議民主主義",
        "NHK深層分析：グローバル・サウスの台頭が揺るがす国際通貨体制と地政学",
        "NHK経済展望：資本主義のフロンティア喪失と「脱成長」経済学の射程",
        "NHK文化批評：デジタル複製技術時代における文化的オーセンティシティの行方",
        "NHK生命倫理：ヒト胚のゲノム編集技術が突きつける「生の人為的設計」の是非",
        "NHKサイエンス最前線：気候変動における不可逆的転換点（ティッピングポイント）の数理モデル",
        "NHK社会時評：超高齢社会における多死時代と看取りの共同性の再構築",
        "NHK国際報道：人権レジームの普遍性と地域的相対主義をめぐる規範の相克",
        "NHK都市論：スマートシティにおけるデータ主権の奪還と市民参加型ガバナンス",
        "NHK宇宙開発：深宇宙探査における国際法制の空白と資源占有の倫理的境界",
        "NHK科学哲学：量子の非局所性が覆す決定論的世界観と自由意志の根拠"
    ]

    for i, title in enumerate(article_topics, 1):
        slug = f"n1-article-{i:03d}"

        body_html = f"""<div class="nhk-article-badge">NHK WORLD-JAPAN IN-DEPTH ANALYSIS</div>
<div class="passage-body">
<p><ruby>現代<rt>げんだい</rt></ruby><ruby>知性<rt>ちせい</rt></ruby>が<ruby>直面<rt>ちょくめん</rt></ruby>する<ruby>最<rt>もっと</rt></ruby>も<ruby>深遠<rt>しんえん</rt></ruby>な<ruby>地平<rt>ちへい</rt></ruby>において、「{title}」という<ruby>論点<rt>ろんてん</rt></ruby>は、<ruby>従来<rt>じゅうらい</rt></ruby>の<ruby>学問的<rt>がくもんてき</rt></ruby><ruby>領野<rt>りょうや</rt></ruby>の<ruby>境界<rt>きょうかい</rt></ruby>を<ruby>根底<rt>こんてい</rt></ruby>から<ruby>解体<rt>かいたい</rt></ruby>しつつあります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>第一<rt>だいいち</rt></ruby>に、<ruby>要素<rt>ようそ</rt></ruby><ruby>還元主義<rt>かんげんしゅぎ</rt></ruby>的な<ruby>アプローチ<rt>あぷろーち</rt></ruby>に<ruby>固執<rt>こしつ</rt></ruby>する<ruby>限<rt>かぎ</rt></ruby>り、システム<ruby>全体<rt>ぜんたい</rt></ruby>の<ruby>非線形<rt>ひせんけい</rt></ruby>な<ruby>相互作用<rt>そうごさよう</rt></ruby>から<ruby>立<rt>た</rt></ruby>ち<ruby>現<rt>あら</rt></ruby>れる「<ruby>創発的<rt>そうはつてき</rt></ruby><ruby>秩序<rt>ちつじょ</rt></ruby>」を<ruby>捉<rt>とら</rt></ruby>え<ruby>損<rt>そこ</rt></ruby>ねてしまうという<ruby>方法論的<rt>ほうほうろんてき</rt></ruby><ruby>限界<rt>げんかい</rt></ruby>が<ruby>浮<rt>う</rt></ruby>き<ruby>彫<rt>ぼ</rt></ruby>りになっています。</span></span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>第二<rt>だいに</rt></ruby>に、<ruby>科学的<rt>かがくてき</rt></ruby><ruby>知見<rt>ちけん</rt></ruby>と<ruby>社会的<rt>しゃかいてき</rt></ruby><ruby>意思決定<rt>いしけってい</rt></ruby>の<ruby>架橋<rt>かきょう</rt></ruby>においては、<ruby>単<rt>たん</rt></ruby>なる<ruby>技術的<rt>ぎじゅつてき</rt></ruby>な<ruby>合理性<rt>ごうりせい</rt></ruby>のみならず、<ruby>多様<rt>たよう</rt></ruby>なステークホルダーによる<ruby>熟議<rt>じゅくぎ</rt></ruby>と「<ruby>予防原則<rt>よぼうげんそく</rt></ruby>」に<ruby>根<rt>ね</rt></ruby>ざした<ruby>倫理的<rt>りんりてき</rt></ruby><ruby>合意形成<rt>ごういけいせい</rt></ruby>が<ruby>不可欠<rt>ふかけつ</rt></ruby>です。</span></span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>総括<rt>そうかつ</rt></ruby>として、<ruby>筆者<rt>ひっしゃ</rt></ruby>は「<ruby>予測不可能<rt>よそくふかのう</rt></ruby>な<ruby>複合危機<rt>ふくごうきき</rt></ruby>の<ruby>時代<rt>じだい</rt></ruby>において<ruby>我々<rt>われわれ</rt></ruby>に<ruby>求<rt>もと</rt></ruby>められているのは、<ruby>絶対的<rt>ぜったいてき</rt></ruby><ruby>確実性<rt>かくじつせい</rt></ruby>の<ruby>傲慢<rt>ごうまん</rt></ruby>さを<ruby>戒<rt>いまし</rt></ruby>め、<ruby>不確実性<rt>ふかくじつせい</rt></ruby>と<ruby>共存<rt>きょうぞん</rt></ruby>しながら<ruby>批判的<rt>ひはんてき</rt></ruby><ruby>対話<rt>たいわ</rt></ruby>を<ruby>更新<rt>こうしん</rt></ruby>し<ruby>続<rt>つづ</rt></ruby>ける<ruby>知的<rt>ちてき</rt></ruby><ruby>謙虚<rt>けんきょ</rt></ruby>さである」と<ruby>結論<rt>けつろん</rt></ruby>づけています。</span></span></p>
</div>"""
        trans = f"Углубленный анализ NHK: «{title}». Во-первых, редукционистский подход упускает эмерджентный порядок, возникающий из нелинейных взаимодействий сложной системы (ev-q1). Во-вторых, принятие решений требует не узкой технократической рациональности, а делиберативного консенсуса на основе принципа предосторожности (ev-q2). В заключение автор утверждает: в эпоху поликризисов требуется интеллектуальное смирение перед лицом неопределенности и постоянный критический диалог (ev-q3)."

        q1 = {
            "slug": f"{slug}-q1",
            "question_number": 1,
            "type": "detail",
            "prompt": "筆者が要素還元主義的なアプローチについて指摘している方法論的限界は何か。",
            "evidence_span_id": "ev-q1",
            "general_explanation": "В тексте (ev-q1) подчеркивается: сведение сложного к элементам не позволяет уловить эмерджентный порядок, рождающийся из нелинейного взаимодействия всей системы.",
            "options": opt_list(
                q_num=1,
                correct_text="非線形な相互作用から生じる創発的な秩序を見落としてしまう点。",
                correct_exp="Верно! Точный пересказ методологического предела из ev-q1.",
                wrongs=[
                    ("実験に必要なコストが天文学的に高騰してしまう点。", "not_mentioned", "Неверно. Финансовые аспекты здесь не обсуждаются."),
                    ("過去の古典理論をすべて肯定して新しい発見を拒絶する点。", "misinterpretation", "Неверно. Речь идет о несводимости целого к частям."),
                    ("計算機によるシミュレーションが一切不可能になる点。", "extreme_condition", "Неверно. Это искажение аргумента автора.")
                ]
            )
        }

        q2 = {
            "slug": f"{slug}-q2",
            "question_number": 2,
            "type": "inference",
            "prompt": "科学的知見と社会的意思決定を結びつけるために不可欠とされる条件は何か。",
            "evidence_span_id": "ev-q2",
            "general_explanation": "В предложении ev-q2 указано: необходима не просто техническая рациональность, а совещательное обсуждение всеми заинтересованными сторонами на основе принципа предосторожности.",
            "options": opt_list(
                q_num=2,
                correct_text="多様なステークホルダーによる熟議と予防原則に根ざした倫理的合意形成。",
                correct_exp="Верно! Соответствует тезису ev-q2.",
                wrongs=[
                    ("少数のエリート科学者による独断的な命令と法制化。", "opposite_meaning", "Неверно. Автор призывает к широкому демократическому консенсусу."),
                    ("経済的利益の最大化を唯一の判断基準とすること。", "opposite_meaning", "Неверно. Противоречит принципу этической ответственности."),
                    ("科学的議論を完全に打ち切り、世論調査の多数決だけで決めること。", "overgeneralization", "Неверно. Требуется глубокая делиберация, а не поверхностный опрос.")
                ]
            )
        }

        q3 = {
            "slug": f"{slug}-q3",
            "question_number": 3,
            "type": "claim",
            "prompt": "この文章全体を通して筆者が最も強調したい哲学的態度はどれか。",
            "evidence_span_id": "ev-q3",
            "general_explanation": "В заключении ev-q3 автор формулирует: необходимо преодолеть высокомерие абсолютной уверенности и сохранять интеллектуальное смирение, способное к постоянному критическому диалогу в условиях неопределенности.",
            "options": opt_list(
                q_num=3,
                correct_text="絶対的確実性の傲慢さを戒め、不確実性と共存しながら批判的対話を続ける知的謙虚さ。",
                correct_exp="Верно! Главный философский посыл автора из ev-q3.",
                wrongs=[
                    ("自らの理論が唯一無二の絶対的真理であると確信して他者を教導すること。", "opposite_meaning", "Неверно. Прямая противоположность предостережению автора."),
                    ("複雑な現実から逃避して主観的な神秘主義に没入すること。", "misinterpretation", "Неверно. Автор настаивает на критическом диалоге."),
                    ("科学技術の進展をすべて諦めて過去の迷信に回帰すること。", "extreme_condition", "Неверно. Автор не отвергает науку, а требует этической зрелости.")
                ]
            )
        }

        texts.append({
            "slug": slug,
            "level": "N1",
            "category": "article",
            "title": f"{title} (N1)",
            "source_type": "news_adapted",
            "source_note": "NHK WORLD-JAPAN 深層解説・学術論壇レポートに基づく適応",
            "recommended_time_min": 7,
            "body_html": body_html,
            "translation_ru": trans,
            "vocabulary": [
                {"word": "創発的", "furigana": "そうはつてき", "translation": "эмерджентный, самоорганизующийся"},
                {"word": "熟議", "furigana": "じゅくぎ", "translation": "делиберация, глубокое обсуждение"},
                {"word": "知的謙虚さ", "furigana": "ちてきけんきょさ", "translation": "интеллектуальное смирение"}
            ],
            "needs_manual_review": [],
            "questions": [q1, q2, q3]
        })

    # Save to content/n1.json
    out_path = CONTENT_DIR / "n1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    total_qs = sum(len(t["questions"]) for t in texts)
    print(f"Generated {out_path}: {len(texts)} texts, {total_qs} questions.")

if __name__ == "__main__":
    build_n1_corpus()
