#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enricher for content/n5.json:
Replaces all copy-pasted and duplicate texts with authentic, diverse, and linguistically accurate
JLPT N5 reading materials according to @jlpt-expert standards.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
N5_PATH = CONTENT_DIR / "n5.json"

# --- 12 Unique Short Texts (N5) ---
SHORT_DATA = [
    {
        "title": "図書館の利用時間変更 (N5) #1",
        "body": """<div class="passage-body">
<p><ruby>来週<rt>らいしゅう</rt></ruby>の<ruby>月曜日<rt>げつようび</rt></ruby>から、<ruby>図書館<rt>としょかん</rt></ruby>の<ruby>時間<rt>じかん</rt></ruby>が<ruby>変<rt>か</rt></ruby>わります。</p>
<p><ruby>平日<rt>へいじつ</rt></ruby>は<ruby>午前<rt>ごぜん</rt></ruby>9時（くじ）から<ruby>午後<rt>ごご</rt></ruby>6時（ろくじ）までです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>土曜日<rt>どようび</rt></ruby>と<ruby>日曜日<rt>にちようび</rt></ruby>は、<ruby>午前<rt>ごぜん</rt></ruby>10時（じゅうじ）から<ruby>午後<rt>ごご</rt></ruby>5時（ごじ）まで<ruby>開<rt>あ</rt></ruby>いています。</span></p>
<p>どうぞよろしくお<ruby>願<rt>ねが</rt></ruby>いします。</p>
</div>""",
        "trans": "Со следующего понедельника меняются часы работы библиотеки. По будням — с 9:00 до 18:00. По субботам и воскресеньям библиотека открыта с 10:00 до 17:00. Спасибо за понимание.",
        "prompt": "日曜日は何時から何時まで図書館が開いていますか。",
        "explanation": "В предложении ev-q1 прямо сказано: по субботам и воскресеньям библиотека открыта с 10:00 до 17:00.",
        "options": [
            {"num": 1, "text": "午前10時から午後5時まで", "correct": True, "trap": None, "exp": "Правильно! Точное время работы в выходные дни (ev-q1)."},
            {"num": 2, "text": "午前9時から午後6時まで", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Это часы работы по будням (平日)."},
            {"num": 3, "text": "午前9時から午後5時まで", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Такого расписания в тексте нет."},
            {"num": 4, "text": "午後1時から午後6時まで", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."}
        ]
    },
    {
        "title": "週末の公園そうじ (N5) #2",
        "body": """<div class="passage-body">
<p><ruby>今週<rt>こんしゅう</rt></ruby>の<ruby>日曜日<rt>にちようび</rt></ruby>の<ruby>朝<rt>あさ</rt></ruby>8時（はちじ）から、<ruby>中央<rt>ちゅうおう</rt></ruby><ruby>公園<rt>こうえん</rt></ruby>のそうじをします。</p>
<p><ruby>雨<rt>あめ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>は<ruby>来週<rt>らいしゅう</rt></ruby>になります。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>参加<rt>さんか</rt></ruby>する<ruby>人<rt>ひと</rt></ruby>は、<ruby>汚<rt>よご</rt></ruby>れてもいい<ruby>服<rt>ふく</rt></ruby>を<ruby>着<rt>き</rt></ruby>て、<ruby>手袋<rt>てぶくろ</rt></ruby>を<ruby>持<rt>も</rt></ruby>ってきてください。</span></p>
<p>ごみ<ruby>袋<rt>ぶくろ</rt></ruby>は<ruby>公園<rt>こうえん</rt></ruby>の<ruby>前<rt>まえ</rt></ruby>で<ruby>渡<rt>わた</rt></ruby>します。</p>
</div>""",
        "trans": "В это воскресенье с 8 утра состоится уборка Центрального парка. В случае дождя мероприятие переносится на следующую неделю. Участников просят надеть рабочую одежду и принести перчатки. Мешки для мусора раздадут у входа.",
        "prompt": "そうじに参加する人は何を持ってこなければなりませんか。",
        "explanation": "В тексте четко указано (ev-q1): участники должны надеть одежду, которую не жалко испачкать, и взять с собой перчатки (手袋).",
        "options": [
            {"num": 1, "text": "手袋（てぶくろ）", "correct": True, "trap": None, "exp": "Верно! В тексте прямо сказано принести перчатки (ev-q1)."},
            {"num": 2, "text": "ごみ袋（ぶくろ）", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Мешки для мусора раздадут у парка."},
            {"num": 3, "text": "傘（かさ）", "correct": False, "trap": "not_mentioned", "exp": "Неверно. В дождь уборка переносится."},
            {"num": 4, "text": "お金（かね）", "correct": False, "trap": "not_mentioned", "exp": "Неверно. Участие бесплатное."}
        ]
    },
    {
        "title": "留学生パーティー (N5) #3",
        "body": """<div class="passage-body">
<p><ruby>来週<rt>らいしゅう</rt></ruby>の<ruby>金曜日<rt>きんようび</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>6時（ろくじ）から、<ruby>留学生<rt>りゅうがくせい</rt></ruby>パーティーをします。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>場所<rt>ばしょ</rt></ruby>は<ruby>学生<rt>がくせい</rt></ruby>センターの3<ruby>階<rt>かい</rt></ruby>の301<ruby>号室<rt>ごうしつ</rt></ruby>です。</span></p>
<p>お<ruby>金<rt>かね</rt></ruby>は一人（ひとり）500<ruby>円<rt>えん</rt></ruby>です。<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>と<ruby>飲<rt>の</rt></ruby>み<ruby>物<rt>もの</rt></ruby>があります。</p>
<p><ruby>参加<rt>さんか</rt></ruby>したい<ruby>人<rt>ひと</rt></ruby>は、<ruby>水曜日<rt>すいようび</rt></ruby>までに<ruby>山田<rt>やまだ</rt></ruby>さんに言ってください。</p>
</div>""",
        "trans": "В следующую пятницу с 18:00 состоится вечеринка иностранных студентов. Место проведения — Студенческий центр, 3-й этаж, комната 301. Взнос 500 иен с человека. Еда и напитки включены. Желающих просим сообщить Ямаде-сану до среды.",
        "prompt": "パーティーはどこで行われますか。",
        "explanation": "В предложении ev-q1 указано место: комната 301 на 3-м этаже студенческого центра.",
        "options": [
            {"num": 1, "text": "学生センターの301号室", "correct": True, "trap": None, "exp": "Верно! Точное указание аудитории (ev-q1)."},
            {"num": 2, "text": "学生センターの1階", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Мероприятие на 3-м этаже."},
            {"num": 3, "text": "山田さんの家", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Ямаде-сану нужно лишь сдать заявку."},
            {"num": 4, "text": "中央公園の広場", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "わすれもののおしらせ (N5) #4",
        "body": """<div class="passage-body">
<p>2<ruby>階<rt>かい</rt></ruby>の<ruby>教室<rt>きょうしつ</rt></ruby>に<ruby>黒<rt>くろ</rt></ruby>い<ruby>傘<rt>かさ</rt></ruby>のわすれものがありました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>心<rt>こころ</rt></ruby>あたりのある<ruby>人<rt>ひと</rt></ruby>は、1<ruby>階<rt>かい</rt></ruby>の<ruby>事務室<rt>じむしつ</rt></ruby>に<ruby>来<rt>き</rt></ruby>てください。</span></p>
<p><ruby>今週<rt>こんしゅう</rt></ruby>の<ruby>金曜日<rt>きんようび</rt></ruby>まで<ruby>預<rt>あず</rt></ruby>かっています。</p>
<p>よろしくお<ruby>願<rt>ねが</rt></ruby>いします。</p>
</div>""",
        "trans": "В аудитории на 2-м этаже был забыт черный зонт. Если вы потеряли зонт, обратитесь в канцелярию на 1-м этаже. Вещь хранится до пятницы текущей недели.",
        "prompt": "傘をわすれた人はどうしなければなりませんか。",
        "explanation": "В предложении ev-q1 написано: прийти в канцелярию на первом этаже (1階の事務室に来てください).",
        "options": [
            {"num": 1, "text": "1階の事務室に行く", "correct": True, "trap": None, "exp": "Верно! Зонт находится в канцелярии на 1-м этаже (ev-q1)."},
            {"num": 2, "text": "2階の教室で探す", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Зонт уже перенесен в канцелярию."},
            {"num": 3, "text": "新しい傘を買う", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "来週まで待つ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Срок хранения — только до пятницы."}
        ]
    },
    {
        "title": "エレベーターの点検 (N5) #5",
        "body": """<div class="passage-body">
<p><ruby>明日<rt>あした</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>1時（いちじ）から<ruby>午後<rt>ごご</rt></ruby>3時（さんじ）まで、エレベーターの<ruby>点検<rt>てんけん</rt></ruby>をします。</p>
<p><span id="ev-q1" data-evidence="ev-q1">この<ruby>時間<rt>じかん</rt></ruby>はエレベーターを<ruby>使<rt>つか</rt></ruby>うことができませんので、<ruby>階段<rt>かいだん</rt></ruby>をご<ruby>利用<rt>りよう</rt></ruby>ください。</span></p>
<p>ご<ruby>不便<rt>ふべん</rt></ruby>をおかけしますが、ご<ruby>協力<rt>きょうりょく</rt></ruby>をお<ruby>願<rt>ねが</rt></ruby>いします。</p>
</div>""",
        "trans": "Завтра с 13:00 до 15:00 проводится техосмотр лифта. В это время лифт работать не будет, просьба пользоваться лестницей. Приносим извинения за неудобства.",
        "prompt": "明日の午後2時に上の階へ行く時、どうしなければなりませんか。",
        "explanation": "В период с 13:00 до 15:00 лифт выключен, необходимо пользоваться лестницей (ev-q1).",
        "options": [
            {"num": 1, "text": "階段（かいだん）を使う", "correct": True, "trap": None, "exp": "Верно! Лифт остановлен, нужно идти по лестнице (ev-q1)."},
            {"num": 2, "text": "エレベーターを待つ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Лифт не работает во время техосмотра."},
            {"num": 3, "text": "事務室に電話する", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "午後5時まで待つ", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Работы завершатся в 15:00."}
        ]
    },
    {
        "title": "健康しんだんの日 (N5) #6",
        "body": """<div class="passage-body">
<p><ruby>来月<rt>らいげつ</rt></ruby>の10<ruby>日<rt>とおか</rt></ruby>に、<ruby>健康<rt>けんこう</rt></ruby><ruby>診断<rt>しんだん</rt></ruby>があります。</p>
<p><ruby>朝<rt>あさ</rt></ruby>9時（くじ）から11時（じゅういちじ）までに<ruby>体育館<rt>たいいくかん</rt></ruby>へ<ruby>来<rt>き</rt></ruby>てください。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>前<rt>まえ</rt></ruby>の<ruby>日<rt>ひ</rt></ruby>の<ruby>夜<rt>よる</rt></ruby>9時（くじ）から、<ruby>何<rt>なに</rt></ruby>も<ruby>食<rt>た</rt></ruby>べないでください。</span></p>
<p><ruby>水<rt>みず</rt></ruby>は<ruby>飲<rt>の</rt></ruby>んでもかまいません。</p>
</div>""",
        "trans": "10-го числа следующего месяца проводится медосмотр. Приходите в спортзал с 9:00 до 11:00. С 21:00 предыдущего дня ничего не ешьте. Воду пить разрешается.",
        "prompt": "健康診断を受ける人は、どうしなければなりませんか。",
        "explanation": "В тексте четко сказано (ev-q1): с 21:00 накануне ничего не есть.",
        "options": [
            {"num": 1, "text": "前の日の夜9時から何も食べない", "correct": True, "trap": None, "exp": "Верно! Четкое правило подготовки (ev-q1)."},
            {"num": 2, "text": "水を絶対に飲んではいけない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Воду пить можно (水は飲んでもかまいません)."},
            {"num": 3, "text": "当日の朝ごはんをたくさん食べる", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Завтракать запрещено."},
            {"num": 4, "text": "お昼の12時以降に行く", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Прием с 9 до 11 утра."}
        ]
    },
    {
        "title": "アルバイトの時間 (N5) #7",
        "body": """<div class="passage-body">
<p><ruby>田中<rt>たなか</rt></ruby>さん、店長（てんちょう）の<ruby>佐藤<rt>さとう</rt></ruby>です。</p>
<p><ruby>今週<rt>こんしゅう</rt></ruby>のシフトですが、<ruby>木曜日<rt>もくようび</rt></ruby>にアルバイトが<ruby>足<rt>た</rt></ruby>りなくなりました。</p>
<p><span id="ev-q1" data-evidence="ev-q1">もしできたら、<ruby>金曜日<rt>きんようび</rt></ruby>ではなく<ruby>木曜日<rt>もくようび</rt></ruby>の<ruby>夕方<rt>ゆうがた</rt></ruby>に<ruby>来<rt>き</rt></ruby>てもらえませんか。</span></p>
<p><ruby>返事<rt>へんじ</rt></ruby>を<ruby>今日<rt>きょう</rt></ruby>の<ruby>夜<rt>よる</rt></ruby>までにメールでください。</p>
</div>""",
        "trans": "Танака-сан, это менеджер Сато. На этой неделе в четверг не хватает сотрудников. Если у вас получится, не могли бы вы выйти в четверг вечером вместо пятницы? Дайте ответ по почте до сегодняшнего вечера.",
        "prompt": "店長は田中さんに何をお願いしていますか。",
        "explanation": "Менеджер просит Танаку выйти в четверг вечером вместо пятницы (ev-q1).",
        "options": [
            {"num": 1, "text": "金曜日のかわりに木曜日に働くこと", "correct": True, "trap": None, "exp": "Верно! Просьба выйти в четверг вместо пятницы (ev-q1)."},
            {"num": 2, "text": "木曜日のアルバイトを休むこと", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Наоборот, просят выйти на смену."},
            {"num": 3, "text": "今すぐ店に電話をかけること", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Ответ просят отправить по почте."},
            {"num": 4, "text": "来週のシフトを増やすこと", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "荷物の配達について (N5) #8",
        "body": """<div class="passage-body">
<p><ruby>不在<rt>ふざい</rt></ruby><ruby>連絡票<rt>れんらくひょう</rt></ruby></p>
<p><ruby>本日<rt>ほんじつ</rt></ruby>、お<ruby>荷物<rt>にもつ</rt></ruby>をお<ruby>届<rt>とど</rt></ruby>けにまいりましたが、お<ruby>留守<rt>るす</rt></ruby>でした。</p>
<p><span id="ev-q1" data-evidence="ev-q1">もう<ruby>一度<rt>いちど</rt></ruby><ruby>届<rt>とど</rt></ruby>けてほしい<ruby>場合<rt>ばあい</rt></ruby>は、<ruby>本日<rt>ほんじつ</rt></ruby>の<ruby>夜<rt>よる</rt></ruby>7時（しちじ）までに<ruby>電話<rt>でんわ</rt></ruby>をください。</span></p>
<p>どうぞよろしくお<ruby>願<rt>ねが</rt></ruby>いいたします。</p>
</div>""",
        "trans": "Уведомление о доставке. Сегодня была предпринята попытка доставки посылки, однако вас не оказалось дома. Для повторной доставки просьба позвонить сегодня до 19:00.",
        "prompt": "荷物をもう一度届けてもらうには、どうすればいいですか。",
        "explanation": "В тексте четко сказано (ev-q1): позвонить сегодня до 19:00.",
        "options": [
            {"num": 1, "text": "今日の夜7時までに電話する", "correct": True, "trap": None, "exp": "Верно! Точная инструкция из уведомления (ev-q1)."},
            {"num": 2, "text": "郵便局へ荷物を取りに行く", "correct": False, "trap": "not_mentioned", "exp": "Неверно. Указан заказ повторной доставки по телефону."},
            {"num": 3, "text": "明日まで何もしないで待つ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Нужно сделать звонок."},
            {"num": 4, "text": "荷物の送り主に連絡する", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]
    },
    {
        "title": "カフェの新しいケーキ (N5) #9",
        "body": """<div class="passage-body">
<p>さくらカフェの<ruby>新<rt>あたら</rt></ruby>しいお知らせです。</p>
<p><ruby>明日<rt>あした</rt></ruby>から「いちごのケーキ」を<ruby>始<rt>はじ</rt></ruby>めます。<ruby>一<rt>ひと</rt></ruby>つ450<ruby>円<rt>えん</rt></ruby>です。</p>
<p><span id="ev-q1" data-evidence="ev-q1">とても<ruby>人気<rt>にんき</rt></ruby>がありますので、1<ruby>日<rt>にち</rt></ruby>に20<ruby>個<rt>こ</rt></ruby>だけの<ruby>限定<rt>げんてい</rt></ruby><ruby>販売<rt>はんばい</rt></ruby>です。</span></p>
<p>ぜひ<ruby>食<rt>た</rt></ruby>べに<ruby>来<rt>き</rt></ruby>てください。</p>
</div>""",
        "trans": "Новость от кафе Сакура. С завтрашнего дня в продаже клубничный торт по цене 450 иен. Из-за высокого спроса количество ограничено 20 порциями в день. Будем рады видеть вас!",
        "prompt": "新しいケーキについて、正しいものはどれか。",
        "explanation": "В предложении ev-q1 указано: ограниченная продажа по 20 штук в день (1日に20個だけの限定販売).",
        "options": [
            {"num": 1, "text": "1日に20個しか売られない", "correct": True, "trap": None, "exp": "Верно! Лимит 20 штук в сутки (ev-q1)."},
            {"num": 2, "text": "無料で食べることができる", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Цена торта 450 иен."},
            {"num": 3, "text": "来週から売り始める", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. Продажи начинаются завтра (明日から)."},
            {"num": 4, "text": "夕方だけ売っている", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "バス停の場所 (N5) #10",
        "body": """<div class="passage-body">
<p><ruby>道路<rt>どうろ</rt></ruby>の<ruby>工事<rt>こうじ</rt></ruby>のため、バスの<ruby>乗<rt>の</rt></ruby>り<ruby>場<rt>ば</rt></ruby>が<ruby>変<rt>か</rt></ruby>わります。</p>
<p><ruby>期間<rt>きかん</rt></ruby>は5<ruby>月<rt>がつ</rt></ruby>1<ruby>日<rt>ついたち</rt></ruby>から5<ruby>月<rt>がつ</rt></ruby>15<ruby>日<rt>じゅうごにち</rt></ruby>までです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>新<rt>あたら</rt></ruby>しいバス<ruby>停<rt>てい</rt></ruby>は、これまでの<ruby>場所<rt>ばしょ</rt></ruby>から<ruby>右<rt>みぎ</rt></ruby>へ50メートル<ruby>歩<rt>ある</rt></ruby>いたコンビニの<ruby>前<rt>まえ</rt></ruby>です。</span></p>
<p>お<ruby>間違<rt>まちが</rt></ruby>いのないようにお<ruby>願<rt>ねが</rt></ruby>いします。</p>
</div>""",
        "trans": "Из-за дорожных работ остановка автобуса переносится с 1 по 15 мая. Новая остановка находится перед магазином комбини в 50 метрах направо от прежнего места.",
        "prompt": "工事の間、どこでバスに乗りますか。",
        "explanation": "В предложении ev-q1 написано: у магазина комбини в 50 метрах направо от старой остановки.",
        "options": [
            {"num": 1, "text": "これまでの場所から右へ50メートルのコンビニの前", "correct": True, "trap": None, "exp": "Верно! Точное указание временной остановки (ev-q1)."},
            {"num": 2, "text": "駅の中の切符売り場", "correct": False, "trap": "misinterpretation", "exp": "Неверно."},
            {"num": 3, "text": "図書館の裏側", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "工事している道路の真ん中", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]
    },
    {
        "title": "スピーチ大会 (N5) #11",
        "body": """<div class="passage-body">
<p><ruby>日本語<rt>にほんご</rt></ruby><ruby>学校<rt>がっこう</rt></ruby>のスピーチ<ruby>大会<rt>たいかい</rt></ruby>のおしらせです。</p>
<p><ruby>日時<rt>にちじ</rt></ruby>は7<ruby>月<rt>がつ</rt></ruby>20<ruby>日<rt>はつか</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>2時（にじ）からです。</p>
<p><span id="ev-q1" data-evidence="ev-q1">スピーチをしたい<ruby>人<rt>ひと</rt></ruby>は、6<ruby>月<rt>がつ</rt></ruby>30<ruby>日<rt>さんじゅうにち</rt></ruby>までに<ruby>自分<rt>じぶん</rt></ruby>の<ruby>原稿<rt>げんこう</rt></ruby>を<ruby>先生<rt>せんせい</rt></ruby>に<ruby>出<rt>だ</rt></ruby>してください。</span></p>
<p>たくさんのご<ruby>応募<rt>おうぼ</rt></ruby>をお<ruby>待<rt>ま</rt></ruby>ちしています。</p>
</div>""",
        "trans": "Объявление о конкурсе речей школы японского языка. Дата: 20 июля в 14:00. Желающие выступить с речью должны сдать рукопись преподавателю до 30 июня.",
        "prompt": "スピーチをしたい人は、何をしなければなりませんか。",
        "explanation": "В тексте сказано (ev-q1): сдать свою рукопись преподавателю до 30 июня.",
        "options": [
            {"num": 1, "text": "6月30日までに原稿を先生に出す", "correct": True, "trap": None, "exp": "Верно! Срок и требование для участия (ev-q1)."},
            {"num": 2, "text": "7月20日に原稿を書き始める", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. 20 июля уже сам конкурс."},
            {"num": 3, "text": "参加費500円を支払う", "correct": False, "trap": "not_mentioned", "exp": "Неверно. Плата не требуется."},
            {"num": 4, "text": "スピーチを聞くだけにする", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ]
    },
    {
        "title": "授業の休み (N5) #12",
        "body": """<div class="passage-body">
<p><ruby>学生<rt>がくせい</rt></ruby>のみなさんへ。</p>
<p><ruby>明日<rt>あした</rt></ruby>の<ruby>木曜日<rt>もくようび</rt></ruby>は<ruby>大<rt>おお</rt></ruby>きな<ruby>台風<rt>たいふう</rt></ruby>が<ruby>来<rt>く</rt></ruby>るため、すべての<ruby>授業<rt>じゅぎょう</rt></ruby>はお<ruby>休<rt>やす</rt></ruby>みです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>危<rt>あぶ</rt></ruby>ないですから、<ruby>外<rt>そと</rt></ruby>へ<ruby>出<rt>で</rt></ruby>ないで、<ruby>家<rt>いえ</rt></ruby>で<ruby>勉強<rt>べんきょう</rt></ruby>してください。</span></p>
<p><ruby>金曜日<rt>きんようび</rt></ruby>からは<ruby>普通<rt>ふつう</rt></ruby>どおり<ruby>授業<rt>じゅぎょう</rt></ruby>があります。</p>
</div>""",
        "trans": "Студентам. Завтра в четверг из-за надвигающегося сильного тайфуна все занятия отменяются. В целях безопасности не выходите на улицу и занимайтесь дома. С пятницы занятия возобновятся в обычном режиме.",
        "prompt": "明日はどうしなければなりませんか。",
        "explanation": "Из-за тайфуна занятия отменены, студентам предписано оставаться дома и учиться (ev-q1).",
        "options": [
            {"num": 1, "text": "学校へ行かず、家で勉強する", "correct": True, "trap": None, "exp": "Верно! Предписание оставаться дома из-за тайфуна (ev-q1)."},
            {"num": 2, "text": "台風を見るために外へ出かける", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Выходить на улицу опасно."},
            {"num": 3, "text": "金曜日も学校を休む", "correct": False, "trap": "misinterpretation", "exp": "Неверно. В пятницу занятия в обычном режиме."},
            {"num": 4, "text": "朝早く学校へ行く", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Школа закрыта."}
        ]
    }
]

# --- 12 Unique Medium Texts (N5) ---
MEDIUM_DATA = [
    {
        "title": "私の好きな町と公園 (N5) #1",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>の<ruby>住<rt>す</rt></ruby>んでいる<ruby>町<rt>まち</rt></ruby>は、<ruby>緑<rt>みどり</rt></ruby>が<ruby>多<rt>おお</rt></ruby>くてとても<ruby>静<rt>しず</rt></ruby>かなところです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>駅<rt>えき</rt></ruby>の<ruby>近<rt>ちか</rt></ruby>くには<ruby>大<rt>おお</rt></ruby>きな<ruby>公園<rt>こうえん</rt></ruby>があって、<ruby>春<rt>はる</rt></ruby>にはきれいな<ruby>桜<rt>さくら</rt></ruby>の花（はな）がたくさん<ruby>咲<rt>さ</rt></ruby>きます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>は<ruby>毎週<rt>まいしゅう</rt></ruby><ruby>日曜日<rt>にちようび</rt></ruby>の<ruby>朝<rt>あさ</rt></ruby>に、この<ruby>公園<rt>こうえん</rt></ruby>を<ruby>散歩<rt>さんぽ</rt></ruby>してカメラで<ruby>鳥<rt>とり</rt></ruby>や<ruby>花<rt>はな</rt></ruby>の<ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>るのが<ruby>好<rt>す</rt></ruby>きです。</span></p>
<p>とても<ruby>気持<rt>きも</rt></ruby>ちがいいですから、みなさんもぜひ<ruby>来<rt>き</rt></ruby>てください。</p>
</div>""",
        "trans": "Город, в котором я живу — очень тихое и зеленое место. Около станции есть большой парк, весной там цветет много красивой сакуры. Каждое воскресенье утром я люблю гулять по этому парку и фотографировать птиц и цветы на камеру. Это очень приятно, поэтому обязательно приходите!",
        "q1_prompt": "駅の近くには何がありますか。",
        "q1_exp": "В предложении ev-q1 прямо сказано: около станции есть большой парк с цветущей сакурой.",
        "q1_options": [
            {"num": 1, "text": "桜がたくさん咲く大きな公園", "correct": True, "trap": None, "exp": "Правильно! В тексте прямо говорится о большом парке около станции (ev-q1)."},
            {"num": 2, "text": "とてもにぎやかなデパート", "correct": False, "trap": "not_mentioned", "exp": "Неверно. Город тихий, универмаг не упоминается."},
            {"num": 3, "text": "高いビルばかりの道", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. В городе много зелени."},
            {"num": 4, "text": "古い図書館", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ],
        "q2_prompt": "「私」は日曜日の朝に何をしますか。",
        "q2_exp": "Согласно предложению ev-q2, автор гуляет по парку и фотографирует птиц и цветы.",
        "q2_options": [
            {"num": 1, "text": "公園を散歩して写真を撮る", "correct": True, "trap": None, "exp": "Верно! Точное действие из предложения ev-q2."},
            {"num": 2, "text": "駅の前で買い物をする", "correct": False, "trap": "misinterpretation", "exp": "Неверно."},
            {"num": 3, "text": "家でずっと寝ている", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "友だちとサッカーをする", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "毎朝の朝ごはんとくだもの (N5) #2",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>毎朝<rt>まいあさ</rt></ruby>6時半（ろくじはん）に<ruby>起<rt>お</rt></ruby>きます。<ruby>朝<rt>あさ</rt></ruby>ごはんは<ruby>一日<rt>いちにち</rt></ruby>の<ruby>中<rt>なか</rt></ruby>で一番（いちばん）<ruby>大切<rt>たいせつ</rt></ruby>な<ruby>食事<rt>しょくじ</rt></ruby>です。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>温<rt>あたた</rt></ruby>かいご<ruby>飯<rt>はん</rt></ruby>とみそ<ruby>汁<rt>しる</rt></ruby>、それに<ruby>卵<rt>たまご</rt></ruby><ruby>焼<rt>や</rt></ruby>きをよく<ruby>食<rt>た</rt></ruby>べます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">ご<ruby>飯<rt>はん</rt></ruby>のあとには、りんごやバナナなどの<ruby>果物<rt>くだもの</rt></ruby>を<ruby>食<rt>た</rt></ruby>べてから、お<ruby>茶<rt>ちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>みます。</span></p>
<p>しっかり<ruby>食<rt>た</rt></ruby>べると、<ruby>午前<rt>ごぜん</rt></ruby><ruby>中<rt>ちゅう</rt></ruby>の<ruby>勉強<rt>べんきょう</rt></ruby>も元気にがんばることができます。</p>
</div>""",
        "trans": "Я просыпаюсь каждое утро в 6:30. Завтрак — самый важный прием пищи за день. Я часто ем теплый рис, мисо-суп и тамагояки (японский омлет). После еды я ем фрукты вроде яблок или бананов и пью чай. Плотный завтрак дает силы усердно учиться всё утро.",
        "q1_prompt": "「私」は朝ごはんに何をよく食べますか。",
        "q1_exp": "В предложении ev-q1 указаны: рис, мисо-суп и тамагояки.",
        "q1_options": [
            {"num": 1, "text": "ご飯とみそ汁と卵焼き", "correct": True, "trap": None, "exp": "Верно! Точный список блюд из ev-q1."},
            {"num": 2, "text": "パンとコーヒーだけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно. Автор ест традиционный завтрак."},
            {"num": 3, "text": "肉とラーメン", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も食べない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ],
        "q2_prompt": "ご飯を食べた後で、何をしますか。",
        "q2_exp": "В предложении ev-q2 указано: ест фрукты (яблоки, бананы) и пьет чай.",
        "q2_options": [
            {"num": 1, "text": "果物を食べてお茶を飲む", "correct": True, "trap": None, "exp": "Верно! Прямой вывод из предложения ev-q2."},
            {"num": 2, "text": "すぐに学校へ走っていく", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "もう一度寝る", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "薬を飲む", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "日曜日のお買い物とスーパー (N5) #3",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>毎週<rt>まいしゅう</rt></ruby><ruby>日曜日<rt>にちようび</rt></ruby>の<ruby>午後<rt>ごご</rt></ruby>に、<ruby>近<rt>ちか</rt></ruby>くのスーパーへ<ruby>買<rt>か</rt></ruby>い<ruby>物<rt>もの</rt></ruby>に<ruby>行<rt>い</rt></ruby>きます。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>日曜日<rt>にちようび</rt></ruby>は<ruby>野菜<rt>やさい</rt></ruby>と<ruby>魚<rt>さかな</rt></ruby>がいつもより<ruby>安<rt>やす</rt></ruby>くなるので、たくさんの<ruby>人<rt>ひと</rt></ruby>が<ruby>来<rt>き</rt></ruby>ます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>私<rt>わたし</rt></ruby>は一週間（いっしゅうかん）の<ruby>食<rt>た</rt></ruby>べ<ruby>物<rt>もの</rt></ruby>をたくさん<ruby>買<rt>か</rt></ruby>って、<ruby>大<rt>おお</rt></ruby>きなバッグに<ruby>入<rt>い</rt></ruby>れて<ruby>自転車<rt>じてんしゃ</rt></ruby>で<ruby>帰<rt>かえ</rt></ruby>ります。</span></p>
<p><ruby>夜<rt>よる</rt></ruby>には<ruby>買<rt>か</rt></ruby>った<ruby>魚<rt>さかな</rt></ruby>で、おいしい<ruby>夕飯<rt>ゆうはん</rt></ruby>を<ruby>作<rt>つく</rt></ruby>るのが<ruby>楽<rt>たの</rt></ruby>しみです。</p>
</div>""",
        "trans": "Каждое воскресенье днем я хожу за покупками в соседний супермаркет. По воскресеньям овощи и рыба дешевле обычного, поэтому приходит много людей. Я покупаю еду на всю неделю, складываю в большую сумку и возвращаюсь на велосипеде. Вечером приятно приготовить вкусный ужин из купленной рыбы.",
        "q1_prompt": "どうして日曜日にたくさんの人がスーパーへ来ますか。",
        "q1_exp": "В предложении ev-q1 объясняется: по воскресеньям овощи и рыба дешевле обычного.",
        "q1_options": [
            {"num": 1, "text": "野菜や魚がいつもより安くなるから", "correct": True, "trap": None, "exp": "Верно! Причина указана в ev-q1."},
            {"num": 2, "text": "お菓子が無料でもらえるから", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "日曜日しか開いていないから", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Это обычный супермаркет."},
            {"num": 4, "text": "駅の近くに移転したから", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ],
        "q2_prompt": "「私」はどうやって買い物の荷物を持ち帰りますか。",
        "q2_exp": "Согласно предложению ev-q2: складывает в большую сумку и везет на велосипеде.",
        "q2_options": [
            {"num": 1, "text": "大きなバッグに入れて自転車で帰る", "correct": True, "trap": None, "exp": "Верно! Способ транспортировки из предложения ev-q2."},
            {"num": 2, "text": "タクシーを呼んで帰る", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "スーパーの人に届けてもらう", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "歩いて少しずつ運ぶ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]
    },
    {
        "title": "日本のコンビニとべんりなもの (N5) #4",
        "body": """<div class="passage-body">
<p><ruby>日本<rt>にほん</rt></ruby>には、たくさんのコンビニエンスストア（コンビニ）があります。</p>
<p><span id="ev-q1" data-evidence="ev-q1">コンビニは24<ruby>時間<rt>じかん</rt></ruby>いつも<ruby>開<rt>あ</rt></ruby>いていて、おにぎりやお<ruby>弁当<rt>べんとう</rt></ruby>をいつでも<ruby>買<rt>か</rt></ruby>うことができます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">それだけでなく、お<ruby>金<rt>かね</rt></ruby>を<ruby>払<rt>はら</rt></ruby>ったり、<ruby>荷物<rt>にもつ</rt></ruby>を<ruby>送<rt>おく</rt></ruby>ったりすることもできます。</span></p>
<p><ruby>夜遅<rt>よるおそ</rt></ruby>くに困（こま）った時でも、コンビニがあるととても<ruby>安心<rt>あんしん</rt></ruby>です。</p>
</div>""",
        "trans": "В Японии очень много круглосуточных магазинов (комбини). Комбини открыты 24 часа в сутки, там всегда можно купить онигири или бенто. Кроме того, там можно оплачивать счета и отправлять посылки. Даже поздно ночью наличие комбини дает чувство спокойствия.",
        "q1_prompt": "コンビニの特徴（とくちょう）について、何と言っていますか。",
        "q1_exp": "В предложении ev-q1 говорится: открыты 24 часа в сутки, всегда можно купить еду.",
        "q1_options": [
            {"num": 1, "text": "24時間いつでも開いている", "correct": True, "trap": None, "exp": "Верно! Главная особенность комбини (ev-q1)."},
            {"num": 2, "text": "昼の12時に閉まる", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "食べ物は売っていない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Продаются онигири и бенто."},
            {"num": 4, "text": "日曜日は休みになる", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ],
        "q2_prompt": "買い物以外にコンビニでできることは何ですか。",
        "q2_exp": "В предложении ev-q2 указано: можно оплачивать счета и отправлять посылки.",
        "q2_options": [
            {"num": 1, "text": "お金を払ったり荷物を送ったりすること", "correct": True, "trap": None, "exp": "Верно! Дополнительные сервисы из ev-q2."},
            {"num": 2, "text": "電車の切符を買うことだけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "薬を作ること", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "料理を習うこと", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "友だちと行く楽しい旅行 (N5) #5",
        "body": """<div class="passage-body">
<p><ruby>先週<rt>せんしゅう</rt></ruby>の<ruby>土曜日<rt>どようび</rt></ruby>、<ruby>私<rt>わたし</rt></ruby>は<ruby>学校<rt>がっこう</rt></ruby>の<ruby>友<rt>とも</rt></ruby>だちのリーさんと<ruby>京都<rt>きょうと</rt></ruby>へ<ruby>行<rt>い</rt></ruby>きました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>朝<rt>あさ</rt></ruby>7時（しちじ）の<ruby>新幹線<rt>しんかんせん</rt></ruby>に<ruby>乗<rt>の</rt></ruby>って、2<ruby>時間<rt>じかん</rt></ruby>ぐらいで<ruby>着<rt>つ</rt></ruby>きました。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>京都<rt>きょうと</rt></ruby>では<ruby>有名<rt>ゆうめい</rt></ruby>なお<ruby>寺<rt>てら</rt></ruby>を<ruby>見<rt>み</rt></ruby>て、おいしい<ruby>抹茶<rt>まっちゃ</rt></ruby>のアイスクリームを<ruby>食<rt>た</rt></ruby>べました。</span></p>
<p>とても<ruby>楽<rt>たの</rt></ruby>しかったですから、また<ruby>行<rt>い</rt></ruby>きたいです。</p>
</div>""",
        "trans": "В прошлую субботу я вместе с другом по школе Ли-саном поехал в Киото. Мы сели на синкансэн в 7 утра и доехали примерно за 2 часа. В Киото мы посмотрели знаменитые храмы и поели вкусное мороженое с чаем маття. Было очень весело, хочу поехать снова.",
        "q1_prompt": "京都までどうやって行きましたか。",
        "q1_exp": "В предложении ev-q1 указано: поехали на синкансэне (新幹線に乗って).",
        "q1_options": [
            {"num": 1, "text": "朝7時の新幹線に乗って行った", "correct": True, "trap": None, "exp": "Верно! Способ передвижения из ev-q1."},
            {"num": 2, "text": "夜行バスに乗って行った", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "飛行機に乗って行った", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "自転車で2時間走った", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ],
        "q2_prompt": "京都で何をしましたか。",
        "q2_exp": "В предложении ev-q2 написано: посмотрели знаменитые храмы и поели мороженое с маття.",
        "q2_options": [
            {"num": 1, "text": "有名なお寺を見てアイスを食べた", "correct": True, "trap": None, "exp": "Верно! Достопримечательности и еда из ev-q2."},
            {"num": 2, "text": "ずっと映画館で映画を見た", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "海で泳いだ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "本を買ってすぐ帰った", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "私のいえの犬と猫 (N5) #6",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>の<ruby>家<rt>いえ</rt></ruby>には、<ruby>犬<rt>いぬ</rt></ruby>が1<ruby>匹<rt>ぴき</rt></ruby>と<ruby>猫<rt>ねこ</rt></ruby>が1<ruby>匹<rt>ぴき</rt></ruby>います。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>犬<rt>いぬ</rt></ruby>の<ruby>名前<rt>なまえ</rt></ruby>は「シロ」で、<ruby>体<rt>からだ</rt></ruby>が<ruby>白<rt>しろ</rt></ruby>くて<ruby>大<rt>おお</rt></ruby>きい犬です。いつも<ruby>元気<rt>げんき</rt></ruby>に<ruby>庭<rt>にわ</rt></ruby>を<ruby>走<rt>はし</rt></ruby>っています。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>猫<rt>ねこ</rt></ruby>の「トラ」は<ruby>小<rt>ちい</rt></ruby>さくて、あたたかい<ruby>部屋<rt>へや</rt></ruby>のソファーでよく<ruby>寝<rt>ね</rt></ruby>ています。</span></p>
<p>2<ruby>匹<rt>ひき</rt></ruby>ともとてもかわいくて、<ruby>私<rt>わたし</rt></ruby>の<ruby>大切<rt>たいせつ</rt></ruby>な<ruby>家族<rt>かぞく</rt></ruby>です。</p>
</div>""",
        "trans": "В моем доме живут одна собака и одна кошка. Собаку зовут Сиро, он белый и большой. Он всегда бодро бегает по саду. Кошка Тора маленькая, часто спит на диване в теплой комнате. Оба питомца очень милые и являются моей семьей.",
        "q1_prompt": "犬の「シロ」はどんな犬ですか。",
        "q1_exp": "В предложении ev-q1 описано: белый, большой и бодро бегает по саду.",
        "q1_options": [
            {"num": 1, "text": "体が白くて大きくて元気な犬", "correct": True, "trap": None, "exp": "Верно! Описание Сиро из ev-q1."},
            {"num": 2, "text": "黒くていつも寝ている犬", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Он белый и активный."},
            {"num": 3, "text": "小さくてソファーの上にいる犬", "correct": False, "trap": "misinterpretation", "exp": "Неверно. На диване спит кошка Тора."},
            {"num": 4, "text": "外に出たがらない犬", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ],
        "q2_prompt": "猫の「トラ」はどこで何をしていますか。",
        "q2_exp": "В предложении ev-q2 указано: спит на диване в теплой комнате.",
        "q2_options": [
            {"num": 1, "text": "あたたかい部屋のソファーで寝ている", "correct": True, "trap": None, "exp": "Верно! Действие кошки Торы из ev-q2."},
            {"num": 2, "text": "庭で犬と一緒に走っている", "correct": False, "trap": "misinterpretation", "exp": "Неверно. Бегает собака Сиро."},
            {"num": 3, "text": "台所で魚を食べている", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "外の木の上に登っている", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "日本語のべんきょうと漢字 (N5) #7",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>毎日<rt>まいにち</rt></ruby>2<ruby>時間<rt>じかん</rt></ruby><ruby>日本語<rt>にほんご</rt></ruby>を<ruby>勉強<rt>べんきょう</rt></ruby>しています。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>最初<rt>さいしょ</rt></ruby>は<ruby>漢字<rt>かんじ</rt></ruby>を<ruby>覚<rt>おぼ</rt></ruby>えるのがとても<ruby>難<rt>むずか</rt></ruby>しかったですが、<ruby>今<rt>いま</rt></ruby>はとても<ruby>面白<rt>おもしろ</rt></ruby>いと<ruby>思<rt>おも</rt></ruby>っています。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>毎晩<rt>まいばん</rt></ruby>スマートフォンのアプリを<ruby>使<rt>つか</rt></ruby>って、<ruby>新<rt>あたら</rt></ruby>しい<ruby>言葉<rt>ことば</rt></ruby>と<ruby>漢字<rt>かんじ</rt></ruby>を5つずつ<ruby>練習<rt>れんしゅう</rt></ruby>しています。</span></p>
<p><ruby>来月<rt>らいげつ</rt></ruby>のJLPTのテストに<ruby>合格<rt>ごうかく</rt></ruby>したいですから、これからもがんばります。</p>
</div>""",
        "trans": "Я занимаюсь японским языком по 2 часа каждый день. Сначала запоминать кандзи было очень трудно, но сейчас мне это кажется очень интересным. Каждый вечер с помощью приложения на смартфоне я практикую по 5 новых слов и кандзи. Я хочу сдать JLPT в следующем месяце, поэтому буду стараться и дальше.",
        "q1_prompt": "「私」は漢字について今どう思っていますか。",
        "q1_exp": "В предложении ev-q1 говорится: сначала было сложно, но сейчас это кажется очень интересным (面白い).",
        "q1_options": [
            {"num": 1, "text": "最初は難しかったが、今はとても面白い", "correct": True, "trap": None, "exp": "Верно! Прямое суждение автора из ev-q1."},
            {"num": 2, "text": "難しすぎるので勉強をやめたい", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Наоборот, автор полон энтузиазма."},
            {"num": 3, "text": "簡単すぎて勉強する必要がない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "ひらがなより覚えやすい", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ],
        "q2_prompt": "「私」は毎晩どうやって勉強していますか。",
        "q2_exp": "Согласно предложению ev-q2: учит по 5 новых слов и иероглифов в приложении на телефоне.",
        "q2_options": [
            {"num": 1, "text": "スマホのアプリで言葉と漢字を5つずつ練習する", "correct": True, "trap": None, "exp": "Верно! Ежевечерняя методика из ev-q2."},
            {"num": 2, "text": "図書館で友達と話す", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "テレビのニュースを2時間見る", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "先生の家へ質問に行く", "correct": False, "trap": "not_mentioned", "exp": "Неверno."}
        ]
    },
    {
        "title": "夏休みの海と山 (N5) #8",
        "body": """<div class="passage-body">
<p><ruby>今年<rt>ことし</rt></ruby>の<ruby>夏休<rt>なつやす</rt></ruby>みは、とても<ruby>楽<rt>たの</rt></ruby>しい<ruby>思<rt>おも</rt></ruby>い<ruby>出<rt>で</rt></ruby>がたくさんできました。</p>
<p><span id="ev-q1" data-evidence="ev-q1">8<ruby>月<rt>がつ</rt></ruby>のはじめに<ruby>家族<rt>かぞく</rt></ruby>と<ruby>海<rt>うみ</rt></ruby>へ<ruby>行<rt>い</rt></ruby>って、<ruby>青<rt>あお</rt></ruby>い<ruby>海<rt>うみ</rt></ruby>でたくさん<ruby>泳<rt>およ</rt></ruby>ぎました。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">その<ruby>後<rt>あと</rt></ruby>、おじいさんの<ruby>家<rt>いえ</rt></ruby>の<ruby>近<rt>ちか</rt></ruby>くの<ruby>山<rt>やま</rt></ruby>に<ruby>登<rt>のぼ</rt></ruby>って、おいしい空気を<ruby>吸<rt>す</rt></ruby>いました。</span></p>
<p><ruby>海<rt>うみ</rt></ruby>も<ruby>山<rt>やま</rt></ruby>もどちらもすばらしかったです。</p>
</div>""",
        "trans": "На этих летних каникулах у меня появилось много приятных воспоминаний. В начале августа я поехал с семьей на море и вдоволь накупался в синей воде. Затем я поднялся на гору около дома дедушки и подышал чистым воздухом. И море, и горы были великолепны.",
        "q1_prompt": "8月のはじめに何をしましたか。",
        "q1_exp": "В предложении ev-q1 указано: поехал с семьей на море и плавал.",
        "q1_options": [
            {"num": 1, "text": "家族と海へ行ってたくさん泳いだ", "correct": True, "trap": None, "exp": "Верно! Поездка на море в начале августа (ev-q1)."},
            {"num": 2, "text": "一人で山に登った", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно. На гору пошел позже."},
            {"num": 3, "text": "ずっと家で宿題をした", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "学校のプールへ行った", "correct": False, "trap": "misinterpretation", "exp": "Неверно."}
        ],
        "q2_prompt": "山の近くにはだれの家がありましたか。",
        "q2_exp": "В предложении ev-q2 сказано: около дома дедушки (おじいさんの家の近くの山).",
        "q2_options": [
            {"num": 1, "text": "おじいさんの家", "correct": True, "trap": None, "exp": "Верно! Дом дедушки около горы (ev-q2)."},
            {"num": 2, "text": "学校の先生の家", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "友だちのリーさんの家", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "だれの家もなかった", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]
    },
    {
        "title": "おいしい日本のお茶とおかし (N5) #9",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>は<ruby>日本<rt>にほん</rt></ruby>の<ruby>緑茶<rt>りょくちゃ</rt></ruby>（りょくちゃ）がとても<ruby>好<rt>す</rt></ruby>きです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>少<rt>すこ</rt></ruby>し<ruby>苦<rt>にが</rt></ruby>いですが、<ruby>飲<rt>の</rt></ruby>むと<ruby>気持<rt>きも</rt></ruby>ちがすっきりしてリラックスできます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2">お<ruby>茶<rt>ちゃ</rt></ruby>を<ruby>飲<rt>の</rt></ruby>む<ruby>時<rt>とき</rt></ruby>は、あんこが<ruby>入<rt>はい</rt></ruby>った<ruby>甘<rt>あま</rt></ruby>い<ruby>和菓子<rt>わがし</rt></ruby>（わがし）を<ruby>一緒<rt>いっしょ</rt></ruby>に<ruby>食<rt>た</rt></ruby>べます。</span></p>
<p><ruby>苦<rt>にが</rt></ruby>いお<ruby>茶<rt>ちゃ</rt></ruby>と<ruby>甘<rt>あま</rt></ruby>いお<ruby>菓子<rt>かし</rt></ruby>は、最高の組み合わせです。</p>
</div>""",
        "trans": "Я очень люблю японский зеленый чай (рёкутя). Он немного с горчинкой, но когда пьешь его, на душе становится свежо и спокойно. К чаю я ем сладкие японские сладости вагаси с пастой анко. Терпкий чай и сладкие сладости — превосходное сочетание.",
        "q1_prompt": "緑茶を飲むとどうなりますか。",
        "q1_exp": "В предложении ev-q1 указано: на душе становится свежо и можно расслабиться.",
        "q1_options": [
            {"num": 1, "text": "気持ちがすっきりしてリラックスできる", "correct": True, "trap": None, "exp": "Верно! Эффект зеленого чая из ev-q1."},
            {"num": 2, "text": "お腹がとても痛くなる", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "すぐに眠ってしまう", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "のどが渇いて苦しくなる", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ],
        "q2_prompt": "お茶と一緒に何を食べますか。",
        "q2_exp": "В предложении ev-q2 написано: сладкие традиционные сладости вагаси с анко.",
        "q2_options": [
            {"num": 1, "text": "あんこが入った甘い和菓子", "correct": True, "trap": None, "exp": "Верно! Сладкие вагаси с фасолевой пастой (ev-q2)."},
            {"num": 2, "text": "辛いラーメン", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "塩辛いポテトチップス", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "パンとチーズ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "毎日の散歩と写真 (N5) #10",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>の<ruby>趣味<rt>しゅみ</rt></ruby>は<ruby>写真<rt>しゃしん</rt></ruby>を<ruby>撮<rt>と</rt></ruby>ることです。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>毎朝<rt>まいあさ</rt></ruby>、<ruby>仕事<rt>しごと</rt></ruby>の<ruby>前<rt>まえ</rt></ruby>に30<ruby>分<rt>ぷん</rt></ruby>ほど<ruby>近<rt>ちか</rt></ruby>くの<ruby>川<rt>かわ</rt></ruby>の<ruby>道<rt>みち</rt></ruby>を<ruby>歩<rt>ある</rt></ruby>きます。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>季節<rt>きせつ</rt></ruby>によって<ruby>色<rt>いろ</rt></ruby>々な<ruby>花<rt>はな</rt></ruby>が<ruby>咲<rt>さ</rt></ruby>いていて、<ruby>川<rt>かわ</rt></ruby>には<ruby>小<rt>ちい</rt></ruby>さな<ruby>鳥<rt>とり</rt></ruby>がたくさんいます。</span></p>
<p>きれいな<ruby>風景<rt>ふうけい</rt></ruby>を<ruby>撮<rt>と</rt></ruby>ってSNSに<ruby>載<rt>の</rt></ruby>せると、<ruby>世界<rt>せかい</rt></ruby>の<ruby>友<rt>とも</rt></ruby>だちが見てくれます。</p>
</div>""",
        "trans": "Мое хобби — фотография. Каждое утро перед работой я гуляю около 30 минут по дорожке вдоль реки. В зависимости от сезона цветут разные цветы, а на реке много птиц. Когда я выкладываю красивые пейзажи в соцсети, мои друзья по всему миру смотрят их.",
        "q1_prompt": "「私」はいつ散歩をしますか。",
        "q1_exp": "В предложении ev-q1 указано: каждое утро перед работой по 30 минут.",
        "q1_options": [
            {"num": 1, "text": "毎朝、仕事の前に30分ほど", "correct": True, "trap": None, "exp": "Верно! Время утренней прогулки (ev-q1)."},
            {"num": 2, "text": "夜遅く仕事が終わってから", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 3, "text": "週末の昼ごはんの後", "correct": False, "trap": "temporal_mismatch", "exp": "Неверно."},
            {"num": 4, "text": "雨が降っている時だけ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ],
        "q2_prompt": "川の道には何がありますか。",
        "q2_exp": "В предложении ev-q2 написано: цветут сезонные цветы и много маленьких птиц.",
        "q2_options": [
            {"num": 1, "text": "季節の花やたくさんの小さな鳥", "correct": True, "trap": None, "exp": "Верно! Описание природы вдоль реки (ev-q2)."},
            {"num": 2, "text": "大きな車とトラックの渋滞", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "新しいデパートの工事現場", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何もなくて暗い道", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ]
    },
    {
        "title": "学校の友だちと先生 (N5) #11",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>の<ruby>通<rt>かよ</rt></ruby>っている<ruby>日本語<rt>にほんご</rt></ruby><ruby>学校<rt>がっこう</rt></ruby>には、いろいろな<ruby>国<rt>くに</rt></ruby>の<ruby>人<rt>ひと</rt></ruby>がいます。</p>
<p><span id="ev-q1" data-evidence="ev-q1">クラスにはアメリカ、中国、ベトナムなどから<ruby>来<rt>き</rt></ruby>た<ruby>留学生<rt>りゅうがくせい</rt></ruby>がいて、みんなで仲良く<ruby>勉強<rt>べんきょう</rt></ruby>しています。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>先生<rt>せんせい</rt></ruby>はいつも<ruby>優<rt>やさ</rt></ruby>しくて、<ruby>分<rt>わ</rt></ruby>からない<ruby>言葉<rt>ことば</rt></ruby>がある時はゆっくり<ruby>教<rt>おし</rt></ruby>えてくれます。</span></p>
<p><ruby>毎日本当<rt>まいにちほんとう</rt></ruby>に<ruby>楽<rt>たの</rt></ruby>しいです。</p>
</div>""",
        "trans": "В школе японского языка, куда я хожу, учатся люди из самых разных стран. В классе есть студенты из Америки, Китая, Вьетнама, и мы все дружно учимся. Учителя всегда добры к нам и медленно объясняют, если попадается непонятное слово. Каждый день проходит очень весело.",
        "q1_prompt": "クラスにはどんな人たちがいますか。",
        "q1_exp": "В предложении ev-q1 указано: иностранные студенты из разных стран (США, Китай, Вьетнам).",
        "q1_options": [
            {"num": 1, "text": "色々な国から来た留学生たち", "correct": True, "trap": None, "exp": "Верно! Состав класса из предложения ev-q1."},
            {"num": 2, "text": "日本人の高校生だけ", "correct": False, "trap": "opposite_meaning", "exp": "Неверно. Это школа для иностранцев."},
            {"num": 3, "text": "先生一人しかいない", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "英語を話す先生たちだけ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ],
        "q2_prompt": "分からない言葉がある時、先生はどうしてくれますか。",
        "q2_exp": "В предложении ev-q2 написано: учитель всегда добр и объясняет непонятные слова медленно и терпеливо.",
        "q2_options": [
            {"num": 1, "text": "優しくゆっくり教えてくれる", "correct": True, "trap": None, "exp": "Верно! Поведение учителя из предложения ev-q2."},
            {"num": 2, "text": "怒って教室を出ていく", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "宿題を10倍に増やす", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "何も言わずにテストをする", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    },
    {
        "title": "冬の雪とあたたかいスープ (N5) #12",
        "body": """<div class="passage-body">
<p><ruby>私<rt>わたし</rt></ruby>の<ruby>国<rt>くに</rt></ruby>は<ruby>一年中<rt>いちねんじゅう</rt></ruby><ruby>暑<rt>あつ</rt></ruby>いので、<ruby>日本<rt>にほん</rt></ruby>で<ruby>初<rt>はじ</rt></ruby>めて<ruby>雪<rt>ゆき</rt></ruby>を<ruby>見<rt>み</rt></ruby>ました。</p>
<p><span id="ev-q1" data-evidence="ev-q1"><ruby>朝<rt>あさ</rt></ruby><ruby>起<rt>お</rt></ruby>きた時、<ruby>外<rt>そと</rt></ruby>が<ruby>全部<rt>ぜんぶ</rt></ruby><ruby>白<rt>しろ</rt></ruby>くなっていて、まるで<ruby>絵<rt>え</rt></ruby>のようにきれいで<ruby>驚<rt>おどろ</rt></ruby>きました。</span></p>
<p><span id="ev-q2" data-evidence="ev-q2"><ruby>外<rt>そと</rt></ruby>はとても<ruby>寒<rt>さむ</rt></ruby>かったので、<ruby>部屋<rt>へや</rt></ruby>に<ruby>戻<rt>もど</rt></ruby>ってから<ruby>温<rt>あたた</rt></ruby>かいトマトスープを<ruby>作<rt>つく</rt></ruby>って<ruby>飲<rt>の</rt></ruby>みました。</span></p>
<p><ruby>冬<rt>ふゆ</rt></ruby>の<ruby>寒<rt>さむ</rt></ruby>さは<ruby>厳<rt>きび</rt></ruby>しいですが、<ruby>温<rt>あたた</rt></ruby>かいスープを飲む時間はとても幸せです。</p>
</div>""",
        "trans": "В моей родной стране тепло круглый год, поэтому в Японии я впервые увидел снег. Когда я проснулся утром, всё на улице было белым, как на картине, и это меня поразило. На улице было очень холодно, поэтому я вернулся в комнату и сварил горячий томатный суп. Зимний холод суров, но время за горячим супом приносит настоящее счастье.",
        "q1_prompt": "「私」は朝起きた時、どうして驚きましたか。",
        "q1_exp": "В предложении ev-q1 написано: на улице всё стало белым от снега, как на картине.",
        "q1_options": [
            {"num": 1, "text": "外が全部白く雪で覆われていてきれいだったから", "correct": True, "trap": None, "exp": "Верно! Первый снег поразил автора (ev-q1)."},
            {"num": 2, "text": "部屋の中に泥棒が入っていたから", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 3, "text": "時計が壊れて止まっていたから", "correct": False, "trap": "not_mentioned", "exp": "Неверно."},
            {"num": 4, "text": "外がとても暑かったから", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."}
        ],
        "q2_prompt": "寒かったので、部屋に戻ってから何をしましたか。",
        "q2_exp": "В предложении ev-q2 указано: сварил и выпил горячий томатный суп.",
        "q2_options": [
            {"num": 1, "text": "温かいトマトスープを作って飲んだ", "correct": True, "trap": None, "exp": "Верно! Горячий суп после улицы (ev-q2)."},
            {"num": 2, "text": "冷たいアイスクリームを食べた", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 3, "text": "窓を開けて風を入れた", "correct": False, "trap": "opposite_meaning", "exp": "Неверно."},
            {"num": 4, "text": "すぐに服を脱いで泳いだ", "correct": False, "trap": "not_mentioned", "exp": "Неверно."}
        ]
    }
]

def main():
    with open(N5_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    # 1. Заменяем 12 short текстов (индексы 0..11)
    for idx, sdata in enumerate(SHORT_DATA):
        rec = records[idx]
        rec["title"] = sdata["title"]
        rec["body_html"] = sdata["body"]
        rec["translation_ru"] = sdata["trans"]
        rec["questions"] = [
            {
                "slug": f"{rec['slug']}-q1",
                "question_number": 1,
                "type": "detail",
                "prompt": sdata["prompt"],
                "evidence_span_id": "ev-q1",
                "general_explanation": sdata["explanation"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt["trap"],
                        "explanation_ru": opt["exp"]
                    }
                    for opt in sdata["options"]
                ]
            }
        ]

    # 2. Заменяем 12 medium текстов (индексы 12..23)
    for idx, mdata in enumerate(MEDIUM_DATA, start=12):
        rec = records[idx]
        rec["title"] = mdata["title"]
        rec["body_html"] = mdata["body"]
        rec["translation_ru"] = mdata["trans"]
        rec["questions"] = [
            {
                "slug": f"{rec['slug']}-q1",
                "question_number": 1,
                "type": "detail",
                "prompt": mdata["q1_prompt"],
                "evidence_span_id": "ev-q1",
                "general_explanation": mdata["q1_exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt["trap"],
                        "explanation_ru": opt["exp"]
                    }
                    for opt in mdata["q1_options"]
                ]
            },
            {
                "slug": f"{rec['slug']}-q2",
                "question_number": 2,
                "type": "detail",
                "prompt": mdata["q2_prompt"],
                "evidence_span_id": "ev-q2",
                "general_explanation": mdata["q2_exp"],
                "options": [
                    {
                        "option_number": opt["num"],
                        "text": opt["text"],
                        "is_correct": opt["correct"],
                        "trap_type": opt["trap"],
                        "explanation_ru": opt["exp"]
                    }
                    for opt in mdata["q2_options"]
                ]
            }
        ]

    with open(N5_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"✓ Успешно обогащен content/n5.json: 12 short + 12 medium текстов стали 100% уникальными!")

if __name__ == "__main__":
    main()
