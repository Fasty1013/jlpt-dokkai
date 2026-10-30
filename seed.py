import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, engine, Base
from models import Text, Question, Option


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear and re-seed to build the comprehensive 12-text library
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Text).delete()
    db.commit()

    print("Seeding rich multi-level JLPT Dokkai texts (12 comprehensive texts with multi-question architecture & NHK World news)...")

    # =========================================================================
    # 1. N5 SHORT MEMO (短文): スミスさんからのメモ (1 Question)
    # =========================================================================
    text_n5_1 = Text(
        title="スミスさんからのメモ (Записка от Смита)",
        level="N5",
        category="short",
        source_exam="JLPT N5 練習問題",
        is_nhk=False,
        recommended_time_min=2,
        content_html="""
<div class="passage-body">
    <p>タナカさんへ</p>
    <p><ruby>昨日<rt>きのう</rt></ruby><ruby>話<rt>はな</rt></ruby>した<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>辞書<rt>じしょ</rt></ruby>を<ruby>持<rt>も</rt></ruby>ってきました。<ruby>机<rt>つくえ</rt></ruby>の<ruby>上<rt>うえ</rt></ruby>に<ruby>置<rt>お</rt></ruby>いておきますね。</p>
    <p><span id="ev-n5-1"><ruby>今日<rt>きょう</rt></ruby>は５<ruby>時<rt>じ</rt></ruby>から<ruby>図書館<rt>としょかん</rt></ruby>でアルバイトがあるので、４<ruby>時<rt>じ</rt></ruby><ruby>半<rt>はん</rt></ruby>に<ruby>教室<rt>きょうしつ</rt></ruby>を<ruby>出<rt>で</rt></ruby>ます。</span>もし<ruby>質問<rt>しつもん</rt></ruby>があったら、それまでに<ruby>聞<rt>き</rt></ruby>いてください。</p>
    <p>スミスより</p>
</div>
""".strip(),
        translation_ru="Танака-сан!\nЯ принёс словарь японского языка, о котором мы говорили вчера. Я оставлю его у вас на столе.\nСегодня с 5 часов у меня подработка в библиотеке, поэтому в 4:30 я уйду из аудитории. Если у вас будут вопросы, спросите меня до этого времени.\nОт Смита.",
        vocabulary_json=[
            {"word": "辞書", "furigana": "じしょ", "translation": "словарь"},
            {"word": "置く", "furigana": "おく", "translation": "класть, оставлять"},
            {"word": "それまでに", "furigana": "それまでに", "translation": "к тому моменту / до этого времени"},
            {"word": "アルバイト", "furigana": "あるばいと", "translation": "подработка"}
        ]
    )
    q_n5_1 = Question(
        question_number=1,
        question_text="タナカさんはスミスさんに質問したいとき、どうしなければなりませんか。",
        general_explanation="Правильный ответ — вариант 2. В предложении ev-n5-1 Смит прямо указывает, что уходит из аудитории в 4:30, и просит задать вопросы до этого времени (それまでに).",
        evidence_span_id="ev-n5-1"
    )
    q_n5_1.options = [
        Option(option_number=1, option_text="５時までに図書館へ行きます。", is_correct=False, option_explanation="Неверно. В 5:00 Смит уже будет работать в библиотеке."),
        Option(option_number=2, option_text="４時半までに教室で聞きます。", is_correct=True, option_explanation="Верно! Смит уходит из класса в 4:30, спросить нужно до этого."),
        Option(option_number=3, option_text="５時半に辞書を返します。", is_correct=False, option_explanation="Неверно. О времени возврата словаря ничего не говорится."),
        Option(option_number=4, option_text="４時に図書館へ電話をします。", is_correct=False, option_explanation="Неверно. Звонить в библиотеку не требуется.")
    ]
    text_n5_1.questions = [q_n5_1]

    # =========================================================================
    # 2. N5 INFO SEARCH (情報検索): バーベキュー大会のお知らせ (1 Question)
    # =========================================================================
    text_n5_2 = Text(
        title="留学生バーベキュー大会のお知らせ (Объявление о барбекю)",
        level="N5",
        category="info_search",
        source_exam="JLPT N5 生活情報",
        is_nhk=False,
        recommended_time_min=3,
        content_html="""
<div class="flyer-container">
    <div class="flyer-header">
        <div class="flyer-badge">春のイベント</div>
        <h2 class="flyer-title"><ruby>留学生<rt>りゅうがくせい</rt></ruby>バーベキュー<ruby>大会<rt>たいかい</rt></ruby>の<ruby>知<rt>し</rt></ruby>らせ</h2>
        <p class="flyer-subtitle">みんなでおいしいお肉を食べながら楽しく話しましょう！</p>
    </div>
    <table class="flyer-table">
        <tbody>
            <tr>
                <th><ruby>日時<rt>にちじ</rt></ruby></th>
                <td>5<ruby>月<rt>がつ</rt></ruby>12<ruby>日<rt>にち</rt></ruby>（<ruby>日<rt>にち</rt></ruby>）11:00 〜 15:00</td>
            </tr>
            <tr>
                <th><ruby>場所<rt>ばしょ</rt></ruby></th>
                <td>みどり<ruby>公園<rt>こうえん</rt></ruby>（<ruby>南口<rt>みなみぐち</rt></ruby>から<ruby>歩<rt>ある</rt></ruby>いて5<ruby>分<rt>ふん</rt></ruby>）</td>
            </tr>
            <tr>
                <th><ruby>参加費<rt>さんかひ</rt></ruby></th>
                <td>1,500<ruby>円<rt>えん</rt></ruby>（<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>・お<ruby>茶<rt>ちゃ</rt></ruby>代）</td>
            </tr>
        </tbody>
    </table>
    <div class="flyer-notes">
        <h3>【<ruby>大切<rt>たいせつ</rt></ruby>なお<ruby>知<rt>し</rt></ruby>らせ】</h3>
        <ul>
            <li><span id="ev-n5-bbq-1">● お<ruby>茶<rt>ちゃ</rt></ruby>はありますが、ジュースや<ruby>好<rt>す</rt></ruby>きな<ruby>飲<rt>の</rt></ruby>み<ruby>物<rt>もの</rt></ruby>は<ruby>自分<rt>じぶん</rt></ruby>で<ruby>持<rt>も</rt></ruby>ってきてください。</span></li>
            <li>● <ruby>雨<rt>あめ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>は<ruby>中止<rt>ちゅうし</rt></ruby>になります。<ruby>朝<rt>あさ</rt></ruby>8<ruby>時<rt>じ</rt></ruby>にホームページでお<ruby>知<rt>し</rt></ruby>らせします。</li>
        </ul>
    </div>
</div>
""".strip(),
        translation_ru="Объявление о барбекю для иностранных студентов:\nДата: 12 мая (вс) 11:00 - 15:00.\nМесто: парк Мидори (5 мин пешком от южного выхода).\nВзнос: 1,500 иен (еда и чай).\nВажные примечания:\n- Чай есть, но соки и свои любимые напитки приносите с собой сами.\n- В случае дождя мероприятие отменяется (сообщение на сайте в 8 утра).",
        vocabulary_json=[
            {"word": "お知らせ", "furigana": "おしらせ", "translation": "объявление"},
            {"word": "参加費", "furigana": "さんかひ", "translation": "взнос за участие"},
            {"word": "中止", "furigana": "ちゅうし", "translation": "отмена"}
        ]
    )
    q_n5_2 = Question(
        question_number=1,
        question_text="バーベキューに参加する人は、何を自分で持って行かなければなりませんか。",
        general_explanation="Правильный ответ — вариант 3. В примечании с id='ev-n5-bbq-1' прямо указано, что чай и еда есть, а соки и свои любимые напитки нужно принести самостоятельно.",
        evidence_span_id="ev-n5-bbq-1"
    )
    q_n5_2.options = [
        Option(option_number=1, option_text="バーベキューのお肉", is_correct=False, option_explanation="Неверно. Еда включена во взнос 1,500 иен."),
        Option(option_number=2, option_text="飲むためのお茶", is_correct=False, option_explanation="Неверно. Чай предоставляется организаторами (お茶はあります)."),
        Option(option_number=3, option_text="ジュースなどの好きな飲み物", is_correct=True, option_explanation="Верно! Свои напитки нужно принести самому."),
        Option(option_number=4, option_text="雨の日のための傘", is_correct=False, option_explanation="Неверно. В дождь мероприятие отменяется.")
    ]
    text_n5_2.questions = [q_n5_2]

    # =========================================================================
    # 3. N4 MEDIUM STORY (中文): 京都への一人旅 (2 Questions)
    # =========================================================================
    text_n4_kyoto = Text(
        title="京都への一人旅 (Одиночное путешествие в Киото)",
        level="N4",
        category="medium",
        source_exam="JLPT N4 過去問類題",
        is_nhk=False,
        recommended_time_min=4,
        content_html="""
<div class="passage-body">
    <p><ruby>先週<rt>せんしゅう</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>初<rt>はじ</rt></ruby>めて<ruby>一人<rt>ひとり</rt></ruby>で<ruby>京都<rt>きょうと</rt></ruby>へ<ruby>旅行<rt>りょこう</rt></ruby>に<ruby>行<rt>い</rt></ruby>きました。<ruby>友達<rt>ともだち</rt></ruby>と<ruby>一緒<rt>いっしょ</rt></ruby>にいく<ruby>旅行<rt>りょこう</rt></ruby>もにぎやかで<ruby>楽<rt>たの</rt></ruby>しいですが、いつも<ruby>相手<rt>あいて</rt></ruby>の<ruby>行<rt>い</rt></ruby>きたい<ruby>場所<rt>ばしょ</rt></ruby>や<ruby>時間<rt>じかん</rt></ruby>に<ruby>合<rt>あ</rt></ruby>わせなければなりません。<span id="ev-n4-1">今回は自分の好きな時に好きな場所をゆっくり見たかったので、一人で行くことに決めました。</span></p>
    <p><ruby>京都<rt>きょうと</rt></ruby>では、<ruby>有名<rt>ゆうめい</rt></ruby>な<ruby>寺<rt>てら</rt></ruby>を<ruby>見<rt>み</rt></ruby>るだけでなく、<ruby>小<rt>ちい</rt></ruby>さな<ruby>通<rt>とお</rt></ruby>りをのんびり<ruby>散歩<rt>さんぽ</rt></ruby>しました。<span id="ev-n4-2">道に迷って偶然見つけた古い和菓子屋で食べたお茶と団子は、ガイドブックに載っているどんな店より美味しく感じられました。</span></p>
    <p><ruby>一人<rt>ひとり</rt></ruby>の<ruby>旅<rt>たび</rt></ruby>は<ruby>少<rt>すこ</rt></ruby>し<ruby>不安<rt>ふあん</rt></ruby>でしたが、<ruby>自分<rt>じぶん</rt></ruby>だけの<ruby>特別<rt>とくべつ</rt></ruby>な<ruby>思<rt>おも</rt></ruby>い<ruby>出<rt>で</rt></ruby>ができて、とてもよかったです。また<ruby>一人<rt>ひとり</rt></ruby>でどこかへ<ruby>行<rt>い</rt></ruby>ってみたいです。</p>
</div>
""".strip(),
        translation_ru="На прошлой неделе я впервые один отправился в путешествие в Киото. Поездки с друзьями тоже весёлые, но всегда приходится подстраиваться под других. В этот раз мне хотелось спокойно посмотреть то, что нравится мне, поэтому я поехал один.\nВ Киото я не только осматривал знаменитые храмы, но и гулял по улочкам. Чай и данго в старой лавке, найденной случайно, когда я заблудился, показались вкуснее любого места из путеводителя.\nБыло немного тревожно, но остались чудесные воспоминания.",
        vocabulary_json=[
            {"word": "相手に合わせる", "furigana": "あいてにあわせる", "translation": "подстраиваться под спутника"},
            {"word": "道に迷う", "furigana": "みちにまよう", "translation": "заблудиться"},
            {"word": "偶然", "furigana": "ぐうぜん", "translation": "случайно"},
            {"word": "和菓子屋", "furigana": "わがしや", "translation": "лавка японских сладостей"}
        ]
    )
    q_n4_1 = Question(
        question_number=1,
        question_text="「私」はどうして一人で京都へ行きましたか。",
        general_explanation="Правильный ответ — вариант 3. В предложении ev-n4-1 автор говорит, что хотел посмотреть места в своём темпе, не подстраиваясь под чужие планы.",
        evidence_span_id="ev-n4-1"
    )
    q_n4_1.options = [
        Option(option_number=1, option_text="友達と休みの日が合わなかったから。", is_correct=False, option_explanation="Неверно. Автор не говорит, что друзья были заняты."),
        Option(option_number=2, option_text="京都の有名な寺を全部見たかったから。", is_correct=False, option_explanation="Неверно. Целью было спокойствие, а не осмотр абсолютно всех храмов."),
        Option(option_number=3, option_text="他人に合わせず、自分のペースで楽しみたかったから。", is_correct=True, option_explanation="Верно! Точный пересказ фразы «自分の好きな時に好きな場所をゆっくり見たかった»."),
        Option(option_number=4, option_text="一人旅のガイドブックをもらったから。", is_correct=False, option_explanation="Неверно. Напротив, лучшие места были найдены случайно без гида.")
    ]
    q_n4_2 = Question(
        question_number=2,
        question_text="「私」が一番美味しく感じたのはどれですか。",
        general_explanation="Правильный ответ — вариант 4. Согласно ev-n4-2, самыми вкусными оказались чай и данго в неприметной старой лавке, найденной когда автор заблудился.",
        evidence_span_id="ev-n4-2"
    )
    q_n4_2.options = [
        Option(option_number=1, option_text="有名な寺の近くで食べた料理", is_correct=False, option_explanation="Неверно. Возле храмов автор не выделял еду."),
        Option(option_number=2, option_text="ガイドブックで一番おすすめされていた店のお菓子", is_correct=False, option_explanation="Неверно. Лавка как раз не была указана в путеводителе."),
        Option(option_number=3, option_text="友達が教えてくれた京都のレストランの食事", is_correct=False, option_explanation="Неверно. Друзья не давали рекомендаций."),
        Option(option_number=4, option_text="道に迷ったときに見つけた古い店のお茶と団子", is_correct=True, option_explanation="Верно! Прямое совпадение с предложением в <span id='ev-n4-2'>.")
    ]
    text_n4_kyoto.questions = [q_n4_1, q_n4_2]

    # =========================================================================
    # 4. N4 NHK NEWS EASY (記事): 富士山の登山ルートで新しい予約制度 (2 Questions)
    # =========================================================================
    text_n4_nhk = Text(
        title="富士山の登山で新しいルール：予約が必要に (Новые правила восхождения на Фудзи)",
        level="N4",
        category="article",
        source_exam="NHK World Easy News",
        is_nhk=True,
        recommended_time_min=4,
        content_html="""
<div class="nhk-article-badge">NHK WORLD-JAPAN NEWS EASY</div>
<div class="passage-body">
    <p><ruby>日本<rt>にほん</rt></ruby>でいちばん<ruby>高<rt>たか</rt></ruby>い<ruby>山<rt>やま</rt></ruby>の<ruby>富士山<rt>ふじさん</rt></ruby>では、<ruby>夏<rt>なつ</rt></ruby>になると<ruby>世界中<rt>せかいじゅう</rt></ruby>から<ruby>大勢<rt>おおぜい</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>が<ruby>登<rt>のぼ</rt></ruby>りに<ruby>来<rt>き</rt></ruby>ます。<ruby>山頂<rt>さんちょう</rt></ruby>で<ruby>美<rt>うつく</rt></ruby>しい<ruby>日<rt>ひ</rt></ruby>の<ruby>出<rt>で</rt></ruby>を<ruby>見<rt>み</rt></ruby>るため、<ruby>夜<rt>よる</rt></ruby>に<ruby>休<rt>やす</rt></ruby>まないで<ruby>一気<rt>いっき</rt></ruby>に<ruby>登<rt>のぼ</rt></ruby>る「<ruby>弾丸<rt>だんがん</rt></ruby><ruby>登山<rt>とざん</rt></ruby>」をする<ruby>人<rt>ひと</rt></ruby>も<ruby>多<rt>おお</rt></ruby>く、けがや<ruby>病気<rt>びょうき</rt></ruby>になることが<ruby>問題<rt>もんだい</rt></ruby>になっていました。</p>
    <p><span id="ev-n4-nhk-1">このため山梨県は、今年の夏から一番人気のある「吉田ルート」で、1日に登る人の数を4,000人までに制限し、1人2,000円の通行料をとることを決めました。</span></p>
    <p><span id="ev-n4-nhk-2">さらに、山小屋に泊まる予約をしていない人は、午後4時から翌朝の午前3時まで登山口を通ることができなくなります。</span><ruby>県<rt>けん</rt></ruby>の<ruby>担当者<rt>たんとうしゃ</rt></ruby>は「<ruby>混雑<rt>こんざつ</rt></ruby>を<ruby>防<rt>ふせ</rt></ruby>ぎ、みんなが<ruby>安全<rt>あんぜん</rt></ruby>に<ruby>楽<rt>たの</rt></ruby>しめるようにルールを<ruby>守<rt>まも</rt></ruby>ってほしい」と<ruby>呼<rt>よ</rt></ruby>びかけています。</p>
</div>
""".strip(),
        translation_ru="На самую высокую гору Японии, Фудзи, летом съезжается множество туристов со всего мира. Чтобы увидеть восход солнца на вершине, многие совершали «пулевое восхождение» — шли ночью без отдыха, из-за чего участились травмы и болезни.\nПо этой причине префектура Яманаси с этого лета ввела ограничение на самом популярном маршруте «Ёсида»: не более 4 000 человек в день и плата за проход 2 000 иен с человека.\nКроме того, те, кто не забронировал ночлег в горном приюте, не смогут пройти через ворота с 16:00 до 03:00 утра. Власти призывают соблюдать правила ради безопасности.",
        vocabulary_json=[
            {"word": "山頂", "furigana": "さんちょう", "translation": "вершина горы"},
            {"word": "弾丸登山", "furigana": "だんがんとざん", "translation": "восхождение 'пулей' (без ночевки)"},
            {"word": "通行料", "furigana": "つうこうりょう", "translation": "плата за проход"},
            {"word": "混雑", "furigana": "こんざつ", "translation": "столпотворение, давка"}
        ]
    )
    q_n4_nhk_1 = Question(
        question_number=1,
        question_text="山梨県が富士山で新しいルールを作った一番の理由は何ですか。",
        general_explanation="Правильный ответ — вариант 2. В первом абзаце и ev-n4-nhk-1 объясняется: ночные восхождения без отдыха приводили к давке, травмам и опасным болезням, поэтому введены лимиты.",
        evidence_span_id="ev-n4-nhk-1"
    )
    q_n4_nhk_1.options = [
        Option(option_number=1, option_text="外国からの観光客を増やしてお金をたくさん集めるため。", is_correct=False, option_explanation="Неверно. Цель — безопасность, а не привлечение большего числа туристов."),
        Option(option_number=2, option_text="危険な登山や混雑を減らし、安全を守るため。", is_correct=True, option_explanation="Верно! Правила направлены против опасного «пулевого восхождения» (けがや病気、混雑を防ぐため)."),
        Option(option_number=3, option_text="山小屋をすべて新しい建物に建て替えるため。", is_correct=False, option_explanation="Неверно. О сносе и перестройке приютов речи нет."),
        Option(option_number=4, option_text="夏以外の季節にも登山客を集めるため。", is_correct=False, option_explanation="Неверно. Новые правила касаются именно летнего сезона.")
    ]
    q_n4_nhk_2 = Question(
        question_number=2,
        question_text="山小屋を予約していない人は、どうなりますか。",
        general_explanation="Правильный ответ — вариант 4. В предложении ev-n4-nhk-2 прямо сказано: без брони в приюте запрещено проходить на тропу с 16:00 вечера до 03:00 утра.",
        evidence_span_id="ev-n4-nhk-2"
    )
    q_n4_nhk_2.options = [
        Option(option_number=1, option_text="富士山に登ることが絶対にできなくなる。", is_correct=False, option_explanation="Неверно. Днём до 16:00 подняться можно, ограничение действует только в вечернее и ночное время."),
        Option(option_number=2, option_text="通行料を4,000円払わなければならない。", is_correct=False, option_explanation="Неверно. 通行料 составляет 2,000 иен, а 4,000 — это лимит человек."),
        Option(option_number=3, option_text="山頂で日の出を見ることが必ずできる。", is_correct=False, option_explanation="Неверно. Наоборот, ночной проход закрыт."),
        Option(option_number=4, option_text="夕方4時から朝3時までの間は登ることができない。", is_correct=True, option_explanation="Верно! Точное соответствие предложению с тегом ev-n4-nhk-2.")
    ]
    text_n4_nhk.questions = [q_n4_nhk_1, q_n4_nhk_2]

    # =========================================================================
    # 5. N3 ARCHIVE SHORT (短文): ほめて育てることの真意 (1 Question)
    # =========================================================================
    text_n3_arch_short = Text(
        title="ほめて育てることの真意 (Истинный смысл похвалы)",
        level="N3",
        category="short",
        source_exam="JLPT 2021.12 N3 過去問",
        is_nhk=False,
        recommended_time_min=3,
        content_html="""
<div class="passage-body">
    <p><ruby>子<rt>こ</rt></ruby>どもや<ruby>部下<rt>ぶか</rt></ruby>を「ほめて<ruby>育<rt>そだ</rt></ruby>てる」ことが<ruby>良<rt>よ</rt></ruby>いとよく<ruby>言<rt>い</rt></ruby>われます。<ruby>確<rt>たし</rt></ruby>かに、ほめられると<ruby>誰<rt>だれ</rt></ruby>でもうれしくなり、やる<ruby>気<rt>き</rt></ruby>が<ruby>出<rt>で</rt></ruby>るものです。</p>
    <p>しかし、「すごいね」「よくできたね」と<ruby>結果<rt>けっか</rt></ruby>だけをほめ<ruby>続<rt>つづ</rt></ruby>けていると、<ruby>失敗<rt>しっぱい</rt></ruby>を<ruby>極端<rt>きょくたん</rt></ruby>に<ruby>恐<rt>おそ</rt></ruby>れるようになり、<ruby>難<rt>むずか</rt></ruby>しいことに<ruby>挑戦<rt>ちょうせん</rt></ruby>しなくなるという<ruby>弊害<rt>へいがい</rt></ruby>があります。</p>
    <p><span id="ev-n3-arch-1"><ruby>本当<rt>ほんとう</rt></ruby>の<ruby>意味<rt>いみ</rt></ruby>で<ruby>人<rt>ひと</rt></ruby>を<ruby>成長<rt>せいちょう</rt></ruby>させるためには、<ruby>点数<rt>てんすう</rt></ruby>や<ruby>成果<rt>せいか</rt></ruby>そのものではなく、そこへ<ruby>至<rt>いた</rt></ruby>るまでにどれだけ<ruby>工夫<rt>くふう</rt></ruby>し<ruby>努力<rt>どりょく</rt></ruby>したかという「プロセス」を<ruby>認<rt>みと</rt></ruby>めてほめることが<ruby>不可欠<rt>ふかけつ</rt></ruby>なのです。</span></p>
</div>
""".strip(),
        translation_ru="Часто говорят, что воспитывать детей или подчинённых лучше «через похвалу». Действительно, когда человека хвалят, любому это приятно и придаёт мотивации.\nОднако, если постоянно хвалить только за итоговый результат («здорово!», «отлично получилось!»), возникает вредный побочный эффект: человек начинает панически бояться ошибок и перестаёт браться за трудные задачи.\nЧтобы способствовать подлинному росту, необходимо признавать и хвалить не сам балл или результат, а «процесс» — то, сколько усилий и изобретательности было приложено на пути к нему.",
        vocabulary_json=[
            {"word": "弊害", "furigana": "へいがい", "translation": "вредный побочный эффект"},
            {"word": "プロセス", "furigana": "ぷろせす", "translation": "процесс, путь достижения"},
            {"word": "不可欠", "furigana": "ふかけつ", "translation": "крайне необходимый"}
        ]
    )
    q_n3_arch_1 = Question(
        question_number=1,
        question_text="筆者によると、人を本当に成長させるためにはどのようにほめるべきか。",
        general_explanation="Правильный ответ — вариант 3. В предложении ev-n3-arch-1 прямо подчеркнуто: хвалить нужно не сам результат или оценку, а процесс стараний и приложенных усилий (そこへ至るまでの工夫や努力のプロセス).",
        evidence_span_id="ev-n3-arch-1"
    )
    q_n3_arch_1.options = [
        Option(option_number=1, option_text="良い点数や高い成果が出たときだけ大きくほめる。", is_correct=False, option_explanation="Неверно (Ловушка результата). Похвала только за результат развивает страх ошибок."),
        Option(option_number=2, option_text="失敗したときには一切何も言わずに見守る。", is_correct=False, option_explanation="Неверно. Автор не говорит о молчаливом игнорировании."),
        Option(option_number=3, option_text="結果に至るまでの努力や工夫の過程に注目してほめる。", is_correct=True, option_explanation="Верно! Пересказ тезиса: «プロセスを認めてほめることが不可欠»."),
        Option(option_number=4, option_text="難しいことに挑戦したときだけ結果を評価する。", is_correct=False, option_explanation="Неверно. Оценивать нужно процесс, а не итог.")
    ]
    text_n3_arch_short.questions = [q_n3_arch_1]

    # =========================================================================
    # 6. N3 ARCHIVE MEDIUM (中文): 電子書籍と紙の本 (2 Questions)
    # =========================================================================
    text_n3_arch_med = Text(
        title="電子書籍と紙の本の共存 (Электронные и бумажные книги)",
        level="N3",
        category="medium",
        source_exam="JLPT 2022.07 N3 過去問",
        is_nhk=False,
        recommended_time_min=4,
        content_html="""
<div class="passage-body">
    <p><ruby>近年<rt>きんねん</rt></ruby>、スマートフォンや専用リーダーで<ruby>電子書籍<rt>でんししょせき</rt></ruby>を<ruby>読<rt>よ</rt></ruby>む<ruby>人<rt>ひと</rt></ruby>が<ruby>急速<rt>きゅうそく</rt></ruby>に<ruby>増<rt>ふ</rt></ruby>えています。<ruby>何冊<rt>なんさつ</rt></ruby>もの<ruby>本<rt>ほん</rt></ruby>を<ruby>軽<rt>かる</rt></ruby>く<ruby>持<rt>も</rt></ruby>ち<ruby>歩<rt>ある</rt></ruby>け、いつでもどこでもすぐに<ruby>購入<rt>こうにゅう</rt></ruby>できる<ruby>利便性<rt>りべんせい</rt></ruby>は、<ruby>紙<rt>かみ</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>にはない<ruby>大<rt>おお</rt></ruby>きな<ruby>魅力<rt>みりょく</rt></ruby>です。</p>
    <p>そのため、「いずれ<ruby>紙<rt>かみ</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>は<ruby>完全<rt>かんぜん</rt></ruby>になくなるだろう」と<ruby>予測<rt>よそく</rt></ruby>する<ruby>専門家<rt>せんもんか</rt></ruby>もいました。<span id="ev-n3-arch-med-1">しかし実際には、紙の手触りやページの厚みによって「全体のどのあたりを読んでいるか」を五感で把握できる紙の本の需要は衰えていません。</span></p>
    <p><ruby>情報<rt>じょうほう</rt></ruby>を<ruby>素早<rt>すばや</rt></ruby>く<ruby>得<rt>え</rt></ruby>たいビジネス<ruby>書<rt>しょ</rt></ruby>やマンガは<ruby>電子<rt>でんし</rt></ruby>で、<ruby>繰<rt>く</rt></ruby>り<ruby>返<rt>かえ</rt></ruby>しじっくり<ruby>味<rt>あじ</rt></ruby>わいたい<ruby>小説<rt>しょうせつ</rt></ruby>は<ruby>紙<rt>かみ</rt></ruby>で、というように、<span id="ev-n3-arch-med-2">現代の読者は目的や好みに応じて両者を上手に使い分けて共存させているのです。</span></p>
</div>
""".strip(),
        translation_ru="В последние годы число читателей электронных книг стремительно растёт. Удобство носить множество книг с собой — огромное преимущество.\nНекоторые эксперты предрекали исчезновение бумажных книг. Однако тактильные ощущения и толщина страниц позволяют физически ощущать прогресс чтения, поэтому спрос на них не падает.\nСовременные читатели гармонично разделяют форматы: быстрый нон-фикшн читают в электронном виде, а романы — на бумаге.",
        vocabulary_json=[
            {"word": "利便性", "furigana": "りべんせい", "translation": "удобство, практичность"},
            {"word": "手触り", "furigana": "てざわり", "translation": "ощупь, тактильные ощущения"},
            {"word": "使い分ける", "furigana": "つかいわける", "translation": "дифференцированно использовать"}
        ]
    )
    q_n3_med_1 = Question(
        question_number=1,
        question_text="紙の本の需要が衰えない理由として、文章で挙げられているのはどれか。",
        general_explanation="Правильный ответ — вариант 2. В предложении ev-n3-arch-med-1 указано: бумажная книга позволяет физически ощущать осязанием и объемом страниц, где именно находится читатель.",
        evidence_span_id="ev-n3-arch-med-1"
    )
    q_n3_med_1.options = [
        Option(option_number=1, option_text="電子書籍より価格が安く購入しやすいから。", is_correct=False, option_explanation="Неверно. О цене книг в тексте речи нет."),
        Option(option_number=2, option_text="手触りや厚みによって読書の進み具合を五感で実感できるから。", is_correct=True, option_explanation="Верно! Полное соответствие фразе: «全体のどのあたりを読んでいるかを五感で把握できる»."),
        Option(option_number=3, option_text="スマートフォンよりも目が疲れにくいと専門家が証明したから。", is_correct=False, option_explanation="Неверно. Усталость глаз не упоминается."),
        Option(option_number=4, option_text="何冊もの本を一度に持ち運ぶのに便利だから。", is_correct=False, option_explanation="Неверно. Это плюс электронных книг.")
    ]
    q_n3_med_2 = Question(
        question_number=2,
        question_text="電子書籍と紙の本について、現代の読者はどのように接していると筆者は述べているか。",
        general_explanation="Правильный ответ — вариант 4. В предложении ev-n3-arch-med-2 автор заключает: читатели умело разграничивают форматы по целям (両者を上手に使い分けて共存させている).",
        evidence_span_id="ev-n3-arch-med-2"
    )
    q_n3_med_2.options = [
        Option(option_number=1, option_text="紙の本を読むのをやめ、すべて電子書籍に切り替えた。", is_correct=False, option_explanation="Неверно. Это противоречит тексту."),
        Option(option_number=2, option_text="小説もビジネス書も関係なく、常に紙の本だけを選んでいる。", is_correct=False, option_explanation="Неверно. Читатели активно используют электронный формат."),
        Option(option_number=3, option_text="電子書籍の不便さに気づき、再び紙の本しか買わなくなった。", is_correct=False, option_explanation="Неверно. Оба формата популярны."),
        Option(option_number=4, option_text="本のジャンルや読書の目的に合わせて、両方をうまく使い分けている。", is_correct=True, option_explanation="Верно! Пересказ: «目的や好みに応じて両者を上手に使い分けて共存させている».")
    ]
    text_n3_arch_med.questions = [q_n3_med_1, q_n3_med_2]

    # =========================================================================
    # 7. N3 INFO SEARCH: サクラ・フィットネスクラブ利用案内 (2 Questions)
    # =========================================================================
    text_n3_flyer = Text(
        title="サクラ・フィットネスクラブ ご利用案内 (Памятка фитнес-клуба Сакура)",
        level="N3",
        category="info_search",
        source_exam="JLPT N3 情報検索 典型題",
        is_nhk=False,
        recommended_time_min=5,
        content_html="""
<div class="flyer-container">
    <div class="flyer-header">
        <div class="flyer-badge">春の新規会員募集！</div>
        <h2 class="flyer-title"><ruby>桜<rt>さくら</rt></ruby>フィットネスクラブ <ruby>利用<rt>りよう</rt></ruby><ruby>案内<rt>あんない</rt></ruby></h2>
        <p class="flyer-subtitle">最新マシン・温水プール・スタジオレッスン完備！</p>
    </div>
    <table class="flyer-table">
        <thead>
            <tr><th>プラン名</th><th>利用可能時間</th><th>月会費（税込）</th></tr>
        </thead>
        <tbody>
            <tr><td>デイタイム</td><td>平日 10:00 〜 17:00</td><td>6,000円</td></tr>
            <tr><td>ナイト</td><td>平日 18:00 〜 22:00</td><td>6,500円</td></tr>
            <tr><td>ホリデー</td><td>土・日・祝日 10:00 〜 20:00</td><td>5,500円</td></tr>
            <tr class="highlight-row"><td>フルタイム</td><td>いつでも全日 10:00 〜 22:00</td><td>9,500円</td></tr>
        </tbody>
    </table>
    <div class="flyer-notes">
        <h3>【ご注意・各種割引について】</h3>
        <ul>
            <li><span id="ev-info-1"><strong>● 学生割引：</strong> 学生証提示で<strong>月会費が1,000円引き</strong>。（※ホリデープランは対象外）</span></li>
            <li><span id="ev-info-2"><strong>● 春のキャンペーン：</strong> 登録事務手数料<strong>3,000円がWeb申込で【0円（無料）】</strong>！</span></li>
            <li><strong>● 個人ロッカー：</strong> 月額1,100円（任意）。</li>
        </ul>
    </div>
</div>
""".strip(),
        translation_ru="Фитнес-клуб Сакура:\nТарифы: Дэйтайм - 6,000; Найт - 6,500; Холидэй - 5,500; Фуллтайм - 9,500.\nСкидки: Студентам -1,000 иен (кроме Холидэй). Регистрация 3,000 бесплатно при онлайн-заявке. Шкафчик 1,100 иен.",
        vocabulary_json=[
            {"word": "月会費", "furigana": "げっかいひ", "translation": "ежемесячный взнос"},
            {"word": "対象外", "furigana": "たいしょうがい", "translation": "исключение, не подпадает"}
        ]
    )
    q_n3_flyer_1 = Question(
        question_number=1,
        question_text="大学3年生のタナカさんは平日の夜（19時以降）と土曜日の午後に利用したい。学生割引を使って最も安く利用できるプランと月会費はどれか。",
        general_explanation="Правильный ответ — вариант 3. Нужны и будни вечер, и суббота. Подходит только 'フルタイム' (9,500). Со студенческой скидкой 1,000: 9,500 - 1,000 = 8,500円.",
        evidence_span_id="ev-info-1"
    )
    q_n3_flyer_1.options = [
        Option(option_number=1, option_text="ナイトプラン：5,500円", is_correct=False, option_explanation="Неверно. Не действует по субботам."),
        Option(option_number=2, option_text="ホリデープラン：4,500円", is_correct=False, option_explanation="Неверно. Не действует по будням вечером, плюс на него нет скидки."),
        Option(option_number=3, option_text="フルタイムプラン：8,500円", is_correct=True, option_explanation="Верно! Покрывает все дни, а со скидкой 1,000 получается 8,500 иен."),
        Option(option_number=4, option_text="フルタイムプラン：9,500円", is_correct=False, option_explanation="Неверно. 9,500 — базовая стоимость без студенческой скидки.")
    ]
    q_n3_flyer_2 = Question(
        question_number=2,
        question_text="タナカさんが今月中Webから入会し、個人ロッカーも申し込む場合、初月の合計金額はいくらか。",
        general_explanation="Правильный ответ — вариант 1. 8,500 (абонемент) + 0 (акция отменяет 3,000) + 1,100 (шкафчик) = 9,600円.",
        evidence_span_id="ev-info-2"
    )
    q_n3_flyer_2.options = [
        Option(option_number=1, option_text="9,600円", is_correct=True, option_explanation="Верно! 8,500 + 0 + 1,100 = 9,600 иен."),
        Option(option_number=2, option_text="12,600円", is_correct=False, option_explanation="Неверно. Ошибочно посчитали 3,000 за регистрацию."),
        Option(option_number=3, option_text="8,500円", is_correct=False, option_explanation="Неверно. Забыли 1,100 за шкафчик."),
        Option(option_number=4, option_text="10,600円", is_correct=False, option_explanation="Неверно. Забыли вычесть скидку студента.")
    ]
    text_n3_flyer.questions = [q_n3_flyer_1, q_n3_flyer_2]

    # =========================================================================
    # 8. N3 NHK NEWS ARTICLE (記事): フードロス削減に向けたスーパーのAI活用 (3 Questions)
    # =========================================================================
    text_n3_nhk = Text(
        title="食品ロスを減らすスーパーの挑戦：AIが値引き時間を判断 (Борьба с пищевыми отходами: AI в супермаркетах)",
        level="N3",
        category="article",
        source_exam="NHK World Japan News",
        is_nhk=True,
        recommended_time_min=5,
        content_html="""
<div class="nhk-article-badge">NHK WORLD-JAPAN NEWS</div>
<div class="passage-body">
    <p><ruby>日本<rt>にほん</rt></ruby>のスーパーマーケットでは、まだ<ruby>食<rt>た</rt></ruby>べられるのに<ruby>消費<rt>しょうひ</rt></ruby><ruby>期限<rt>きげん</rt></ruby>が<ruby>近<rt>ちか</rt></ruby>づいて<ruby>捨<rt>す</rt></ruby>てられてしまう「<ruby>食品<rt>しょくひん</rt>ロス」の<ruby>削減<rt>さくげん</rt></ruby>が<ruby>大<rt>おお</rt></ruby>きな<ruby>課題<rt>かだい</rt></ruby>となっています。これまで<ruby>惣菜<rt>そうざい</rt></ruby>やパンなどの<ruby>見切<rt>みき</rt></ruby>り<ruby>品<rt>ひん</rt></ruby>の<ruby>値引<rt>ねび</rt></ruby>きシールは、<ruby>店員<rt>てんいん</rt></ruby>が<ruby>経験<rt>けいけん</rt></ruby>と<ruby>勘<rt>かん</rt></ruby>に<ruby>頼<rt>たよ</rt></ruby>って<ruby>夕方<rt>ゆうがた</rt></ruby>に<ruby>貼<rt>は</rt></ruby>っていましたが、タイミングが<ruby>遅<rt>おそ</rt></ruby>いと<ruby>売<rt>う</rt></ruby>れ<ruby>残<rt>のこ</rt></ruby>り、<ruby>早<rt>はや</rt></ruby>すぎると<ruby>利益<rt>りえき</rt></ruby>が<ruby>減<rt>へ</rt></ruby>るという<ruby>悩<rt>なや</rt></ruby>みがありました。</p>
    <p><span id="ev-n3-nhk-1">そこで大手スーパーでは、過去の販売実績や当日の天気、周辺イベントの情報などを人工知能（AI）に分析させ、最適な値引き率と時間を提示するシステムを導入しました。</span>AIの<ruby>指示<rt>しじ</rt></ruby>に<ruby>基<rt>もと</rt></ruby>づいて<ruby>価格<rt>かかく</rt></ruby>を<ruby>下<rt>さ</rt></ruby>げることで、<ruby>作業<rt>さぎょう</rt></ruby>の<ruby>手間<rt>てま</rt></ruby>を<ruby>省<rt>はぶ</rt></ruby>きながら<ruby>廃棄<rt>はいき</rt></ruby>を<ruby>劇的<rt>げきてき</rt></ruby>に<ruby>減<rt>へ</rt></ruby>らすことに<ruby>成功<rt>せいこう</rt></ruby>しています。</p>
    <p><span id="ev-n3-nhk-2">さらにこのシステムは、消費者の購買意欲を促すだけでなく、閉店間際の従業員の作業負担を大幅に軽くするという副次的な効果も生み出しています。</span><ruby>環境<rt>かんきょう</rt></ruby>への<ruby>配慮<rt>はいりょ</rt></ruby>と<ruby>人手<rt>ひとで</rt></ruby><ruby>不足<rt>ぶそく</rt></ruby><ruby>対策<rt>たいさく</rt></ruby>の<ruby>両立<rt>りょうりつ</rt></ruby>として、<ruby>全国<rt>ぜんこく</rt></ruby>の<ruby>店舗<rt>てんぽ</rt></ruby>に<ruby>広<rt>ひろ</rt></ruby>がりを<ruby>見<rt>み</rt></ruby>せています。</p>
</div>
""".strip(),
        translation_ru="В супермаркетах Японии сокращение пищевых отходов (продуктов, выбрасываемых из-за истечения срока годности) стало острой задачей. Раньше скидочные стикеры клеили сотрудники на глаз: припозднишься — останется непроданным, поспешишь — упадёт прибыль.\nКрупные сети внедрили систему, где AI анализирует прошлые продажи, погоду и городские события, подсказывая точный момент и размер скидки.\nПомимо роста покупок, это существенно снизило нагрузку на персонал перед закрытием, помогая экологии и решая проблему нехватки кадров.",
        vocabulary_json=[
            {"word": "食品ロス", "furigana": "しょくひんろす", "translation": "пищевые отходы"},
            {"word": "惣菜", "furigana": "そうざい", "translation": "готовые блюда, кулинария"},
            {"word": "廃棄", "furigana": "はいき", "translation": "утилизация, списание в мусор"},
            {"word": "副次的な効果", "furigana": "ふくじてきなこうか", "translation": "вторичный (сопутствующий) эффект"}
        ]
    )
    q_n3_nhk_1 = Question(
        question_number=1,
        question_text="従来の店員による値引き作業にはどのような難しさがありましたか。",
        general_explanation="Правильный ответ — вариант 2. В первом абзаце указано: если снизить цену слишком рано — пострадает прибыль, если слишком поздно — товар испортится и пойдёт на выброс.",
        evidence_span_id="ev-n3-nhk-1"
    )
    q_n3_nhk_1.options = [
        Option(option_number=1, option_text="値引きシールを作るのに高額な機械が必要だったこと。", is_correct=False, option_explanation="Неверно. Про стоимость аппарата для печати стикеров ничего не говорится."),
        Option(option_number=2, option_text="値引きの時期が早すぎると利益が減り、遅すぎると廃棄になること。", is_correct=True, option_explanation="Верно! Точное повторение проблемы из текста: «タイミングが遅いと売れ残り、早すぎると利益が減る»."),
        Option(option_number=3, option_text="惣菜を買う客が年々減少していたこと。", is_correct=False, option_explanation="Неверно. Покупательский спрос не падал."),
        Option(option_number=4, option_text="天気予報をスーパーで確認することが禁止されていたこと。", is_correct=False, option_explanation="Неверно и абсурдно.")
    ]
    q_n3_nhk_2 = Question(
        question_number=2,
        question_text="AI値引きシステムはどのようなデータを使って判断していますか。",
        general_explanation="Правильный ответ — вариант 3. В предложении ev-n3-nhk-1 перечислено: прошлые продажи, погода в этот день и события вокруг магазина (過去の販売実績や当日の天気、周辺イベントの情報).",
        evidence_span_id="ev-n3-nhk-1"
    )
    q_n3_nhk_2.options = [
        Option(option_number=1, option_text="店員の年齢と経験年数のデータ", is_correct=False, option_explanation="Неверно. Опыт сотрудников AI как раз заменяет объективными данными."),
        Option(option_number=2, option_text="全国の他社スーパーの平均価格のみ", is_correct=False, option_explanation="Неверно. Цены конкурентов не упоминаются."),
        Option(option_number=3, option_text="過去の販売実績やその日の天気、周辺のイベント情報", is_correct=True, option_explanation="Верно! Прямое перечисление факторов из <span id='ev-n3-nhk-1'>."),
        Option(option_number=4, option_text="食品メーカーの製造コストの推移", is_correct=False, option_explanation="Неверно. Себестоимость производства не является ключевым параметром системы.")
    ]
    q_n3_nhk_3 = Question(
        question_number=3,
        question_text="このAIシステムがもたらした「副次的な効果」として正しいものはどれか。",
        general_explanation="Правильный ответ — вариант 1. В предложении ev-n3-nhk-2 прямо сказано: кроме снижения отходов, существенно уменьшилась нагрузка на персонал перед закрытием (閉店間際の従業員の作業負担を大幅に軽くする).",
        evidence_span_id="ev-n3-nhk-2"
    )
    q_n3_nhk_3.options = [
        Option(option_number=1, option_text="閉店近くの従業員の作業負担が軽くなったこと。", is_correct=True, option_explanation="Верно! Точное соответствие цитате в ev-n3-nhk-2: «従業員の作業負担を大幅に軽くするという副次的な効果»."),
        Option(option_number=2, option_text="店内の照明代が半分になったこと。", is_correct=False, option_explanation="Неверно. Расходы на освещение не рассматриваются."),
        Option(option_number=3, option_text="惣菜の種類を倍に増やすことができたこと。", is_correct=False, option_explanation="Неверно. Ассортимент не увеличивали."),
        Option(option_number=4, option_text="従業員を全員解雇して無人店舗にできたこと。", is_correct=False, option_explanation="Неверно. Система лишь помогает персоналу, а не увольняет его.")
    ]
    text_n3_nhk.questions = [q_n3_nhk_1, q_n3_nhk_2, q_n3_nhk_3]

    # =========================================================================
    # 9. N2 ARCHIVE SHORT: 適切に「断る」技術と責任 (1 Question)
    # =========================================================================
    text_n2_arch_short = Text(
        title="適切に「断る」技術と責任 (Умение грамотно отказывать)",
        level="N2",
        category="short",
        source_exam="JLPT 2020.12 N2 過去問",
        is_nhk=False,
        recommended_time_min=3,
        content_html="""
<div class="passage-body">
    <p><ruby>頼<rt>たの</rt></ruby>まれごとをされると、<ruby>相手<rt>あいて</rt></ruby>に<ruby>悪<rt>わる</rt></ruby>いと<ruby>感<rt>かん</rt></ruby>じてつい「はい」と<ruby>引<rt>ひ</rt></ruby>き<ruby>受<rt>う</rt></ruby>けてしまう<ruby>人<rt>ひと</rt></ruby>は<ruby>多<rt>おお</rt></ruby>い。しかし、<ruby>自分<rt>じぶん</rt></ruby>のキャパシティ（<ruby>許容量<rt>きょようりょう</rt></ruby>）を<ruby>超<rt>こ</rt></ruby>えた<ruby>仕事<rt>しごと</rt></ruby>を<ruby>抱<rt>かか</rt></ruby>え<ruby>込<rt>こ</rt></ruby>むと、かえって<ruby>締<rt>し</rt></ruby>め<ruby>切<rt>き</rt></ruby>りを<ruby>破<rt>やぶ</rt></ruby>ったりクオリティを<ruby>下<rt>さ</rt></ruby>げたりして、<ruby>結果的<rt>けっかてき</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>迷惑<rt>めいわく</rt></ruby>をかけることになる。</p>
    <p><span id="ev-n2-arch-1"><ruby>適切<rt>てきせつ</rt></ruby>に「断る」という行為は、決して不親切なのではなく、自らの責任を果たせる範囲を見極め、引き受けた仕事に対して誠実であり続けるためのプロフェッショナルとしての決断なのである。</span></p>
</div>
""".strip(),
        translation_ru="Многие люди соглашаются на любую просьбу из вежливости. Однако перегрузка приводит к срыву сроков и падению качества.\nГрамотный отказ — это не бестактность, а профессиональное решение, позволяющее очертить границы ответственности и качественно сделать уже взятую работу.",
        vocabulary_json=[
            {"word": "許容量", "furigana": "きょようりょう", "translation": "предел нагрузки"},
            {"word": "見極める", "furigana": "みきわめる", "translation": "трезво оценивать"}
        ]
    )
    q_n2_arch_1 = Question(
        question_number=1,
        question_text="「適切に断る」ことについて、筆者はどのように考えているか。",
        general_explanation="Правильный ответ — вариант 3. В ev-n2-arch-1 автор формулирует: отказ — это профессиональное действие для сохранения ответственности и качества работы.",
        evidence_span_id="ev-n2-arch-1"
    )
    q_n2_arch_1.options = [
        Option(option_number=1, option_text="人間関係を壊さないために、できる限り避けるべき行為だ。", is_correct=False, option_explanation="Неверно. Автор призывает уметь отказывать."),
        Option(option_number=2, option_text="相手への好意が足りないことを示す不親切な態度である。", is_correct=False, option_explanation="Неверно. Автор подчеркивает: «決して不親切なのではなく»."),
        Option(option_number=3, option_text="自分の責任の範囲を守り、誠実に仕事をするために必要な判断である。", is_correct=True, option_explanation="Верно! Перефразирование ключевого тезиса в <span id='ev-n2-arch-1'>."),
        Option(option_number=4, option_text="頼まれた仕事のクオリティを気にせずにすむ便利な手段である。", is_correct=False, option_explanation="Неверно. Отказ нужен для защиты качества.")
    ]
    text_n2_arch_short.questions = [q_n2_arch_1]

    # =========================================================================
    # 10. N2 NHK WORLD ARTICLE: 日本の伝統工芸とデジタル技術の融合 (2 Questions)
    # =========================================================================
    text_n2_nhk = Text(
        title="伝統工芸を守る3Dスキャン技術：後継者不足に挑む職人たち (Слияние традиционных ремёсел и 3D-технологий)",
        level="N2",
        category="article",
        source_exam="NHK World Japan Culture & Tech",
        is_nhk=True,
        recommended_time_min=6,
        content_html="""
<div class="nhk-article-badge">NHK WORLD-JAPAN IN-DEPTH</div>
<div class="passage-body">
    <p><ruby>何百年<rt>なんびゃくねん</rt></ruby>もの<ruby>歴史<rt>れきし</rt></ruby>を<ruby>誇<rt>ほこ</rt></ruby>る<ruby>日本<rt>にほん</rt></ruby>の<ruby>伝統<rt>でんとう</rt></ruby><ruby>工芸<rt>こうげい</rt></ruby>が、いま<ruby>深刻<rt>しんこく</rt></ruby>な<ruby>後継者<rt>こうけいしゃ</rt></ruby><ruby>不足<rt>ぶそく</rt></ruby>に<ruby>直面<rt>ちょくめん</rt></ruby>している。<ruby>熟練<rt>じゅくれん</rt></ruby>の<ruby>職人<rt>しょくにん</rt></ruby>が<ruby>長年<rt>ながねん</rt></ruby>の<ruby>修業<rt>しゅぎょう</rt></ruby>で<ruby>培<rt>つちか</rt></ruby>った「<ruby>手<rt>て</rt></ruby>の<ruby>感覚<rt>かんかく</rt>」や「<ruby>勘<rt>かん</rt>」といった<ruby>暗黙知<rt>あんもくち</rt></ruby>は、<ruby>言葉<rt>ことば</rt></ruby>やマニュアルで<ruby>伝承<rt>でんしょう</rt></ruby>することが<ruby>極<rt>きわ</rt></ruby>めて<ruby>困難<rt>こんなん</rt></ruby>であり、<ruby>高齢化<rt>こうれいか</rt></ruby>とともにその<ruby>技術<rt>ぎじゅつ</rt></ruby>が<ruby>永遠<rt>えいえん</rt></ruby>に<ruby>失<rt>うしな</rt></ruby>われる<ruby>危機<rt>きき</rt></ruby>にあった。</p>
    <p><span id="ev-n2-nhk-1">こうした状況を打破するため、京都の西陣織や石川県の輪島塗の工房では、職人の指先の繊細な動きをモーションキャプチャーや高精度3Dスキャナーでデジタル数値化する試みが始まった。</span>かつては何年もかかっていた基本動作の習得期間が、データによる可視化で大幅に短縮され、若手や外国人クリエイターの参入障壁を下げることに成功している。</p>
    <p><span id="ev-n2-nhk-2">一部からは「機械に頼れば伝統の魂が失われる」との懸念の声もあったが、現場の職人は「記録できる技術をデジタルに残すからこそ、人間にしか生み出せない美の追求に専念できる」と語る。</span>デジタル化は伝統を破壊するのではなく、むしろ次世代へとつなぐ最強の防壁となりつつある。</p>
</div>
""".strip(),
        translation_ru="Японские ремёсла с вековой историей столкнулись с дефицитом преемников. Негласные навыки и интуиция мастеров тяжело поддаются описанию в инструкциях и рискуют исчезнуть со старением мастеров.\nВ Киото и Исикаве движения пальцев мастеров начали оцифровывать с помощью захвата движения и 3D-сканеров. Это позволило визуализировать базовые техники и сократить годы обучения для молодых специалистов.\nНесмотря на опасения о «потере души ремесла», сами мастера отмечают: оцифровка базовой техники освобождает время для чистого творчества, сохраняя наследие.",
        vocabulary_json=[
            {"word": "暗黙知", "furigana": "あんもくち", "translation": "неявное (интуитивное) знание"},
            {"word": "伝承する", "furigana": "でんしょうする", "translation": "передавать из поколения в поколение"},
            {"word": "可視化", "furigana": "かしか", "translation": "визуализация"},
            {"word": "懸念", "furigana": "けねん", "translation": "опасение, тревога"}
        ]
    )
    q_n2_nhk_1 = Question(
        question_number=1,
        question_text="伝統工芸の技術の継承がこれまで困難であった理由として、文章で述べられているのはどれか。",
        general_explanation="Правильный ответ — вариант 3. В первом абзаце указано: мастерство основано на интуиции и руках (暗黙知), что крайне трудно описать словами или в инструкциях (言葉やマニュアルで伝承することが極めて困難).",
        evidence_span_id="ev-n2-nhk-1"
    )
    q_n2_nhk_1.options = [
        Option(option_number=1, option_text="道具の原材料が世界的に高騰し手に入らなくなったから。", is_correct=False, option_explanation="Неверно. Про сырье речь не идет."),
        Option(option_number=2, option_text="若い世代が伝統工芸品を一切買わなくなったから。", is_correct=False, option_explanation="Неверно. Говорится о нехватке мастеров, а не о спросе."),
        Option(option_number=3, option_text="職人の技が言葉やマニュアルで表しにくい感覚的なものだったから。", is_correct=True, option_explanation="Верно! Пересказ: «手の感覚や勘といった暗黙知は言葉で伝承することが困難»."),
        Option(option_number=4, option_text="海外の安価な機械製品との競争に敗れたから。", is_correct=False, option_explanation="Неверно. Это не указано в тексте.")
    ]
    q_n2_nhk_2 = Question(
        question_number=2,
        question_text="デジタル技術を導入することに対して、現場の職人はどのように考えているか。",
        general_explanation="Правильный ответ — вариант 4. В предложении ev-n2-nhk-2 мастера говорят: сохраняя технику в цифре, они могут сосредоточиться на уникальной красоте, которую способен создать только человек.",
        evidence_span_id="ev-n2-nhk-2"
    )
    q_n2_nhk_2.options = [
        Option(option_number=1, option_text="機械が職人の代わりになり、人間は一切作業しなくて済むと考えている。", is_correct=False, option_explanation="Неверно. Человеческий труд по-прежнему в центре процесса."),
        Option(option_number=2, option_text="伝統の魂が失われるため、今すぐに利用をやめるべきだと主張している。", is_correct=False, option_explanation="Неверно. Это было лишь опасением критиков со стороны."),
        Option(option_number=3, option_text="外国人クリエイターに工房をすべて任せる手段だと捉えている。", is_correct=False, option_explanation="Неверно."),
        Option(option_number=4, option_text="技術を記録することで、人間にしか生み出せない美の追求に集中できると考えている。", is_correct=True, option_explanation="Верно! Точное соответствие цитате в ev-n2-nhk-2: «人間にしか生み出せない美の追求に専念できる».")
    ]
    text_n2_nhk.questions = [q_n2_nhk_1, q_n2_nhk_2]

    # =========================================================================
    # 11. N2 ARCHIVE LONG ARTICLE: デジタル時代における「無駄な時間」の価値 (2 Questions)
    # =========================================================================
    text_n2_article = Text(
        title="デジタル時代における「無駄な時間」の価値 (Ценность «потерянного времени» в цифровую эпоху)",
        level="N2",
        category="article",
        source_exam="JLPT 2021.07 N2 過去問",
        is_nhk=False,
        recommended_time_min=6,
        content_html="""
<div class="passage-body">
    <p><ruby>現代<rt>げんだい</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>においては、あらゆる<ruby>場面<rt>ばめん</rt></ruby>で「タイパ（タイムパフォーマンス）」や「<ruby>効率<rt>こうりつ</rt>」が<ruby>最優先<rt>さいゆうせん</rt></ruby>されるようになった。<ruby>動画<rt>どうが</rt></ruby>を<ruby>倍速<rt>ばいそく</rt></ruby>で<ruby>視聴<rt>しちょう</rt></ruby>し、<ruby>要約<rt>ようやく</rt></ruby>された情報だけを<ruby>手早<rt>てばや</rt></ruby>く<ruby>消費<rt>しょうひ</rt></ruby>するスタイルは、<ruby>情報<rt>じょうほう</rt></ruby><ruby>過多<rt>かた</rt></ruby>の<ruby>時代<rt>じだい</rt></ruby>を<ruby>生<rt>い</rt></ruby>き<ruby>抜<rt>ぬ</rt></ruby>くための<ruby>合理的<rt>ごうりてき</rt></ruby>な<ruby>手段<rt>しゅだん</rt></ruby>のようにも<ruby>見<rt>み</rt></ruby>える。</p>
    <p>しかし、<ruby>知識<rt>ちしき</rt></ruby>の<ruby>獲得<rt>かくとく</rt></ruby>と<ruby>真<rt>しん</rt></ruby>の<ruby>思考<rt>しこう</rt></ruby>は<ruby>決<rt>けっ</rt></ruby>して<ruby>同義<rt>どうぎ</rt></ruby>ではない。<span id="ev-n2-1">あらかじめ結論が整えられた情報ばかりを摂取していると、物事の背景にある文脈や、一見矛盾するように見える複雑なニュアンスを自らの頭で咀嚼する力が急速に衰えてしまう。</span></p>
    <p>かつて<ruby>思索<rt>しさく</rt></ruby>とは、<ruby>迷<rt>まよ</rt></ruby>い、<ruby>立<rt>た</rt></ruby>ち<ruby>止<rt>ど</rt></ruby>まり、あてもなく<ruby>考<rt>かんが</rt></ruby>えを<ruby>巡<rt>めぐ</rt></ruby>らせるという、ある<ruby>種<rt>しゅ</rt></ruby>の「<ruby>無駄<rt>むだ</rt>」の<ruby>中<rt>なか</rt></ruby>にこそ<ruby>宿<rt>やど</rt></ruby>るものであった。<span id="ev-n2-2">効率化を突き詰めた先にあるのは、画一的な正解を素早く出力する機械のような人間であり、そこからは新たな価値や深い洞察は生まれにくいのではないか。</span></p>
    <p>われわれは<ruby>今<rt>いま</rt></ruby>こそ、<ruby>成果<rt>せいか</rt></ruby>に<ruby>直結<rt>ちょっけつ</rt></ruby>しない「<ruby>余白<rt>よはく</rt>の<ruby>時間<rt>じかん</rt></ruby>」を<ruby>恐<rt>おそ</rt></ruby>れず、<ruby>自<rt>みずか</rt></ruby>らを<ruby>深<rt>ふか</rt></ruby>めるための<ruby>贅沢<rt>ぜいたく</rt></ruby>として<ruby>取<rt>と</rt></ruby>り<ruby>戻<rt>もど</rt></ruby>すべきなのである。</p>
</div>
""".strip(),
        translation_ru="В современном обществе скорость и эффективность стали культом. Видео на скорости x2 и краткие дайджесты кажутся выходом.\nНо накопление готовой информации не равно мышлению. Потребляя лишь готовые выжимки, человек разучивается самостоятельно осмысливать контекст.\nПогоня за продуктивностью делает человека машиной для типовых ответов. Нам нужно вернуть себе роскошь 'пауз и неторопливого размышления'.",
        vocabulary_json=[
            {"word": "タイムパフォーマンス", "furigana": "たいむぱふぉーまんす", "translation": "тайпа (эффективность затраченного времени)"},
            {"word": "咀嚼する", "furigana": "そしゃくする", "translation": "глубоко переваривать, осмысливать"},
            {"word": "余白", "furigana": "よはく", "translation": "пауза, резерв времени"}
        ]
    )
    q_n2_art_1 = Question(
        question_number=1,
        question_text="「要約された情報ばかりを摂取している」ことの弊害として、筆者が指摘しているのはどれか。",
        general_explanation="Правильный ответ — вариант 2. В абзаце ev-n2-1 прямо указано: атрофируется способность самому глубоко переваривать контекст и противоречия.",
        evidence_span_id="ev-n2-1"
    )
    q_n2_art_1.options = [
        Option(option_number=1, option_text="新しい情報技術に適応できなくなること。", is_correct=False, option_explanation="Неверно. Автор не говорит о трудностях с технологиями."),
        Option(option_number=2, option_text="物事の文脈や複雑な意味を、自分の頭で深く考える力が弱まること。", is_correct=True, option_explanation="Верно! Пересказ: «自らの頭で咀嚼する力が急速に衰えてしまう»."),
        Option(option_number=3, option_text="動画を倍速で見ることで、視力や集中力が低下すること。", is_correct=False, option_explanation="Неверно. Физиология не упоминается."),
        Option(option_number=4, option_text="他者と知識の量を競い合うようになってしまうこと。", is_correct=False, option_explanation="Неверно.")
    ]
    q_n2_art_2 = Question(
        question_number=2,
        question_text="筆者がこの文章で最も主張したいことは何か。",
        general_explanation="Правильный ответ — вариант 4. Главный вывод: не бояться пауз и времени без сиюминутной пользы ради глубины собственного разума.",
        evidence_span_id="ev-n2-2"
    )
    q_n2_art_2.options = [
        Option(option_number=1, option_text="仕事の効率を上げるために、タイパを意識した生活を徹底すべきだ。", is_correct=False, option_explanation="Неверно. Автор критикует тотальную оптимизацию."),
        Option(option_number=2, option_text="人間はAI機械には勝てないので、知識を暗記するのはやめるべきだ。", is_correct=False, option_explanation="Неверно."),
        Option(option_number=3, option_text="インターネット上の要約サイトや倍速視聴の利用を法律で禁止すべきだ。", is_correct=False, option_explanation="Неверно."),
        Option(option_number=4, option_text="効率ばかりを追わず、思索を深めるための「余白の時間」を取り戻すべきだ。", is_correct=True, option_explanation="Верно! Истинная мысль заключительного предложения текста.")
    ]
    text_n2_article.questions = [q_n2_art_1, q_n2_art_2]

    # =========================================================================
    # 12. N1 ARCHIVE EDITORIAL: 他者理解の不可能性と誠実さ (2 Questions)
    # =========================================================================
    text_n1 = Text(
        title="他者理解の不可能性と誠実さ (Невозможность полного понимания Другого)",
        level="N1",
        category="long",
        source_exam="JLPT 2022.12 N1 過去問",
        is_nhk=False,
        recommended_time_min=7,
        content_html="""
<div class="passage-body">
    <p><ruby>他者<rt>たしゃ</rt></ruby>を「<ruby>理解<rt>りかい</rt></ruby>する」とは<ruby>一体<rt>いったい</rt></ruby>どういうことなのだろうか。<ruby>現代<rt>げんだい</rt></ruby>のコミュニケーションにおいては、SNSなどを<ruby>通<rt>つう</rt></ruby>じて「わかりやすさ」や「<ruby>即時的<rt>そくじてき</rt></ruby>な<ruby>共感<rt>きょうかん</rt>」ばかりが<ruby>称揚<rt>しょうよう</rt></ruby>される<ruby>傾向<rt>けいこう</rt></ruby>にある。しかし、<ruby>安易<rt>あんい</rt></ruby>に「あなたの<ruby>気持<rt>きも</rt></ruby>ちがよくわかる」と<ruby>口<rt>くち</rt></ruby>にすることは、かえって<ruby>相手<rt>あいて</rt></ruby>の<ruby>抱<rt>かか</rt></ruby>える<ruby>固有<rt>こゆう</rt></ruby>の<ruby>痛<rt>いた</rt></ruby>みや<ruby>複雑<rt>ふくざつ</rt></ruby>さを、<ruby>自<rt>みずか</rt></ruby>らの<ruby>貧弱<rt>ひんじゃく</rt></ruby>な<ruby>尺度<rt>しゃくど</rt></ruby>へと<ruby>矮小化<rt>わいしょうか</rt></ruby>してしまう<ruby>暴挙<rt>ぼうきょ</rt></ruby>になりかねない。</p>
    <p><span id="ev-n1-1"><ruby>真<rt>しん</rt></ruby>の<ruby>対話<rt>たいわ</rt></ruby>の<ruby>出発点<rt>しゅっぱつてん</rt></ruby>とは、「<ruby>自分<rt>じぶん</rt></ruby>には<ruby>他者<rt>たしゃ</rt></ruby>のすべてを<ruby>完全<rt>かんぜん</rt></ruby>に<ruby>分<rt>わ</rt></ruby>かりきることはできない」という、ある<ruby>種<rt>しゅ</rt></ruby>の<ruby>絶対的<rt>ぜったいてき</rt></ruby>な<ruby>断絶<rt>だんぜつ</rt></ruby>を<ruby>謙虚<rt>けんきょ</rt></ruby>に<ruby>受<rt>う</rt></ruby>け<ruby>入<rt>い</rt></ruby>れることにほかならない。</span>どれほど<ruby>言葉<rt>ことば</rt></ruby>を<ruby>尽<rt>つ</rt></ruby>くしても<ruby>埋<rt>う</rt></ruby>まらない<ruby>溝<rt>みぞ</rt></ruby>があるからこそ、われわれは<ruby>耳<rt>みみ</rt></ruby>を<ruby>傾<rt>かたむ</rt></ruby>け<ruby>続<rt>つづ</rt></ruby>け、<ruby>想像力<rt>そうぞうりょく</rt></ruby>を<ruby>働<rt>はたら</rt></ruby>かせようとするのである。</p>
    <p><span id="ev-n1-2"><ruby>分<rt>わ</rt></ruby>かりあえないという<ruby>絶望<rt>ぜつぼう</rt></ruby>を<ruby>踏<rt>ふ</rt></ruby>まえた<ruby>上<rt>うえ</rt></ruby>でなお、<ruby>相手<rt>あいて</rt></ruby>の<ruby>言葉<rt>ことば</rt></ruby>の<ruby>響<rt>ひび</rt></ruby>きに<ruby>寄<rt>よ</rt></ruby>り<ruby>添<rt>そ</rt></ruby>おうとする<ruby>不断<rt>ふだん</rt></ruby>の<ruby>姿勢<rt>しせい</rt></ruby>こそが、<ruby>人間<rt>にんげん</rt></ruby>が<ruby>紡<rt>つむ</rt></ruby>ぎうる<ruby>最<rt>もっと</rt></ruby>も<ruby>誠実<rt>せいじつ</rt></ruby>な<ruby>関係性<rt>かんけいせい</rt></ruby>なのではないだろうか。</span></p>
</div>
""".strip(),
        translation_ru="Что значит понять другого? В соцсетях превозносится мгновенное сопереживание. Но легко брошенное 'я тебя понимаю' низводит чужую боль до собственных рамок.\nДиалог начинается с признания пропасти между нами. Зная о ней, мы продолжаем чутко слушать и пытаться понять другого — в этом высшая искренность отношений.",
        vocabulary_json=[
            {"word": "称揚する", "furigana": "しょうようする", "translation": "превозносить"},
            {"word": "矮小化", "furigana": "わいしょうか", "translation": "умаление, упрощение"},
            {"word": "断絶", "furigana": "だんぜつ", "translation": "разрыв, непреодолимая пропасть"}
        ]
    )
    q_n1_1 = Question(
        question_number=1,
        question_text="筆者によると、「真の対話の出発点」とはどのようなことか。",
        general_explanation="Правильный ответ — вариант 3. В ev-n1-1 автор прямо утверждает: исходный пункт диалога — смиренное признание того, что до конца понять другого невозможно (他者を完全に分かりきることはできないと受け入れること).",
        evidence_span_id="ev-n1-1"
    )
    q_n1_1.options = [
        Option(option_number=1, option_text="SNSを通じて互いの意見を即時的に共有し合うこと。", is_correct=False, option_explanation="Неверно. Автор критикует поверхностность мгновенных реакций."),
        Option(option_number=2, option_text="相手の気持ちを自分の尺度に当てはめて共感すること。", is_correct=False, option_explanation="Неверно. Сведение чужих чувств к своим меркам автор называет насилием."),
        Option(option_number=3, option_text="他者を完全に理解することはできないという断絶を認めること。", is_correct=True, option_explanation="Верно! Прямое совпадение с ключевым тезисом в <span id='ev-n1-1'>."),
        Option(option_number=4, option_text="言葉を使わずに感情だけで分かり合える関係を築くこと。", is_correct=False, option_explanation="Неверно.")
    ]
    q_n1_2 = Question(
        question_number=2,
        question_text="この文章の結びとして、筆者が最も伝えたいことはどれか。",
        general_explanation="Правильный ответ — вариант 1. Согласно ev-n1-2, самая искренняя форма отношений — зная о непреодолимой пропасти, всё равно продолжать чутко слушать и пытаться понять другого.",
        evidence_span_id="ev-n1-2"
    )
    q_n1_2.options = [
        Option(option_number=1, option_text="完全には理解し合えないと知りつつも、相手に寄り添い続けようとする姿勢が大切だ。", is_correct=True, option_explanation="Верно! Квинтэссенция мысли автора из предложения с тегом ev-n1-2."),
        Option(option_number=2, option_text="分かり合えない人間関係には意味がないので、孤独を受け入れるべきだ。", is_correct=False, option_explanation="Неверно. Автор не призывает закрываться в одиночестве."),
        Option(option_number=3, option_text="誤解を避けるために、言葉数をできるだけ少なく抑えるべきだ。", is_correct=False, option_explanation="Неверно."),
        Option(option_number=4, option_text="自分とまったく同じ考えを持つ人だけと付き合うのが誠実さである。", is_correct=False, option_explanation="Неверно.")
    ]
    text_n1.questions = [q_n1_1, q_n1_2]

    all_texts = [
        text_n5_1,
        text_n5_2,
        text_n4_kyoto,
        text_n4_nhk,
        text_n3_arch_short,
        text_n3_arch_med,
        text_n3_flyer,
        text_n3_nhk,
        text_n2_arch_short,
        text_n2_nhk,
        text_n2_article,
        text_n1
    ]

    db.add_all(all_texts)
    db.commit()
    print(f"Database successfully seeded with {len(all_texts)} high-quality JLPT texts across N5-N1!")
    db.close()


if __name__ == "__main__":
    seed_database()
