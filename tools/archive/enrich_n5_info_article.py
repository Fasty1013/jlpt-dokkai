#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enricher for N5 info_search (12 items) and article (12 items).
Defines 100% unique authentic flyers, tables, articles, questions, and options.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

# =============================================================================
# 12 UNIQUE INFO SEARCH TEXTS (2 questions each)
# =============================================================================
INFO_DATA = [
    {
        "slug": "n5-info-001",
        "title": "さくらスポーツクラブの案内 (N5) #1",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">さくらスポーツクラブ利用案内</h2>
<table class="flyer-table">
  <thead><tr><th>プラン</th><th>使える時間</th><th>月会費</th></tr></thead>
  <tbody>
    <tr><td>朝コース</td><td>平日 9:00〜13:00</td><td>3,000円</td></tr>
    <tr class="highlight-row"><td>レギュラーコース</td><td>平日・土日 9:00〜21:00</td><td>5,000円</td></tr>
    <tr><td>夜コース</td><td>平日 18:00〜21:00</td><td>3,500円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【お知らせ】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>学生割引（学割）：</strong> 学生証を見せると、どのコースも<strong>毎月1,000円安く</strong>なります。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>休館日：</strong> 毎週月曜日はプール清掃のため休みです。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник спортивного клуба «Сакура». Утренний абонемент (будни 9-13): 3,000 иен. Обычный (будни и выходные 9-21): 5,000 иен. Вечерний (будни 18-21): 3,500 иен. Студенческая скидка: при предъявлении студенческого билета любой абонемент дешевле на 1,000 иен в месяц. Выходной день: каждый понедельник клуб закрыт на чистку бассейна.",
        "vocab": [{"word": "会費", "furigana": "かいひ", "translation": "членский взнос"}, {"word": "休館日", "furigana": "きゅうかんび", "translation": "выходной день заведения"}],
        "q1": {"prompt": "学生のキムさんがレギュラーコースを利用する場合、月会費はいくらですか。", "exp": "В предложении ev-q1 указано: студентам скидка 1,000 иен от любого тарифа. Обычный стоит 5,000 иен, значит 5,000 - 1,000 = 4,000 иен.", "opts": [
            {"num": 1, "text": "4,000円", "correct": True, "trap": None, "exp": "Верно! Базовая цена 5,000 иен минус скидка 1,000 иен = 4,000 иен (ev-q1)."},
            {"num": 2, "text": "5,000円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 5,000 иен — цена без студенческой скидки."},
            {"num": 3, "text": "3,000円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это цена утреннего курса."},
            {"num": 4, "text": "無料（0円）", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "このスポーツクラブが休みの日はいつですか。", "exp": "В предложении ev-q2 прямо сказано: каждый понедельник клуб закрыт.", "opts": [
            {"num": 1, "text": "毎週月曜日", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "毎週日曜日", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. В воскресенье клуб открыт."},
            {"num": 3, "text": "平日が全部休み", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "休みの日はない", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-002",
        "title": "市民プールの利用時間と休み (N5) #2",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">中央市民プール 利用案内</h2>
<table class="flyer-table">
  <thead><tr><th>区分</th><th>時間</th><th>料金（2時間）</th></tr></thead>
  <tbody>
    <tr><td>大人（高校生以上）</td><td>9:00〜17:00</td><td>400円</td></tr>
    <tr><td>子ども（小・中学生）</td><td>9:00〜17:00</td><td>200円</td></tr>
    <tr class="highlight-row"><td>夜間（全員）</td><td>18:00〜21:00</td><td>300円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【ご注意】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● 水泳帽（スイミングキャップ）を必ずかぶってください。受付で100円で借りられます。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>休館日：</strong> 毎週木曜日と、12月29日〜1月3日は休みです。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник городского бассейна. Взрослые (с 16 лет): 400 иен за 2 часа. Дети: 200 иен. Вечерний сеанс (18:00-21:00): 300 иен для всех. Примечания: обязательно надевайте плавательную шапочку (можно взять на стойке регистрации за 100 иен). Выходные: каждый четверг, а также с 29 декабря по 3 января.",
        "vocab": [{"word": "区分", "furigana": "くぶん", "translation": "категория"}, {"word": "夜間", "furigana": "やかん", "translation": "вечернее / ночное время"}],
        "q1": {"prompt": "水泳帽を持っていない人はどうしなければなりませんか。", "exp": "В предложении ev-q1 сказано: обязательно надеть шапочку, на стойке регистрации ее можно арендовать за 100 иен.", "opts": [
            {"num": 1, "text": "受付で100円で借りる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "帽子をかぶらずに泳ぐ。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Шапочка обязательна."},
            {"num": 3, "text": "家に帰って明日また来る。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "受付で3,000円で新しい水着を買う。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "大人が夜間（午後7時）に利用する場合、料金はいくらですか。", "exp": "В строке таблицы 夜間（全員）указано: 300 иен.", "opts": [
            {"num": 1, "text": "300円", "correct": True, "trap": None, "exp": "Верно! По таблице в вечернее время для всех тариф 300 иен."},
            {"num": 2, "text": "400円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 400 иен — дневной тариф для взрослых."},
            {"num": 3, "text": "200円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это детский дневной тариф."},
            {"num": 4, "text": "無料", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-003",
        "title": "中央図書館のカードの作り方 (N5) #3",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">中央図書館 利用カードのご案内</h2>
<table class="flyer-table">
  <thead><tr><th>貸出できるもの</th><th>冊数・点数</th><th>期間</th></tr></thead>
  <tbody>
    <tr><td>本・ざっし</td><td>1人 10冊まで</td><td>2週間</td></tr>
    <tr class="highlight-row"><td>CD・DVD</td><td>1人 2点まで</td><td>1週間</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【カードの作り方】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● 住所がわかるもの（在留カード、健康保険証、学生証など）を受付で見せてください。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● カードの発行（はっこう）は無料です。カードの有効期間は3年です。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник читательского билета Центральной библиотеки. Книги и журналы: до 10 штук на 2 недели. CD/DVD: до 2 штук на 1 неделю. Как оформить билет: покажите на стойке документ с адресом (карту резидента, страховку или студенческий билет). Оформление бесплатно, срок действия билета — 3 года.",
        "vocab": [{"word": "期間", "furigana": "きかん", "translation": "период, срок"}, {"word": "有効", "furigana": "ゆうこう", "translation": "действительный"}],
        "q1": {"prompt": "図書館カードを作るために何を持っていく必要がありますか。", "exp": "В предложении ev-q1 указано: документ с адресом (карта резидента, страховка, студенческий билет).", "opts": [
            {"num": 1, "text": "住所がわかるもの（在留カードや学生証など）", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "現金1,000円", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Оформление карты бесплатно."},
            {"num": 3, "text": "パスポート用の写真5枚", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "推薦状", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "CDやDVDは何点まで何週間借りることができますか。", "exp": "В таблице прямо указано: CD・DVD — 2点まで, 1週間.", "opts": [
            {"num": 1, "text": "2点まで、1週間", "correct": True, "trap": None, "exp": "Верно! Данные из строки CD・DVD таблицы."},
            {"num": 2, "text": "10冊まで、2週間", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это правила для обычных книг."},
            {"num": 3, "text": "何点でも無制限に借りられる", "correct": False, "trap": "extreme_condition", "exp": "Неверно."},
            {"num": 4, "text": "1点だけ、3日間", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-004",
        "title": "バスの切符と乗り場 (N5) #4",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">空港行き 高速バスのご案内</h2>
<table class="flyer-table">
  <thead><tr><th>のりば</th><th>行き先</th><th>片道料金</th><th>所要時間</th></tr></thead>
  <tbody>
    <tr><td>1番のりば</td><td>成田空港 第1・第2ターミナル</td><td>1,200円</td><td>約65分</td></tr>
    <tr class="highlight-row"><td>2番のりば</td><td>羽田空港 国内線・国際線</td><td>900円</td><td>約40分</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【ご案内】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● 子ども（小学生）は<strong>大人の半額</strong>（成田600円／羽田450円）です。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 切符はのりばの横の自動販売機で事前に買ってください。ICカードも使えます。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник скоростных автобусов в аэропорт. Платформа 1: в аэропорт Нарита (1,200 иен, около 65 мин). Платформа 2: в аэропорт Ханэда (900 иен, около 40 мин). Примечания: детский билет (школьники) — за полцены от взрослого. Билеты приобретайте заранее в автомате рядом с остановкой; также принимаются транспортные IC-карты.",
        "vocab": [{"word": "片道", "furigana": "かたみち", "translation": "в одну сторону"}, {"word": "所要時間", "furigana": "しょようじかん", "translation": "время в пути"}],
        "q1": {"prompt": "羽田空港へ行くバスに乗るには、何番のりばでいくら払いますか。", "exp": "По таблице: 羽田空港 — 2番のりば, 片道 900円.", "opts": [
            {"num": 1, "text": "2番のりばで、900円", "correct": True, "trap": None, "exp": "Верно! Точные данные из строки 2番 таблицы."},
            {"num": 2, "text": "1番のりばで、1,200円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 1番 — это автобус в Нариту."},
            {"num": 3, "text": "3番のりばで、450円", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "どこでも自由に無料", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "小学生の子ども料金について、正しいものはどれですか。", "exp": "В пункте ev-q1 прямо сказано: для детей действует тариф за полцены от взрослого.", "opts": [
            {"num": 1, "text": "大人料金の半額である。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "大人と同じ料金を払う。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "子どもはバスに乗れない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "大人の2倍の料金がかかる。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-005",
        "title": "秋の日本語教室のおしらせ (N5) #5",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">秋の市民日本語教室 参加者募集</h2>
<table class="flyer-table">
  <thead><tr><th>クラス</th><th>曜日・時間</th><th>定員</th><th>費用（全10回）</th></tr></thead>
  <tbody>
    <tr><td>はじめての日本語</td><td>毎週土曜日 10:00〜12:00</td><td>15名</td><td>2,000円</td></tr>
    <tr class="highlight-row"><td>会話・読解ステップ</td><td>毎週土曜日 14:00〜16:00</td><td>15名</td><td>2,000円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【申込について】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>教科書代：</strong> 教科書は教室で<strong>無料で配ります</strong>。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● <strong>申込締切：</strong> 10月15日（水）までに市民センター窓口へ申し込んでください。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Набор в осенний городской класс японского языка. Класс «Японский с нуля»: субботы 10:00-12:00, 15 человек, 2,000 иен за 10 занятий. Класс «Разговор и чтение»: субботы 14:00-16:00, 15 человек, 2,000 иен. Учебники выдаются в классе бесплатно. Дедлайн подачи заявки: до 15 октября (ср) в окне городского центра.",
        "vocab": [{"word": "定員", "furigana": "ていいん", "translation": "вместимость, лимит мест"}, {"word": "締切", "furigana": "しめきり", "translation": "крайний срок, дедлайн"}],
        "q1": {"prompt": "教科書のお金はいくら必要ですか。", "exp": "В предложении ev-q1 прямо указано: учебники раздаются бесплатно (0 иен).", "opts": [
            {"num": 1, "text": "無料（0円）で配られる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "2,000円かかる。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 2,000 иен — взнос за весь курс из 10 занятий."},
            {"num": 3, "text": "自分で本屋で買って持ってくる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "毎月5,000円払う。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "参加したい人はいつまでに申し込まなければなりませんか。", "exp": "В предложении ev-q2 указан дедлайн: до 15 октября (среда).", "opts": [
            {"num": 1, "text": "10月15日（水）まで", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "10月の終わりまでいつでもよい", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Есть строгий дедлайн."},
            {"num": 3, "text": "教室が始まる当日の朝", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "来年の4月まで", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-006",
        "title": "カメラ屋さんのセール案内 (N5) #6",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">秋のカメラ＆家電特別セール</h2>
<table class="flyer-table">
  <thead><tr><th>対象商品</th><th>割引率</th><th>特典</th></tr></thead>
  <tbody>
    <tr><td>デジタルカメラ本体</td><td>表示価格から 10% 引き</td><td>カメラケース無料</td></tr>
    <tr class="highlight-row"><td>レンズ各種</td><td>表示価格から 15% 引き</td><td>クリーニングクロスつき</td></tr>
    <tr><td>三脚・SDカード</td><td>表示価格から 20% 引き</td><td>なし</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【セール期間】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>期間：</strong> 10月12日（土）〜10月14日（月・祝）の3日間限定です。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● デジタルカメラ本体を買うと、<strong>カメラケースが無料</strong>でもらえます。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Осенняя распродажа фотоаппаратов и техники. Фотоаппараты: скидка 10% от цены, чехол в подарок бесплатно. Объективы: скидка 15%, чистящая салфетка в подарок. Штативы и SD-карты: скидка 20%. Сроки акции: 3 дня с 12 по 14 октября. При покупке фотоаппарата чехол предоставляется бесплатно.",
        "vocab": [{"word": "対象", "furigana": "たいしょう", "translation": "объект, категория товара"}, {"word": "本体", "furigana": "ほんたい", "translation": "корпус, сам аппарат"}],
        "q1": {"prompt": "セールはいつ行われますか。", "exp": "В предложении ev-q1 указано: 3 дня с 12 октября (суббота) по 14 октября (понедельник).", "opts": [
            {"num": 1, "text": "10月12日（土）〜10月14日（月・祝）の3日間", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "10月中ずっと毎日", "correct": False, "trap": "extreme_condition", "exp": "Неверно. Акция длится только 3 дня."},
            {"num": 3, "text": "毎週水曜日だけ", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "来月の最初の日曜日", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "デジタルカメラ本体を買った人は、どんな特典がもらえますか。", "exp": "В таблице и предложении ev-q2 указано: чехол для камеры бесплатно.", "opts": [
            {"num": 1, "text": "カメラケースが無料でもらえる。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q2."},
            {"num": 2, "text": "高級レンズが1本もらえる。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."},
            {"num": 3, "text": "旅行券が当たる。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "特典は何もない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-007",
        "title": "病院の受付時間と休診日 (N5) #7",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">みどり町内科クリニック 診療案内</h2>
<table class="flyer-table">
  <thead><tr><th>診療時間</th><th>月〜金</th><th>土</th><th>日・祝</th></tr></thead>
  <tbody>
    <tr><td>午前 9:00〜12:30</td><td>○</td><td>○</td><td>×（休診）</td></tr>
    <tr class="highlight-row"><td>午後 15:00〜18:30</td><td>○</td><td>×（休診）</td><td>×（休診）</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【初めて受診される方へ】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>持ち物：</strong> 健康保険証（またはマイナンバーカード）を必ずお持ちください。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 土曜日の午後は休診ですのでご注意ください。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник терапевтической клиники «Мидори-тё». Утренний прием (9:00-12:30): с понедельника по субботу. Вечерний прием (15:00-18:30): с понедельника по пятницу. В субботу во второй половине дня и по воскресеньям/праздникам — приема нет. При первом обращении обязательно возьмите страховой полис.",
        "vocab": [{"word": "診療", "furigana": "しんりょう", "translation": "прием врача, осмотр"}, {"word": "休診", "furigana": "きゅうしん", "translation": "выходной день в больнице"}],
        "q1": {"prompt": "土曜日に病院で診察を受けたい場合、何時に行かなければなりませんか。", "exp": "В таблице и ev-q2 указано: в субботу прием только утром (9:00〜12:30), днем приема нет.", "opts": [
            {"num": 1, "text": "午前の9:00〜12:30に行く。", "correct": True, "trap": None, "exp": "Верно! По таблице в субботу открыто только утром."},
            {"num": 2, "text": "午後の15:00〜18:30に行く。", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. В субботу днем клиника закрыта (ev-q2)."},
            {"num": 3, "text": "夜8時に行く。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "土曜日は一日中休みである。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Утром открыто."}
        ]},
        "q2": {"prompt": "初めて受診する人は何を持っていく必要がありますか。", "exp": "В предложении ev-q1 прямо сказано: обязательно взять полис медицинского страхования.", "opts": [
            {"num": 1, "text": "健康保険証", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "写真3枚と印鑑", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "卒業証明書", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も持っていく必要はない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-008",
        "title": "パソコン室の使い方のルール (N5) #8",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">学生センター パソコン室利用規則</h2>
<table class="flyer-table">
  <thead><tr><th>サービス</th><th>利用時間・枚数</th><th>料金</th></tr></thead>
  <tbody>
    <tr><td>パソコンの利用</td><td>1人 1回 2時間まで</td><td>無料</td></tr>
    <tr class="highlight-row"><td>白黒印刷（モノクロ）</td><td>制限なし</td><td>1枚 10円</td></tr>
    <tr><td>カラー印刷</td><td>制限なし</td><td>1枚 30円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【守るルール】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● パソコン室の中では、<strong>飲食（食べること・飲むこと）は禁止</strong>です。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 印刷をする時は、受付で印刷カード（100円〜）を買ってください。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Правила пользования компьютерным классом в студенческом центре. Использование ПК: бесплатно, до 2 часов за один раз. Черно-белая печать: 10 иен за лист. Цветная печать: 30 иен за лист. Правила: внутри компьютерного класса строго запрещено есть и пить. Для печати приобретите карту печати на стойке регистрации (от 100 иен).",
        "vocab": [{"word": "印刷", "furigana": "いんさつ", "translation": "печать на принтере"}, {"word": "飲食", "furigana": "いんしょく", "translation": "прием пищи и напитков"}],
        "q1": {"prompt": "パソコン室の中でしてはいけないことは何ですか。", "exp": "В предложении ev-q1 прямо сказано: запрещено есть и пить (飲食禁止).", "opts": [
            {"num": 1, "text": "飲食（食べることや飲むこと）", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "宿題をすること", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Учиться можно."},
            {"num": 3, "text": "日本語の辞書を使うこと", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "白黒でレポートを印刷すること", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Печать разрешена."}
        ]},
        "q2": {"prompt": "パソコンを1回で何時間まで利用することができますか。", "exp": "В таблице в первой строке указано: до 2 часов (2時間まで).", "opts": [
            {"num": 1, "text": "2時間まで", "correct": True, "trap": None, "exp": "Верно! Точно из таблицы."},
            {"num": 2, "text": "何時間でも朝まで自由", "correct": False, "trap": "extreme_condition", "exp": "Неверно. Есть лимит 2 часа."},
            {"num": 3, "text": "10分だけ", "correct": False, "trap": "misinterpretation", "exp": "Неверно."},
            {"num": 4, "text": "利用できない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-009",
        "title": "映画館のチケット割引案内 (N5) #9",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">シネマさくら 映画鑑賞料金と割引デー</h2>
<table class="flyer-table">
  <thead><tr><th>区分・サービスデー</th><th>対象・日時</th><th>料金</th></tr></thead>
  <tbody>
    <tr><td>一般（大人）</td><td>毎日</td><td>1,900円</td></tr>
    <tr><td>学生（大学・専門）</td><td>毎日（学生証必要）</td><td>1,500円</td></tr>
    <tr class="highlight-row"><td>水曜サービスデー</td><td>毎週水曜日（誰でも）</td><td>1,200円</td></tr>
    <tr><td>レイトショー</td><td>毎日 20:00以降の回</td><td>1,300円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【お得な情報】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>水曜日は誰でも1,200円</strong>で映画を見ることができます。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 学生割引を利用する人は、チケット購入時に<strong>学生証</strong>を提示してください。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник кинотеатра «Синема Сакура». Взрослый билет: 1,900 иен. Студенческий: 1,500 иен (при наличии студенческого билета). День скидок по средам: 1,200 иен для всех. Ночной сеанс (после 20:00): 1,300 иен. По средам любой зритель может посмотреть кино за 1,200 иен. Для студенческой скидки обязательно покажите студенческий билет.",
        "vocab": [{"word": "鑑賞", "furigana": "かんしょう", "translation": "просмотр (фильма, искусства)"}, {"word": "提示", "furigana": "ていじ", "translation": "предъявление (документа)"}],
        "q1": {"prompt": "水曜日に映画を見に行く場合、チケット代はいくらですか。", "exp": "В таблице и в пункте ev-q1 указано: по средам для всех билет стоит 1,200 иен.", "opts": [
            {"num": 1, "text": "1,200円", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1 и таблицы."},
            {"num": 2, "text": "1,900円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 1,900 иен — обычный взрослый тариф в другие дни."},
            {"num": 3, "text": "1,500円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 1,500 иен — студенческий тариф в обычные дни."},
            {"num": 4, "text": "無料", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "学生割引を使うにはどうしなければなりませんか。", "exp": "В пункте ev-q2 сказано: обязательно предъявить студенческий билет.", "opts": [
            {"num": 1, "text": "チケット購入時に学生証を見せる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q2."},
            {"num": 2, "text": "夜8時以降にしか入れない。", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Это правило ночного сеанса."},
            {"num": 3, "text": "先生と一緒に行く必要がある。", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も見せなくてよい。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-010",
        "title": "スキー場のリフト料金 (N5) #10",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">白山スキー場 リフト券＆レンタル料金</h2>
<table class="flyer-table">
  <thead><tr><th>チケット種類</th><th>時間</th><th>大人料金</th><th>子ども料金</th></tr></thead>
  <tbody>
    <tr><td>1日券</td><td>8:30〜17:00</td><td>4,500円</td><td>2,500円</td></tr>
    <tr class="highlight-row"><td>4時間券</td><td>購入から4時間</td><td>3,200円</td><td>1,800円</td></tr>
    <tr><td>ナイター券</td><td>17:00〜21:00</td><td>2,000円</td><td>1,000円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【レンタル情報】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● スキー・スノーボード用具セットは<strong>1日 3,000円</strong>で借りられます。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● レストランで使える500円のお食事券がつく「お得パック」もあります。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Справочник горнолыжного курорта «Хакусан». Дневной ски-пасс (8:30-17:00): взрослые 4,500 иен, дети 2,500 иен. 4-часовой билет: 3,200 иен. Вечерний билет (17:00-21:00): 2,000 иен. Прокат: комплект лыж или сноуборда стоит 3,000 иен в день. Доступен выгодный комбо-билет с купоном на обед в 500 иен.",
        "vocab": [{"word": "種類", "furigana": "しゅるい", "translation": "вид, тип"}, {"word": "用具", "furigana": "ようぐ", "translation": "снаряжение, экипировка"}],
        "q1": {"prompt": "大人が4時間だけスキーをする場合、リフト券はいくらですか。", "exp": "По таблице в строке 4時間券: взрослый тариф составляет 3,200 иен.", "opts": [
            {"num": 1, "text": "3,200円", "correct": True, "trap": None, "exp": "Верно! Точно из таблицы для 4-часового билета."},
            {"num": 2, "text": "4,500円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 4,500 иен — билет на целый день."},
            {"num": 3, "text": "1,800円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 1,800 иен — детский 4-часовой билет."},
            {"num": 4, "text": "2,000円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это вечерний ски-пасс."}
        ]},
        "q2": {"prompt": "スキーの用具セットを借りたい場合、いくらかかりますか。", "exp": "В предложении ev-q1 прямо сказано: комплект снаряжения стоит 3,000 иен в день.", "opts": [
            {"num": 1, "text": "1日 3,000円", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "無料（0円）", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "10,000円", "correct": False, "trap": "extreme_condition", "exp": "Неверно."},
            {"num": 4, "text": "レンタルはやっていない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]}
    },
    {
        "slug": "n5-info-011",
        "title": "電話会社の学割プラン (N5) #11",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">さくらモバイル 学生応援スマホプラン</h2>
<table class="flyer-table">
  <thead><tr><th>プラン名</th><th>月間データ容量</th><th>月額基本料（学割適用後）</th></tr></thead>
  <tbody>
    <tr><td>プランS（ミニ）</td><td>3GB</td><td>1,200円</td></tr>
    <tr class="highlight-row"><td>プランM（標準）</td><td>10GB</td><td>2,200円</td></tr>
    <tr><td>プランL（たっぷり）</td><td>25GB</td><td>3,500円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【学割の特典と条件】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>通話特典：</strong> 1回5分以内の国内通話は何回かけても<strong>無料</strong>です。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 申込には、学校の発行した<strong>学生証</strong>と在留カードが必要です。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Студенческий тариф от «Сакура Мобайл». Тариф S (3 ГБ): 1,200 иен/мес со скидкой. Тариф M (10 ГБ): 2,200 иен/мес. Тариф L (25 ГБ): 3,500 иен/мес. Бонусы: звонки до 5 минут по Японии полностью бесплатны без ограничений по количеству. Условия: требуется студенческий билет и карта резидента.",
        "vocab": [{"word": "容量", "furigana": "ようりょう", "translation": "объем (памяти, данных)"}, {"word": "通話", "furigana": "つうわ", "translation": "телефонный звонок, разговор"}],
        "q1": {"prompt": "10GB使えるプランMは、毎月いくらですか。", "exp": "По таблице в строке プランM указано: 2,200円.", "opts": [
            {"num": 1, "text": "2,200円", "correct": True, "trap": None, "exp": "Верно! Точная сумма из строкиプランM таблицы."},
            {"num": 2, "text": "1,200円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 1,200 иен — цена тарифа S (3GB)."},
            {"num": 3, "text": "3,500円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 3,500 иен — тариф L."},
            {"num": 4, "text": "5,000円", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "電話の通話について、どんな特典がありますか。", "exp": "В предложении ev-q1 прямо сказано: звонки длительностью до 5 минут бесплатны.", "opts": [
            {"num": 1, "text": "1回5分以内の通話が何回でも無料になる。", "correct": True, "trap": None, "exp": "Верно! Предложение ev-q1."},
            {"num": 2, "text": "電話は一切使えない。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "1分ごとに100円かかる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "海外への電話が全部無料。", "correct": False, "trap": "extreme_condition", "exp": "Неверно (только внутренние звонки)."}
        ]}
    },
    {
        "slug": "n5-info-012",
        "title": "荷物の送り方と料金 (N5) #12",
        "body": """<div class="flyer-container">
<h2 class="flyer-title">スピード宅配便 サイズ別料金表（関東エリア内）</h2>
<table class="flyer-table">
  <thead><tr><th>サイズ（縦＋横＋高さ）</th><th>重さ</th><th>通常料金</th></tr></thead>
  <tbody>
    <tr><td>Sサイズ（60cm以内）</td><td>2kgまで</td><td>700円</td></tr>
    <tr class="highlight-row"><td>Mサイズ（80cm以内）</td><td>5kgまで</td><td>950円</td></tr>
    <tr><td>Lサイズ（100cm以内）</td><td>10kgまで</td><td>1,200円</td></tr>
  </tbody>
</table>
<div class="flyer-notes">
  <h3>【割引とお届けオプション】</h3>
  <ul>
    <li><span id="ev-q1" data-evidence="ev-q1">● <strong>持込割引：</strong> 営業所の窓口へ自分で荷物を持っていくと、<strong>1個につき100円引き</strong>になります。</span></li>
    <li><span id="ev-q2" data-evidence="ev-q2">● 午前中（9:00〜12:00）のお届け指定は無料です。</span></li>
  </ul>
</div>
</div>""",
        "trans": "Тарифы экспресс-доставки по региону Канто. Размер S (до 60 см, до 2 кг): 700 иен. Размер M (до 80 см, до 5 кг): 950 иен. Размер L (до 100 см, до 10 кг): 1,200 иен. Скидки: при самостоятельной сдаче посылки в пункт приема скидка 100 иен за коробку. Доставка утром (9:00-12:00) бесплатна.",
        "vocab": [{"word": "宅配便", "furigana": "たくはいびん", "translation": "курьерская доставка"}, {"word": "持込", "furigana": "もちこみ", "translation": "приносить с собой (лично сдавать)"}],
        "q1": {"prompt": "営業所の窓口に自分で荷物を持っていくと、どうなりますか。", "exp": "В предложении ev-q1 указано: при самостоятельной сдаче скидка 100 иен за штуку.", "opts": [
            {"num": 1, "text": "1個につき100円安くなる。", "correct": True, "trap": None, "exp": "Верно! Точно из предложения ev-q1."},
            {"num": 2, "text": "手数料として200円多く払う。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Дается скидка, а не доплата."},
            {"num": 3, "text": "荷物を送ることができなくなる。", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "無料で送ることができる。", "correct": False, "trap": "extreme_condition", "exp": "Неверно."}
        ]},
        "q2": {"prompt": "重さ3kg、縦横高さ合計75cmの荷物を窓口へ持参した場合、いくら払いますか。", "exp": "75cm и 3kg относится к M-размеру (до 80cm/5kg) = 950円. Минус 100円 скидка за сдачу в окно = 850円.", "opts": [
            {"num": 1, "text": "850円", "correct": True, "trap": None, "exp": "Верно! Базовый тариф M-размера 950 иен минус 100 иен скидка = 850 иен."},
            {"num": 2, "text": "950円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 950 иен — без учета скидки 100 иен за самопривоз."},
            {"num": 3, "text": "700円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это тариф для размера S (до 60cm/2kg)."},
            {"num": 4, "text": "1,200円", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это тариф L-размера."}
        ]}
    }
]

print(f"INFO_DATA defined: {len(INFO_DATA)} items.")
