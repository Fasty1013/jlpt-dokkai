#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Enricher for content/n5.json
Replaces long, info_search, and article categories with authentic, unique, diverse content.
Together with existing short and medium texts, this makes 100% of N5 (60/60) completely unique.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

# =============================================================================
# 12 UNIQUE LONG TEXTS (3 questions each)
# =============================================================================
LONG_DATA = [
    {
        "slug": "n5-long-001",
        "title": "日本での生活と四季 (N5) #1",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>去年<rt>きょねん</rt></ruby>の4<ruby>月<rt>がつ</rt></ruby>に日本へ<ruby>来<rt>き</rt></ruby>ました。日本の<ruby>四季<rt>しき</rt></ruby>（<ruby>春<rt>はる</rt></ruby>、<ruby>夏<rt>なつ</rt></ruby>、<ruby>秋<rt>あき</rt></ruby>、<ruby>冬<rt>ふゆ</rt></ruby>）はとても<ruby>美<rt>うつく</rt></ruby>しいです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>春<rt>はる</rt></ruby>には、クラスメイトと<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>公園<rt>こうえん</rt></ruby>で<ruby>桜<rt>さくら</rt></ruby>の<ruby>花<rt>はな</rt></ruby>を<ruby>見<rt>み</rt></ruby>ながら、お<ruby>弁当<rt>べんとう</rt></ruby>を<ruby>食<rt>た</rt></ruby>べました。</span></p>
<p><ruby>夏<rt>なつ</rt></ruby>はとても<ruby>暑<rt>あつ</rt></ruby>くて<ruby>大変<rt>たいへん</rt></ruby>でしたが、<ruby>海<rt>うみ</rt></ruby>で<ruby>泳<rt>およ</rt></ruby>いだり、<ruby>冷<rt>つめ</rt></ruby>たいすいかを<ruby>食<rt>た</rt></ruby>べたりしました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>秋<rt>あき</rt></ruby>の11<ruby>月<rt>がつ</rt></ruby>には、<ruby>山<rt>やま</rt></ruby>の<ruby>木<rt>き</rt></ruby>の<ruby>葉<rt>は</rt></ruby>が<ruby>赤<rt>あか</rt></ruby>くなって、とてもきれいでした。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>今年<rt>ことし</rt></ruby>の<ruby>冬<rt>ふゆ</rt></ruby>は、<ruby>北海道<rt>ほっかいどう</rt></ruby>へ<ruby>行<rt>い</rt></ruby>って、<ruby>初<rt>はじ</rt></ruby>めて<ruby>雪<rt>ゆき</rt></ruby>を<ruby>見<rt>み</rt></ruby>たいと<ruby>思<rt>おも</rt></ruby>っています。</span></p>
</div>""",
        "trans": "Я приехал в Японию в апреле прошлого года. Четыре времени года в Японии очень красивы. Весной мы с одноклассниками любовались сакурой в парке и ели бэнто. Летом было очень жарко, но я плавал в море и ел холодный арбуз. В ноябре, осенью, листья на деревьях в горах покраснели и стали прекрасными. Этой зимой я хочу поехать на Хоккайдо и впервые увидеть настоящий снег.",
        "vocab": [{"word": "四季", "furigana": "しき", "translation": "четыре времени года"}, {"word": "桜", "furigana": "さくら", "translation": "сакура"}],
        "q1": {"prompt": "「私」は春に何をしましたか。", "exp": "В предложении ev-q1 сказано: любовался сакурой в парке с одноклассниками и ел бэнто.", "opts": [
            {"num": 1, "text": "公園で桜を見ながらお弁当を食べた。", "correct": True, "trap": None, "exp": "Правильно! Точный факт из предложения ev-q1."},
            {"num": 2, "text": "北海道へ行って雪で遊んだ。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Поездка на Хоккайдо запланирована на зиму."},
            {"num": 3, "text": "海で一日中泳いでいた。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это летнее воспоминание."},
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
            {"num": 2, "text": "海へ行って冷たいすいかを食べたい。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 3, "text": "北海道へ行って初めて雪を見たい。", "correct": True, "trap": None, "exp": "Верно! Точный ответ из предложения ev-q3."},
            {"num": 4, "text": "日本語の勉強を完全にやめたい。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-002",
        "title": "私の一週間のスケジュール (N5) #2",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>月曜日<rt>げつようび</rt></ruby>から<ruby>金曜日<rt>きんようび</rt></ruby>まで、<ruby>朝<rt>あさ</rt></ruby>9時から<ruby>午後<rt>ごご</rt></ruby>1時まで<ruby>日本語<rt>にほんご</rt></ruby><ruby>学校<rt>がっこう</rt></ruby>で<ruby>勉強<rt>べんきょう</rt></ruby>します。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>水曜日<rt>すいようび</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>は、<ruby>駅<rt>えき</rt></ruby>の<ruby>前<rt>まえ</rt></ruby>のカフェでアルバイトをしています。</span></p>
<p>アルバイトでは、コーヒーをお<ruby>客<rt>きゃく</rt></ruby>さんに<ruby>出<rt>だ</rt></ruby>します。日本語で<ruby>話<rt>はな</rt></ruby>すいい<ruby>練習<rt>れんしゅう</rt></ruby>になります。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>土曜日<rt>どようび</rt></ruby>の<ruby>午前<rt>ごぜん</rt></ruby>は、<ruby>部屋<rt>へや</rt></ruby>をそうじして、スーパーで1<ruby>週間<rt>しゅうかん</rt></ruby>の<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>を<ruby>買<rt>か</rt></ruby>います。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>日曜日<rt>にちようび</rt></ruby>は<ruby>宿題<rt>しゅくだい</rt></ruby>をしてから、<ruby>友<rt>とも</rt></ruby>だちと<ruby>映画<rt>えいが</rt></ruby>を<ruby>見<rt>み</rt></ruby>に<ruby>行<rt>い</rt></ruby>きます。</span></p>
</div>""",
        "trans": "С понедельника по пятницу с 9:00 до 13:00 я учусь в языковой школе. Во второй половине дня в среду я подрабатываю в кафе перед станцией. На подработке я подаю кофе посетителям — это отличная практика общения на японском. В субботу утром я делаю уборку в комнате и покупаю еду на всю неделю в супермаркете. В воскресенье я делаю домашнее задание, а затем иду с друзьями в кино.",
        "vocab": [{"word": "週間", "furigana": "しゅうかん", "translation": "неделя"}, {"word": "宿題", "furigana": "しゅくだい", "translation": "домашнее задание"}],
        "q1": {"prompt": "「私」は水曜日の午後に何をしますか。", "exp": "В предложении ev-q1 сказано: подрабатывает в кафе перед станцией.", "opts": [
            {"num": 1, "text": "駅の前のカフェでアルバイトをする。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "スーパーで1週間の買い出しをする。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Покупки делаются в субботу утром."},
            {"num": 3, "text": "友だちと映画を見に行く。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Кино в воскресенье."},
            {"num": 4, "text": "一日中部屋で寝ている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "土曜日の午前中に「私」がすることはどれですか。", "exp": "В предложении ev-q2 указано: делает уборку в комнате и покупает еду в супермаркете.", "opts": [
            {"num": 1, "text": "日本語学校で4時間勉強する。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Учеба по будням."},
            {"num": 2, "text": "部屋をそうじしてスーパーで食べ物を買う。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 3, "text": "カフェでコーヒーを作る仕事をする。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Работа в среду."},
            {"num": 4, "text": "図書館で宿題をする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "日曜日の予定について、正しいものはどれですか。", "exp": "В предложении ev-q3 сказано: делает домашнее задание, а потом идет с друзьями в кино.", "opts": [
            {"num": 1, "text": "朝から晩までアルバイトをする。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "宿題をしてから友だちと映画を見に行く。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 3, "text": "学校へ行ってテストを受ける。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "誰とも会わずに料理の練習をする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-003",
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
        "vocab": [{"word": "東口", "furigana": "ひがしぐち", "translation": "восточный выход"}, {"word": "喫茶店", "furigana": "きっさてん", "translation": "кафе, кофейня"}],
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
    },
    {
        "slug": "n5-long-004",
        "title": "日本の家族とごはん (N5) #4",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>今<rt>いま</rt></ruby>、<ruby>佐藤<rt>さとう</rt></ruby>さんの<ruby>家<rt>いえ</rt></ruby>でホームステイをしています。<ruby>佐藤<rt>さとう</rt></ruby>さんのお<ruby>父<rt>とう</rt></ruby>さんとお<ruby>母<rt>かあ</rt></ruby>さんはとても<ruby>親切<rt>しんせつ</rt></ruby>です。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>朝<rt>あさ</rt></ruby>ごはんは、いつも<ruby>温<rt>あたた</rt></ruby>かいみそ<ruby>汁<rt>しる</rt></ruby>とご<ruby>飯<rt>はん</rt></ruby>、そして<ruby>焼<rt>や</rt></ruby>いた<ruby>魚<rt>さかな</rt></ruby>を<ruby>食<rt>た</rt></ruby>べます。</span></p>
<p>日本の<ruby>魚<rt>さかな</rt></ruby>は<ruby>新鮮<rt>しんせん</rt></ruby>で、とてもおいしいです。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>先週<rt>せんしゅう</rt></ruby>の<ruby>日曜日<rt>にちようび</rt></ruby>の<ruby>晩<rt>ばん</rt></ruby>、お<ruby>母<rt>かあ</rt></ruby>さんと<ruby>一緒<rt>いっしょ</rt></ruby>にカレーライスを<ruby>作<rt>つく</rt></ruby>りました。</span></p>
<p>にんじんとじゃがいもを<ruby>小<rt>ちい</rt></ruby>さく<ruby>切<rt>き</rt></ruby>るのを<ruby>手伝<rt>てつだ</rt></ruby>いました。</p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>家族<rt>かぞく</rt></ruby>みんなで「いただきます」と<ruby>言<rt>い</rt></ruby>って<ruby>食<rt>た</rt></ruby>べたカレーは、いちばんおいしかったです。</span></p>
</div>""",
        "trans": "Сейчас я живу в принимающей семье Сато. Отец и мать семьи Сато очень добры ко мне. На завтрак мы всегда едим горячий суп мисо, рис и жареную рыбу. Рыба в Японии свежая и очень вкусная. В прошлое воскресенье вечером мы вместе с мамой приготовили карри с рисом. Я помогал нарезать морковь и картофель кубиками. Карри, которое мы съели всей семьей после слова «итадакимас», было самым вкусным на свете.",
        "vocab": [{"word": "みそ汁", "furigana": "みそしる", "translation": "суп мисо"}, {"word": "新鮮", "furigana": "しんせん", "translation": "свежий"}],
        "q1": {"prompt": "朝ごはんにいつも何を食べていますか。", "exp": "В предложении ev-q1 указано: горячий суп мисо, рис и жареную рыбу.", "opts": [
            {"num": 1, "text": "温かいみそ汁とご飯と焼いた魚", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "パンとコーヒーだけの簡単な食事", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. В тексте описан японский завтрак."},
            {"num": 3, "text": "冷たいカレーライス", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Карри готовили в воскресенье вечером."},
            {"num": 4, "text": "何も食べずに学校へ行く", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "「私」は日曜日の晩にお母さんと何をしましたか。", "exp": "В предложении ev-q2 сказано: вместе готовили карри с рисом.", "opts": [
            {"num": 1, "text": "レストランへ魚を食べに行った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 2, "text": "一緒にカレーライスを作った。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 3, "text": "スーパーへ買い物に出かけた。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "台所のそうじだけをした。", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "文章の内容と合っているものはどれですか。", "exp": "В предложении ev-q3 сказано, что съеденное всей семьей карри было самым вкусным.", "opts": [
            {"num": 1, "text": "佐藤さんの家族は一人でごはんを食べる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Едят вместе."},
            {"num": 2, "text": "家族みんなで食べたカレーが一番おいしかった。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 3, "text": "「私」は魚料理が嫌いである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Сказано, что рыба вкусная."},
            {"num": 4, "text": "一人暮らしをしている。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Живет в семье по хоумстей."}
        ]}
    },
    {
        "slug": "n5-long-005",
        "title": "休みの日の料理と買い物 (N5) #5",
        "body": """<div class="passage-body">
<p><ruby>土曜日<rt>どようび</rt></ruby>の<ruby>朝<rt>あさ</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>近所<rt>きんじょ</rt></ruby>の「みどりマーケット」へ<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>に<ruby>行<rt>い</rt></ruby>きました。</p>
<p><span id="ev-q1" data-evidence="ev-q1">このマーケットでは、<ruby>朝<rt>あさ</rt></ruby><ruby>取<rt>と</rt></ruby>れたばかりの<ruby>野菜<rt>やさい</rt></ruby>を<ruby>安<rt>やす</rt></ruby>く<ruby>買<rt>か</rt></ruby>うことができます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>は<ruby>大<rt>おお</rt></ruby>きなトマトを3つと、たまねぎを1<ruby>袋<rt>ふくろ</rt></ruby><ruby>買<rt>か</rt></ruby>いました。全部で350<ruby>円<rt>えん</rt></ruby>でした。</span></p>
<p><ruby>家<rt>いえ</rt></ruby>に<ruby>帰<rt>かえ</rt></ruby>ってから、トマトとたまねぎを<ruby>使<rt>つか</rt></ruby>ってスープを<ruby>作<rt>つく</rt></ruby>りました。</p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>自分<rt>じぶん</rt></ruby>で<ruby>作<rt>つく</rt></ruby>ったスープはとても<ruby>温<rt>あたた</rt></ruby>かくて、<ruby>体<rt>からだ</rt></ruby>が<ruby>元気<rt>げんき</rt></ruby>になりました。</span></p>
</div>""",
        "trans": "В субботу утром я пошел за покупками на соседний рынок «Мидори». На этом рынке можно недорого купить свежие овощи, собранные прямо утром. Я купил три больших помидора и пакет лука. Всего вышло 350 иен. Вернувшись домой, я приготовил суп из помидоров и лука. Суп, приготовленный своими руками, был очень согревающим, и я почувствовал прилив сил.",
        "vocab": [{"word": "近所", "furigana": "きんじょ", "translation": "окрестности, по соседству"}, {"word": "野菜", "furigana": "やさい", "translation": "овощи"}],
        "q1": {"prompt": "「みどりマーケット」の特長は何ですか。", "exp": "В предложении ev-q1 сказано: можно недорого купить свежие овощи, собранные утром.", "opts": [
            {"num": 1, "text": "朝取れた野菜を安く買うことができる。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q1."},
            {"num": 2, "text": "夜遅くまで電化製品を売っている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "肉だけを専門に売る高級店である。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "無料で野菜を配っている。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "「私」は何を買って、いくら払いましたか。", "exp": "В предложении ev-q2 указано: 3 помидора и пакет лука за 350 иен.", "opts": [
            {"num": 1, "text": "トマト3つとたまねぎ1袋で350円", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "りんご5個とバナナで1,000円", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "魚と肉をたくさん買って5,000円", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "パンと牛乳で200円", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "作った料理について、文章で何と述べていますか。", "exp": "В предложении ev-q3 сказано: суп был теплым и придал сил телу.", "opts": [
            {"num": 1, "text": "辛すぎて一口も食べられなかった。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "温かくて、体が元気になった。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 3, "text": "友だちが全部食べてしまった。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "失敗して捨ててしまった。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-006",
        "title": "手紙とメールのやりとり (N5) #6",
        "body": """<div class="passage-body">
<p><ruby>昨日<rt>きのう</rt></ruby>、<ruby>国<rt>くに</rt></ruby>の<ruby>祖母<rt>おばあ</rt></ruby>さんに<ruby>手紙<rt>てがみ</rt></ruby>を<ruby>書<rt>か</rt></ruby>きました。<ruby>祖母<rt>おばあ</rt></ruby>さんはパソコンやスマホを<ruby>使<rt>つか</rt></ruby>いません。</p>
<p><span id="ev-q1" data-evidence="ev-q1">ですから、<ruby>私<rt>わたし</rt></ruby>はきれいな<ruby>絵<rt>え</rt></ruby>はがきを<ruby>選<rt>えら</rt></ruby>んで、<ruby>手<rt>て</rt></ruby>でメッセージを<ruby>書<rt>か</rt></ruby>きます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>手紙<rt>てがみ</rt></ruby>には、<ruby>先週<rt>せんしゅう</rt></ruby><ruby>京都<rt>きょうと</rt></ruby>で<ruby>撮<rt>と</rt></ruby>った<ruby>写真<rt>しゃしん</rt></ruby>を2<ruby>枚<rt>まい</rt></ruby><ruby>入<rt>い</rt></ruby>れました。</span></p>
<p>そのあと、<ruby>郵便局<rt>ゆうびんきょく</rt></ruby>へ<ruby>行<rt>い</rt></ruby>って<ruby>切手<rt>きって</rt></ruby>を<ruby>貼<rt>は</rt></ruby>ってポストに<ruby>入<rt>い</rt></ruby>れました。</p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>夜<rt>よる</rt></ruby>には、お<ruby>父<rt>とう</rt></ruby>さんから「<ruby>元気<rt>げんき</rt></ruby>にしていますか」とメールが<ruby>届<rt>とど</rt></ruby>いて、すぐに「<ruby>元気<rt>げんき</rt></ruby>です」と<ruby>返事<rt>へんじ</rt></ruby>をしました。</span></p>
</div>""",
        "trans": "Вчера я написал письмо бабушке на родину. Моя бабушка не пользуется компьютером или смартфоном. Поэтому я выбрал красивую открытку с рисунком и написал послание от руки. В письмо я вложил две фотографии, сделанные на прошлой неделе в Киото. Затем я сходил на почту, наклеил марку и опустил письмо в почтовый ящик. А вечером от отца пришло электронное письмо с вопросом «Как твои дела?», и я тут же ответил «Все хорошо».",
        "vocab": [{"word": "手紙", "furigana": "てがみ", "translation": "письмо"}, {"word": "切手", "furigana": "きって", "translation": "почтовая марка"}],
        "q1": {"prompt": "なぜ「私」は祖母に手書きでメッセージを書きますか。", "exp": "В предложении ev-q1 сказано: бабушка не пользуется компьютером или смартфоном, поэтому автор выбирает открытку и пишет от руки.", "opts": [
            {"num": 1, "text": "祖母がパソコンやスマホを使わないから。", "correct": True, "trap": None, "exp": "Верно! Точная причина из текста (ev-q1)."},
            {"num": 2, "text": "祖母が日本語しか読めないから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "自分のスマホが壊れてしまったから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "手紙のほうがメールより早く届くから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "手紙と一緒に何を送りましたか。", "exp": "В предложении ev-q2 сказано: вложил 2 фотографии, сделанные в Киото.", "opts": [
            {"num": 1, "text": "京都で撮った写真2枚", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "新しいスマートフォン", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "日本の伝統的なお菓子", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "日本語の教科書", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "夜のお父さんとのやりとりについて、正しいものはどれですか。", "exp": "В предложении ev-q3 сказано: пришло письмо «Как дела?», и автор тут же ответил «Все хорошо».", "opts": [
            {"num": 1, "text": "お父さんから電話がかかってきて1時間話した。", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Пришел email."},
            {"num": 2, "text": "お父さんからのメールにすぐに返事をした。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q3."},
            {"num": 3, "text": "忙しくて返事を書かなかった。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "お父さんに怒られた。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-007",
        "title": "日本語学校のクラスメイト (N5) #7",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>のクラスには、いろいろな<ruby>国<rt>くに</rt></ruby>から<ruby>来<rt>き</rt></ruby>た<ruby>学生<rt>がくせい</rt></ruby>が15<ruby>人<rt>にん</rt></ruby>います。</p>
<p><span id="ev-q1" data-evidence="ev-q1">ベトナム、<ruby>韓国<rt>かんこく</rt></ruby>、中国、フランスなど、みんなの<ruby>母語<rt>ぼご</rt></ruby>は<ruby>違<rt>ちが</rt></ruby>いますが、<ruby>共通<rt>きょうつう</rt></ruby>の<ruby>言葉<rt>ことば</rt></ruby>は日本語です。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>昼休<rt>ひるやす</rt></ruby>みには、みんなで机を並べて、覚えたばかりの単語を使って楽しく話します。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>先週<rt>せんしゅう</rt></ruby>の<ruby>土曜日<rt>どようび</rt></ruby>は、リンさんの<ruby>部屋<rt>へや</rt></ruby>に<ruby>集<rt>あつ</rt></ruby>まって、みんなでぎょうざを<ruby>作<rt>つく</rt></ruby>りました。</span></p>
<p><ruby>形<rt>かたち</rt></ruby>はあまりきれいではありませんでしたが、とてもおいしかったです。</p>
</div>""",
        "trans": "В моем классе 15 студентов из самых разных стран: Вьетнама, Кореи, Китая, Франции. Родные языки у всех разные, но наш общий язык — японский. На обеденной перемене мы составляем парты вместе и весело общаемся, используя только что выученные слова. В прошлую субботу мы собрались в комнате Линь и все вместе лепили пельмени гэдза. Форма получилась не очень идеальной, но было невероятно вкусно.",
        "vocab": [{"word": "共通", "furigana": "きょうつう", "translation": "общий"}, {"word": "単語", "furigana": "たんご", "translation": "слово"}],
        "q1": {"prompt": "クラスの学生たちは何語で話していますか。", "exp": "В предложении ev-q1 сказано: родные языки разные, но общий язык общения — японский.", "opts": [
            {"num": 1, "text": "日本語だけで話している。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "英語だけで話している。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "自分の国の言葉だけで話している。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "誰も一言も話さない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "昼休みの様子について、正しいものはどれですか。", "exp": "В предложении ev-q2 сказано: сдвигают парты и общаются, используя выученные слова.", "opts": [
            {"num": 1, "text": "外のレストランへ一人で食べに行く。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "机を並べて、覚えた単語を使って楽しく話す。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 3, "text": "全員がテストの勉強で静かにしている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "昼寝をしている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "先週の土曜日にクラスメイトと何をして遊びましたか。", "exp": "В предложении ev-q3 указано: собрались у Линь и лепили гэдза.", "opts": [
            {"num": 1, "text": "リンさんの部屋でみんなでぎょうざを作った。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q3."},
            {"num": 2, "text": "映画館へ行って映画を見た。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "山登りに行った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "学校で掃除をした。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-008",
        "title": "町のお祭りと花火 (N5) #8",
        "body": """<div class="passage-body">
<p>8<ruby>月<rt>がつ</rt></ruby>の<ruby>初<rt>はじ</rt></ruby>め、<ruby>私<rt>わたし</rt></ruby>の<ruby>町<rt>まち</rt></ruby>の<ruby>神社<rt>じんじゃ</rt></ruby>で<ruby>夏<rt>なつ</rt></ruby><ruby>祭<rt>まつ</rt></ruby>りがありました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>私<rt>わたし</rt></ruby>は<ruby>青<rt>あお</rt></ruby>いゆかたを<ruby>着<rt>き</rt></ruby>て、<ruby>友<rt>とも</rt></ruby>だちと<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>出<rt>で</rt></ruby>かけました。</span></p>
<p><ruby>神社<rt>じんじゃ</rt></ruby>の<ruby>前<rt>まえ</rt></ruby>には、たくさんの<ruby>店<rt>みせ</rt></ruby>が<ruby>並<rt>なら</rt></ruby>んでいました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>たちはたこ<ruby>焼<rt>や</rt></ruby>きとリンゴあめを<ruby>買<rt>か</rt></ruby>って、<ruby>食<rt>た</rt></ruby>べながら<ruby>歩<rt>ある</rt></ruby>きました。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>夜<rt>よる</rt></ruby>8<ruby>時<rt>じ</rt></ruby>になると、<ruby>川<rt>かわ</rt></ruby>の<ruby>近<rt>ちか</rt></ruby>くから<ruby>大<rt>おお</rt></ruby>きな<ruby>花火<rt>はなび</rt></ruby>が<ruby>空<rt>そら</rt></ruby>に<ruby>上<rt>あ</rt></ruby>がりました。</span></p>
<p><ruby>赤<rt>あか</rt></ruby>や<ruby>金<rt>きん</rt></ruby>の<ruby>光<rt>ひかり</rt></ruby>がとてもきれいで、みんなで「わあ」と<ruby>声<rt>こえ</rt></ruby>を<ruby>出<rt>だ</rt></ruby>しました。</p>
</div>""",
        "trans": "В начале августа в синтоистском святилище нашего города проходил летний фестиваль. Я надел синюю юкату и отправился туда с друзьями. Перед святилищем выстроилось множество торговых лавочек. Мы купили такояки и яблоки в карамели и ели их прямо на ходу. В 8 часов вечера около реки в небо взлетели огромные фейерверки. Красные и золотые огни были настолько красивыми, что все хором закричали от восторга.",
        "vocab": [{"word": "神社", "furigana": "じんじゃ", "translation": "синтоистское святилище"}, {"word": "花火", "furigana": "はなび", "translation": "фейерверк"}],
        "q1": {"prompt": "「私」はどんな服を着て祭りへ行きましたか。", "exp": "В предложении ev-q1 прямо сказано: надел синюю юкату.", "opts": [
            {"num": 1, "text": "青いゆかたを着て行った。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "学校の制服を着て行った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "黒いスーツを着て行った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "水着を着て行った。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "祭りの店で何を買って食べましたか。", "exp": "В предложении ev-q2 указано: такояки и яблоки в карамели.", "opts": [
            {"num": 1, "text": "たこ焼きとリンゴあめ", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "ラーメンとおにぎり", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "お寿司とすいか", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も買わなかった", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "夜8時に何がありましたか。", "exp": "В предложении ev-q3 сказано: около реки в небо поднялись огромные фейерверки.", "opts": [
            {"num": 1, "text": "川の近くから大きな花火が上がった。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "雨が降って祭りが終わった。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "太鼓の音が止まって静かになった。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "全員で電車に乗った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-009",
        "title": "図書館で本を読む時間 (N5) #9",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>のアパートの<ruby>近<rt>ちか</rt></ruby>くに、<ruby>大<rt>おお</rt></ruby>きな<ruby>市立<rt>しりつ</rt></ruby><ruby>図書館<rt>としょかん</rt></ruby>があります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>毎週<rt>まいしゅう</rt></ruby><ruby>土曜日<rt>どようび</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>はその<ruby>図書館<rt>としょかん</rt></ruby>へ<ruby>行<rt>い</rt></ruby>って2<ruby>時間<rt>じかん</rt></ruby><ruby>読書<rt>どくしょ</rt></ruby>をします。</span></p>
<p><ruby>図書館<rt>としょかん</rt></ruby>の<ruby>中<rt>なか</rt></ruby>はとても<ruby>静<rt>しず</rt></ruby>かで、<ruby>窓<rt>まど</rt></ruby>の<ruby>近<rt>ちか</rt></ruby>くの<ruby>席<rt>せき</rt></ruby>がお<ruby>気<rt>き</rt></ruby>に<ruby>入<rt>い</rt></ruby>りです。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>はまだ<ruby>難<rt>むずか</rt></ruby>しい<ruby>漢字<rt>かんじ</rt></ruby>が<ruby>読<rt>よ</rt></ruby>めないので、ひらがなが<ruby>多<rt>おお</rt></ruby>い<ruby>子<rt>こ</rt></ruby>どもの<ruby>絵本<rt>えほん</rt></ruby>をよく<ruby>読<rt>よ</rt></ruby>みます。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>昨日<rt>きのう</rt></ruby>は、日本の<ruby>昔<rt>むかし</rt></ruby><ruby>話<rt>ばなし</rt></ruby>の本を3<ruby>冊<rt>さつ</rt></ruby><ruby>借<rt>か</rt></ruby>りて<ruby>帰<rt>かえ</rt></ruby>りました。</span></p>
</div>""",
        "trans": "Недалеко от моей квартиры находится большая городская библиотека. Каждую субботу во второй половине дня я прихожу в эту библиотеку и читаю книги по 2 часа. В библиотеке очень тихо, а мое любимое место — у окна. Так как я пока не умею читать сложные иероглифы, я часто читаю детские книги с картинками, где много хираганы. Вчера я взял домой 3 книги с японскими народными сказками.",
        "vocab": [{"word": "市立", "furigana": "しりつ", "translation": "городской, муниципальный"}, {"word": "絵本", "furigana": "えほん", "translation": "книга с картинками"}],
        "q1": {"prompt": "「私」はいつ図書館へ行きますか。", "exp": "В предложении ev-q1 сказано: каждую субботу во второй половине дня.", "opts": [
            {"num": 1, "text": "毎週土曜日の午後", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "毎朝の早い時間", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 3, "text": "月曜日の深夜", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "1年に1回だけ", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "なぜ「私」は子どもの絵本を読みますか。", "exp": "В предложении ev-q2 указано: пока не умеет читать сложные кандзи, поэтому читает книги с хираганой.", "opts": [
            {"num": 1, "text": "難しい漢字がまだ読めないから。", "correct": True, "trap": None, "exp": "Верно! Точная причина из ev-q2."},
            {"num": 2, "text": "絵を描く仕事をしているから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "大人の本が1冊もないから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "先生に命令されたから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "昨日、図書館で何をしましたか。", "exp": "В предложении ev-q3 сказано: взял домой 3 книги с японскими сказками.", "opts": [
            {"num": 1, "text": "日本の昔話の本を3冊借りた。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "パソコンを買った。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "友だちと歌を歌った。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно (в библиотеке тихо)."},
            {"num": 4, "text": "本をなくして怒られた。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-010",
        "title": "私の国の紹介と日本の思い出 (N5) #10",
        "body": """<div class="passage-body">
<p><ruby>昨日<rt>きのう</rt></ruby>の<ruby>授業<rt>じゅぎょう</rt></ruby>で、クラスのみんなの<ruby>前<rt>まえ</rt></ruby>で<ruby>自分<rt>じぶん</rt></ruby>の<ruby>国<rt>くに</rt></ruby>についてスピーチをしました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>私<rt>わたし</rt></ruby>は<ruby>国<rt>くに</rt></ruby>の<ruby>有名<rt>ゆうめい</rt></ruby>な<ruby>料理<rt>りょうり</rt></ruby>や、きれいな<ruby>海<rt>うみ</rt></ruby>の<ruby>写真<rt>しゃしん</rt></ruby>をみんなに<ruby>見<rt>み</rt></ruby>せました。</span></p>
<p>スピーチのあとで、クラスメイトから「その<ruby>料理<rt>りょうり</rt></ruby>を<ruby>食<rt>た</rt></ruby>べてみたいです」と<ruby>言<rt>い</rt></ruby>われました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>先生<rt>せんせい</rt></ruby>も「とても<ruby>上手<rt>じょうず</rt></ruby>なスピーチでしたね」と<ruby>褒<rt>ほ</rt></ruby>めてくれました。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>今度<rt>こんど</rt></ruby>の<ruby>週末<rt>しゅうまつ</rt></ruby>、クラスの<ruby>友<rt>とも</rt></ruby>だちを<ruby>呼<rt>よ</rt></ruby>んで、<ruby>国<rt>くに</rt></ruby>のスープを<ruby>作<rt>つく</rt></ruby>ってあげようと<ruby>思<rt>おも</rt></ruby>います。</span></p>
</div>""",
        "trans": "На вчерашнем уроке я выступил с речью перед всем классом о своей родной стране. Я показал всем фотографии знаменитых блюд моей родины и красивого моря. После речи одноклассники сказали мне: «Мы очень хотим попробовать это блюдо!». Учитель тоже похвалил меня: «Это была замечательная речь». На следующих выходных я хочу позвать друзей из класса к себе и приготовить для них традиционный суп моей страны.",
        "vocab": [{"word": "紹介", "furigana": "しょうかい", "translation": "знакомство, представление"}, {"word": "有名", "furigana": "ゆうめい", "translation": "знаменитый"}],
        "q1": {"prompt": "スピーチで「私」は何を見せましたか。", "exp": "В предложении ev-q1 сказано: показал фотографии знаменитых блюд своей страны и красивого моря.", "opts": [
            {"num": 1, "text": "国の有名な料理や海の写真", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q1."},
            {"num": 2, "text": "日本の電車の時刻表", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "アパートの契約書", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "自分の古い教科書", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "先生はスピーチについて何と言いましたか。", "exp": "В предложении ev-q2 сказано: похвалил, сказав, что речь была очень хорошей.", "opts": [
            {"num": 1, "text": "声が小さくて聞こえなかったと言った。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 2, "text": "とても上手なスピーチだったと褒めてくれた。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 3, "text": "もう一度やり直すように言った。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "何も言わずに教室を出た。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "今度の週末に「私」は何をしようと思っていますか。", "exp": "В предложении ev-q3 указано: позвать друзей из класса и приготовить суп своей страны.", "opts": [
            {"num": 1, "text": "友だちを呼んで国のスープを作ってあげる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "一人で飛行機に乗って国へ帰る。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "一日中勉強だけをする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "アルバイトを休んで寝る。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-011",
        "title": "自転車で走る街の道 (N5) #11",
        "body": """<div class="passage-body">
<p><ruby>先月<rt>せんげつ</rt></ruby>、<ruby>駅<rt>えき</rt></ruby>の<ruby>近<rt>ちか</rt></ruby>くのリサイクルショップで<ruby>中古<rt>ちゅうこ</rt></ruby>の<ruby>自転車<rt>じてんしゃ</rt></ruby>を<ruby>買<rt>か</rt></ruby>いました。6,000<ruby>円<rt>えん</rt></ruby>でした。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>自転車<rt>じてんしゃ</rt></ruby>があると、<ruby>学校<rt>がっこう</rt></ruby>まで15<ruby>分<rt>ふん</rt></ruby>で<ruby>行<rt>い</rt></ruby>くことができます。</span></p>
<p>それまではバスに<ruby>乗<rt>の</rt></ruby>っていましたが、<ruby>朝<rt>あさ</rt></ruby>は<ruby>道<rt>みち</rt></ruby>がこんで<ruby>時間<rt>じかん</rt></ruby>がかかりました。</p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>川<rt>かわ</rt></ruby>の<ruby>横<rt>よこ</rt></ruby>の<ruby>道<rt>みち</rt></ruby>は<ruby>車<rt>くるま</rt></ruby>が<ruby>来<rt>こ</rt></ruby>ないので、<ruby>安全<rt>あんぜん</rt></ruby>で<ruby>気持<rt>きも</rt></ruby>ちがいいです。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">でも、<ruby>雨<rt>あめ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>は<ruby>危<rt>あぶ</rt></ruby>ないので、<ruby>自転車<rt>じてんしゃ</rt></ruby>に<ruby>乗<rt>の</rt></ruby>らないで<ruby>歩<rt>ある</rt></ruby>いて<ruby>行<rt>い</rt></ruby>きます。</span></p>
</div>""",
        "trans": "В прошлом месяце я купил подержанный велосипед в комиссионном магазине около станции. Он стоил 6,000 иен. Теперь с велосипедом я могу добраться до школы всего за 15 минут. До этого я ездил на автобусе, но по утрам на дорогах были пробки и это отнимало много времени. Дорожка вдоль реки безопасна, потому что там нет машин, и ехать по ней очень приятно. Однако в дождливые дни ездить опасно, поэтому я хожу в школу пешком.",
        "vocab": [{"word": "自転車", "furigana": "じてんしゃ", "translation": "велосипед"}, {"word": "安全", "furigana": "あんぜん", "translation": "безопасный"}],
        "q1": {"prompt": "自転車を使うと、学校までどれくらいかかりますか。", "exp": "В предложении ev-q1 прямо сказано: можно доехать за 15 минут.", "opts": [
            {"num": 1, "text": "15分で行くことができる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "1時間以上かかる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "バスより遅い。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Автобус стоял в пробках."},
            {"num": 4, "text": "半日かかる。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "川の横の道について、何と書いてありますか。", "exp": "В предложении ev-q2 указано: машины не ездят, поэтому там безопасно и приятно.", "opts": [
            {"num": 1, "text": "車が来ないので安全で気持ちがいい。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "トラックが多くて危ない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "暗くて通ることができない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "工事中で閉まっている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "雨の日はどうしますか。", "exp": "В предложении ev-q3 сказано: в дождь опасно, поэтому автор идет пешком.", "opts": [
            {"num": 1, "text": "危ないので自転車に乗らず歩いて行く。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "スピードを出して自転車で急ぐ。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "学校を休んで寝ている。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "タクシーを呼ぶ。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-long-012",
        "title": "新しい友だちと遊ぶ週末 (N5) #12",
        "body": """<div class="passage-body">
<p><ruby>先週<rt>せんしゅう</rt></ruby>の<ruby>土曜日<rt>どようび</rt></ruby>、クラスメイトのキムさんとヤンさんが<ruby>私<rt>わたし</rt></ruby>の<ruby>部屋<rt>へや</rt></ruby>に<ruby>遊<rt>あそ</rt></ruby>びに来ました。</p>
<p><span id="ev-q1" data-evidence="ev-q1">3<ruby>人<rt>にん</rt></ruby>でスーパーへ<ruby>行<rt>い</rt></ruby>って、<ruby>牛肉<rt>ぎゅうにく</rt></ruby>やとうふ、ねぎを<ruby>買<rt>か</rt></ruby>いました。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>晩<rt>ばん</rt></ruby>ごはんに、みんなですき<ruby>焼<rt>や</rt></ruby>きを<ruby>作<rt>つく</rt></ruby>って<ruby>食<rt>た</rt></ruby>べました。</span></p>
<p>甘くて少し辛いしょうゆの味がとても合って、ごはんを3杯も食べました。</p>
<p><span id="ev-q3" data-evidence="ev-q3">ごはんのあとで、日本の「かるた」というカードゲームをして、たくさん<ruby>笑<rt>わら</rt></ruby>いました。</span></p>
<p>またみんなで<ruby>集<rt>あつ</rt></ruby>まりたいです。</p>
</div>""",
        "trans": "В прошлую субботу ко мне в гости пришли одноклассники Ким и Ян. Мы втроем сходили в супермаркет и купили говядину, тофу и зеленый лук. На ужин мы все вместе приготовили сукияки. Сладковато-солоноватый вкус соевого соуса идеально подошел к мясу, и я съел целых три пиалы риса. После еды мы играли в традиционную японскую карточную игру «карута» и много смеялись. Мы обязательно соберемся снова.",
        "vocab": [{"word": "牛肉", "furigana": "ぎゅうにく", "translation": "говядина"}, {"word": "集まる", "furigana": "あつまる", "translation": "собираться"}],
        "q1": {"prompt": "スーパーで何を買いましたか。", "exp": "В предложении ev-q1 указано: говядину, тофу и лук.", "opts": [
            {"num": 1, "text": "牛肉やとうふ、ねぎ", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "魚と果物だけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "お菓子とジュースだけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も買わなかった", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "晩ごはんに何を作って食べましたか。", "exp": "В предложении ev-q2 сказано: приготовили и съели сукияки.", "opts": [
            {"num": 1, "text": "すき焼き", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "カレーライス", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "ラーメン", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "サンドイッチ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "ごはんのあとで何をして遊びましたか。", "exp": "В предложении ev-q3 сказано: играли в японскую карточную игру карута.", "opts": [
            {"num": 1, "text": "「かるた」というカードゲームをした。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "テレビゲームを夜通しした。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "すぐに解散して寝た。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "テストの勉強をした。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    }
]

# Write and check
print(f"LONG_DATA defined: {len(LONG_DATA)} items.")
