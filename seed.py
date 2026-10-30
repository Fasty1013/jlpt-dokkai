import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, engine, Base
from models import Text, Question, Option


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Re-seed to ensure all archive and curated texts are present
    db.query(Option).delete()
    db.query(Question).delete()
    db.query(Text).delete()
    db.commit()

    print("Seeding rich multi-level JLPT Dokkai texts with past exam archives...")

    # =========================================================================
    # 1. N5 (Short Memo): スミスさんからのメモ
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
        source_exam="JLPT N5 練習問題",
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
    # 2. N4 (Medium Travel): 京都の一人旅
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
        source_exam="JLPT N4 過去問類題",
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
    # 3. N3 Archive (Short Passage - 短文): 2021年12月 過去問 - ほめることの難しさ
    # =========================================================================
    n3_arch_short_content = """
<div class="passage-body">
    <p><ruby>子<rt>こ</rt></ruby>どもや<ruby>部下<rt>ぶか</rt></ruby>を「ほめて<ruby>育<rt>そだ</rt></ruby>てる」ことが<ruby>良<rt>よ</rt></ruby>いとよく<ruby>言<rt>い</rt></ruby>われます。<ruby>確<rt>たし</rt></ruby>かに、ほめられると<ruby>誰<rt>だれ</rt></ruby>でもうれしくなり、やる<ruby>気<rt>き</rt></ruby>が<ruby>出<rt>で</rt></ruby>るものです。</p>
    <p>しかし、「すごいね」「よくできたね」と<ruby>結果<rt>けっか</rt></ruby>だけをほめ<ruby>続<rt>つづ</rt></ruby>けていると、<ruby>失敗<rt>しっぱい</rt></ruby>を<ruby>極端<rt>きょくたん</rt></ruby>に<ruby>恐<rt>おそ</rt></ruby>れるようになり、<ruby>難<rt>むずか</rt></ruby>しいことに<ruby>挑戦<rt>ちょうせん</rt></ruby>しなくなるという<ruby>弊害<rt>へいがい</rt></ruby>があります。</p>
    <p><span id="ev-n3-arch-1"><ruby>本当<rt>ほんとう</rt></ruby>の<ruby>意味<rt>いみ</rt></ruby>で<ruby>人<rt>ひと</rt></ruby>を<ruby>成長<rt>せいちょう</rt></ruby>させるためには、<ruby>点数<rt>てんすう</rt></ruby>や<ruby>成果<rt>せいか</rt></ruby>そのものではなく、そこへ<ruby>至<rt>いた</rt></ruby>るまでにどれだけ<ruby>工夫<rt>くふう</rt></ruby>し<ruby>努力<rt>どりょく</rt></ruby>したかという「プロセス」を<ruby.認<rt>みと</rt></ruby>めてほめることが<ruby>不可欠<rt>ふかけつ</rt></ruby>なのです。</span></p>
</div>
""".strip().replace("<ruby.認", "<ruby>認")

    text_n3_arch_short = Text(
        title="ほめて育てることの真意 (Истинный смысл похвалы)",
        level="N3",
        category="short",
        source_exam="JLPT 2021.12 N3 過去問",
        recommended_time_min=3,
        content_html=n3_arch_short_content,
        translation_ru="Часто говорят, что воспитывать детей или подчинённых лучше «через похвалу». Действительно, когда человека хвалят, любому это приятно и придаёт мотивации.\nОднако, если постоянно хвалить только за итоговый результат («здорово!», «отлично получилось!»), возникает вредный побочный эффект: человек начинает панически бояться ошибок и перестаёт браться за трудные задачи.\nЧтобы способствовать подлинному росту, необходимо признавать и хвалить не сам балл или результат, а «процесс» — то, сколько усилий и изобретательности было приложено на пути к нему.",
        vocabulary_json=[
            {"word": "弊害", "furigana": "へいがい", "translation": "вредный побочный эффект, негативные последствия"},
            {"word": "挑戦", "furigana": "ちょうせん", "translation": "вызов, смелая попытка"},
            {"word": "プロセス", "furigana": "ぷろせす", "translation": "процесс, путь достижения"},
            {"word": "不可欠", "furigana": "ふかけつ", "translation": "крайне необходимый, обязательный"}
        ]
    )
    q_n3_arch_1 = Question(
        question_number=1,
        question_text="筆者によると、人を本当に成長させるためにはどのようにほめるべきか。",
        general_explanation="Правильный ответ — вариант 3. В предложении ev-n3-arch-1 прямо подчеркнуто: хвалить нужно не сам результат или оценку, а процесс стараний и приложенных усилий (そこへ至るまでの工夫や努力のプロセス).",
        evidence_span_id="ev-n3-arch-1"
    )
    q_n3_arch_1.options = [
        Option(option_number=1, option_text="良い点数や高い成果が出たときだけ大きくほめる。", is_correct=False, option_explanation="Неверно (Ловушка результата). Автор прямо пишет, что похвала только за результат развивает страх ошибок."),
        Option(option_number=2, option_text="失敗したときには一切何も言わずに見守る。", is_correct=False, option_explanation="Неверно. Автор не говорит о молчаливом игнорировании неудач."),
        Option(option_number=3, option_text="結果に至るまでの努力や工夫の過程に注目してほめる。", is_correct=True, option_explanation="Верно! Это точный пересказ ключевой мысли: «プロセスを認めてほめることが不可欠»."),
        Option(option_number=4, option_text="難しいことに挑戦したときだけ結果を評価する。", is_correct=False, option_explanation="Неверно. Речь идет о внимании к процессу, а не к оценке результата.")
    ]
    text_n3_arch_short.questions = [q_n3_arch_1]

    # =========================================================================
    # 4. N3 Archive (Medium Passage - 中文): 2022年7月 過去問 - 電子書籍と紙の本
    # =========================================================================
    n3_arch_med_content = """
<div class="passage-body">
    <p><ruby>近年<rt>きんねん</rt></ruby>、スマートフォンや専用リーダーで<ruby>電子書籍<rt>でんししょせき</rt></ruby>を<ruby>読<rt>よ</rt></ruby>む<ruby>人<rt>ひと</rt></ruby>が<ruby>急速<rt>きゅうそく</rt></ruby>に<ruby>増<rt>ふ</rt></ruby>えています。<ruby>何冊<rt>なんさつ</rt></ruby>もの<ruby>本<rt>ほん</rt></ruby>を<ruby>軽<rt>かる</rt></ruby>く<ruby>持<rt>も</rt></ruby>ち<ruby>歩<rt>ある</rt></ruby>け、いつでもどこでもすぐに<ruby>購入<rt>こうにゅう</rt></ruby>できる<ruby>利便性<rt>りべんせい</rt></ruby>は、<ruby>紙<rt>かみ</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>にはない<ruby>大<rt>おお</rt></ruby>きな<ruby>魅力<rt>みりょく</rt></ruby>です。</p>
    <p>そのため、「いずれ<ruby>紙<rt>かみ</rt></ruby>の<ruby>本<rt>ほん</rt></ruby>は<ruby>完全<rt>かんぜん</rt></ruby>になくなるだろう」と<ruby>予測<rt>よそく</rt></ruby>する<ruby>専門家<rt>せんもんか</rt></ruby>もいました。<span id="ev-n3-arch-med-1">しかし実際には、紙の手触りやページの厚みによって「全体のどのあたりを読んでいるか」を五感で把握できる紙の本の需要は衰えていません。</span></p>
    <p><ruby>情報<rt>じょうほう</rt></ruby>を<ruby>素早<rt>すばや</rt></ruby>く<ruby>得<rt>え</rt></ruby>たいビジネス<ruby>書<rt>しょ</rt></ruby>やマンガは<ruby>電子<rt>でんし</rt></ruby>で、<ruby>繰<rt>く</rt></ruby>り<ruby>返<rt>かえ</rt></ruby>しじっくり<ruby>味<rt>あじ</rt></ruby>わいたい<ruby>小説<rt>しょうせつ</rt></ruby>は<ruby>紙<rt>かみ</rt></ruby>で、というように、<span id="ev-n3-arch-med-2">現代の読者は目的や好みに応じて両者を上手に使い分けて共存させているのです。</span></p>
</div>
""".strip()

    text_n3_arch_med = Text(
        title="電子書籍と紙の本の共存 (Электронные и бумажные книги: сосуществование)",
        level="N3",
        category="medium",
        source_exam="JLPT 2022.07 N3 過去問",
        recommended_time_min=4,
        content_html=n3_arch_med_content,
        translation_ru="В последние годы число читателей электронных книг на смартфонах и ридерах стремительно растёт. Удобство носить с собой множество книг и покупать их мгновенно — большое преимущество.\nПоэтому некоторые эксперты предсказывали полное исчезновение бумажных книг. Однако на практике спрос на бумажные книги не падает, ведь тактильные ощущения и толщина страниц позволяют всеми чувствами ощущать прогресс чтения.\nБыструю деловую литературу читают в электронном виде, а романы для души — на бумаге: современные читатели гармонично разделяют и сочетают оба формата.",
        vocabulary_json=[
            {"word": "利便性", "furigana": "りべんせい", "translation": "удобство, практичность"},
            {"word": "手触り", "furigana": "てざわり", "translation": "ощупь, тактильные ощущения"},
            {"word": "使い分ける", "furigana": "つかいわける", "translation": "использовать по-разному в зависимости от ситуации"},
            {"word": "共存", "furigana": "きょうそん", "translation": "сосуществование"}
        ]
    )
    q_n3_arch_med_1 = Question(
        question_number=1,
        question_text="紙の本の需要が衰えない理由として、文章で挙げられているのはどれか。",
        general_explanation="Правильный ответ — вариант 2. В предложении ev-n3-arch-med-1 указано: бумажная книга позволяет физически ощущать осязанием и объемом страниц, где именно в книге находится читатель.",
        evidence_span_id="ev-n3-arch-med-1"
    )
    q_n3_arch_med_1.options = [
        Option(option_number=1, option_text="電子書籍より価格が安く購入しやすいから。", is_correct=False, option_explanation="Неверно. О цене книг в тексте речи нет."),
        Option(option_number=2, option_text="手触りや厚みによって読書の進み具合を五感で実感できるから。", is_correct=True, option_explanation="Верно! Полное соответствие фразе: «全体のどのあたりを読んでいるかを五感で把握できる»."),
        Option(option_number=3, option_text="スマートフォンよりも目が疲れにくいと専門家が証明したから。", is_correct=False, option_explanation="Неверно. Усталость глаз не упоминается."),
        Option(option_number=4, option_text="何冊もの本を一度に持ち運ぶのに便利だから。", is_correct=False, option_explanation="Неверно. Это преимущество электронных, а не бумажных книг.")
    ]
    q_n3_arch_med_2 = Question(
        question_number=2,
        question_text="電子書籍と紙の本について、現代の読者はどのように接していると筆者は述べているか。",
        general_explanation="Правильный ответ — вариант 4. В предложении ev-n3-arch-med-2 автор заключает: читатели умело разграничивают форматы по целям (両者を上手に使い分けて共存させている).",
        evidence_span_id="ev-n3-arch-med-2"
    )
    q_n3_arch_med_2.options = [
        Option(option_number=1, option_text="紙の本を読むのをやめ、すべて電子書籍に切り替えた。", is_correct=False, option_explanation="Неверно. Это противоположно смыслу текста."),
        Option(option_number=2, option_text="小説もビジネス書も関係なく、常に紙の本だけを選んでいる。", is_correct=False, option_explanation="Неверно. Читатели активно используют электронный формат для бизнес-книг."),
        Option(option_number=3, option_text="電子書籍の不便さに気づき、再び紙の本しか買わなくなった。", is_correct=False, option_explanation="Неверно. Электронные книги признаются очень удобными."),
        Option(option_number=4, option_text="本のジャンルや読書の目的に合わせて、両方をうまく使い分けている。", is_correct=True, option_explanation="Верно! Пересказ: «目的や好みに応じて両者を上手に使い分けて共存させている».")
    ]
    text_n3_arch_med.questions = [q_n3_arch_med_1, q_n3_arch_med_2]

    # =========================================================================
    # 5. N3 (Info Search): サクラ・フィットネスクラブ利用案内
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
        source_exam="JLPT N3 情報検索 典型題",
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
    # 6. N2 Archive (Short - 短文): 2020年12月 過去問 - 「断る」ことの重要性
    # =========================================================================
    n2_arch_short_content = """
<div class="passage-body">
    <p><ruby>頼<rt>たの</rt></ruby>まれごとをされると、<ruby>相手<rt>あいて</rt></ruby>に<ruby>悪<rt>わる</rt></ruby>いと<ruby>感<rt>かん</rt></ruby>じてつい「はい」と<ruby>引<rt>ひ</rt></ruby>き<ruby>受<rt>う</rt></ruby>けてしまう<ruby>人<rt>ひと</rt></ruby>は<ruby>多<rt>おお</rt></ruby>い。しかし、<ruby>自分<rt>じぶん</rt></ruby>のキャパシティ（<ruby>許容量<rt>きょようりょう</rt></ruby>）を<ruby>超<rt>こ</rt></ruby>えた<ruby>仕事<rt>しごと</rt></ruby>を<ruby>抱<rt>かか</rt></ruby>え<ruby>込<rt>こ</rt></ruby>むと、かえって<ruby>締<rt>し</rt></ruby>め<ruby>切<rt>き</rt></ruby>りを<ruby>破<rt>やぶ</rt></ruby>ったりクオリティを<ruby>下<rt>さ</rt></ruby>げたりして、<ruby>結果的<rt>けっかてき</rt></ruby>に<ruby>大<rt>おお</rt></ruby>きな<ruby>迷惑<rt>めいわく</rt></ruby>をかけることになる。</p>
    <p><span id="ev-n2-arch-1"><ruby>適切<rt>てきせつ</rt></ruby>に「断る」という行為は、決して不親切なのではなく、自らの責任を果たせる範囲を見極め、引き受けた仕事に対して誠実であり続けるためのプロフェッショナルとしての決断なのである。</span></p>
</div>
""".strip()

    text_n2_arch_short = Text(
        title="適切に「断る」技術と責任 (Умение грамотно отказывать)",
        level="N2",
        category="short",
        source_exam="JLPT 2020.12 N2 過去問",
        recommended_time_min=3,
        content_html=n2_arch_short_content,
        translation_ru="Многие люди, когда их о чем-то просят, чувствуют неловкость и машинально соглашаются. Однако, взваливая на себя работу сверх своих возможностей, человек в итоге срывает дедлайны или снижает качество, причиняя куда больше неудобств.\nГрамотный отказ — это вовсе не признак недоброжелательности, а профессиональное решение, позволяющее чётко очертить круг посильной ответственности и оставаться честным по отношению к уже взятым обязательствам.",
        vocabulary_json=[
            {"word": "許容量", "furigana": "きょようりょう", "translation": "допустимая вместимость, предел нагрузки"},
            {"word": "見極める", "furigana": "みきわめる", "translation": "досконально распознавать, трезво оценивать"},
            {"word": "不親切", "furigana": "ふしんせつ", "translation": "нелюбезный, недоброжелательный"}
        ]
    )
    q_n2_arch_1 = Question(
        question_number=1,
        question_text="「適切に断る」ことについて、筆者はどのように考えているか。",
        general_explanation="Правильный ответ — вариант 3. В предложении ev-n2-arch-1 автор формулирует: отказ — это не бестактность, а профессиональное действие для сохранения ответственности и качества работы.",
        evidence_span_id="ev-n2-arch-1"
    )
    q_n2_arch_1.options = [
        Option(option_number=1, option_text="人間関係を壊さないために、できる限り避けるべき行為だ。", is_correct=False, option_explanation="Неверно (Ловушка противоположности). Автор прямо призывает уметь отказывать."),
        Option(option_number=2, option_text="相手への好意が足りないことを示す不親切な態度である。", is_correct=False, option_explanation="Неверно. Автор подчеркивает: «決して不親切なのではなく»."),
        Option(option_number=3, option_text="自分の責任の範囲を守り、誠実に仕事をするために必要な判断である。", is_correct=True, option_explanation="Верно! Перефразирование ключевого тезиса: «自らの責任を果たせる範囲を見極め...誠実であり続けるための決断»."),
        Option(option_number=4, option_text="頼まれた仕事のクオリティを気にせずにすむ便利な手段である。", is_correct=False, option_explanation="Неверно. Отказ нужен именно для сохранения высокого качества.")
    ]
    text_n2_arch_short.questions = [q_n2_arch_1]

    # =========================================================================
    # 7. N2 Archive (Long Article - 長文): 2021年7月 過去問 - デジタル時代の「思考の余白」
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
        source_exam="JLPT 2021.07 N2 過去問",
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
    # 8. N1 Archive (Editorial - 論説文): 2022年12月 過去問 - 他者理解の不可能性
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
        source_exam="JLPT 2022.12 N1 過去問",
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
        text_n5_1,
        text_n4_kyoto,
        text_n3_arch_short,
        text_n3_arch_med,
        text_n3_flyer,
        text_n2_arch_short,
        text_n2_article,
        text_n1
    ]

    db.add_all(all_texts)
    db.commit()
    print(f"Database seeded with {len(all_texts)} high-quality JLPT texts with real exam archives!")
    db.close()


if __name__ == "__main__":
    seed_database()
