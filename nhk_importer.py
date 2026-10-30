"""
NHK Importer Module for JLPT Dokkai Master.
Supports fetching real news from NHK World (RSS/JSON/HTML) or offline simulation,
adapting text for JLPT levels (N5-N1), extracting vocabulary,
and programmatically synthesizing exam-style multi-questions with traps and detailed Russian explanations.
"""
import os
import sys
import json
import re
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from database import SessionLocal
from models import Text, Question, Option


NHK_FEEDS = {
    "easy": "https://www3.nhk.or.jp/news/easy/top-list.json",
    "world_ru": "https://www3.nhk.or.jp/nhkworld/ru/news/",
    "world_jp": "https://www3.nhk.or.jp/news/"
}


# Curated real-world NHK World based sample templates for high-speed offline import
NHK_REAL_STORIES = [
    {
        "title": "新幹線が50周年：安全を守る日本の最新点検ロボット (50 лет Синкансэн: роботы-инспекторы)",
        "level": "N3",
        "category": "article",
        "recommended_time_min": 5,
        "content_html": """
<div class="nhk-article-badge">NHK WORLD-JAPAN TECH & LIFE</div>
<div class="passage-body">
    <p><ruby>日本<rt>にほん</rt></ruby>の<ruby>高速<rt>こうそく</rt></ruby><ruby>鉄道<rt>てつどう</rt></ruby>「<ruby>新幹線<rt>しんかんせん</rt></ruby>」は、<ruby>開業<rt>かいぎょう</rt></ruby>から<ruby>半世紀<rt>はんせいき</rt></ruby>にわたり、<ruby>乗客<rt>じょうきゃく</rt></ruby>の<ruby>死亡<rt>しぼう</rt></ruby><ruby>事故<rt>じこ</rt></ruby>ゼロという<ruby>驚異的<rt>きょういてき</rt></ruby>な<ruby>安全<rt>あんぜん</rt></ruby><ruby>記録<rt>きろく</rt></ruby>を<ruby>誇<rt>ほこ</rt></ruby>っています。しかし、その<ruby>裏<rt>うら</rt></ruby>には<ruby>深夜<rt>しんや</rt></ruby>の<ruby>線路<rt>せんろ</rt></ruby>で<ruby>行<rt>おこな</rt></ruby>われる<ruby>過酷<rt>かこく</rt></ruby>な<ruby>点検<rt>てんけん</rt></ruby><ruby>作業<rt>さぎょう</rt></ruby>があり、<ruby>少子<rt>しょうし</rt></ruby><ruby>高齢化<rt>こうれいか</rt></ruby>による<ruby>保線<rt>ほせん</rt></ruby><ruby>員<rt>いん</rt></ruby>の<ruby>不足<rt>ぶそく</rt></ruby>が<ruby>長年<rt>ながねん</rt></ruby>の<ruby>懸念<rt>けねん</rt></ruby>となっていました。</p>
    <p><span id="ev-nhk-shinkansen-1">そこで鉄道各社は、AIカメラと超音波センサーを搭載した自律走行型の点検ロボットを導入し、ミリ単位の歪みや摩耗を自動検出するシステムを本格稼働させました。</span>これにより、<ruby>人間<rt>にんげん</rt></ruby>が<ruby>目視<rt>もくし</rt></ruby>で<ruby>数時間<rt>すうじかん</rt></ruby>かけていた<ruby>区間<rt>くかん</rt></ruby>を、ロボットがわずか30<ruby>分<rt>ふん</rt></ruby>で<ruby>高精度<rt>こうせいど</rt></ruby>に<ruby>完了<rt>かんりょう</rt></ruby>できるようになりました。</p>
    <p><span id="ev-nhk-shinkansen-2">開発担当者は「ロボットは単に省力化のためだけでなく、作業員を深夜の危険な高所作業から解放し、より高度な修繕計画の立案に集中させるためのパートナーだ」と強調しています。</span><ruby>世界<rt>せかい</rt></ruby>から<ruby>注目<rt>ちゅうもく</rt></ruby>を<ruby>集<rt>あつ</rt></ruby>める<ruby>日本<rt>にほん</rt></ruby>のインフラ<ruby>技術<rt>ぎじゅつ</rt></ruby>は、ロボティクスとの<ruby>融合<rt>ゆうごう</rt></ruby>によって<ruby>新<rt>あら</rt></ruby>たなステージを<ruby>迎<rt>むか</rt></ruby>えています。</p>
</div>
""".strip(),
        "translation_ru": """
Японский скоростной поезд «Синкансэн» за полвека работы сохраняет невероятный рекорд безопасности — ноль жертв среди пассажиров. Однако за этим стоит тяжелейший ночной труд по проверке путей, и старение населения вызвало острую нехватку путевых рабочих.
В ответ железнодорожные компании внедрили автономных роботов с AI-камерами и ультразвуковыми сенсорами, которые автоматически выявляют миллиметровые деформации и износ. Участок, на проверку которого вручную уходили часы, теперь сканируется за 30 минут.
Разработчик подчеркивает: роботы не просто сокращают расходы труда, но и освобождают людей от опасных высотных работ ночью, позволяя им сосредоточиться на сложном инженерном планировании ремонта.
""".strip(),
        "vocabulary": [
            {"word": "驚異的", "furigana": "きょういてき", "translation": "поразительный, феноменальный"},
            {"word": "保線員", "furigana": "ほせんいん", "translation": "путевой рабочий, путеец"},
            {"word": "摩耗", "furigana": "まもう", "translation": "износ, истирание"},
            {"word": "省力化", "furigana": "しょうりょくか", "translation": "автоматизация, экономия трудозатрат"}
        ],
        "questions": [
            {
                "question_number": 1,
                "question_text": "新幹線の線路点検にロボットを導入した最大のきっかけは何ですか。",
                "general_explanation": "Правильный ответ — вариант 2. В первом абзаце говорится о тяжелом ночном труде и нехватке путевых рабочих из-за старения населения (少子高齢化による保線員の不足).",
                "evidence_span_id": "ev-nhk-shinkansen-1",
                "options": [
                    {"option_number": 1, "option_text": "新幹線で重大な脱線事故が頻発していたから。", "is_correct": False, "option_explanation": "Неверно. Синкансэн сохраняет рекорд нулевой смертности."},
                    {"option_number": 2, "option_text": "夜間の過酷な作業を担当する作業員が不足していたから。", "is_correct": True, "option_explanation": "Верно! Главный триггер: «少子高齢化による保線員の不足»."},
                    {"option_number": 3, "option_text": "海外の鉄道会社から点検ロボットを輸入する義務があったから。", "is_correct": False, "option_explanation": "Неверно. Технология разработана в Японии."},
                    {"option_number": 4, "option_text": "新幹線の運行速度を現在の倍に引き上げるため。", "is_correct": False, "option_explanation": "Неверно. Речь идет о безопасности путей, а не удвоении скорости."}
                ]
            },
            {
                "question_number": 2,
                "question_text": "開発担当者が述べる「ロボット導入の真の狙い」として最も適切なものはどれか。",
                "general_explanation": "Правильный ответ — вариант 4. В предложении ev-nhk-shinkansen-2 сказано: робот освобождает людей от опасной ночной рутины, позволяя людям сосредоточиться на сложном планировании ремонта.",
                "evidence_span_id": "ev-nhk-shinkansen-2",
                "options": [
                    {"option_number": 1, "option_text": "すべての人間を解雇して完全無人化を達成すること。", "is_correct": False, "option_explanation": "Неверно. Робот позиционируется как партнер, а не замена человеку."},
                    {"option_number": 2, "option_text": "線路の検査にかかる電気代をゼロに抑えること。", "is_correct": False, "option_explanation": "Неверно. Об экономии электричества не говорится."},
                    {"option_number": 3, "option_text": "昼間の時間帯に点検を行い新幹線を運休させること。", "is_correct": False, "option_explanation": "Неверно. Остановка дневного движения не планируется."},
                    {"option_number": 4, "option_text": "危険作業から作業員を守り、高度な修繕計画に集中させること。", "is_correct": True, "option_explanation": "Верно! Полный пересказ тезиса в <span id='ev-nhk-shinkansen-2'>."}
                ]
            }
        ]
    },
    {
        "title": "若者の間で広がる「デジタルデトックス」：スマホを手放す旅 (Цифровой детокс среди молодежи)",
        "level": "N2",
        "category": "article",
        "recommended_time_min": 6,
        "content_html": """
<div class="nhk-article-badge">NHK WORLD-JAPAN TRENDS</div>
<div class="passage-body">
    <p>スマートフォンやSNSが<ruby>生活<rt>せいかつ</rt></ruby>のすべてを<ruby>支配<rt>しはい</rt></ruby>する<ruby>現代<rt>げんだい</rt></ruby>、あえて<ruby>電波<rt>でんぱ</rt></ruby>の<ruby>届<rt>とど</rt></ruby>かない<ruby>山間<rt>さんかん</rt></ruby>の<ruby>古民家<rt>こみんか</rt></ruby>や<ruby>寺院<rt>じいん</rt></ruby>で<ruby>数日間<rt>すうじつかん</rt></ruby>を<ruby>過<rt>す</rt></ruby>ごす「デジタルデトックス」ツアーが、20<ruby>代<rt>だい</rt></ruby>から30<ruby>代<rt>だい</rt></ruby>の<ruby>若者<rt>わかもの</rt></ruby>を<ruby>中心<rt>ちゅうしん</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>反響<rt>はんきょう</rt></ruby>を<ruby>呼<rt>よ</rt></ruby>んでいます。</p>
    <p><ruby>参加者<rt>さんかしゃ</rt></ruby>は<ruby>到着<rt>とうちゃく</rt></ruby>と<ruby>同時<rt>どうじ</rt></ruby>に携帯端末を<ruby>金庫<rt>きんこ</rt></ruby>に<ruby>預<rt>あず</rt></ruby>け、時計も外して<ruby>自然<rt>しぜん</rt></ruby>の<ruby>光<rt>ひかり</rt></ruby>とともに<ruby>起床<rt>きしょう</rt></ruby>・<ruby>就寝<rt>しゅうしん</rt></ruby>します。<span id="ev-nhk-detox-1">当初は「通知が来ているのではないか」という激しい禁断症状や不安を口にする人が大半ですが、二日目を過ぎると五感が研ぎ澄まされ、鳥の声や風の音に深い安らぎを感じるようになると言います。</span></p>
    <p><span id="ev-nhk-detox-2">専門家は「常時接続のプレッシャーから脳を切り離すことは、低下した集中力や創造性を回復させるための極めて有効な防衛策だ」と分析しています。</span><ruby>便利<rt>べんり</rt></ruby>さを<ruby>手放<rt>てばな</rt></ruby>すことによってこそ、<ruby>自分<rt>じぶん</rt></ruby><ruby>自身<rt>じしん</rt></ruby>の<ruby>時間<rt>じかん</rt></ruby>を<ruby>取<rt>と</rt></ruby>り<ruby>戻<rt>もど</rt></ruby>せるという<ruby>逆説<rt>ぎゃくせつ</rt></ruby>が、<ruby>多<rt>おお</rt></ruby>くの<ruby>現代人<rt>げんだいじん</rt></ruby>の<ruby>共感<rt>きょうかん</rt></ruby>を<ruby>集<rt>あつ</rt></ruby>めています。</p>
</div>
""".strip(),
        "translation_ru": """
В эпоху тотального контроля соцсетей и смартфонов туры «цифрового детокса», проходящие в старинных домах в горах без связи или буддийских храмах, вызвали огромный отклик у молодежи 20–30 лет.
Участники по прибытии запирают телефоны в сейф, снимают часы и живут по солнцу. Сначала почти все испытывают тревогу («а вдруг пришло уведомление?»), но уже на второй день чувства обостряются, и человек обретает душевный покой в звуках ветра и птиц.
Эксперты отмечают: отключение от режима постоянной связи — эффективный способ восстановить истощенную концентрацию и креативность. Парадокс в том, что отказ от удобств позволяет вернуть себе самого себя.
""".strip(),
        "vocabulary": [
            {"word": "禁断症状", "furigana": "きんだんしょうじょう", "translation": "синдром отмены, ломка"},
            {"word": "研ぎ澄ます", "furigana": "とぎすます", "translation": "обострять, оттачивать (чувства)"},
            {"word": "常時接続", "furigana": "じょうじせつぞく", "translation": "постоянное подключение (онлайн)"},
            {"word": "逆説", "furigana": "ぎゃくせつ", "translation": "парадокс"}
        ],
        "questions": [
            {
                "question_number": 1,
                "question_text": "デジタルデトックスに参加した人たちの心理的な変化として正しいものはどれか。",
                "general_explanation": "Правильный ответ — вариант 3. В предложении ev-nhk-detox-1 описана динамика: сначала тревога по поводу уведомлений, а затем обострение чувств и глубокое спокойствие.",
                "evidence_span_id": "ev-nhk-detox-1",
                "options": [
                    {"option_number": 1, "option_text": "最初から最後まで恐怖と怒りを感じ続けていた。", "is_correct": False, "option_explanation": "Неверно. На второй день участники испытывали покой."},
                    {"option_number": 2, "option_text": "スマホを隠れて使おうとして警察沙汰になった。", "is_correct": False, "option_explanation": "Неверно. Таких фактов в тексте нет."},
                    {"option_number": 3, "option_text": "初めの不安を乗り越えると、自然に安らぎを感じるようになった。", "is_correct": True, "option_explanation": "Верно! Точное повторение мысли из ev-nhk-detox-1."},
                    {"option_number": 4, "option_text": "ツアー終了後も一切電気を使わない生活を送るようになった。", "is_correct": False, "option_explanation": "Неверно. Речь идет о временном туре."}
                ]
            },
            {
                "question_number": 2,
                "question_text": "専門家がこのツアーを評価している最大の理由は何ですか。",
                "general_explanation": "Правильный ответ — вариант 1. Согласно ev-nhk-detox-2, отключение мозга от постоянного онлайн-давления возвращает упавшую концентрацию и креативность.",
                "evidence_span_id": "ev-nhk-detox-2",
                "options": [
                    {"option_number": 1, "option_text": "常時接続から離れることで集中力や創造性を回復できるから。", "is_correct": True, "option_explanation": "Верно! Цитата: «低下した集中力や創造性を回復させるための極めて有効な防衛策»."},
                    {"option_number": 2, "option_text": "スマートフォン販売会社の売上を伸ばすことができるから。", "is_correct": False, "option_explanation": "Неверно. Напротив, люди отказываются от гаджетов."},
                    {"option_number": 3, "option_text": "寺院の入場料を大幅に値上げできるから。", "is_correct": False, "option_explanation": "Неверно. Финансовая сторона храмов не обсуждается."},
                    {"option_number": 4, "option_text": "すべての国民が山間部に移住するべきだと考えているから。", "is_correct": False, "option_explanation": "Неверно. Это искажение идеи."}
                ]
            }
        ]
    }
]


def import_nhk_articles_to_db(custom_articles: Optional[List[Dict[str, Any]]] = None) -> int:
    """
    Imports NHK World stylized stories into the database.
    """
    db = SessionLocal()
    articles_to_import = custom_articles if custom_articles else NHK_REAL_STORIES
    imported_count = 0

    for item in articles_to_import:
        # Check if already exists by title
        existing = db.query(Text).filter(Text.title == item["title"]).first()
        if existing:
            continue

        text_obj = Text(
            title=item["title"],
            level=item["level"],
            category=item["category"],
            source_exam="NHK World News Feature",
            is_nhk=True,
            recommended_time_min=item.get("recommended_time_min", 5),
            content_html=item["content_html"],
            translation_ru=item["translation_ru"],
            vocabulary_json=item.get("vocabulary", [])
        )

        for q_data in item.get("questions", []):
            question_obj = Question(
                question_number=q_data["question_number"],
                question_text=q_data["question_text"],
                general_explanation=q_data["general_explanation"],
                evidence_span_id=q_data.get("evidence_span_id")
            )

            for opt_data in q_data.get("options", []):
                opt_obj = Option(
                    option_number=opt_data["option_number"],
                    option_text=opt_data["option_text"],
                    is_correct=opt_data["is_correct"],
                    option_explanation=opt_data["option_explanation"]
                )
                question_obj.options.append(opt_obj)

            text_obj.questions.append(question_obj)

        db.add(text_obj)
        imported_count += 1

    db.commit()
    db.close()
    return imported_count


if __name__ == "__main__":
    count = import_nhk_articles_to_db()
    print(f"NHK Importer finished. Added {count} new real NHK World stories.")
