#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full definition of 12 unique authentic N5 articles.
"""

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
        "trans": "Японские комбини предназначены не только для покупки еды — они предлагают множество полезных услуг. Почти все комбини работают 24 часа в сутки, поэтому за покупками можно спокойно зайти даже поздней ночью. В них можно снять наличные в банкомате или оплатить коммунальные счета за свет и воду прямо на кассе. Зимой рядом с кассой продают горячий одэн и мясные пирожки никуман, которые пользуются огромной популярностью. Комбини — неотъемлемая часть нашей жизни.",
        "vocab": [{"word": "料金", "furigana": "りょうきん", "translation": "плата, тариф"}, {"word": "安心", "furigana": "あんしん", "translation": "спокойствие"}],
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
            {"num": 2, "text": "冷たいかき氷やすいか", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
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
        "vocab": [{"word": "歴史", "furigana": "れきし", "translation": "история"}, {"word": "魅力", "furigana": "みりょく", "translation": "очарование"}],
        "q1": {"prompt": "京都や奈良のお寺について、何と書いてありますか。", "exp": "В предложении ev-q1 сказано: построено из дерева более 1,000 лет назад.", "opts": [
            {"num": 1, "text": "1,000年以上前に木で作られた有名なお寺が多い。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "去年コンクリートで作られたばかりである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "お寺は全部壊れて今は何もない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "誰も入れない秘密の場所である。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "お寺の庭に入るとどう感じますか。", "exp": "В предложении ev-q2 указано: очень тихо и на душе спокойно.", "opts": [
            {"num": 1, "text": "とても静かで心が落ち着く。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "車の音がうるさくて頭が痛くなる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "暗くて怖くて逃げたくなる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "何も感じない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "外国からの観光客は何に驚きますか。", "exp": "В предложении ev-q3 сказано: удивляются тому, что рядом стоят новые современные здания.", "opts": [
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
        "vocab": [{"word": "分別", "furigana": "ぶんべつ", "translation": "сортировка"}, {"word": "指定", "furigana": "してい", "translation": "назначенный"}],
        "q1": {"prompt": "日本のゴミはどのように出さなければなりませんか。", "exp": "В предложении ev-q1 сказано: разделять на сгораемый, несгораемый, пластиковые бутылки и банки.", "opts": [
            {"num": 1, "text": "もえるゴミやペットボトルなどに分けて出す。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "全部を1つの大きな袋に混ぜて捨てる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
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
    },
    {
        "slug": "n5-article-004",
        "title": "春の桜と花見の文化 (N5) #4",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>では、3<ruby>月<rt>がつ</rt></ruby>の<ruby>終<rt>お</rt></ruby>わりから4<ruby>月<rt>がつ</rt></ruby>にかけて、ピンクの<ruby>桜<rt>さくら</rt></ruby>の<ruby>花<rt>はな</rt></ruby>が<ruby>咲<rt>さ</rt></ruby>きます。</p>
<p><span id="ev-q1" data-evidence="ev-q1">この<ruby>時期<rt>じき</rt></ruby>になると、<ruby>家族<rt>かぞく</rt></ruby>や<ruby>会社<rt>かいしゃ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>たちが<ruby>公園<rt>こうえん</rt></ruby>に<ruby>集<rt>あつ</rt></ruby>まって、「お<ruby>花見<rt>はなみ</rt></ruby>」をします。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>桜<rt>さくら</rt></ruby>の<ruby>木<rt>き</rt></ruby>の<ruby>下<rt>した</rt></ruby>にシートを敷いて、お<ruby>弁当<rt>べんとう</rt></ruby>やお<ruby>菓子<rt>かし</rt></ruby>を<ruby>食<rt>た</rt></ruby>べながら<ruby>楽<rt>たの</rt></ruby>しく<ruby>話<rt>はな</rt></ruby>します。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">また、4<ruby>月<rt>がつ</rt></ruby>は<ruby>学校<rt>がっこう</rt></ruby>の<ruby>入学式<rt>にゅうがくしき</rt></ruby>や<ruby>会社<rt>かいしゃ</rt></ruby>の<ruby>入社式<rt>にゅうしゃしき</rt></ruby>があり、<ruby>桜<rt>さくら</rt></ruby>は「<ruby>新<rt>あたら</rt></ruby>しいスタート」のシンボルです。</span></p>
<p><ruby>桜<rt>さくら</rt></ruby>の<ruby>花<rt>はな</rt></ruby>は1<ruby>週間<rt>しゅうかん</rt></ruby>ほどで<ruby>散<rt>ち</rt></ruby>ってしまいますが、だからこそとても<ruby>美<rt>うつく</rt></ruby>しいと<ruby>感<rt>かん</rt></ruby>じられます。</p>
</div>""",
        "trans": "В Японии с конца марта по апрель расцветает розовая сакура. В эту пору семьи и коллеги собираются в парках на «ханами» — любование цветами. Под деревьями сакуры расстилают коврики, едят бэнто и сладости и весело общаются. Кроме того, в апреле проходят церемонии поступления в школы и начала работы в компаниях, поэтому сакура — символ нового старта. Лепестки опадают примерно через неделю, но именно поэтому они воспринимаются столь прекрасными.",
        "vocab": [{"word": "花見", "furigana": "はなみ", "translation": "любование сакурой"}, {"word": "入学式", "furigana": "にゅうがくしき", "translation": "церемония поступления в школу"}],
        "q1": {"prompt": "お花見では人々は何をしますか。", "exp": "В предложении ev-q2 указано: расстилают коврики под сакурой, едят бэнто и сладости и общаются.", "opts": [
            {"num": 1, "text": "桜の下でシートを敷いて、お弁当を食べて楽しく話す。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "木に登って桜の枝を全部折る。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "プールで泳ぐ。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "部屋に閉じこもってテレビを見る。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "4月と桜の関係について、文章で何と述べていますか。", "exp": "В предложении ev-q3 сказано: в апреле проходят церемонии поступления, сакура — символ нового старта.", "opts": [
            {"num": 1, "text": "入学式などがあり、新しいスタートのシンボルである。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q3."},
            {"num": 2, "text": "学校が全部休みになる悲しい時期である。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "全員が外国へ引っ越す月である。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "冬眠を始める季節である。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "桜の花が特に美しいと感じられる理由は何ですか。", "exp": "В заключении сказано: лепестки опадают примерно через неделю, мимолетность делает их особенно красивыми.", "opts": [
            {"num": 1, "text": "1週間ほどで散ってしまう短い美しさがあるから。", "correct": True, "trap": None, "exp": "Верно! Автор подчеркивает ценность недолговечности сакуры."},
            {"num": 2, "text": "一年中ずっと咲き続けるから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "値段がとても高いから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "食べると甘い味がするから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-005",
        "title": "夏休みの祭りとおどり (N5) #5",
        "body": """<div class="passage-body">
<p>日本の<ruby>夏<rt>なつ</rt></ruby>には、いろいろな<ruby>町<rt>まち</rt></ruby>で「<ruby>盆踊<rt>ぼんおど</rt></ruby>り」の<ruby>祭<rt>まつ</rt></ruby>りが<ruby>開<rt>ひら</rt></ruby>かれます。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>広場<rt>ひろば</rt></ruby>の<ruby>真<rt>ま</rt></ruby>ん<ruby>中<rt>なか</rt></ruby>に「やぐら」という<ruby>高<rt>たか</rt></ruby>い<ruby>台<rt>だい</rt></ruby>が<ruby>立<rt>た</rt></ruby>てられ、その<ruby>上<rt>うえ</rt></ruby>で<ruby>太鼓<rt>たいこ</rt></ruby>をたたきます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>人々<rt>ひとびと</rt></ruby>はやぐらの<ruby>周<rt>まわ</rt></ruby>りを<ruby>大<rt>おお</rt></ruby>きな<ruby>輪<rt>わ</rt></ruby>になって、<ruby>音楽<rt>おんがく</rt></ruby>に<ruby>合<rt>あ</rt></ruby>わせて<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>踊<rt>おど</rt></ruby>ります。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>踊<rt>おど</rt></ruby>りを知らない人や<ruby>外国人<rt>がいこくじん</rt></ruby>でも、<ruby>自由<rt>じゆう</rt></ruby>に<ruby>輪<rt>わ</rt></ruby>に<ruby>入<rt>はい</rt></ruby>って<ruby>楽<rt>たの</rt></ruby>しむことができます。</span></p>
<p><ruby>夜<rt>よる</rt></ruby>風に吹かれながら踊ると、夏の暑さを忘れることができます。</p>
</div>""",
        "trans": "Летом в самых разных уголках Японии проводятся фестивали танцев «бон-одори». В центре площади устанавливают высокий деревянный помост «ягура», на котором бьют в барабаны тайко. Люди выстраиваются в большой хоровод вокруг помоста и танцуют под традиционную музыку. Даже те, кто не знает движений, и иностранные гости могут свободно присоединиться к хороводу и веселиться. Танцуя под ночным ветерком, забываешь о дневной летней жаре.",
        "vocab": [{"word": "盆踊り", "furigana": "ぼんおどり", "translation": "танец бон-одори"}, {"word": "太鼓", "furigana": "たいこ", "translation": "барабан тайко"}],
        "q1": {"prompt": "広場の真ん中にある「やぐら」の上で何をしますか。", "exp": "В предложении ev-q1 сказано: на помосте ягура бьют в барабаны тайко.", "opts": [
            {"num": 1, "text": "太鼓をたたく。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "火を燃やす。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "寝る。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "映画を上映する。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "人々はどのように踊りますか。", "exp": "В предложении ev-q2 указано: встают в большой круг вокруг ягуры и танцуют под музыку.", "opts": [
            {"num": 1, "text": "やぐらの周りを大きな輪になって一緒に踊る。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "一人ずつ順番に部屋に入って踊る。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "全員が走って逃げる。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "座って動かない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "踊りを知らない人や外国人はどうできますか。", "exp": "В предложении ev-q3 сказано: могут свободно войти в круг и танцевать вместе со всеми.", "opts": [
            {"num": 1, "text": "自由に輪に入って楽しむことができる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "祭り会場に入ってはいけない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "高いお金を払わなければならない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "試験に合格しないと見てはいけない。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-006",
        "title": "日本の新幹線と安全な旅 (N5) #6",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>の<ruby>新幹線<rt>しんかんせん</rt></ruby>は、とても<ruby>速<rt>はや</rt></ruby>くて<ruby>便利<rt>べんり</rt></ruby>な<ruby>乗<rt>の</rt></ruby>り<ruby>物<rt>もの</rt></ruby>として<ruby>世界<rt>せかい</rt></ruby>で<ruby>知<rt>し</rt></ruby>られています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>最高<rt>さいこう</rt></ruby>スピードは<ruby>時速<rt>じそく</rt></ruby>300キロ近くにもなりますが、<ruby>車内<rt>しゃない</rt></ruby>はとても<ruby>静<rt>しず</rt></ruby>かで<ruby>揺<rt>ゆ</rt></ruby>れも<ruby>少<rt>すく</rt></ruby>ないです。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">また、新幹線は<ruby>時間<rt>じかん</rt></ruby>にとても<ruby>正確<rt>せいかく</rt></ruby>で、ほとんど<ruby>遅<rt>おく</rt></ruby>れることがありません。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>席<rt>せき</rt></ruby>で「<ruby>駅弁<rt>えきべん</rt></ruby>」というお<ruby>弁当<rt>べんとう</rt></ruby>を<ruby>食<rt>た</rt></ruby>べながら、<ruby>窓<rt>まど</rt></ruby>から<ruby>富士山<rt>ふじさん</rt></ruby>を<ruby>眺<rt>なが</rt></ruby>めるのは<ruby>最高<rt>さいこう</rt></ruby>の<ruby>体験<rt>たいけん</rt></ruby>です。</span></p>
<p><ruby>安心<rt>あんしん</rt></ruby>して<ruby>旅行<rt>りょこう</rt></ruby>ができる<ruby>素晴<rt>すばら</rt></ruby>らしい<ruby>電車<rt>でんしゃ</rt></ruby>です。</p>
</div>""",
        "trans": "Японский синкансэн известен во всем мире как невероятно быстрый и удобный транспорт. Максимальная скорость достигает почти 300 км/ч, однако внутри вагонов очень тихо и почти не трясет. Кроме того, синкансэн исключительно пунктуален и практически никогда не опаздывает. Сидеть на своем месте, есть станционное бэнто «экибэн» и любоваться горой Фудзи из окна — это незабываемое впечатление. На этом великолепном поезде можно путешествовать в полном спокойствии.",
        "vocab": [{"word": "新幹線", "furigana": "しんかんせん", "translation": "синкансэн (скоростной поезд)"}, {"word": "正確", "furigana": "せいかく", "translation": "точный, пунктуальный"}],
        "q1": {"prompt": "新幹線の車内の様子について何と書いてありますか。", "exp": "В предложении ev-q1 сказано: очень тихо и тряски мало.", "opts": [
            {"num": 1, "text": "とても静かで揺れも少ない。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "ものすごくうるさくて立っていられない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "窓がなくて外が見えない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "席がなくて全員が立つ。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "新幹線の運行時間について、どんな特徴がありますか。", "exp": "В предложении ev-q2 указано: очень пунктуален и почти никогда не опаздывает.", "opts": [
            {"num": 1, "text": "時間にとても正確で、ほとんど遅れない。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "毎日何時間も遅れるのが普通である。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "時刻表がなく、いつ来るかわからない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "夜しか走らない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "新幹線の中での最高の体験として、何が挙げられていますか。", "exp": "В предложении ev-q3 сказано: есть экибэн и любоваться горой Фудзи из окна.", "opts": [
            {"num": 1, "text": "駅弁を食べながら窓から富士山を眺めること。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "車内で運動をすること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "運転手とずっと話すこと。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "荷物を全部捨てること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-007",
        "title": "和食のおいしさと魚料理 (N5) #7",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>の<ruby>伝統的<rt>でんとうてき</rt></ruby>な「<ruby>和食<rt>わしょく</rt></ruby>」は、ユネスコの<ruby>無形文化遺産<rt>むけいぶんかいさん</rt></ruby>にも<ruby>選<rt>えら</rt></ruby>ばれました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>基本<rt>きほん</rt></ruby>の<ruby>形<rt>かたち</rt></ruby>は「<ruby>一汁三菜<rt>いちじゅうさんさい</rt></ruby>」と<ruby>呼<rt>よ</rt></ruby>ばれ、ご<ruby>飯<rt>はん</rt></ruby>、お<ruby>汁<rt>しる</rt></ruby>、そして3つの<ruby>料理<rt>りょうり</rt></ruby>を<ruby>並<rt>なら</rt></ruby>べます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>特<rt>とく</rt></ruby>に<ruby>魚<rt>さかな</rt></ruby><ruby>料理<rt>りょうり</rt></ruby>が<ruby>豊富<rt>ほうふ</rt></ruby>で、<ruby>生<rt>なま</rt></ruby>で<ruby>食<rt>た</rt></ruby>べる「<ruby>刺身<rt>さしみ</rt></ruby>」や、しょうゆで<ruby>焼<rt>や</rt></ruby>く「<ruby>照<rt>て</rt></ruby>り<ruby>焼<rt>や</rt></ruby>き」などがあります。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>油<rt>あぶら</rt></ruby>をあまり<ruby>使<rt>つか</rt></ruby>わないので、とてもヘルシーで<ruby>体<rt>からだ</rt></ruby>にいいです。</span></p>
<p><ruby>季節<rt>きせつ</rt></ruby>ごとの<ruby>旬<rt>しゅん</rt></ruby>の<ruby>味<rt>あじ</rt></ruby>を<ruby>楽<rt>たの</rt></ruby>しむことができるのが、和食の<ruby>素晴<rt>すばら</rt></ruby>しさです。</p>
</div>""",
        "trans": "Традиционная японская кухня «васёку» признана нематериальным культурным наследием ЮНЕСКО. Ее базовая формула называется «итидзю-сансай»: миска риса, суп и три гарнира/блюда. Особенно богато меню рыбными блюдами: от сырой рыбы «сасими» до жаренной в соевом соусе «терияки». При готовке используется мало масла, поэтому она очень полезна для здоровья. Прелесть васёку — в наслаждении сезонными вкусами.",
        "vocab": [{"word": "和食", "furigana": "わしょく", "translation": "японская кухня"}, {"word": "基本", "furigana": "きほん", "translation": "основа, база"}],
        "q1": {"prompt": "和食の基本の形「一汁三菜」とは何ですか。", "exp": "В предложении ev-q1 указано: рис, суп и 3 блюда.", "opts": [
            {"num": 1, "text": "ご飯、お汁、そして3つの料理の組み合わせ。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "お肉を3キロ食べること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "パンとスープだけの食事。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "デザートだけを3つ並べること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "魚料理について、文章でどんな例が挙げられていますか。", "exp": "В предложении ev-q2 указаны: сасими (сырая рыба) и терияки (жареная).", "opts": [
            {"num": 1, "text": "生で食べる「刺身」や、しょうゆで焼く「照り焼き」。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "魚をそのまま捨てること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "魚は一切使わないこと。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "砂糖漬けにした魚。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "和食が体に良い理由は何ですか。", "exp": "В предложении ev-q3 сказано: используется мало масла, поэтому еда здоровая.", "opts": [
            {"num": 1, "text": "油をあまり使わないのでとてもヘルシーだから。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "薬がたくさん入っているから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "塩を大量に使うから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "冷たい水しか飲まないから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-008",
        "title": "町のボランティア活動 (N5) #8",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>の<ruby>多<rt>おお</rt></ruby>くの<ruby>地域<rt>ちいき</rt></ruby>では、<ruby>住民<rt>じゅうみん</rt></ruby>がボランティアとしていろいろな<ruby>活動<rt>かつどう</rt></ruby>をしています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>例<rt>たと</rt></ruby>えば、<ruby>毎月<rt>まいつき</rt></ruby>1<ruby>回<rt>かい</rt></ruby>、みんなで<ruby>公園<rt>こうえん</rt></ruby>や<ruby>道路<rt>どうろ</rt></ruby>のごみを<ruby>拾<rt>ひろ</rt></ruby>う「<ruby>町<rt>まち</rt></ruby>のそうじ」があります。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">また、<ruby>市民<rt>しみん</rt></ruby>センターでは、ボランティアの<ruby>先生<rt>せんせい</rt></ruby>が<ruby>外国人<rt>がいこくじん</rt></ruby>に<ruby>無料<rt>むりょう</rt></ruby>で日本語を<ruby>教<rt>おし</rt></ruby>えています。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">ボランティアを<ruby>通<rt>とお</rt></ruby>して、<ruby>近所<rt>きんじょ</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>たちと<ruby>仲良<rt>なかよ</rt></ruby>くなることができます。</span></p>
<p><ruby>助<rt>たす</rt></ruby>け<ruby>合<rt>あ</rt></ruby>いの<ruby>気持<rt>きも</rt></ruby>ちが、<ruby>安全<rt>あんぜん</rt></ruby>な<ruby>町<rt>まち</rt></ruby>を<ruby>作<rt>つく</rt></ruby>っています。</p>
</div>""",
        "trans": "Во многих районах Японии жители ведут активную волонтерскую деятельность. Например, раз в месяц все вместе собирают мусор в парках и на улицах во время общественной уборки. В городских центрах преподаватели-волонтеры бесплатно обучают иностранцев японскому языку. Благодаря волонтерству можно подружиться с соседями. Взаимопомощь делает города безопасными и уютными.",
        "vocab": [{"word": "活動", "furigana": "かつどう", "translation": "деятельность, активность"}, {"word": "住民", "furigana": "じゅうみん", "translation": "жители"}],
        "q1": {"prompt": "毎月1回行われるボランティア活動の例は何ですか。", "exp": "В предложении ev-q1 сказано: сбор мусора в парках и на дорогах.", "opts": [
            {"num": 1, "text": "公園や道路のごみを拾う「町のそうじ」。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "山を全部削る工事。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "大きなビルを壊すこと。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "お金を集めて配ること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "市民センターではどんなボランティアが行われていますか。", "exp": "В предложении ev-q2 указано: учителя-волонтеры бесплатно учат иностранцев японскому языку.", "opts": [
            {"num": 1, "text": "外国人に無料で日本語を教える活動。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "高い授業料を取って英語を教えること。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "パソコンを壊すこと。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "食事を作らせて売ること。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "ボランティア活動に参加すると、どんないいことがありますか。", "exp": "В предложении ev-q3 сказано: можно подружиться с соседями по району.", "opts": [
            {"num": 1, "text": "近所の人たちと仲良くなることができる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "給料がたくさんもらえる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно (волонтерство бесплатно)."},
            {"num": 3, "text": "仕事をしなくてもよくなる。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."},
            {"num": 4, "text": "何もいいことはない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-009",
        "title": "外国人留学生の一日 (N5) #9",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>で<ruby>暮<rt>く</rt></ruby>らす<ruby>外国人<rt>がいこくじん</rt></ruby><ruby>留学生<rt>りゅうがくせい</rt></ruby>は、どんな<ruby>一日<rt>いちにち</rt></ruby>を<ruby>送<rt>おく</rt></ruby>っているのでしょうか。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>朝<rt>あさ</rt></ruby>は9<ruby>時<rt>じ</rt></ruby>から<ruby>日本語<rt>にほんご</rt></ruby><ruby>学校<rt>がっこう</rt></ruby>で、<ruby>文法<rt>ぶんぽう</rt></ruby>や<ruby>漢字<rt>かんじ</rt></ruby>の<ruby>勉強<rt>べんきょう</rt></ruby>を4<ruby>時間<rt>じかん</rt></ruby>します。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>授業<rt>じゅぎょう</rt></ruby>が<ruby>終<rt>お</rt></ruby>わると、<ruby>図書館<rt>としょかん</rt></ruby>で<ruby>宿題<rt>しゅくだい</rt></ruby>をしたり、<ruby>友<rt>とも</rt></ruby>だちとおしゃべりしたりします。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>夕方<rt>ゆうがた</rt></ruby>からは、コンビニやレストランでアルバイトをして、<ruby>生活費<rt>せいかつひ</rt></ruby>を<ruby>稼<rt>かせ</rt></ruby>ぐ<ruby>人<rt>ひと</rt></ruby>も<ruby>多<rt>おお</rt></ruby>いです。</span></p>
<p><ruby>忙<rt>いそが</rt></ruby>しい<ruby>毎日<rt>まいにち</rt></ruby>ですが、みんな<ruby>夢<rt>ゆめ</rt></ruby>に<ruby>向<rt>む</rt></ruby>かって<ruby>一生懸命<rt>いっしょうけんめい</rt></ruby>がんばっています。</p>
</div>""",
        "trans": "Как проходит день иностранного студента в Японии? Утром с 9:00 они занимаются в языковой школе: 4 часа учат грамматику и иероглифы. После занятий делают домашнее задание в библиотеке или общаются с друзьями. С вечера многие подрабатывают в комбини или ресторанах, чтобы оплачивать расходы на жизнь. Хотя дни наполнены делами, все упорно стремятся к своей мечте.",
        "vocab": [{"word": "留学生", "furigana": "りゅうがくせい", "translation": "иностранный студент"}, {"word": "生活費", "furigana": "せいかつひ", "translation": "расходы на жизнь"}],
        "q1": {"prompt": "留学生は朝に何をしますか。", "exp": "В предложении ev-q1 сказано: с 9:00 учат грамматику и кандзи в языковой школе 4 часа.", "opts": [
            {"num": 1, "text": "日本語学校で文法や漢字を4時間勉強する。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "ずっと寝ている。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "朝から夜までアルバイトだけをする。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Подработка вечером."},
            {"num": 4, "text": "山登りをする。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "授業が終わった後の行動について、何と書いてありますか。", "exp": "В предложении ev-q2 указано: делают домашнее задание в библиотеке или общаются.", "opts": [
            {"num": 1, "text": "図書館で宿題をしたり、友だちと話したりする。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "すぐに飛行機に乗って帰国する。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "病院へ行く。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "学校のドアを全部閉める。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "夕方からの時間について、正しいものはどれですか。", "exp": "В предложении ev-q3 сказано: многие подрабатывают в комбини или ресторанах.", "opts": [
            {"num": 1, "text": "コンビニやレストランでアルバイトをする人が多い。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "全員がパーティーをする。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."},
            {"num": 3, "text": "外に出てはいけない決まりがある。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "アルバイトは禁止されている。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-010",
        "title": "日本の自動販売機の多さ (N5) #10",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>を<ruby>旅<rt>たび</rt></ruby>する<ruby>外国人<rt>がいこくじん</rt></ruby>が<ruby>驚<rt>おどろ</rt></ruby>くことの1つに、「<ruby>自動販売機<rt>じどうはんばいき</rt></ruby>の<ruby>多<rt>おお</rt></ruby>さ」があります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>駅<rt>えき</rt></ruby>だけでなく、<ruby>町<rt>まち</rt></ruby>の<ruby>道<rt>みち</rt></ruby>や<ruby>山<rt>やま</rt></ruby>の<ruby>上<rt>うえ</rt></ruby>など、どこにでも<ruby>設置<rt>せっち</rt></ruby>されています。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">1つの<ruby>機械<rt>きかい</rt></ruby>で、<ruby>冷<rt>つめ</rt></ruby>たいジュースと<ruby>温<rt>あたた</rt></ruby>かいコーヒーを<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>売<rt>う</rt></ruby>っています。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">また、<ruby>治安<rt>ちあん</rt></ruby>がとてもいいので、<ruby>夜<rt>よる</rt></ruby>でも<ruby>壊<rt>こわ</rt></ruby>されたりお金を盗まれたりしません。</span></p>
<p>いつでも手軽に飲み物を買える、とても便利なシステムです。</p>
</div>""",
        "trans": "Одна из вещей, которая больше всего удивляет иностранных туристов в Японии — это огромное количество торговых автоматов. Они установлены везде: не только на станциях, но и вдоль обычных улиц и даже на вершинах гор. В одном автомате одновременно продаются холодные соки и горячий кофе в банках. Кроме того, благодаря отличной общественной безопасности автоматы не ломают и деньги из них не воруют даже ночью. Это очень удобная система, позволяющая купить напиток в любой момент.",
        "vocab": [{"word": "自動販売機", "furigana": "じどうはんばいき", "translation": "торговый автомат"}, {"word": "治安", "furigana": "ちあん", "translation": "общественная безопасность"}],
        "q1": {"prompt": "日本の自動販売機はどこにありますか。", "exp": "В предложении ev-q1 сказано: не только на станциях, но и на улицах и даже на вершинах гор, повсюду.", "opts": [
            {"num": 1, "text": "駅だけでなく、道の横や山の上などどこにでもある。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "空港のロビーに1台だけある。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "東京の地下にしかない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "日本には自動販売機が1台もない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "販売機の機能について何と書いてありますか。", "exp": "В предложении ev-q2 указано: в одном автомате одновременно продаются холодные и горячие напитки.", "opts": [
            {"num": 1, "text": "冷たい飲み物と温かい飲み物を一緒に売っている。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "水しか売っていない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "お湯が沸かせない。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "お金を入れても何も出ない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "なぜ外に置かれた自動販売機が壊されませんか。", "exp": "В предложении ev-q3 прямо сказано: потому что общественная безопасность (чиан) в Японии очень хорошая.", "opts": [
            {"num": 1, "text": "治安がとてもよく、安全だから。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "警察官が24時間見張っているから。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "中にお金が入っていないから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "誰も近づかないから。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-011",
        "title": "お茶の歴史と楽しい飲み方 (N5) #11",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>では、<ruby>昔<rt>むかし</rt></ruby>から「お<ruby>茶<rt>ちゃ</rt></ruby>」を<ruby>飲<rt>の</rt></ruby>む<ruby>文化<rt>ぶんか</rt></ruby>が<ruby>大切<rt>たいせつ</rt></ruby>にされています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>日常的<rt>にちじょうてき</rt></ruby>に<ruby>飲<rt>の</rt></ruby>まれているのは「<ruby>煎茶<rt>せんちゃ</rt></ruby>」という<ruby>緑茶<rt>りょくちゃ</rt></ruby>で、ご<ruby>飯<rt>はん</rt></ruby>の<ruby>後<rt>あと</rt></ruby>によく<ruby>出<rt>だ</rt></ruby>されます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">また、「<ruby>茶道<rt>さどう</rt></ruby>」という<ruby>特別<rt>とくべつ</rt></ruby>なルールでお<ruby>茶<rt>ちゃ</rt></ruby>をたてる<ruby>伝統<rt>でんとう</rt></ruby>もあります。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3"><ruby>抹茶<rt>まっちゃ</rt></ruby>の<ruby>苦<rt>にが</rt></ruby>い<ruby>味<rt>あじ</rt></ruby>と、<ruby>甘<rt>あま</rt></ruby>い「<ruby>和菓子<rt>わがし</rt></ruby>」は、とてもよく<ruby>合<rt>あ</rt></ruby>います。</span></p>
<p>静かな部屋でお茶を飲むと、忙しい毎日の中でもリラックスできます。</p>
</div>""",
        "trans": "В Японии с древности бережно хранится культура чаепития. В повседневной жизни чаще всего пьют зеленый чай «сэнтя», его часто подают после еды. Также существует традиция «тядо» (чайная церемония), где чай готовят по особым правилам. Горьковатый вкус чая маття и сладкие традиционные сладости «вагаси» идеально сочетаются друг с другом. Чаепитие в тихой комнате дарит глубокое расслабление даже в самые занятые дни.",
        "vocab": [{"word": "日常的", "furigana": "にちじょうてき", "translation": "повседневный"}, {"word": "和菓子", "furigana": "わがし", "translation": "японские сладости"}],
        "q1": {"prompt": "日本で日常的によく飲まれているお茶は何ですか。", "exp": "В предложении ev-q1 указано: зеленый чай сэнтя (煎茶).", "opts": [
            {"num": 1, "text": "「煎茶」という緑茶", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "コーヒーだけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "冷たいコーラ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "甘いミルクティー", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "茶道（さどう）について何と書いてありますか。", "exp": "В предложении ev-q2 сказано: традиция приготовления чая по особым правилам.", "opts": [
            {"num": 1, "text": "特別なルールでお茶をたてる伝統である。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "お茶を一気に早飲みするスポーツである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "お茶の葉を投げる遊びである。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "昨日始まった新しいゲームである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "抹茶の苦い味には何がよく合いますか。", "exp": "В предложении ev-q3 указано: сладкие традиционные сладости вагаси.", "opts": [
            {"num": 1, "text": "甘い「和菓子」", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "辛いカレー", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "塩辛い魚", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "酸っぱいレモン", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-article-012",
        "title": "日本語を学ぶ楽しさ (N5) #12",
        "body": """<div class="passage-body">
<p><ruby>世界<rt>せかい</rt></ruby>には、<ruby>多<rt>おお</rt></ruby>くの<ruby>人<rt>ひと</rt></ruby>が<ruby>趣味<rt>しゅみ</rt></ruby>や<ruby>仕事<rt>しごと</rt></ruby>のために<ruby>日本語<rt>にほんご</rt></ruby>を<ruby>勉強<rt>べんきょう</rt></ruby>しています。</p>
<p><span id="ev-q1" data-evidence="ev-q1">日本語には「ひらがな」「カタカナ」「<ruby>漢字<rt>かんじ</rt></ruby>」の3<ruby>種類<rt>しゅるい</rt></ruby>の<ruby>文字<rt>もじ</rt></ruby>があります。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>初<rt>はじ</rt></ruby>めは<ruby>覚<rt>おぼ</rt></ruby>えるのが<ruby>大変<rt>たいへん</rt></ruby>ですが、<ruby>町<rt>まち</rt></ruby>の<ruby>看板<rt>かんばん</rt></ruby>が<ruby>読<rt>よ</rt></ruby>めるようになるととても<ruby>嬉<rt>うれ</rt></ruby>しいです。</span></p>
<p><span id="ev-q3" data-evidence="ev-q3">また、日本人に日本語で「ありがとう」と<ruby>言<rt>い</rt></ruby>うと、みんな<ruby>笑顔<rt>えがお</rt></ruby>で<ruby>返事<rt>へんじ</rt></ruby>をしてくれます。</span></p>
<p><ruby>言葉<rt>ことば</rt></ruby>を<ruby>通<rt>とお</rt></ruby>して<ruby>人<rt>ひと</rt></ruby>と<ruby>心<rt>こころ</rt></ruby>が<ruby>通<rt>つう</rt></ruby>じ<ruby>合<rt>あ</rt></ruby>う瞬間こそ、<ruby>語学<rt>ごがく</rt></ruby>の<ruby>一番<rt>いちばん</rt></ruby>の<ruby>楽<rt>たの</rt></ruby>しさです。</p>
</div>""",
        "trans": "По всему миру множество людей изучают японский язык для работы или как хобби. В японском языке три вида письменности: хирагана, катакана и кандзи (иероглифы). Сначала учить их непросто, но когда начинаешь читать вывески на улицах, испытываешь огромную радость. А когда говоришь японцам «аригато», они всегда отвечают с теплой улыбкой. Момент, когда через язык соединяются сердца людей — самая большая радость изучения языков.",
        "vocab": [{"word": "文字", "furigana": "もじ", "translation": "письменный знак, буква"}, {"word": "看板", "furigana": "かんばん", "translation": "вывеска"}],
        "q1": {"prompt": "日本語には何種類の文字がありますか。", "exp": "В предложении ev-q1 сказано: три вида — хирагана, катакана и кандзи.", "opts": [
            {"num": 1, "text": "ひらがな、カタカナ、漢字の3種類", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "アルファベット1種類だけ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "数字の10種類だけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "文字は存在しない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "勉強していてどんなときに嬉しいと感じますか。", "exp": "В предложении ev-q2 указано: когда начинаешь читать вывески в городе.", "opts": [
            {"num": 1, "text": "町の看板が読めるようになったとき。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "教科書を全部なくしたとき。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "宿題を忘れて叱られたとき。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "誰とも話さなかったとき。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]},
        "q3": {"prompt": "日本人に「ありがとう」と言うと、どんな反応をしてくれますか。", "exp": "В предложении ev-q3 указано: все отвечают с теплой улыбкой.", "opts": [
            {"num": 1, "text": "みんな笑顔で返事をしてくれる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q3."},
            {"num": 2, "text": "怒って逃げていく。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "お金を要求する。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "誰も返事をしない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    }
]

print(f"ARTICLE_DATA full defined: {len(ARTICLE_DATA)} items.")
