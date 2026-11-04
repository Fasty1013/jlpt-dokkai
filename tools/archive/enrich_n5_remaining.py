#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enricher for N5 remaining categories: long, info_search, and article.
Replaces all duplicate boilerplate with authentic, unique, diverse content.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

# =============================================================================
# 12 UNIQUE N5 LONG TEXTS (3 questions each)
# =============================================================================
LONG_DATA = [
    {
        "title": "日本での生活と四季 (N5) #1",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>去年<rt>きょねん</rt></ruby>の4<ruby>月<rt>がつ</rt></ruby>に日本へ<ruby>来<rt>き</rt></ruby>ました。日本の<ruby>四季<rt>しき</rt></ruby>（<ruby>春<rt>はる</rt></ruby>、<ruby>夏<rt>なつ</rt></ruby>、<ruby>秋<rt>あき</rt></ruby>、<ruby>冬<rt>ふゆ</rt></ruby>）はとても<ruby>美<rt>うつく</rt></ruby>しいです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>春<rt>はる</rt></ruby>には、クラスメイトと<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>公園<rt>こうえん</rt></ruby>で<ruby>桜<rt>さくら</rt></ruby>の<ruby>花<rt>はな</rt></ruby>を<ruby>見<rt>み</rt></ruby>ながら、お<ruby>弁当<rt>べんとう</rt></ruby>を<ruby>食<rt>た</rt></ruby>べました。</span></p>
<p><ruby>夏<rt>なつ</rt></ruby>はとても<ruby>暑<rt>あつ</rt></ruby>くて<ruby>大変<rt>たいへん</rt></ruby>でしたが、<ruby>海<rt>うみ</rt></ruby>で<ruby>泳<rt>およ</rt></ruby>いだり、<ruby>冷<rt>つめ</rt></ruby>たいすいかを<ruby>食<rt>た</rt></ruby>べたりしました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>秋<rt>あき</rt></ruby>の11<ruby>月<rt>がつ</rt></ruby>には、<ruby>山<rt>やま</rt></ruby>の<ruby>木<rt>き</rt></ruby>の<ruby>葉<rt>は</rt></ruby>が<ruby>赤<rt>あか</rt></ruby>くなって、とてもきれいでした。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>今年<rt>ことし</rt></ruby>の<ruby>冬<rt>ふゆ</rt></ruby>は、<ruby>北海道<rt>ほっかいどう</rt></ruby>へ<ruby>行<rt>い</rt></ruby>って、<ruby>初<rt>はじ</rt></ruby>めて<ruby>雪<rt>ゆき</rt></ruby>を<ruby>見<rt>み</rt></ruby>たいと<ruby>思<rt>おも</rt></ruby>っています。</span></p>
</div>""",
        "trans": "Я приехал в Японию в апреле прошлого года. Четыре времени года в Японии очень красивы. Весной мы с одноклассниками любовались сакурой в парке и ели бэнто. Летом было очень жарко, но я плавал в море и ел холодный арбуз. В ноябре, осенью, листья на деревьях в горах покраснели и стали прекрасными. Этой зимой я хочу поехать на Хоккайдо и впервые увидеть настоящий снег.",
        "q1": {"prompt": "「私」は春に何をしましたか。", "exp": "В предложении ev-q1 сказано: любовался сакурой в парке с одноклассниками и ел бэнто.", "opts": [
            {"num": 1, "text": "公園で桜を見ながらお弁当を食べた。", "correct": True, "trap": None, "exp": "Правильно! Точный факт из предложения ev-q1."},
            {"num": 2, "text": "北海道へ行って雪で遊んだ。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Поехать на Хоккайдо автор планирует зимой."},
            {"num": 3, "text": "海で一日中泳いでいた。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. В море автор плавал летом."},
            {"num": 4, "text": "一人で部屋で寝ていた。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "秋の山の様子について、文章で何と書いてありますか。", "exp": "В предложении ev-q2 сказано, что в ноябре листья на деревьях в горах стали красными.", "opts": [
            {"num": 1, "text": "雪がたくさん降って寒かった。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Снег бывает зимой."},
            {"num": 2, "text": "木の葉が赤くなってとてもきれいだった。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 3, "text": "雨ばかり降って外へ出られなかった。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "暑すぎて桜の花が咲いた。", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "「私」は今年の冬に何をしたいと思っていますか。", "exp": "В предложении ev-q3 указано: поехать на Хоккайдо и впервые увидеть снег.", "opts": [
            {"num": 1, "text": "自分の国へすぐに帰りたい。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 2, "text": "海へ行って冷たいすいかを食べたい。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это летнее занятие."},
            {"num": 3, "text": "北海道へ行って初めて雪を見たい。", "correct": True, "trap": None, "exp": "Верно! Точный ответ из предложения ev-q3."},
            {"num": 4, "text": "日本語の勉強を完全にやめたい。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "title": "私の一週間のスケジュール (N5) #2",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>月曜日<rt>げつようび</rt></ruby>から<ruby>金曜日<rt>きんようび</rt></ruby>まで、<ruby>朝<rt>あさ</rt></ruby>9時から<ruby>午後<rt>ごご</rt></ruby>1時まで<ruby>日本語<rt>にほんご</rt></ruby><ruby>学校<rt>がっこう</rt></ruby>で<ruby>勉強<rt>べんきょう</rt></ruby>します。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>水曜日<rt>すいようび</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>は、<ruby>駅<rt>えき</rt></ruby>の<ruby>前<rt>まえ</rt></ruby>のカフェでアルバイトをしています。</span></p>
<p>アルバイトでは、コーヒーをお<ruby>客<rt>きゃく</rt></ruby>さんに<ruby>出<rt>だ</rt></ruby>します。日本語で<ruby>話<rt>はな</rt></ruby>すいい<ruby>練習<rt>れんしゅう</rt></ruby>になります。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>土曜日<rt>どようび</rt></ruby>の<ruby>午前<rt>ごぜん</rt></ruby>は、<ruby>部屋<rt>へや</rt></ruby>をそうじして、スーパーで1<ruby>週間<rt>しゅうかん</rt></ruby>の<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>を<ruby>買<rt>か</rt></ruby>います。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>日曜日<rt>にちようび</rt></ruby>は<ruby>宿題<rt>しゅくだい</rt></ruby>をしてから、<ruby>友<rt>とも</rt></ruby>だちと<ruby>映画<rt>えいが</rt></ruby>を<ruby>見<rt>み</rt></ruby>に<ruby>行<rt>い</rt></ruby>きます。</span></p>
</div>""",
        "trans": "С понедельника по пятницу с 9:00 до 13:00 я учусь в языковой школе. Во второй половине дня в среду я подрабатываю в кафе перед станцией. На подработке я подаю кофе посетителям — это отличная практика общения на японском. В субботу утром я делаю уборку в комнате и покупаю еду на всю неделю в супермаркете. В воскресенье я делаю домашнее задание, а затем иду с друзьями в кино.",
        "q1": {"prompt": "「私」は水曜日の午後に何をしますか。", "exp": "В предложении ev-q1 прямо сказано: подрабатывает в кафе перед станцией.", "opts": [
            {"num": 1, "text": "駅の前のカフェでアルバイトをする。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "スーパーで1週間の買い出しをする。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Покупки делаются в субботу утром."},
            {"num": 3, "text": "友だちと映画を見に行く。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Кино планируется на воскресенье."},
            {"num": 4, "text": "一日中部屋で寝ている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "土曜日の午前中に「私」がすることはどれですか。", "exp": "В предложении ev-q2 указано: делает уборку в комнате и покупает еду в супермаркете.", "opts": [
            {"num": 1, "text": "日本語学校で4時間勉強する。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Школа с понедельника по пятницу."},
            {"num": 2, "text": "部屋をそうじしてスーパーで食べ物を買う。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 3, "text": "カフェでコーヒーを作る仕事をする。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Работа в кафе в среду."},
            {"num": 4, "text": "図書館で宿題をする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "日曜日の予定について、正しいものはどれですか。", "exp": "В предложении ev-q3 сказано: делает домашнее задание, а потом идет с друзьями в кино.", "opts": [
            {"num": 1, "text": "朝から晩までアルバイトをする。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "宿題をしてから友だちと映画を見に行く。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 3, "text": "学校へ行ってテストを受ける。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. В воскресенье школа закрыта."},
            {"num": 4, "text": "誰とも会わずに料理の練習をする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "title": "電車に乗って出かける日 (N5) #3",
        "body": """<div class="passage-body">
<p><ruby>先週<rt>せんしゅう</rt></ruby>の<ruby>日曜日<rt>にちようび</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>電車<rt>でんしゃ</rt></ruby>に<ruby>乗<rt>の</rt></ruby>って<ruby>新宿<rt>しんじゅく</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>駅<rt>えき</rt></ruby>の<ruby>東口<rt>ひがしぐち</rt></ruby>で、<ruby>友<rt>とも</rt></ruby>だちの<ruby>田中<rt>たなか</rt></ruby>さんと10<ruby>時<rt>じ</rt></ruby>に<ruby>会<rt>あ</rt></ruby>いました。</span></p>
<p>それから、<ruby>二人<rt>ふたり</rt></ruby>で<ruby>大<rt>おお</rt></ruby>きな<ruby>本屋<rt>ほんや</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>は<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>漢字<rt>かんじ</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>と、<ruby>日本<rt>にほん</rt></ruby><ruby>料理<rt>りょうり</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>を2<ruby>冊<rt>さつ</rt></ruby><ruby>買<rt>か</rt></ruby>いました。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>午後<rt>ごご</rt></ruby>は<ruby>静<rt>しず</rt></ruby>かな<ruby>喫茶店<rt>きっさてん</rt></ruby>で、おいしい<ruby>緑茶<rt>りょくちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みながらたくさん<ruby>話<rt>はな</rt></ruby>しました。</span></p>
<p>とても<ruby>楽<rt>たの</rt></ruby>しい<ruby>一日<rt>いちにち</rt></ruby>でした。</p>
</div>""",
        "trans": "В прошлое воскресенье я поехал на поезде в Синдзюку. У восточного выхода со станции я встретился с другом Танакой в 10:00. Затем мы вдвоем пошли в большой книжный магазин. Я купил две книги: пособие по кандзи и книгу о японской кухне. Во второй половине дня мы сидели в тихом кафе, пили вкусный зеленый чай и много разговаривали. Это был очень приятный день.",
        "q1": {"prompt": "「私」は田中さんとどこで何時に会いましたか。", "exp": "В предложении ev-q1 прямо сказано: у восточного выхода со станции в 10 часов.", "opts": [
            {"num": 1, "text": "駅の東口で10時に会った。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "本屋の中で午後2時に会った。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Встреча была у восточного выхода в 10:00."},
            {"num": 3, "text": "喫茶店で夜8時に会った。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "学校の門の前で9時に会った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "本屋で「私」は何を買いましたか。", "exp": "В предложении ev-q2 сказано: купил 2 книги — по кандзи и по японской кулинарии.", "opts": [
            {"num": 1, "text": "英語の辞書とノートを3冊買った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 2, "text": "漢字の本と日本料理の本を2冊買った。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 3, "text": "電車の切符とお茶の葉を買った。", "correct": False, "trap": "misinterpretation", "exp": "Неверно."},
            {"num": 4, "text": "何も買わずにすぐに出た。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "午後の二人の行動について、正しいものはどれですか。", "exp": "В предложении ev-q3 сказано: в тихом кафе пили зеленый чай и беседовали.", "opts": [
            {"num": 1, "text": "電車に乗ってすぐに家に帰った。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "静かな喫茶店で緑茶を飲みながら話した。", "correct": True, "trap": None, "exp": "Верно! Точный ответ из предложения ev-q3."},
            {"num": 3, "text": "レストランで夜遅くまでお酒を飲んだ。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "公園で運動をした。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    }
]

# Write a small script to verify syntax and then append remaining items
print(f"Loaded {len(LONG_DATA)} long items defined so far.")

