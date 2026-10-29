import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, engine, Base
from models import Text, Question, Option


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Re-seed if less than 5 texts to provide rich multi-level variety
    existing_count = db.query(Text).count()
    if existing_count >= 5:
        print(f"Database already has {existing_count} texts. Skipping seed.")
        db.close()
        return

    # Clear old data to ensure clean updated state
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Text).delete()
    db.commit()

    print("Seeding rich multi-level JLPT Dokkai texts (N5, N4, N3, N2)...")

    # =========================================================================
    # 1. LEVEL N5: Short Memo (短文・連絡メモ)
    # =========================================================================
    n5_content = """
<div class="passage-body">
    <p>タナカさんへ</p>
    <p><ruby>昨日<rt>きのう</rt></ruby><ruby>話<rt>はな</rt></ruby>した<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>辞書<rt>じしょ</rt></ruby>を<ruby>持<rt>も</rt></ruby>ってきました。<ruby>机<rt>つくえ</rt></ruby>の<ruby>上<rt>うえ</rt></ruby>に<ruby>置<rt>お</rt></ruby>いておきますね。</p>
    <p><span id="ev-n5-1"><ruby>今日<rt>きょう</rt></ruby>は５<ruby>時<rt>じ</rt></ruby>から<ruby>図書館<rt>としょかん</rt></ruby>でアルバイトがあるので、４<ruby>時<rt>じ</rt></ruby><ruby>半<rt>はん</rt></ruby>に<ruby>教室<rt>きょうしつ</rt></ruby>を<ruby>出<rt>で</rt></ruby>ます。</span>もし<ruby>質問<rt>しつもん</rt></ruby>があったら、それまでに<ruby>聞<rt>き</rt></ruby>いてください。</p>
    <p>スミスより</p>
</div>
""".strip()

    n5_translation = """
Танака-сан!
Я принёс словарь японского языка, о котором мы говорили вчера. Я оставлю его у вас на столе.
Сегодня с 5 часов у меня подработка в библиотеке, поэтому в 4:30 я уйду из аудитории. Если у вас будут вопросы, спросите меня до этого времени.
От Смита.
""".strip()

    n5_vocab = [
        {"word": "辞書", "furigana": "じしょ", "translation": "словарь"},
        {"word": "置く", "furigana": "おく", "translation": "класть, ставить"},
        {"word": "それまでに", "furigana": "それまでに", "translation": "до этого времени / к тому моменту"},
        {"word": "アルバイト", "furigana": "あるばいと", "translation": "подработка (байт)"}
    ]

    text_n5 = Text(
        title="スミスさんからのメモ (Записка от Смита)",
        level="N5",
        category="short",
        recommended_time_min=2,
        content_html=n5_content,
        translation_ru=n5_translation,
        vocabulary_json=n5_vocab
    )

    q_n5 = Question(
        question_number=1,
        question_text="タナカさんはスミスさんに質問したいとき、どうしなければなりませんか。",
        general_explanation=(
            "Правильный ответ — вариант 2. Смит пишет: «библиотека с 5:00, поэтому я ухожу в 4:30. Если есть вопросы — спроси до этого времени (それまでに)». Значит, задать вопрос нужно до 4:30."
        ),
        evidence_span_id="ev-n5-1"
    )

    q_n5.options = [
        Option(option_number=1, option_text="５時までに図書館へ行きます。", is_correct=False,
               option_explanation="Неверно. В 5 часов Смит уже будет работать в библиотеке, а не отвечать на вопросы по словарю в аудитории."),
        Option(option_number=2, option_text="４時半までに教室で聞きます。", is_correct=True,
               option_explanation="Верно! В тексте прямо указано: уходит из аудитории в 4:30, спросить нужно до этого времени (それまでに)."),
        Option(option_number=3, option_text="５時半に辞書を返します。", is_correct=False,
               option_explanation="Неверно. Про возврат словаря в 5:30 в записке вообще ничего не сказано."),
        Option(option_number=4, option_text="４時に図書館へ電話をします。", is_correct=False,
               option_explanation="Неверно. Звонить в библиотеку не требуется, Смит до 4:30 находится в аудитории.")
    ]
    text_n5.questions = [q_n5]

    # =========================================================================
    # 2. LEVEL N4: Medium Travel Story (中文・旅行記)
    # =========================================================================
    n4_content = """
<div class="passage-body">
    <p><ruby>先週<rt>せんしゅう</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>初<rt>はじ</rt></ruby>めて<ruby>一人<rt>ひとり</rt></ruby>で<ruby>京都<rt>きょうと</rt></ruby>へ<ruby>旅行<rt>りょこう</rt></ruby>に<ruby>行<rt>い</rt></ruby>きました。<ruby>友達<rt>ともだち</rt></ruby>と<ruby>一緒<rt>いっしょ</rt></ruby>にいく<ruby>旅行<rt>りょこう</rt></ruby>もにぎやかで<ruby>楽<rt>たの</rt></ruby>しいですが、いつも<ruby>相手<rt>あいて</rt></ruby>の<ruby>行<rt>い</rt></ruby>きたい<ruby>場所<rt>ばしょ</rt></ruby>や<ruby>時間<rt>じかん</rt></ruby>に<ruby>合<rt>あ</rt></ruby>わせなければなりません。<span id="ev-n4-1">今回は自分の好きな時に好きな場所をゆっくり見たかったので、一人で行くことに決めました。</span></p>
    <p><ruby>京都<rt>きょうと</rt></ruby>では、<ruby>有名<rt>ゆうめい</rt></ruby>な<ruby>寺<rt>てら</rt></ruby>を<ruby>見<rt>み</rt></ruby>るだけでなく、<ruby>小<rt>ちい</rt></ruby>さな<ruby>通<rt>とお</rt></ruby>りをのんびり<ruby>散歩<rt>さんぽ</rt></ruby>しました。<span id="ev-n4-2">道に迷って偶然見つけた古い和菓子屋で食べたお茶と団子は、ガイドブックに載っているどんな店より美味しく感じられました。</span></p>
    <p><ruby>一人<rt>ひとり</rt></ruby>の<ruby>旅<rt>たび</rt></ruby>は<ruby>少<rt>すこ</rt></ruby>し<ruby>不安<rt>ふあん</rt></ruby>でしたが、<ruby>自分<rt>じぶん</rt></ruby>だけの<ruby>特別<rt>とくべつ</rt></ruby>な<ruby>思<rt>おも</rt></ruby>い<ruby>出<rt>で</rt></ruby>ができて、とてもよかったです。また<ruby>一人<rt>ひとり</rt></ruby>でどこかへ<ruby>行<rt>い</rt></ruby>ってみたいです。</p>
</div>
""".strip()

    n4_translation = """
На прошлой неделе я впервые один отправился в путешествие в Киото. Поездки с друзьями тоже весёлые и оживлённые, но всегда приходится подстраиваться под чужое время и желания. В этот раз мне хотелось не спеша и в любое удобное время посмотреть именно те места, которые нравятся мне, поэтому я решил поехать один.
В Киото я не только осматривал знаменитые храмы, но и неторопливо гулял по маленьким улочкам. Чай и данго в старой лавке традиционных сладостей, которую я нашел случайно, заблудившись, показались мне вкуснее, чем в любом заведении из путеводителя.
Путешествовать одному было немного тревожно, но у меня остались свои особенные воспоминания, и это было замечательно. Я хочу снова попробовать съездить куда-нибудь один.
""".strip()

    n4_vocab = [
        {"word": "相手に合わせる", "furigana": "あいてにあわせる", "translation": "подстраиваться под собеседника / спутника"},
        {"word": "のんびり", "furigana": "のんびり", "translation": "беззаботно, не торопясь"},
        {"word": "道に迷う", "furigana": "みちにまよう", "translation": "заблудиться"},
        {"word": "偶然", "furigana": "ぐうぜん", "translation": "случайно, неожиданно"},
        {"word": "和菓子屋", "furigana": "わがしや", "translation": "магазин традиционных японских сладостей"},
        {"word": "載る", "furigana": "のる", "translation": "быть напечатанным, внесённым (в список)"}
    ]

    text_n4 = Text(
        title="京都への一人旅 (Одиночное путешествие в Киото)",
        level="N4",
        category="medium",
        recommended_time_min=4,
        content_html=n4_content,
        translation_ru=n4_translation,
        vocabulary_json=n4_vocab
    )

    q_n4_1 = Question(
        question_number=1,
        question_text="「私」はどうして一人で京都へ行きましたか。",
        general_explanation=(
            "Правильный ответ — вариант 3. В предложении ev-n4-1 автор объясняет мотив: в поездках с друзьями приходится подстраиваться, а в этот раз хотелось погулять в своём темпе (自分の好きな時に好きな場所をゆっくり見たかった)."
        ),
        evidence_span_id="ev-n4-1"
    )
    q_n4_1.options = [
        Option(option_number=1, option_text="友達と休みの日が合わなかったから。", is_correct=False,
               option_explanation="Неверно (Ловушка додумывания). В тексте не сказано, что у друзей не совпали выходные."),
        Option(option_number=2, option_text="京都の有名な寺を全部見たかったから。", is_correct=False,
               option_explanation="Неверно. Автор хотел увидеть не 'все' храмы, а спокойно погулять в своём ритме."),
        Option(option_number=3, option_text="他人に合わせず、自分のペースで楽しみたかったから。", is_correct=True,
               option_explanation="Верно! Это синонимичный пересказ фразы «自分の好きな時に好きな場所をゆっくり見たかった»."),
        Option(option_number=4, option_text="一人旅のガイドブックをもらったから。", is_correct=False,
               option_explanation="Неверно. Наоборот, лучшим местом оказалась лавка, которой не было в путеводителях.")
    ]

    q_n4_2 = Question(
        question_number=2,
        question_text="「私」が一番美味しく感じたのはどれですか。",
        general_explanation=(
            "Правильный ответ — вариант 4. Согласно ev-n4-2, когда автор заблудился и случайно наткнулся на старую лавочку, чай и данго там показались вкуснее любого распиаренного места из гида."
        ),
        evidence_span_id="ev-n4-2"
    )
    q_n4_2.options = [
        Option(option_number=1, option_text="有名な寺の近くで食べた料理", is_correct=False,
               option_explanation="Неверно. Знаменитые храмы не связаны с самым вкусным угощением."),
        Option(option_number=2, option_text="ガイドブックで一番おすすめされていた店のお菓子", is_correct=False,
               option_explanation="Неверно. Напротив, угощение было вкуснее, чем в любом заведении из путеводителя (ガイドブックに載っているどんな店より)."),
        Option(option_number=3, option_text="友達が教えてくれた京都のレストランの食事", is_correct=False,
               option_explanation="Неверно. Друзья не советовали автору рестораны."),
        Option(option_number=4, option_text="道に迷ったときに見つけた古い店のお茶と団子", is_correct=True,
               option_explanation="Верно! Точное соответствие предложению с id='ev-n4-2'.")
    ]
    text_n4.questions = [q_n4_1, q_n4_2]

    # =========================================================================
    # 3. LEVEL N3: Short Text (短文) - Jogging Trap
    # =========================================================================
    n3_short_content = """
<div class="passage-body">
    <p><ruby>最近<rt>さいきん</rt></ruby>、<ruby>健康<rt>けんこう</rt></ruby>のために<ruby>毎朝<rt>まいあさ</rt></ruby>ジョギングを<ruby>始<rt>はじ</rt></ruby>める<ruby>人<rt>ひと</rt></ruby>が<ruby>増<rt>ふ</rt></ruby>えています。</p>
    <p><ruby>走<rt>はし</rt></ruby>ることは<ruby>手軽<rt>てがる</rt></ruby>にできて<ruby>気分<rt>きぶん</rt></ruby>も<ruby>爽<rt>さわ</rt></ruby>やかになるため、<ruby>長<rt>なが</rt></ruby>く<ruby>走<rt>はし</rt></ruby>れば<ruby>走<rt>はし</rt></ruby>るほど<ruby>体<rt>からだ</rt></ruby>にいいと<ruby>思<rt>おも</rt></ruby>われがちです。</p>
    <p>しかし、<ruby>急<rt>きゅう</rt></ruby>に<ruby>無理<rt>むり</rt></ruby>をして<ruby>長距離<rt>ちょうきょり</rt></ruby>を<ruby>走<rt>はし</rt></ruby>ると、かえって<ruby>膝<rt>ひざ</rt></ruby>や<ruby>心臓<rt>しんぞう</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>負担<rt>ふたん</rt></ruby>をかけてしまいます。</p>
    <p><span id="ev-1"><ruby>本当<rt>ほんとう</rt></ruby>に<ruby>大切<rt>たいせつ</rt></ruby>なのは、<ruby>距離<rt>きょり</rt></ruby>やスピードではなく、<ruby>自分<rt>じぶん</rt></ruby>のペースで<ruby>楽<rt>たの</rt></ruby>しく<ruby>続<rt>つづ</rt></ruby>けられる<ruby>運動量<rt>うんどうりょう</rt></ruby>を<ruby>保<rt>たも</rt></ruby>つことです。</span></p>
    <p><ruby>無理<rt>むり</rt></ruby>のない<ruby>習慣<rt>しゅうかん</rt></ruby>こそが、<ruby>健康<rt>けんこう</rt></ruby>への<ruby>一番<rt>いちばん</rt></ruby>の<ruby>近道<rt>ちかみち</rt></ruby>なのです。</p>
</div>
""".strip()

    n3_short_trans = """
В последнее время растёт число людей, которые каждое утро начинают бегать трусцой ради здоровья.
Бегом легко заняться, и он приносит чувство свежести и бодрости, поэтому часто думают, что чем дольше бегаешь, тем лучше для здоровья.
Однако, если резко перегружать себя и бегать на большие дистанции, это, напротив, создаст серьёзную нагрузку на колени и сердце.
Действительно важно не расстояние или скорость, а сохранение такого объёма физической нагрузки, который приносит удовольствие и позволяет продолжать тренировки в своём собственном темпе.
Именно ненавязчивая, посильная привычка является кратчайшим путём к здоровью.
""".strip()

    n3_short_vocab = [
        {"word": "手軽に", "furigana": "てがるに", "translation": "легко, просто, без хлопот"},
        {"word": "〜がち", "furigana": "がち", "translation": "склонный к... / часто бывает так, что..."},
        {"word": "かえって", "furigana": "かえって", "translation": "напротив, наоборот, вопреки ожиданиям"},
        {"word": "負担", "furigana": "ふたん", "translation": "нагрузка, бремя"},
        {"word": "運動量", "furigana": "うんどうりょう", "translation": "объём физической нагрузки"},
        {"word": "近道", "furigana": "ちかみち", "translation": "кратчайший путь"}
    ]

    text_n3_1 = Text(
        title="健康のためのジョギングについて (О беге ради здоровья)",
        level="N3",
        category="short",
        recommended_time_min=3,
        content_html=n3_short_content,
        translation_ru=n3_short_trans,
        vocabulary_json=n3_short_vocab
    )
    q_n3_1 = Question(
        question_number=1,
        question_text="筆者がジョギングについて最も言いたいことは何か。",
        general_explanation=(
            "Правильный ответ — вариант 3. Автор использует классическую для JLPT структуру «общее заблуждение (〜と思われがち) -> опровержение через しかし -> истинная мысль (本当に大切なのは〜)». "
            "Ключевой вывод сформулирован в предложении с маркером '本当に大切なのは' (выделено в тексте): важна не длина дистанции или скорость, а комфортный собственный темп."
        ),
        evidence_span_id="ev-1"
    )
    q_n3_1.options = [
        Option(option_number=1, option_text="走る距離をできるだけ長くすることが最も効果的だ。", is_correct=False,
               option_explanation="Неверно (Ловушка ложного стереотипа). Автор указывает, что суждение «чем длиннее дистанция, тем полезнее» — лишь распространённое заблуждение (〜と思われがち)."),
        Option(option_number=2, option_text="毎朝決まった時間に速いスピードで走ることが必要だ。", is_correct=False,
               option_explanation="Неверно (Ловушка несуществующего требования). В тексте четко сказано: «距離やスピードではなく» — скорость и дистанция не главное."),
        Option(option_number=3, option_text="自分のペースに合わせて、無理なく続けられる運動量を維持することが大切だ。", is_correct=True,
               option_explanation="Верно! Вариант перефразирует мысль автора: «自分のペースで楽しく続けられる運動量を保つこと»."),
        Option(option_number=4, option_text="膝や心臓を痛める危険があるので、ジョギングは避けたほうがよい。", is_correct=False,
               option_explanation="Неверно (Ловушка крайности). Автор не советует избегать бега вообще, а предостерегает от резких чрезмерных перегрузок.")
    ]
    text_n3_1.questions = [q_n3_1]

    # =========================================================================
    # 4. LEVEL N3: Information Search (情報検索) - Fitness Club Flyer
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
                <th>プラン名 (План)</th>
                <th>利用可能時間 (Время доступа)</th>
                <th>月会費（税込） (В месяц)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>デイタイム</strong></td>
                <td>平日 10:00 〜 17:00</td>
                <td>6,000円</td>
            </tr>
            <tr>
                <td><strong>ナイト</strong></td>
                <td>平日 18:00 〜 22:00</td>
                <td>6,500円</td>
            </tr>
            <tr>
                <td><strong>ホリデー</strong></td>
                <td>土・日・祝日 10:00 〜 20:00</td>
                <td>5,500円</td>
            </tr>
            <tr class="highlight-row">
                <td><strong>フルタイム</strong></td>
                <td>いつでも全日 10:00 〜 22:00</td>
                <td>9,500円</td>
            </tr>
        </tbody>
    </table>

    <div class="flyer-notes">
        <h3>【ご注意・各種割引について】</h3>
        <ul>
            <li><span id="ev-info-1"><strong>● 学生割引：</strong> 高校生・大学生・専門学生の方は、学生証のご提示で<strong>月会費が毎月1,000円引き</strong>となります。（※ただし「ホリデープラン」は学生割引の対象外です）</span></li>
            <li><span id="ev-info-2"><strong>● 春の入会キャンペーン：</strong> 通常、登録事務手数料<strong>3,000円が、今月中にWebサイトからお申し込みの場合に限り【0円（無料）】</strong>となります！</span></li>
            <li><strong>● 専用個人ロッカー：</strong> 契約をご希望の方は、月額1,100円（税込）でご利用いただけます（任意）。</li>
            <li>※休館日：毎週月曜日（祝日の場合は翌火曜日が休館となります）。</li>
        </ul>
    </div>
</div>
""".strip()

    n3_flyer_trans = """
Правила и тарифы фитнес-клуба «Сакура» (Набор новых участников этой весной!)
Современные тренажёры, подогреваемый бассейн, студия групповых занятий!

Тарифные планы:
- Дневной (Дэйтайм): будни 10:00 - 17:00 — 6,000 иен
- Вечерний (Найт): будни 18:00 - 22:00 — 6,500 иен
- Выходного дня (Холидэй): сб, вс, праздники 10:00 - 20:00 — 5,500 иен
- Полный безлимит (Фуллтайм): в любое время каждый день 10:00 - 22:00 — 9,500 иен

Внимание и скидки:
- Студенческая скидка: скидка 1,000 иен на ежемесячный взнос (кроме плана «Холидэй»).
- Весенняя кампания: регистрационный сбор 3,000 иен становится БЕСПЛАТНЫМ (0 иен) при подаче заявки через сайт в этом месяце.
- Личный шкафчик: 1,100 иен в месяц (по желанию).
- Выходной день: каждый понедельник.
""".strip()

    n3_flyer_vocab = [
        {"word": "月会費", "furigana": "げっかいひ", "translation": "ежемесячный членский взнос"},
        {"word": "全日", "furigana": "ぜんじつ", "translation": "все дни недели (любой день)"},
        {"word": "提示", "furigana": "ていじ", "translation": "предъявление (документа)"},
        {"word": "対象外", "furigana": "たいしょうがい", "translation": "не подпадающий под действие, исключение"},
        {"word": "登録事務手数料", "furigana": "とうろくじむてすうりょう", "translation": "регистрационный сбор"},
        {"word": "任意", "furigana": "にんい", "translation": "по желанию, опционально"}
    ]

    text_n3_2 = Text(
        title="サクラ・フィットネスクラブ ご利用案内 (Памятка фитнес-клуба Сакура)",
        level="N3",
        category="info_search",
        recommended_time_min=5,
        content_html=n3_flyer_content,
        translation_ru=n3_flyer_trans,
        vocabulary_json=n3_flyer_vocab
    )
    q_n3_2_1 = Question(
        question_number=1,
        question_text="大学3年生のタナカさんは、平日の夜（19時以降）と土曜日の午後に利用したいと考えている。学生割引を使って最も安く利用できるプランと月会費の組み合わせはどれか。",
        general_explanation=(
            "Правильный ответ — вариант 3. Нужны и будни вечер, и суббота. Единственный подходящий план — «フルタイム» (9,500円). Со студенческой скидкой (1,000円引き): 9,500 - 1,000 = 8,500円."
        ),
        evidence_span_id="ev-info-1"
    )
    q_n3_2_1.options = [
        Option(option_number=1, option_text="ナイトプラン：5,500円", is_correct=False, option_explanation="Неверно. План «ナイト» действует только по будням и не позволяет прийти в субботу."),
        Option(option_number=2, option_text="ホリデープラン：4,500円", is_correct=False, option_explanation="Неверно. Не действует по будням вечером, плюс на него прямо запрещена студенческая скидка."),
        Option(option_number=3, option_text="フルタイムプラン：8,500円", is_correct=True, option_explanation="Верно! Покрывает все дни, а со студенческой скидкой 1,000 иен цена составит 8,500 иен."),
        Option(option_number=4, option_text="フルタイムプラン：9,500円", is_correct=False, option_explanation="Неверно. 9,500 — базовая цена без положенной студенческой скидки.")
    ]

    q_n3_2_2 = Question(
        question_number=2,
        question_text="タナカさんが今月中にWebから入会し、専用個人ロッカーも申し込む場合、初月に支払う合計金額（月会費＋登録料＋ロッカー代）はいくらか。",
        general_explanation=(
            "Правильный ответ — вариант 1. Расчет: 8,500 (абонемент студента) + 0 (Web-акция отменяет 3,000) + 1,100 (шкафчик) = 9,600円."
        ),
        evidence_span_id="ev-info-2"
    )
    q_n3_2_2.options = [
        Option(option_number=1, option_text="9,600円", is_correct=True, option_explanation="Верно! Членский взнос (8,500) + регистрация по акции (0) + шкафчик (1,100) = 9,600円."),
        Option(option_number=2, option_text="12,600円", is_correct=False, option_explanation="Неверно. Ошибочно включён регистрационный сбор 3,000, который по акции бесплатный."),
        Option(option_number=3, option_text="8,500円", is_correct=False, option_explanation="Неверно. Забыли учесть аренду личного шкафчика (1,100)."),
        Option(option_number=4, option_text="10,600円", is_correct=False, option_explanation="Неверно. Забыли применить студенческую скидку в 1,000 иен.")
    ]
    text_n3_2.questions = [q_n3_2_1, q_n3_2_2]

    # =========================================================================
    # 5. LEVEL N2: Authentic Article / Column (記事・評論 - 長文)
    # =========================================================================
    n2_article_content = """
<div class="passage-body">
    <p><ruby>現代<rt>げんだい</rt></ruby><ruby>社会<rt>しゃかい</rt></ruby>においては、あらゆる<ruby>場面<rt>ばめん</rt></ruby>で「タイパ（タイムパフォーマンス）」や「<ruby>効率<rt>こうりつ</rt>」が<ruby>最優先<rt>さいゆうせん</rt></ruby>されるようになった。<ruby>動画<rt>どうが</rt></ruby>を<ruby>倍速<rt>ばいそく</rt></ruby>で<ruby>視聴<rt>しちょう</rt></ruby>し、<ruby>要約<rt>ようやく</rt></ruby>された情報だけを<ruby>手早<rt>てばや</rt></ruby>く<ruby>消費<rt>しょうひ</rt></ruby>するスタイルは、<ruby>情報<rt>じょうほう</rt></ruby><ruby>過多<rt>かた</rt></ruby>の<ruby>時代<rt>じだい</rt></ruby>を<ruby>生<rt>い</rt></ruby>き<ruby>抜<rt>ぬ</rt></ruby>くための<ruby>合理的<rt>ごうりてき</rt></ruby>な<ruby>手段<rt>しゅだん</rt></ruby>のようにも<ruby>見<rt>み</rt></ruby>える。</p>
    <p>しかし、<ruby>知識<rt>ちしき</rt></ruby>の<ruby>獲得<rt>かくとく</rt></ruby>と<ruby>真<rt>しん</rt></ruby>の<ruby>思考<rt>しこう</rt></ruby>は<ruby>決<rt>けっ</rt></ruby>して<ruby>同義<rt>どうぎ</rt></ruby>ではない。<span id="ev-n2-1">あらかじめ結論が整えられた情報ばかりを摂取していると、物事の背景にある文脈や、一見矛盾するように見える複雑なニュアンスを自らの頭で咀嚼する力が急速に衰えてしまう。</span></p>
    <p>かつて<ruby>思索<rt>しさく</rt></ruby>とは、<ruby>迷<rt>まよ</rt></ruby>い、<ruby>立<rt>た</rt></ruby>ち<ruby>止<rt>ど</rt></ruby>まり、あてもなく<ruby>考<rt>かんが</rt></ruby>えを<ruby>巡<rt>めぐ</rt></ruby>らせるという、ある<ruby>種<rt>しゅ</rt></ruby>の「<ruby>無駄<rt>むだ</rt>」の<ruby>中<rt>なか</rt></ruby>にこそ<ruby>宿<rt>やど</rt></ruby>るものであった。<span id="ev-n2-2">効率化を突き詰めた先にあるのは、画一的な正解を素早く出力する機械のような人間であり、そこからは新たな価値や深い洞察は生まれにくいのではないか。</span></p>
    <p>われわれは<ruby>今<rt>いま</rt></ruby>こそ、<ruby>成果<rt>せいか</rt></ruby>に<ruby>直結<rt>ちょっけつ</rt></ruby>しない「<ruby>余白<rt>よはく</rt>の<ruby>時間<rt>じかん</rt></ruby>」を<ruby>恐<rt>おそ</rt></ruby>れず、<ruby>自<rt>みずか</rt></ruby>らを<ruby>深<rt>ふか</rt></ruby>めるための<ruby>贅沢<rt>ぜいたく</rt></ruby>として<ruby>取<rt>と</rt></ruby>り<ruby>戻<rt>もど</rt></ruby>すべきなのである。</p>
</div>
""".strip()

    n2_article_trans = """
В современном обществе «тайпа» (эффективность затраченного времени) и продуктивность стали наивысшим приоритетом во всех сферах жизни. Просмотр видео на двойной скорости и быстрое потребление сжатой выжимки информации кажутся рациональным способом выживания в эпоху информационного перегруза.
Однако накопление готовых знаний и подлинное глубокое мышление вовсе не синонимичны. Когда человек потребляет исключительно информацию с заранее подготовленными готовыми выводами, его способность самостоятельно переваривать контекст событий и сложные, кажущиеся противоречивыми нюансы стремительно атрофируется.
Некогда процесс размышления рождался именно в некоторого рода «бесполезной трате времени» — когда человек сомневался, замирал на месте и бесцельно блуждал в мыслях. Не окажется ли так, что на пределе тотальной оптимизации человек уподобится машине, быстро выдающей шаблонные правильные ответы, из которых вряд ли смогут родиться новые ценности и глубокие озарения?
Именно сейчас мы должны перестать бояться «пустого времени», не ведущего к сиюминутному результату, и вернуть его себе как роскошь, необходимую для внутренней глубины.
""".strip()

    n2_article_vocab = [
        {"word": "タイムパフォーマンス", "furigana": "たいむぱふぉーまんす", "translation": "тайпа (эффективность затраченного времени)"},
        {"word": "同義", "furigana": "どうぎ", "translation": "синонимичный, тождественный по смыслу"},
        {"word": "咀嚼する", "furigana": "そしゃくする", "translation": "разжёвывать; глубоко осмысливать, переваривать"},
        {"word": "思索", "furigana": "しさく", "translation": "глубокое размышление, философские поиски"},
        {"word": "画一的", "furigana": "かくいつてき", "translation": "шаблонный, однообразный, унифицированный"},
        {"word": "洞察", "furigana": "どうさつ", "translation": "проницательность, глубинное понимание сути"},
        {"word": "余白", "furigana": "よはく", "translation": "пустое пространство, резерв времени, пауза"}
    ]

    text_n2 = Text(
        title="デジタル時代における「無駄な時間」の価値 (Ценность «потерянного времени» в цифровую эпоху)",
        level="N2",
        category="article",
        recommended_time_min=6,
        content_html=n2_article_content,
        translation_ru=n2_article_trans,
        vocabulary_json=n2_article_vocab
    )

    q_n2_1 = Question(
        question_number=1,
        question_text="「要約された情報ばかりを摂取している」ことの弊害として、筆者が指摘しているのはどれか。",
        general_explanation=(
            "Правильный ответ — вариант 2. В абзаце ev-n2-1 автор прямо формулирует негативное последствие: падает способность самостоятельно осмысливать контекст и сложные противоречивые нюансы (自らの頭で咀嚼する力が急速に衰えてしまう)."
        ),
        evidence_span_id="ev-n2-1"
    )
    q_n2_1.options = [
        Option(option_number=1, option_text="新しい情報技術に適応できなくなること。", is_correct=False,
               option_explanation="Неверно. Автор не говорит о неспособности адаптироваться к технологиям — люди как раз активно пользуются ускоренным просмотром."),
        Option(option_number=2, option_text="物事の文脈や複雑な意味を、自分の頭で深く考える力が弱まること。", is_correct=True,
               option_explanation="Верно! Это точный пересказ фразы: «物事の背景にある文脈や、一見矛盾するように見える複雑なニュアンスを自らの頭で咀嚼する力が急速に衰えてしまう»."),
        Option(option_number=3, option_text="動画を倍速で見ることで、視力や集中力が低下すること。", is_correct=False,
               option_explanation="Неверно (Ловушка физиологических последствий). Про ухудшение зрения автор не упоминает."),
        Option(option_number=4, option_text="他者と知識の量を競い合うようになってしまうこと。", is_correct=False,
               option_explanation="Неверно. В тексте нет речи о конкуренции за объём знаний.")
    ]

    q_n2_2 = Question(
        question_number=2,
        question_text="筆者がこの文章で最も主張したいことは何か。",
        general_explanation=(
            "Правильный ответ — вариант 4. В заключительном предложении (и через риторический вопрос в ev-n2-2) автор формулирует главный посыл: не нужно бояться пауз и времени без сиюминутного результата («余白の時間»), так как именно в нём рождается глубина мысли и подлинные новые ценности."
        ),
        evidence_span_id="ev-n2-2"
    )
    q_n2_2.options = [
        Option(option_number=1, option_text="仕事の効率を上げるために、タイパを意識した生活を徹底すべきだ。", is_correct=False,
               option_explanation="Неверно (Ловушка противоположного смысла). Автор критикует чрезмерную погоню за тайпа."),
        Option(option_number=2, option_text="人間はAI機械には勝てないので、知識を暗記するのはやめるべきだ。", is_correct=False,
               option_explanation="Неверно (Ловушка ложного пессимизма). Автор призывает не механизировать себя, а развивать глубину."),
        Option(option_number=3, option_text="インターネット上の要約サイトや倍速視聴の利用を法律で禁止すべきだ。", is_correct=False,
               option_explanation="Неверно (Ловушка радикального запрета). Автор не требует юридических запретов."),
        Option(option_number=4, option_text="効率ばかりを追わず、思索を深めるための「余白の時間」を取り戻すべきだ。", is_correct=True,
               option_explanation="Верно! Квинтэссенция мысли автора: «成果に直結しない余白の時間を恐れず、自らを深めるための贅沢として取り戻すべき».")
    ]
    text_n2.questions = [q_n2_1, q_n2_2]

    db.add_all([text_n5, text_n4, text_n3_1, text_n3_2, text_n2])
    db.commit()
    print("Database seeding with N5, N4, N3, N2 completed successfully!")
    db.close()


if __name__ == "__main__":
    seed_database()
