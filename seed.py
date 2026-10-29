import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, engine, Base
from models import Text, Question, Option


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Re-seed to ensure all 8 comprehensive texts are present
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Text).delete()
    db.commit()

    print("Seeding rich multi-level JLPT Dokkai texts (N5, N4, N3, N2, N1)...")

    # =========================================================================
    # 1. N5: Short Memo (短文) - スミスさんのメモ
    # =========================================================================
    n5_memo_content = """
<div class="passage-body">
    <p>タナカさんへ</p>
    <p><ruby>昨日<rt>きのう</rt></ruby><ruby>話<rt>はな</rt></ruby>した<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>辞書<rt>じしょ</rt></ruby>を<ruby>持<rt>も</rt></ruby>ってきました。<ruby>机<rt>つくえ</rt></ruby>の<ruby>上<rt>うえ</rt></ruby>に<ruby>置<rt>お</rt></ruby>いておきますね。</p>
    <p><span id="ev-n5-1"><ruby>今日<rt>きょう</rt></ruby>は５<ruby>時<rt>じ</rt></ruby>から<ruby>図書館<rt>としょかん</rt></ruby>でアルバイトがあるので、４<ruby>時<rt>じ</rt></ruby><ruby>半<rt>はん</rt></ruby>に<ruby>教室<rt>きょうしつ</rt></ruby>を<ruby>出<rt>で</rt></ruby>ます。</span>もし<ruby>質問<rt>しつもん</rt></ruby>があったら、それまでに<ruby>聞<rt>き</rt></ruby>いてください。</p>
    <p>スミスより</p>
</div>
""".strip()

    text_n5_1 = Text(
        title="スミスさんからのメモ (Записка от Смита)",
        level="N5",
        category="short",
        recommended_time_min=2,
        content_html=n5_memo_content,
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
        general_explanation="Правильный ответ — вариант 2. Смит прямо указывает, что уходит в 4:30, и просит задать вопросы до этого времени (それまでに).",
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
    # 2. N5: Information Search (情報検索) - バーベキュー大会
    # =========================================================================
    n5_bbq_content = """
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
            <li><span id="ev-n5-bbq-2">● <ruby>雨<rt>あめ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>は<ruby>中止<rt>ちゅうし</rt></ruby>になります。<ruby>朝<rt>あさ</rt></ruby>8<ruby>時<rt>じ</rt></ruby>にホームページでお<ruby>知<rt>し</rt></ruby>らせします。</span></li>
        </ul>
    </div>
</div>
""".strip()

    text_n5_2 = Text(
        title="留学生バーベキュー大会のお知らせ (Объявление о барбекю)",
        level="N5",
        category="info_search",
        recommended_time_min=3,
        content_html=n5_bbq_content,
        translation_ru="Объявление о барбекю для иностранных студентов:\nДата: 12 мая (вс) 11:00 - 15:00.\nМесто: парк Мидори (5 мин пешком от южного выхода).\nВзнос: 1,500 иен (еда и чай).\nВажные примечания:\n- Чай есть, но соки и другие любимые напитки приносите с собой сами.\n- В случае дождя мероприятие отменяется. Объявление будет опубликовано в 8 утра на сайте.",
        vocabulary_json=[
            {"word": "お知らせ", "furigana": "おしらせ", "translation": "объявление, извещение"},
            {"word": "参加費", "furigana": "さんかひ", "translation": "взнос за участие"},
            {"word": "中止", "furigana": "ちゅうし", "translation": "отмена мероприятия"},
            {"word": "南口", "furigana": "みなみぐち", "translation": "южный выход станции"}
        ]
    )
    q_n5_2 = Question(
        question_number=1,
        question_text="バーベキューに参加する人は、何を自分で持って行かなければなりませんか。",
        general_explanation="Правильный ответ — вариант 3. В примечании с id='ev-n5-bbq-1' прямо написано, что чай и еда включены, а соки и свои напитки нужно принести самому.",
        evidence_span_id="ev-n5-bbq-1"
    )
    q_n5_2.options = [
        Option(option_number=1, option_text="バーベキューのお肉", is_correct=False, option_explanation="Неверно. Еда входит в стоимость участия 1,500 иен."),
        Option(option_number=2, option_text="飲むためのお茶", is_correct=False, option_explanation="Неверно. Чай уже предоставляется организаторами (お茶はあります)."),
        Option(option_number=3, option_text="ジュースなどの好きな飲み物", is_correct=True, option_explanation="Верно! Свои любимые напитки нужно приносить самостоятельно."),
        Option(option_number=4, option_text="雨の日のための傘", is_correct=False, option_explanation="Неверно. В дождь барбекю отменяется совсем, зонт не поможет.")
    ]
    text_n5_2.questions = [q_n5_2]

    # =========================================================================
    # 3. N4: Short Trap (短文) - ゴミの分別
    # =========================================================================
    n4_trash_content = """
<div class="passage-body">
    <p>このアパートの<ruby>住人<rt>じゅうにん</rt></ruby>の<ruby>皆<rt>みな</rt></ruby>さんへ。</p>
    <p><ruby>最近<rt>さいきん</rt></ruby>、ゴミの<ruby>出<rt>だ</rt></ruby>し<ruby>方<rt>かた</rt></ruby>のルールが<ruby>守<rt>まも</rt></ruby>られておらず、<ruby>近所<rt>きんじょ</rt></ruby>からの<ruby>苦情<rt>くじょう</rt></ruby>が<ruby>増<rt>ふ</rt></ruby>えています。</p>
    <p><ruby>燃<rt>も</rt></ruby>えるゴミは<ruby>火曜日<rt>かようび</rt></ruby>と<ruby>金曜日<rt>きんようび</rt></ruby>の<ruby>朝<rt>あさ</rt></ruby>8<ruby>時<rt>じ</rt></ruby>までに出してください。<span id="ev-n4-trash-1">缶やビンなどの資源ゴミは水曜日ですが、前日の夜に出すと猫やカラスが荒らすので、必ず当日の朝に出すようにしてください。</span></p>
    <p>ルールを<ruby>守<rt>まも</rt></ruby>って、きれいな<ruby>環境<rt>かんきょう</rt></ruby>をつくりましょう。</p>
</div>
""".strip()

    text_n4_trash = Text(
        title="アパートのゴミ出しのルール (Правила вывоза мусора в апартаментах)",
        level="N4",
        category="short",
        recommended_time_min=3,
        content_html=n4_trash_content,
        translation_ru="Всем жильцам апартаментов!\nВ последнее время правила выброса мусора нарушаются, участились жалобы от соседей.\nСжигаемый мусор выносите по вторникам и пятницам до 8:00 утра. Вторсырьё (жестяные банки и бутылки) собирается по средам, однако выносить мусор накануне вечером запрещено во избежание разорения кошками и воронами — обязательно выносите строго утром в день сбора.",
        vocabulary_json=[
            {"word": "分別", "furigana": "ぶんべつ", "translation": "сортировка, разделение"},
            {"word": "苦情", "furigana": "くじょう", "translation": "жалоба, претензия"},
            {"word": "資源ゴミ", "furigana": "しげんごみ", "translation": "вторсырьё (банки, стекло, бумага)"},
            {"word": "荒らす", "furigana": "あらす", "translation": "разорять, разбрасывать"}
        ]
    )
    q_n4_trash = Question(
        question_number=1,
        question_text="ビンのゴミを出すとき、どうしなければなりませんか。",
        general_explanation="Правильный ответ — вариант 4. В предложении ev-n4-trash-1 указано: вторсырье вывозят по средам, и выносить его накануне вечером нельзя — строго утром в среду.",
        evidence_span_id="ev-n4-trash-1"
    )
    q_n4_trash.options = [
        Option(option_number=1, option_text="火曜日の夜のうちに出しておく。", is_correct=False, option_explanation="Неверно (Ловушка времени). Накануне вечером выносить прямо запрещено из-за птиц и кошек."),
        Option(option_number=2, option_text="火曜日か金曜日の朝8時までに出す。", is_correct=False, option_explanation="Неверно. Вторник и пятница — дни сжигаемого мусора, а не бутылок."),
        Option(option_number=3, option_text="水曜日の夜、暗くなってから出す。", is_correct=False, option_explanation="Неверно. Мусор забирают утром, вечером мусоровоз уже проехал."),
        Option(option_number=4, option_text="水曜日の朝に出す。", is_correct=True, option_explanation="Верно! Стеклянные бутылки (ビン) относятся к ресурсному мусору и выносятся строго утром в среду.")
    ]
    text_n4_trash.questions = [q_n4_trash]

    # =========================================================================
    # 4. N4: Medium Travel (中文) - 京都の一人旅
    # =========================================================================
    n4_content = """
<div class="passage-body">
    <p><ruby>先週<rt>せんしゅう</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>初<rt>はじ</rt></ruby>めて<ruby>一人<rt>ひとり</rt></ruby>で<ruby>京都<rt>きょうと</rt></ruby>へ<ruby>旅行<rt>りょこう</rt></ruby>に<ruby>行<rt>い</rt></ruby>きました。<ruby>友達<rt>ともだち</rt></ruby>と<ruby>一緒<rt>いっしょ</rt></ruby>にいく<ruby>旅行<rt>りょこう</rt></ruby>もにぎやかで<ruby>楽<rt>たの</rt></ruby>しいですが、いつも<ruby>相手<rt>あいて</rt></ruby>の<ruby>行<rt>い</rt></ruby>きたい<ruby>場所<rt>ばしょ</rt></ruby>や<ruby>時間<rt>じかん</rt></ruby>に<ruby>合<rt>あ</rt></ruby>わせなければなりません。<span id="ev-n4-1">今回は自分の好きな時に好きな場所をゆっくり見たかったので、一人で行くことに決めました。</span></p>
    <p><ruby>京都<rt>きょうと</rt></ruby>では、<ruby>有名<rt>ゆうめい</rt></ruby>な<ruby>寺<rt>てら</rt></ruby>を<ruby>見<rt>み</rt></ruby>るだけでなく、<ruby>小<rt>ちい</rt></ruby>さな<ruby>通<rt>とお</rt></ruby>りをのんびり<ruby>散歩<rt>さんぽ</rt></ruby>しました。<span id="ev-n4-2">道に迷って偶然見つけた古い和菓子屋で食べたお茶と団子は、ガイドブックに載っているどんな店より美味しく感じられました。</span></p>
    <p><ruby>一人<rt>ひとり</rt></ruby>の<ruby>旅<rt>たび</rt></ruby>は<ruby>少<rt>すこ</rt></ruby>し<ruby>不安<rt>ふあん</rt></ruby>でしたが、<ruby>自分<rt>じぶん</rt></ruby>だけの<ruby>特別<rt>とくべつ</rt></ruby>な<ruby>思<rt>おも</rt></ruby>い<ruby>出<rt>で</rt></ruby>ができて、とてもよかったです。また<ruby>一人<rt>ひとり</rt></ruby>でどこかへ<ruby>行<rt>い</rt></ruby>ってみたいです。</p>
</div>
""".strip()

    text_n4_kyoto = Text(
        title="京都への一人旅 (Одиночное путешествие в Киото)",
        level="N4",
        category="medium",
        recommended_time_min=4,
        content_html=n4_content,
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
    # 5. N3: Short (短文) - ジョギングの落とし穴
    # =========================================================================
    n3_jogging_content = """
<div class="passage-body">
    <p><ruby>最近<rt>さいきん</rt></ruby>、<ruby>健康<rt>けんこう</rt></ruby>のために<ruby>毎朝<rt>まいあさ</rt></ruby>ジョギングを<ruby>始<rt>はじ</rt></ruby>める<ruby>人<rt>ひと</rt></ruby>が<ruby>増<rt>ふ</rt></ruby>えています。</p>
    <p><ruby>走<rt>はし</rt></ruby>ることは<ruby>手軽<rt>てがる</rt></ruby>にできて<ruby>気分<rt>きぶん</rt></ruby>も<ruby>爽<rt>さわ</rt></ruby>やかになるため、<ruby>長<rt>なが</rt></ruby>く<ruby>走<rt>はし</rt></ruby>れば<ruby>走<rt>はし</rt></ruby>るほど<ruby>体<rt>からだ</rt></ruby>にいいと<ruby>思<rt>おも</rt></ruby>われがちです。</p>
    <p>しかし、<ruby>急<rt>きゅう</rt></ruby>に<ruby>無理<rt>むり</rt></ruby>をして<ruby>長距離<rt>ちょうきょり</rt></ruby>を<ruby>走<rt>はし</rt></ruby>ると、かえって<ruby>膝<rt>ひざ</rt></ruby>や<ruby>心臓<rt>しんぞう</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>負担<rt>ふたん</rt></ruby>をかけてしまいます。</p>
    <p><span id="ev-1"><ruby>本当<rt>ほんとう</rt></ruby>に<ruby>大切<rt>たいせつ</rt></ruby>なのは、<ruby>距離<rt>きょり</rt></ruby>やスピードではなく、<ruby>自分<rt>じぶん</rt></ruby>のペースで<ruby>楽<rt>たの</rt></ruby>しく<ruby>続<rt>つづ</rt></ruby>けられる<ruby>運動量<rt>うんどうりょう</rt></ruby>を<ruby>保<rt>たも</rt></ruby>つことです。</span></p>
    <p><ruby>無理<rt>むり</rt></ruby>のない<ruby>習慣<rt>しゅうかん</rt></ruby>こそが、<ruby>健康<rt>けんこう</rt></ruby>への<ruby>一番<rt>いちばん</rt></ruby>の<ruby>近道<rt>ちかみち</rt></ruby>なのです。</p>
</div>
""".strip()

    text_n3_jogging = Text(
        title="健康のためのジョギングについて (О беге ради здоровья)",
        level="N3",
        category="short",
        recommended_time_min=3,
        content_html=n3_jogging_content,
        translation_ru="В последнее время растёт число людей, которые каждое утро начинают бегать трусцой ради здоровья.\nБегом легко заняться, поэтому часто думают, что чем дольше бегаешь, тем лучше.\nОднако резкие перегрузки создают чрезмерную нагрузку на колени и сердце.\nДействительно важно не расстояние или скорость, а сохранение такого объёма нагрузки, который можно поддерживать в своём комфортном темпе.",
        vocabulary_json=[
            {"word": "手軽に", "furigana": "てがるに", "translation": "легко, просто"},
            {"word": "〜がち", "furigana": "がち", "translation": "склонный к... / часто бывает так"},
            {"word": "かえって", "furigana": "かえって", "translation": "напротив, наоборот"},
            {"word": "負担", "furigana": "ふたん", "translation": "нагрузка, бремя"}
        ]
    )
    q_n3_jog = Question(
        question_number=1,
        question_text="筆者がジョギングについて最も言いたいことは何か。",
        general_explanation="Правильный ответ — вариант 3. В предложении 'ev-1' автор заключает: главное — не скорость и не километраж, а посильная привычка в комфортном темпе.",
        evidence_span_id="ev-1"
    )
    q_n3_jog.options = [
        Option(option_number=1, option_text="走る距離をできるだけ長くすることが最も効果的だ。", is_correct=False, option_explanation="Неверно (Ловушка стереотипа). Автор называет это опасным заблуждением."),
        Option(option_number=2, option_text="毎朝決まった時間に速いスピードで走ることが必要だ。", is_correct=False, option_explanation="Неверно. Скорость автором категорически не навязывается."),
        Option(option_number=3, option_text="自分のペースに合わせて、無理なく続けられる運動量を維持することが大切だ。", is_correct=True, option_explanation="Верно! Перефразирование ключевого тезиса в <span id='ev-1'>."),
        Option(option_number=4, option_text="膝や心臓を痛める危険があるので、ジョギングは避けたほうがよい。", is_correct=False, option_explanation="Неверно. Автор не призывает избегать бега, а советует не перегружаться.")
    ]
    text_n3_jogging.questions = [q_n3_jog]

    # =========================================================================
    # 6. N3: Info Search (情報検索) - フィットネスクラブ案内
    # =========================================================================
    n3_flyer_content = """
<div class="flyer-container">
    <div class="flyer-header">
        <div class="flyer-badge">春の新規会員募集！</div>
        <h2 class="flyer-title"><ruby>桜<rt>さくら</rt></ruby>フィットネスクラブ <ruby>利用<rt>りよう</rt></ruby><ruby>案内<rt>あんない</rt></ruby></h2>
        <p class="flyer-subtitle">最新マシン・温水プール・スタジオレッスン完備！</p>
    </div>
    <table class="flyer-table">
        <thead>
            <tr>
                <th>プラン名</th>
                <th>利用可能時間</th>
                <th>月会費（税込）</th>
            </tr>
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
""".strip()

    text_n3_flyer = Text(
        title="サクラ・フィットネスクラブ ご利用案内 (Памятка фитнес-клуба Сакура)",
        level="N3",
        category="info_search",
        recommended_time_min=5,
        content_html=n3_flyer_content,
        translation_ru="Фитнес-клуб Сакура:\nТарифы: Дэйтайм (будни день) - 6,000; Найт (будни вечер) - 6,500; Холидэй (выходные) - 5,500; Фуллтайм (всегда) - 9,500.\nСкидки: Студентам -1,000 иен (кроме Холидэй). Регистрация 3,000 бесплатно при онлайн-заявке. Шкафчик 1,100 иен.",
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
    # 7. N2: Column / Article (記事・論説) - タイパと無駄な時間
    # =========================================================================
    n2_article_content = """
<div class="passage-body">
    <p><ruby>現代<rt>げんだい</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>においては、あらゆる<ruby>場面<rt>ばめん</rt></ruby>で「タイパ（タイムパフォーマンス）」や「<ruby>効率<rt>こうりつ</rt>」が<ruby>最優先<rt>さいゆうせん</rt></ruby>されるようになった。<ruby>動画<rt>どうが</rt></ruby>を<ruby>倍速<rt>ばいそく</rt></ruby>で<ruby>視聴<rt>しちょう</rt></ruby>し、<ruby>要約<rt>ようやく</rt></ruby>された情報だけを<ruby>手早<rt>てばや</rt></ruby>く<ruby>消費<rt>しょうひ</rt></ruby>するスタイルは、<ruby>情報<rt>じょうほう</rt></ruby><ruby>過多<rt>かた</rt></ruby>の<ruby>時代<rt>じだい</rt></ruby>を<ruby>生<rt>い</rt></ruby>き<ruby>抜<rt>ぬ</rt></ruby>くための<ruby>合理的<rt>ごうりてき</rt></ruby>な<ruby>手段<rt>しゅだん</rt></ruby>のようにも<ruby>見<rt>み</rt></ruby>える。</p>
    <p>しかし、<ruby>知識<rt>ちしき</rt></ruby>の<ruby>獲得<rt>かくとく</rt></ruby>と<ruby>真<rt>しん</rt></ruby>の<ruby>思考<rt>しこう</rt></ruby>は<ruby>決<rt>けっ</rt></ruby>して<ruby>同義<rt>どうぎ</rt></ruby>ではない。<span id="ev-n2-1">あらかじめ結論が整えられた情報ばかりを摂取していると、物事の背景にある文脈や、一見矛盾するように見える複雑なニュアンスを自らの頭で咀嚼する力が急速に衰えてしまう。</span></p>
    <p>かつて<ruby>思索<rt>しさく</rt></ruby>とは、<ruby>迷<rt>まよ</rt></ruby>い、<ruby>立<rt>た</rt></ruby>ち<ruby>止<rt>ど</rt></ruby>まり、あてもなく<ruby>考<rt>かんが</rt></ruby>えを<ruby>巡<rt>めぐ</rt></ruby>らせるという、ある<ruby>種<rt>しゅ</rt></ruby>の「<ruby>無駄<rt>むだ</rt>」の<ruby>中<rt>なか</rt></ruby>にこそ<ruby>宿<rt>やど</rt></ruby>るものであった。<span id="ev-n2-2">効率化を突き詰めた先にあるのは、画一的な正解を素早く出力する機械のような人間であり、そこからは新たな価値や深い洞察は生まれにくいのではないか。</span></p>
    <p>われわれは<ruby>今<rt>いま</rt></ruby>こそ、<ruby>成果<rt>せいか</rt></ruby>に<ruby>直結<rt>ちょっけつ</rt></ruby>しない「<ruby>余白<rt>よはく</rt>の<ruby>時間<rt>じかん</rt></ruby>」を<ruby>恐<rt>おそ</rt></ruby>れず、<ruby>自<rt>みずか</rt></ruby>らを<ruby>深<rt>ふか</rt></ruby>めるための<ruby>贅沢<rt>ぜいたく</rt></ruby>として<ruby>取<rt>と</rt></ruby>り<ruby>戻<rt>もど</rt></ruby>すべきなのである。</p>
</div>
""".strip()

    text_n2_article = Text(
        title="デジタル時代における「無駄な時間」の価値 (Ценность «потерянного времени» в цифровую эпоху)",
        level="N2",
        category="article",
        recommended_time_min=6,
        content_html=n2_article_content,
        translation_ru="В современном обществе эффективность (тайпа) стала главным приоритетом. Видео на скорости x2 и дайджесты кажутся рациональными.\nОднако получение готовых знаний и глубокое мышление не тождественны. Потребляя лишь готовые выжимки, человек теряет способность самостоятельно понимать контекст и тонкие противоречия.\nРазмышление всегда требовало времени 'впустую'. Если всё механизировать, человек превратится в генератор шаблонных ответов. Нам нужно вернуть себе роскошь 'пустого времени' ради глубины мысли.",
        vocabulary_json=[
            {"word": "タイムパフォーマンス", "furigana": "たいむぱふぉーまんす", "translation": "тайпа (эффективность времени)"},
            {"word": "咀嚼する", "furigana": "そしゃくする", "translation": "глубоко осмысливать"},
            {"word": "画一的", "furigana": "かくいつてき", "translation": "шаблонный, одинаковый"},
            {"word": "余白", "furigana": "よはく", "translation": "пауза, резерв времени"}
        ]
    )
    q_n2_1 = Question(
        question_number=1,
        question_text="「要約された情報ばかりを摂取している」ことの弊害として、筆者が指摘しているのはどれか。",
        general_explanation="Правильный ответ — вариант 2. В абзаце ev-n2-1 прямо указано: атрофируется способность самому глубоко переваривать контекст и противоречия.",
        evidence_span_id="ev-n2-1"
    )
    q_n2_1.options = [
        Option(option_number=1, option_text="新しい情報技術に適応できなくなること。", is_correct=False, option_explanation="Неверно. Автор не говорит о неспособности освоить технологии."),
        Option(option_number=2, option_text="物事の文脈や複雑な意味を、自分の頭で深く考える力が弱まること。", is_correct=True, option_explanation="Верно! Пересказ: «自らの頭で咀嚼する力が急速に衰えてしまう»."),
        Option(option_number=3, option_text="動画を倍速で見ることで、視力や集中力が低下すること。", is_correct=False, option_explanation="Неверно. Физиологические последствия не упоминаются."),
        Option(option_number=4, option_text="他者と知識の量を競い合うようになってしまうこと。", is_correct=False, option_explanation="Неверно. Про соперничество в тексте речи нет.")
    ]

    q_n2_2 = Question(
        question_number=2,
        question_text="筆者がこの文章で最も主張したいことは何か。",
        general_explanation="Правильный ответ — вариант 4. Главный вывод: не бояться пауз и времени без сиюминутной пользы ради глубины собственного разума.",
        evidence_span_id="ev-n2-2"
    )
    q_n2_2.options = [
        Option(option_number=1, option_text="仕事の効率を上げるために、タイパを意識した生活を徹底すべきだ。", is_correct=False, option_explanation="Неверно. Автор критикует фанатичную погоню за эффективностью."),
        Option(option_number=2, option_text="人間はAI機械には勝てないので、知識を暗記するのはやめるべきだ。", is_correct=False, option_explanation="Неверно. Автор не делает такого вывода."),
        Option(option_number=3, option_text="インターネット上の要約サイトや倍速視聴の利用を法律で禁止すべきだ。", is_correct=False, option_explanation="Неверно. Автор не призывает к запретам."),
        Option(option_number=4, option_text="効率ばかりを追わず、思索を深めるための「余白の時間」を取り戻すべきだ。", is_correct=True, option_explanation="Верно! Истинная мысль заключительного предложения текста.")
    ]
    text_n2_article.questions = [q_n2_1, q_n2_2]

    # =========================================================================
    # 8. N1: Editorial / Philosophy (長文・論説文) - 読解の最高峰
    # =========================================================================
    n1_content = """
<div class="passage-body">
    <p><ruby>他者<rt>たしゃ</rt></ruby>を「<ruby>理解<rt>りかい</rt></ruby>する」とは<ruby>一体<rt>いったい</rt></ruby>どういうことなのだろうか。<ruby>現代<rt>げんだい</rt></ruby>のコミュニケーションにおいては、SNSなどを<ruby>通<rt>つう</rt></ruby>じて「わかりやすさ」や「<ruby>即時的<rt>そくじてき</rt></ruby>な<ruby>共感<rt>きょうかん</rt>」ばかりが<ruby>称揚<rt>しょうよう</rt></ruby>される<ruby>傾向<rt>けいこう</rt></ruby>にある。しかし、<ruby>安易<rt>あんい</rt></ruby>に「あなたの<ruby>気持<rt>きも</rt></ruby>ちがよくわかる」と<ruby>口<rt>くち</rt></ruby>にすることは、かえって<ruby>相手<rt>あいて</rt></ruby>の<ruby>抱<rt>かか</rt></ruby>える<ruby>固有<rt>こゆう</rt></ruby>の<ruby>痛<rt>いた</rt></ruby>みや<ruby>複雑<rt>ふくざつ</rt></ruby>さを、<ruby>自<rt>みずか</rt></ruby>らの<ruby>貧弱<rt>ひんじゃく</rt></ruby>な<ruby>尺度<rt>しゃくど</rt></ruby>へと<ruby>矮小化<rt>わいしょうか</rt></ruby>してしまう<ruby>暴挙<rt>ぼうきょ</rt></ruby>になりかねない。</p>
    <p><span id="ev-n1-1"><ruby>真<rt>しん</rt></ruby>の<ruby>対話<rt>たいわ</rt></ruby>の<ruby>出発点<rt>しゅっぱつてん</rt></ruby>とは、「<ruby>自分<rt>じぶん</rt></ruby>には<ruby>他者<rt>たしゃ</rt></ruby>のすべてを<ruby>完全<rt>かんぜん</rt></ruby>に<ruby>分<rt>わ</rt></ruby>かりきることはできない」という、ある<ruby>種<rt>しゅ</rt></ruby>の<ruby>絶対的<rt>ぜったいてき</rt></ruby>な<ruby>断絶<rt>だんぜつ</rt></ruby>を<ruby>謙虚<rt>けんきょ</rt></ruby>に<ruby>受<rt>う</rt></ruby>け<ruby>入<rt>い</rt></ruby>れることにほかならない。</span>どれほど<ruby>言葉<rt>ことば</rt></ruby>を<ruby>尽<rt>つ</rt></ruby>くしても<ruby>埋<rt>う</rt></ruby>まらない<ruby>溝<rt>みぞ</rt></ruby>があるからこそ、われわれは<ruby>耳<rt>みみ</rt></ruby>を<ruby>傾<rt>かたむ</rt></ruby>け<ruby>続<rt>つづ</rt></ruby>け、<ruby>想像力<rt>そうぞうりょく</rt></ruby>を<ruby>働<rt>はたら</rt></ruby>かせようとするのである。</p>
    <p><span id="ev-n1-2"><ruby>分<rt>わ</rt></ruby>かりあえないという<ruby>絶望<rt>ぜつぼう</rt></ruby>を<ruby>踏<rt>ふ</rt></ruby>まえた<ruby>上<rt>うえ</rt></ruby>でなお、<ruby>相手<rt>あいて</rt></ruby>の<ruby>言葉<rt>ことば</rt></ruby>の<ruby>響<rt>ひび</rt></ruby>きに<ruby>寄<rt>よ</rt></ruby>り<ruby>添<rt>そ</rt></ruby>おうとする<ruby>不断<rt>ふだん</rt></ruby>の<ruby>姿勢<rt>しせい</rt></ruby>こそが、<ruby>人間<rt>にんげん</rt></ruby>が<ruby>紡<rt>つむ</rt></ruby>ぎうる<ruby>最<rt>もっと</rt></ruby>も<ruby>誠実<rt>せいじつ</rt></ruby>な<ruby>関係性<rt>かんけいせい</rt></ruby>なのではないだろうか。</span></p>
</div>
""".strip()

    text_n1 = Text(
        title="他者理解の不可能性と誠実さ (Невозможность полного понимания Другого и подлинная искренность)",
        level="N1",
        category="long",
        recommended_time_min=7,
        content_html=n1_content,
        translation_ru="Что на самом деле значит 'понять другого человека'? В современных соцсетях превозносится мгновенное сопереживание. Однако легко брошенное 'я прекрасно тебя понимаю' рискует принизить уникальную боль собеседника до собственных рамок.\nПодлинный диалог начинается с признания: мы никогда не сможем понять другого до конца. Именно наличие этой непреодолимой пропасти побуждает нас слушать и подключать воображение.\nОсознавать невозможность абсолютного единения и тем не менее неустанно стремиться навстречу — это и есть самая искренняя форма человеческих отношений.",
        vocabulary_json=[
            {"word": "称揚する", "furigana": "しょうようする", "translation": "восхвалять, превозносить"},
            {"word": "矮小化", "furigana": "わいしょうか", "translation": "умаление, искажение до мелочей"},
            {"word": "断絶", "furigana": "だんぜつ", "translation": "разрыв, пропасть, разобщение"},
            {"word": "不断の", "furigana": "ふだんの", "translation": "непрестанный, постоянный"}
        ]
    )
    q_n1_1 = Question(
        question_number=1,
        question_text="筆者によると、「真の対話の出発点」とはどのようなことか。",
        general_explanation="Правильный ответ — вариант 3. В ev-n1-1 автор прямо утверждает: исходный пункт диалога — смиренное признание того, что до конца понять другого невозможно (他者を完全に分かりきることはできないと受け入れること).",
        evidence_span_id="ev-n1-1"
    )
    q_n1_1.options = [
        Option(option_number=1, option_text="SNSを通じて互いの意見を即時的に共有し合うこと。", is_correct=False, option_explanation="Неверно. Автор критикует поверхностность мгновенных реакций в соцсетях."),
        Option(option_number=2, option_text="相手の気持ちを自分の尺度に当てはめて共感すること。", is_correct=False, option_explanation="Неверно. Наоборот, сведение чужих чувств к своим меркам автор называет насилием (暴挙)."),
        Option(option_number=3, option_text="他者を完全に理解することはできないという断絶を認めること。", is_correct=True, option_explanation="Верно! Прямое совпадение с ключевым тезисом в <span id='ev-n1-1'>."),
        Option(option_number=4, option_text="言葉を使わずに感情だけで分かり合える関係を築くこと。", is_correct=False, option_explanation="Неверно. Автор подчеркивает важность вслушивания в речь (言葉の響き).")
    ]

    q_n1_2 = Question(
        question_number=2,
        question_text="この文章の結びとして、筆者が最も伝えたいことはどれか。",
        general_explanation="Правильный ответ — вариант 1. Согласно ev-n1-2, самая искренняя форма отношений — зная о непреодолимой пропасти, всё равно продолжать чутко слушать и пытаться понять другого.",
        evidence_span_id="ev-n1-2"
    )
    q_n1_2.options = [
        Option(option_number=1, option_text="完全には理解し合えないと知りつつも、相手に寄り添い続けようとする姿勢が大切だ。", is_correct=True, option_explanation="Верно! Квинтэссенция мысли автора из предложения с тегом ev-n1-2."),
        Option(option_number=2, option_text="分かり合えない人間関係には意味がないので、孤独を受け入れるべきだ。", is_correct=False, option_explanation="Неверно (Ловушка нигилизма). Автор не призывает закрываться в одиночестве."),
        Option(option_number=3, option_text="誤解を避けるために、言葉数をできるだけ少なく抑えるべきだ。", is_correct=False, option_explanation="Неверно. Автор говорит о важности вслушивания и поиска взаимопонимания."),
        Option(option_number=4, option_text="自分とまったく同じ考えを持つ人だけと付き合うのが誠実さである。", is_correct=False, option_explanation="Неверно. Это прямо противоположно идее эмпатии к непохожему Другому.")
    ]
    text_n1.questions = [q_n1_1, q_n1_2]

    all_texts = [
        text_n5_1, text_n5_2,
        text_n4_trash, text_n4_kyoto,
        text_n3_jogging, text_n3_flyer,
        text_n2_article,
        text_n1
    ]

    db.add_all(all_texts)
    db.commit()
    print(f"Database seeded with {len(all_texts)} high-quality JLPT texts across N5-N1!")
    db.close()


if __name__ == "__main__":
    seed_database()
