#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enricher for N5 articles (12 items, 3 questions each).
Defines 100% unique authentic articles, questions, options, translations, and vocabulary.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

ARTICLE_DATA = [
    {
        "slug": "n5-article-001",
        "title": "日本のコンビニのべんりなサービス (N5) #1",
        "body": """<div class="passage-body">
<p>日本のコンビニは、<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>を<ruby>買<rt>か</rt></ruby>うだけでなく、いろいろなサービスがあります。</p>
<p><span id="ev-q1" data-evidence="ev-q1">ほとんどのコンビニが24<ruby>時間<rt>じかん</rt></ruby><ruby>開<rt>あ</rt></ruby>いていて、<ruby>夜<rt>よる</rt></ruby><ruby>遅<rt>おそ</rt></ruby>くでも<ruby>安心<rt>あんしん</rt></ruby>して<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>ができます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">お<ruby>金<rt>かね</rt></ruby>をATMで<ruby>出<rt>だ</rt></ruby>したり、<ruby>電気<rt>でんき</rt></ruby>や<ruby>水道<rt>すいどう</rt></ruby>の<ruby>料金<rt>りょうきん</rt></ruby>をレジで<ruby>払<rt>はら</rt></ruby>ったりすることもできます。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>冬<rt>ふゆ</rt></ruby>には、レジの<ruby>横<rt>よこ</rt></ruby>で<ruby>温<rt>あたた</rt></ruby>かいおでんや<ruby>肉<rt>にく</rt></ruby>まんを<ruby>売<rt>う</rt></ruby>っていて、とても<ruby>人気<rt>にんき</rt></ruby>があります。</span></p>
<p>コンビニは、私たちの生活になくてはならない場所です。</p>
</div>""",
        "trans": "Японские комбини (круглосуточные магазины) предназначены не только для покупки еды — они предлагают множество полезных услуг. Почти все комбини работают 24 часа в сутки, поэтому за покупками можно спокойно зайти даже поздней ночью. В них можно снять наличные в банкомате или оплатить коммунальные счета за свет и воду прямо на кассе. Зимой рядом с кассой продают горячий одэн и мясные пирожки никуман, которые пользуются огромной популярностью. Комбини — неотъемлемая часть нашей жизни.",
        "vocab": [{"word": "料金", "furigana": "りょうきん", "translation": "плата, тариф"}, {"word": "安心", "furigana": "あんしん", "translation": "спокойствие, душевный комфорт"}],
        "q1": {"prompt": "コンビニの営業時間について何と書いてありますか。", "exp": "В предложении ev-q1 указано: почти все магазины открыты 24 часа.", "opts": [
            {"num": 1, "text": "ほとんどの店が24時間開いている。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "夜8時には全部閉まる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "朝の3時間しか開いていない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "土曜日と日曜日だけ開いている。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "コンビニのレジでできることは何ですか。", "exp": "В предложении ev-q2 сказано: можно оплатить счета за электричество и воду.", "opts": [
            {"num": 1, "text": "電気や水道の料金を払うこと", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "新しい家を買う契約をすること", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "飛行機のパイロットになる試験を受けること", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "パスポートを作ること", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "冬のコンビニで人気があるものは何ですか。", "exp": "В предложении ev-q3 сказано: теплый одэн и никуман (мясные булочки).", "opts": [
            {"num": 1, "text": "温かいおでんや肉まん", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "冷たいかき氷やすいか", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это летняя еда."},
            {"num": 3, "text": "水着やサンダル", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "何も売っていない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-002",
        "title": "古いお寺と新しい建物 (N5) #2",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>の<ruby>町<rt>まち</rt></ruby>を<ruby>歩<rt>ある</rt></ruby>くと、<ruby>歴史<rt>れきし</rt></ruby>のある<ruby>古<rt>ふる</rt></ruby>いお<ruby>寺<rt>てら</rt></ruby>と、<ruby>高<rt>たか</rt></ruby>いビルが<ruby>並<rt>なら</rt></ruby>んでいるのが<ruby>見<rt>み</rt></ruby>えます。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>特<rt>とく</rt></ruby>に<ruby>京都<rt>きょうと</rt></ruby>や<ruby>奈良<rt>なら</rt></ruby>には、1,000<ruby>年<rt>ねん</rt></ruby><ruby>以上<rt>いじょう</rt></ruby><ruby>前<rt>まえ</rt></ruby>に<ruby>木<rt>き</rt></ruby>で<ruby>作<rt>つく</rt></ruby>られた<ruby>有名<rt>ゆうめい</rt></ruby>なお<ruby>寺<rt>てら</rt></ruby>がたくさんあります。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">お<ruby>寺<rt>てら</rt></ruby>の<ruby>庭<rt>にわ</rt></ruby>には<ruby>緑<rt>みどり</rt></ruby>の<ruby>木<rt>き</rt></ruby>や<ruby>池<rt>いけ</rt></ruby>があって、とても<ruby>静<rt>しず</rt></ruby>かで<ruby>心<rt>こころ</rt></ruby>が<ruby>落<rt>お</rt></ruby>ち<ruby>着<rt>つ</rt></ruby>きます。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">そのすぐ<ruby>近<rt>ちか</rt></ruby>くにガラスの<ruby>新<rt>あたら</rt></ruby>しいビルが<ruby>立<rt>た</rt></ruby>っていて、<ruby>外国<rt>がいこく</rt></ruby>から<ruby>来<rt>き</rt></ruby>た<ruby>観光客<rt>かんこうきゃく</rt></ruby>はみんな<ruby>驚<rt>おどろ</rt></ruby>きます。</span></p>
<p><ruby>古<rt>ふる</rt></ruby>いものと<ruby>新<rt>あたら</rt></ruby>しいものが<ruby>一緒<rt>いっしょ</rt></ruby>にあるのが、日本の<ruby>魅力<rt>みりょく</rt></ruby>です。</p>
</div>""",
        "trans": "Гуляя по японским городам, можно увидеть, как исторические старинные храмы соседствуют с высокими небоскребами. Особенно в Киото и Наре сохранилось множество знаменитых храмов, построенных из дерева более 1,000 лет назад. В садах при храмах есть зеленая листва и пруды, там очень тихо и на душе становится спокойно. А совсем рядом стоят современные стеклянные здания, и туристы из-за рубежа всегда этому удивляются. Сосуществование старины и современности — главное очарование Японии.",
        "vocab": [{"word": "歴史", "furigana": "れきし", "translation": "история"}, {"word": "魅力", "furigana": "みりょく", "translation": "очарование, привлекательность"}],
        "q1": {"prompt": "京都や奈良のお寺について、何と書いてありますか。", "exp": "В предложении ev-q1 сказано: построено из дерева более 1,000 лет назад.", "opts": [
            {"num": 1, "text": "1,000年以上前に木で作られた有名なお寺が多い。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "去年コンクリートで作られたばかりである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "お寺は全部壊れて今は何もない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "誰も入れない秘密の場所である。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "お寺の庭に入るとどう感じますか。", "exp": "В предложении ev-q2 указано: очень тихо и на душе спокойно.", "opts": [
            {"num": 1, "text": "とても静かで心が落ち着く。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "車の音がうるさくて頭が痛くなる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно (в саду тихо)."},
            {"num": 3, "text": "暗くて怖くて逃げたくなる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "何も感じない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "外国からの観光客は何に驚きますか。", "exp": "В предложении ev-q3 сказано: удивляются тому, что совсем рядом с древними храмами стоят современные стеклянные здания.", "opts": [
            {"num": 1, "text": "古いお寺のすぐ近くに新しいビルが立っていること。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "日本人が誰も日本語を話さないこと。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "電車が1日中動いていないこと。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "食べ物が何もないこと。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-003",
        "title": "日本のゴミの分別ルール (N5) #3",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>に<ruby>住<rt>す</rt></ruby>むとき、ゴミの<ruby>出<rt>だ</rt></ruby>し<ruby>方<rt>かた</rt></ruby>のルールを<ruby>覚<rt>おぼ</rt></ruby>えることがとても<ruby>大切<rt>たいせつ</rt></ruby>です。</p>
<p><span id="ev-q1" data-evidence="ev-q1">ゴミは「もえるゴミ」「もえないゴミ」「ペットボトルやかん」などに<ruby>分<rt>わ</rt></ruby>けます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>曜日<rt>ようび</rt></ruby>によって<ruby>出<rt>だ</rt></ruby>すゴミの<ruby>種類<rt>しゅるい</rt></ruby>が<ruby>決<rt>き</rt></ruby>まっていて、<ruby>朝<rt>あさ</rt></ruby>8<ruby>時<rt>じ</rt></ruby>までに<ruby>指定<rt>してい</rt></ruby>の<ruby>場所<rt>ばしょ</rt></ruby>へ<ruby>持<rt>も</rt></ruby>って<ruby>行<rt>い</rt></ruby>きます。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">ルールを<ruby>守<rt>まも</rt></ruby>ることで、<ruby>町<rt>まち</rt></ruby>がきれいに<ruby>保<rt>たも</rt></ruby>たれ、リサイクルもできます。</span></p>
<p><ruby>初<rt>はじ</rt></ruby>めは<ruby>少<rt>すこ</rt></ruby>し<ruby>難<rt>むずか</rt></ruby>しいですが、すぐに<ruby>慣<rt>な</rt></ruby>れることができます。</p>
</div>""",
        "trans": "Когда вы живете в Японии, очень важно выучить правила сортировки мусора. Мусор разделяют на «сгораемый», «несгораемый», «пластиковые бутылки и жестяные банки» и другие категории. Для каждого дня недели определен свой тип мусора, и выносить его на назначенное место нужно до 8:00 утра. Соблюдение этих правил помогает содержать город в чистоте и позволяет перерабатывать отходы. Поначалу это кажется сложным, но к этому быстро привыкаешь.",
        "vocab": [{"word": "分別", "furigana": "ぶんべつ", "translation": "сортировка (мусора)"}, {"word": "指定", "furigana": "してい", "translation": "назначенный, указанный"}],
        "q1": {"prompt": "日本のゴミはどのように出さなければなりませんか。", "exp": "В предложении ev-q1 сказано: разделять на сгораемый, несгораемый, пластиковые бутылки и банки.", "opts": [
            {"num": 1, "text": "もえるゴミやペットボトルなどに分けて出す。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "全部を1つの大きな袋に混ぜて捨てる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Сортировка обязательна."},
            {"num": 3, "text": "川にそのまま投げ込む。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "部屋にためておいて何年も捨てない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "ゴミを出す時間について、何と書いてありますか。", "exp": "В предложении ev-q2 сказано: выносить до 8:00 утра на указанное место.", "opts": [
            {"num": 1, "text": "決められた曜日の朝8時までに指定の場所へ出す。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "夜中の12時以降に出す。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 3, "text": "何時でも好きなときに出してよい。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "1か月に1回だけ昼に出す。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "ゴミの分別ルールを守ると、どんな良いことがありますか。", "exp": "В предложении ev-q3 указано: город остается чистым и работает переработка (ресайкл).", "opts": [
            {"num": 1, "text": "町がきれいに保たれ、リサイクルができる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "お金が毎月たくさんもらえる。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "電車の運賃がタダになる。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "特別なメリットは何もない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    }
]

print(f"ARTICLE_DATA sample defined: {len(ARTICLE_DATA)} items.")

