"""
dictionary.py - Словарь JLPT (N5 - N1) для интерактивного всплывающего словаря (Yomichan-style)
и точной разметки фуриганы (<ruby><rt>).
Все чтения строго на хирагане и соответствуют реальным японским чтениям в контексте.
"""
from typing import Optional, List, Dict
import re

# Полная база лексики с точной хираганой и русским переводом
JLPT_DICTIONARY: List[Dict[str, str]] = [
    # N5
    {"word": "私", "reading": "わたし", "level": "N5", "meaning": "я (вежливо)"},
    {"word": "学生", "reading": "がくせい", "level": "N5", "meaning": "студент, учащийся"},
    {"word": "学校", "reading": "がっこう", "level": "N5", "meaning": "школа"},
    {"word": "先生", "reading": "せんせい", "level": "N5", "meaning": "учитель, преподаватель"},
    {"word": "本", "reading": "ほん", "level": "N5", "meaning": "книга, основа"},
    {"word": "日本語", "reading": "にほんご", "level": "N5", "meaning": "японский язык"},
    {"word": "友達", "reading": "ともだち", "level": "N5", "meaning": "друг, друзья"},
    {"word": "時間", "reading": "じかん", "level": "N5", "meaning": "время, часы"},
    {"word": "毎日", "reading": "まいにち", "level": "N5", "meaning": "каждый день"},
    {"word": "今日", "reading": "きょう", "level": "N5", "meaning": "сегодня"},
    {"word": "明日", "reading": "あした", "level": "N5", "meaning": "завтра"},
    {"word": "昨日", "reading": "きのう", "level": "N5", "meaning": "вчера"},
    {"word": "図書館", "reading": "としょかん", "level": "N5", "meaning": "библиотека"},
    {"word": "電車", "reading": "でんしゃ", "level": "N5", "meaning": "поезд, электричка"},
    {"word": "食べる", "reading": "たべる", "level": "N5", "meaning": "есть, кушать"},
    {"word": "飲む", "reading": "のむ", "level": "N5", "meaning": "пить"},
    {"word": "行く", "reading": "いく", "level": "N5", "meaning": "идти, ехать"},
    {"word": "来る", "reading": "くる", "level": "N5", "meaning": "приходить, приезжать"},
    {"word": "見る", "reading": "みる", "level": "N5", "meaning": "смотреть, видеть"},
    {"word": "聞く", "reading": "きく", "level": "N5", "meaning": "слушать, спрашивать"},
    {"word": "読む", "reading": "よむ", "level": "N5", "meaning": "читать"},
    {"word": "書く", "reading": "かく", "level": "N5", "meaning": "писать"},
    {"word": "買う", "reading": "かう", "level": "N5", "meaning": "покупать"},
    {"word": "新しい", "reading": "あたらしい", "level": "N5", "meaning": "новый"},
    {"word": "古い", "reading": "ふるい", "level": "N5", "meaning": "старый"},
    {"word": "大きい", "reading": "おおきい", "level": "N5", "meaning": "большой"},
    {"word": "小さい", "reading": "ちいさい", "level": "N5", "meaning": "маленький"},
    {"word": "高い", "reading": "たかい", "level": "N5", "meaning": "высокий, дорогой"},
    {"word": "安い", "reading": "やすい", "level": "N5", "meaning": "дешёвый, спокойный"},
    {"word": "面白い", "reading": "おもしろい", "level": "N5", "meaning": "интересный, забавный"},

    # N4
    {"word": "案内", "reading": "あんない", "level": "N4", "meaning": "руководство, извещение, показ"},
    {"word": "安心", "reading": "あんしん", "level": "N4", "meaning": "спокойствие, душевный покой"},
    {"word": "利用", "reading": "りよう", "level": "N4", "meaning": "использование, применение"},
    {"word": "注意", "reading": "ちゅうい", "level": "N4", "meaning": "внимание, предостережение"},
    {"word": "用意", "reading": "ようい", "level": "N4", "meaning": "подготовка, готовность"},
    {"word": "意見", "reading": "いけん", "level": "N4", "meaning": "мнение, точка зрения"},
    {"word": "連絡", "reading": "れんらく", "level": "N4", "meaning": "связь, контакт, сообщение"},
    {"word": "都合", "reading": "つごう", "level": "N4", "meaning": "обстоятельства, удобство времени"},
    {"word": "遠慮", "reading": "えんりょ", "level": "N4", "meaning": "стеснение, воздержание"},
    {"word": "危険", "reading": "きけん", "level": "N4", "meaning": "опасность, опасный"},
    {"word": "便利", "reading": "べんり", "level": "N4", "meaning": "удобный"},
    {"word": "不便", "reading": "ふべん", "level": "N4", "meaning": "неудобный"},
    {"word": "簡単", "reading": "かんたん", "level": "N4", "meaning": "простой, лёгкий"},
    {"word": "複雑", "reading": "ふくざつ", "level": "N4", "meaning": "сложный, запутанный"},
    {"word": "経験", "reading": "けいけん", "level": "N4", "meaning": "опыт, жизненная практика"},
    {"word": "説明", "reading": "せつめい", "level": "N4", "meaning": "объяснение, пояснение"},
    {"word": "理由", "reading": "りゆう", "level": "N4", "meaning": "причина, основание"},
    {"word": "目的", "reading": "もくてき", "level": "N4", "meaning": "цель, намерение"},
    {"word": "場合", "reading": "ばあい", "level": "N4", "meaning": "случай, обстоятельство"},
    {"word": "習慣", "reading": "しゅうかん", "level": "N4", "meaning": "обычай, привычка"},
    {"word": "約束", "reading": "やくそく", "level": "N4", "meaning": "обещание, договорённость"},
    {"word": "関係", "reading": "かんけい", "level": "N4", "meaning": "отношение, связь"},
    {"word": "手伝う", "reading": "てつだう", "level": "N4", "meaning": "помогать, оказывать содействие"},
    {"word": "参加", "reading": "さんか", "level": "N4", "meaning": "участие"},
    {"word": "予定", "reading": "よてい", "level": "N4", "meaning": "план, расписание"},

    # N3
    {"word": "関する", "reading": "かんする", "level": "N3", "meaning": "иметь отношение, касаться"},
    {"word": "影響", "reading": "えいきょう", "level": "N3", "meaning": "влияние, воздействие"},
    {"word": "環境", "reading": "かんきょう", "level": "N3", "meaning": "окружающая среда, обстановка"},
    {"word": "変化", "reading": "へんか", "level": "N3", "meaning": "изменение, перемена"},
    {"word": "結果", "reading": "けっか", "level": "N3", "meaning": "результат, последствие"},
    {"word": "効果", "reading": "こうか", "level": "N3", "meaning": "эффект, действие, результат"},
    {"word": "増加", "reading": "ぞうか", "level": "N3", "meaning": "увеличение, рост"},
    {"word": "減少", "reading": "げんしょう", "level": "N3", "meaning": "уменьшение, спад"},
    {"word": "原因", "reading": "げんいん", "level": "N3", "meaning": "причина, повод"},
    {"word": "解決", "reading": "かいけつ", "level": "N3", "meaning": "решение (проблемы, вопроса)"},
    {"word": "必要", "reading": "ひつよう", "level": "N3", "meaning": "необходимость, нужный"},
    {"word": "重要", "reading": "じゅうよう", "level": "N3", "meaning": "важный, существенный"},
    {"word": "可能", "reading": "かのう", "level": "N3", "meaning": "возможный, выполнимый"},
    {"word": "不可能", "reading": "ふかのう", "level": "N3", "meaning": "невозможный"},
    {"word": "価値", "reading": "かち", "level": "N3", "meaning": "ценность, стоимость"},
    {"word": "調査", "reading": "ちょうさ", "level": "N3", "meaning": "исследование, опрос"},
    {"word": "発表", "reading": "はっぴょう", "level": "N3", "meaning": "публикация, объявление, доклад"},
    {"word": "開発", "reading": "かいはつ", "level": "N3", "meaning": "разработка, освоение"},
    {"word": "発展", "reading": "はってん", "level": "N3", "meaning": "развитие, прогресс"},
    {"word": "比較", "reading": "ひかく", "level": "N3", "meaning": "сравнение, сопоставление"},
    {"word": "傾向", "reading": "けいこう", "level": "N3", "meaning": "тенденция, склонность"},
    {"word": "意識", "reading": "いしき", "level": "N3", "meaning": "сознание, осознание"},
    {"word": "特徴", "reading": "とくちょう", "level": "N3", "meaning": "особенность, характерная черта"},
    {"word": "態度", "reading": "たいど", "level": "N3", "meaning": "отношение, позиция, поведение"},
    {"word": "状況", "reading": "じょうきょう", "level": "N3", "meaning": "ситуация, положение дел"},

    # N2
    {"word": "持続可能", "reading": "じぞくかのう", "level": "N2", "meaning": "устойчивый, экологичный"},
    {"word": "意思決定", "reading": "いしけってい", "level": "N2", "meaning": "принятие решений"},
    {"word": "深刻", "reading": "しんこく", "level": "N2", "meaning": "серьёзный, глубокий, острый"},
    {"word": "課題", "reading": "かだい", "level": "N2", "meaning": "задача, вызов, проблема"},
    {"word": "対象", "reading": "たいしょう", "level": "N2", "meaning": "объект, целевая группа"},
    {"word": "批判", "reading": "ひはん", "level": "N2", "meaning": "критика, суждение"},
    {"word": "主張", "reading": "しゅちょう", "level": "N2", "meaning": "утверждение, позиция автора"},
    {"word": "把握", "reading": "はあく", "level": "N2", "meaning": "понимание, схватывание сути"},
    {"word": "背景", "reading": "はいけい", "level": "N2", "meaning": "фон, подоплёка, контекст"},
    {"word": "指摘", "reading": "してき", "level": "N2", "meaning": "указание (на факт/ошибку)"},
    {"word": "共通", "reading": "きょうつう", "level": "N2", "meaning": "общий, единый"},
    {"word": "独自", "reading": "どくじ", "level": "N2", "meaning": "своеобразный, оригинальный, собственный"},
    {"word": "普及", "reading": "ふきゅう", "level": "N2", "meaning": "распространение, популяризация"},
    {"word": "導入", "reading": "どうにゅう", "level": "N2", "meaning": "внедрение, введение"},
    {"word": "義務", "reading": "ぎむ", "level": "N2", "meaning": "обязанность, долг"},
    {"word": "懸念", "reading": "けねん", "level": "N2", "meaning": "опасение, тревога"},
    {"word": "視点", "reading": "してん", "level": "N2", "meaning": "точка зрения, угол обзора"},
    {"word": "観点", "reading": "かんてん", "level": "N2", "meaning": "аспект, точка зрения"},
    {"word": "基準", "reading": "きじゅん", "level": "N2", "meaning": "стандарт, норма, критерий"},
    {"word": "柔軟", "reading": "じゅうなん", "level": "N2", "meaning": "гибкий, адаптивный"},

    # N1
    {"word": "根底", "reading": "こんてい", "level": "N1", "meaning": "фундамент, глубинная основа"},
    {"word": "概念", "reading": "がいねん", "level": "N1", "meaning": "концепция, понятие"},
    {"word": "本質", "reading": "ほんしつ", "level": "N1", "meaning": "суть, подлинная природа"},
    {"word": "妥協", "reading": "だきょう", "level": "N1", "meaning": "компромисс, уступка"},
    {"word": "示唆", "reading": "しさ", "level": "N1", "meaning": "намек, внушение, подсказка"},
    {"word": "乖離", "reading": "かいり", "level": "N1", "meaning": "расхождение, отчуждение, разрыв"},
    {"word": "看過", "reading": "かんか", "level": "N1", "meaning": "упущение из виду, недосмотр"},
    {"word": "卓越", "reading": "たくえつ", "level": "N1", "meaning": "выдающийся характер, превосходство"},
    {"word": "変遷", "reading": "へんせん", "level": "N1", "meaning": "эволюция, смена эпох, переходы"},
    {"word": "象徴", "reading": "しょうちょう", "level": "N1", "meaning": "символ, олицетворение"},
    {"word": "共生", "reading": "きょうせい", "level": "N1", "meaning": "сосуществование, симбиоз"},
    {"word": "吟味", "reading": "ぎんみ", "level": "N1", "meaning": "тщательное рассмотрение, проба"},
    {"word": "固定観念", "reading": "こていかんねん", "level": "N1", "meaning": "стереотип, закостенелое представление"},
    {"word": "自律", "reading": "じりつ", "level": "N1", "meaning": "автономия, саморегуляция"},
    {"word": "持続可能性", "reading": "じぞくかのうせい", "level": "N1", "meaning": "устойчивость, устойчивое развитие"},

    # Project Theme Keywords & Essential Terms
    {"word": "短文", "reading": "たんぶん", "level": "N4", "meaning": "короткий текст, предложение"},
    {"word": "短文メモ", "reading": "たんぶんめも", "level": "N4", "meaning": "короткая памятка, заметка"},
    {"word": "利用カード", "reading": "りようかーど", "level": "N4", "meaning": "читательский билет, карта пользователя"},
    {"word": "開館時間", "reading": "かいかんじかん", "level": "N4", "meaning": "часы работы, время открытия"},
    {"word": "公園清掃", "reading": "こうえんせいそう", "level": "N4", "meaning": "уборка парка"},
    {"word": "清掃", "reading": "せいそう", "level": "N4", "meaning": "уборка, чистка"},
    {"word": "地域活動", "reading": "ちいきかつどう", "level": "N3", "meaning": "общественная деятельность в районе"},
    {"word": "参加資格", "reading": "さんかしかく", "level": "N3", "meaning": "требования к участникам"},
    {"word": "雨天順延", "reading": "うてんじゅんえん", "level": "N2", "meaning": "перенос в случае дождя"},
    {"word": "交流会", "reading": "こうりゅうかい", "level": "N4", "meaning": "встреча для общения, нетворкинг"},
    {"word": "会費無料", "reading": "かいひむりょう", "level": "N4", "meaning": "бесплатное участие"},
    {"word": "事前申込", "reading": "じぜんもうしこみ", "level": "N3", "meaning": "предварительная заявка"},
    {"word": "窓口対応", "reading": "まどぐちたいおう", "level": "N3", "meaning": "обслуживание в окне / на стойке"},
    {"word": "保管期間", "reading": "ほかんきかん", "level": "N3", "meaning": "срок хранения"},
    {"word": "身分証", "reading": "みぶんしょう", "level": "N4", "meaning": "удостоверение личности"},
    {"word": "拾得物", "reading": "しゅうとくぶつ", "level": "N2", "meaning": "найденные вещи, находка"},
    {"word": "ビル管理", "reading": "びるかんり", "level": "N3", "meaning": "управление зданием"},
    {"word": "停電注意", "reading": "ていでんちゅうい", "level": "N4", "meaning": "внимание: отключение электричества"},
    {"word": "階段利用", "reading": "かいだんりよう", "level": "N5", "meaning": "использование лестницы"},
    {"word": "安全点検", "reading": "あんぜんてんけん", "level": "N3", "meaning": "проверка безопасности"},
    {"word": "健康管理", "reading": "けんこうかんり", "level": "N3", "meaning": "забота о здоровье"},
    {"word": "問診票", "reading": "もんしんひょう", "level": "N2", "meaning": "медицинская анкета"},
    {"word": "前日絶食", "reading": "ぜんじつぜっしょく", "level": "N1", "meaning": "воздержание от еды накануне"},
    {"word": "受診時間", "reading": "じゅしんじかん", "level": "N3", "meaning": "время приема у врача"},
    {"word": "勤務調整", "reading": "きんむちょうせい", "level": "N2", "meaning": "корректировка рабочего графика"},
    {"word": "代替要員", "reading": "だいたいよういん", "level": "N1", "meaning": "сменщик, замещающий сотрудник"},
    {"word": "店長承認", "reading": "てんちょうしょうにん", "level": "N3", "meaning": "одобрение управляющего"},
    {"word": "連絡締切", "reading": "れんらくしめきり", "level": "N3", "meaning": "дедлайн для связи"},
    {"word": "不在票", "reading": "ふざいひょう", "level": "N3", "meaning": "извещение о доставке в отсутствие адресата"},
    {"word": "保管期限", "reading": "ほかんきげん", "level": "N3", "meaning": "предельный срок хранения"},
    {"word": "自動受付", "reading": "じどううけつけ", "level": "N3", "meaning": "автоматический прием заявок"},
    {"word": "指定時間", "reading": "していじかん", "level": "N3", "meaning": "указанное время"},
    {"word": "新商品", "reading": "しんしょうひん", "level": "N4", "meaning": "новый товар, новинка"},
    {"word": "数量限定", "reading": "すうりょうげんてい", "level": "N2", "meaning": "ограниченное количество"},
    {"word": "道路工事", "reading": "どうろこうじ", "level": "N4", "meaning": "дорожные работы"},
    {"word": "迂回運行", "reading": "うかいうんこう", "level": "N1", "meaning": "движение в объезд"},
    {"word": "乗降場所", "reading": "じょうこうばしょ", "level": "N2", "meaning": "место посадки и высадки"},
    {"word": "工事期間", "reading": "こうじきかん", "level": "N3", "meaning": "период ремонтных работ"},
    {"word": "大会要項", "reading": "たいかいようこう", "level": "N2", "meaning": "положение о конкурсе"},
    {"word": "原稿提出", "reading": "げんこうていしゅつ", "level": "N2", "meaning": "подача рукописи / текста"},
    {"word": "審査基準", "reading": "しんさきじゅん", "level": "N2", "meaning": "критерии оценки жюри"},
    {"word": "表彰規定", "reading": "ひょうしょうきてい", "level": "N1", "meaning": "правила награждения"},
    {"word": "休講連絡", "reading": "きゅうこうれんらく", "level": "N3", "meaning": "сообщение об отмене лекции"},
    {"word": "補講日程", "reading": "ほこうにってい", "level": "N2", "meaning": "расписание дополнительных занятий"},
    {"word": "課題提出", "reading": "かだいていしゅつ", "level": "N3", "meaning": "сдача домашнего задания"},
    {"word": "教務課", "reading": "きょうむか", "level": "N2", "meaning": "учебная часть, деканат"},
    {"word": "環境問題", "reading": "かんきょうもんだい", "level": "N3", "meaning": "экологические проблемы"},
    {"word": "資源回収", "reading": "しげんかいしゅう", "level": "N3", "meaning": "сбор вторсырья"},
    {"word": "市民の意識", "reading": "しみんのいしき", "level": "N3", "meaning": "сознательность горожан"},
    {"word": "地域差", "reading": "ちいきさ", "level": "N2", "meaning": "региональные различия"},
    {"word": "深夜営業", "reading": "しんやえいぎょう", "level": "N3", "meaning": "круглосуточная работа ночью"},
    {"word": "利便性", "reading": "りべんせい", "level": "N2", "meaning": "удобство, практичность"},
    {"word": "社会基盤", "reading": "しゃかいきばん", "level": "N2", "meaning": "социальная инфраструктура"},
    {"word": "無人レジ", "reading": "むじんれじ", "level": "N3", "meaning": "касса самообслуживания"},
    {"word": "地方創生", "reading": "ちほうそうせい", "level": "N1", "meaning": "возрождение регионов"},
    {"word": "仕事と休暇", "reading": "しごとときゅうか", "level": "N4", "meaning": "работа и отдых"},
    {"word": "自己管理", "reading": "じこかんり", "level": "N2", "meaning": "самодисциплина, самоконтроль"},
    {"word": "一汁三菜", "reading": "いちじゅうさんさい", "level": "N2", "meaning": "традиционный обед (суп и три блюда)"},
    {"word": "発酵食品", "reading": "はっこうしょくひん", "level": "N2", "meaning": "ферментированные продукты"},
    {"word": "無形文化遺産", "reading": "むけいぶんかいさん", "level": "N1", "meaning": "нематериальное культурное наследие"},
    {"word": "栄養バランス", "reading": "えいようばらんす", "level": "N3", "meaning": "баланс питательных веществ"},
    {"word": "治安の良さ", "reading": "ちあんのよさ", "level": "N3", "meaning": "общественная безопасность"},
    {"word": "冷温同時", "reading": "れいおんどうじ", "level": "N2", "meaning": "одновременный подогрев и охлаждение"},
    {"word": "災害時支援", "reading": "さいがいじしえん", "level": "N2", "meaning": "поддержка при стихийных бедствиях"},
    {"word": "技術革新", "reading": "ぎじゅつかくしん", "level": "N2", "meaning": "технологические инновации"},
    {"word": "孤独の価値", "reading": "こどくのかち", "level": "N2", "meaning": "ценность уединения"},
    {"word": "自由な選択", "reading": "じゆうなせんたく", "level": "N3", "meaning": "свободный выбор"},
    {"word": "未知の体験", "reading": "みちのたいけん", "level": "N2", "meaning": "новый, неизведанный опыт"},
    {"word": "自立心", "reading": "じりつしん", "level": "N2", "meaning": "чувство независимости, самостоятельность"},
    {"word": "手書きの記憶", "reading": "てがきのきおく", "level": "N3", "meaning": "память рукописного письма"},
    {"word": "スケジュール管理", "reading": "すけじゅーるかんり", "level": "N3", "meaning": "управление расписанием"},
    {"word": "愛着", "reading": "あいちゃく", "level": "N1", "meaning": "привязанность, теплое чувство"},
    {"word": "デジタル併用", "reading": "でじたるへいよう", "level": "N2", "meaning": "совместное использование с цифровыми инструментами"},
    {"word": "飼い主の責任", "reading": "かいぬしのせきにん", "level": "N3", "meaning": "ответственность владельца животного"},
    {"word": "動物愛護", "reading": "どうぶつあいご", "level": "N2", "meaning": "защита животных"},
    {"word": "公共の場", "reading": "こうきょうのば", "level": "N3", "meaning": "общественное место"},
    {"word": "共生ルール", "reading": "きょうせいるーる", "level": "N2", "meaning": "правила совместного сосуществования"},
    {"word": "短距離移動", "reading": "たんきょりいどう", "level": "N3", "meaning": "передвижение на короткие расстояния"},
    {"word": "エコ通勤", "reading": "えこつうきん", "level": "N3", "meaning": "экологичные поездки на работу"},
    {"word": "専用ポート", "reading": "せんようぽーと", "level": "N3", "meaning": "специальная станция проката"},
    {"word": "駐輪マナー", "reading": "ちゅうりんまなー", "level": "N3", "meaning": "культура парковки велосипедов"},
    {"word": "個性の表現", "reading": "こせいのひょうげん", "level": "N3", "meaning": "выражение индивидуальности"},
    {"word": "衣類再利用", "reading": "いるいさいりよう", "level": "N3", "meaning": "вторичное использование одежды"},
    {"word": "循環型社会", "reading": "じゅんかんがたしゃかい", "level": "N2", "meaning": "общество с экономикой замкнутого цикла"},
    {"word": "癒しの空間", "reading": "いやしのくうかん", "level": "N2", "meaning": "пространство для душевного отдыха"},
    {"word": "温冷交代浴", "reading": "おんれいこうたいよく", "level": "N1", "meaning": "контрастные водные процедуры"},
    {"word": "地域アイデンティティ", "reading": "ちいきあいでんてぃてぃ", "level": "N2", "meaning": "региональная идентичность"},
    {"word": "親しみやすさ", "reading": "したしみやすさ", "level": "N3", "meaning": "доступность, душевность"},
    {"word": "場面に応じた言葉", "reading": "ばめんにおうじたことば", "level": "N2", "meaning": "речь, уместная в конкретной обстановке"},
    {"word": "文化の多様性", "reading": "ぶんかのたようせい", "level": "N2", "meaning": "культурное разнообразие"},
    {"word": "都市計画", "reading": "としけいかく", "level": "N2", "meaning": "градостроительное планирование"},
    {"word": "緑地保全", "reading": "りょくちほぜん", "level": "N1", "meaning": "сохранение зеленых насаждений"},
    {"word": "生態系ネットワーク", "reading": "せいたいけいねっとわーく", "level": "N1", "meaning": "экологическая сеть"},
    {"word": "心理的充足", "reading": "しんりてきじゅうそく", "level": "N1", "meaning": "психологическое удовлетворение"},
    {"word": "著作権", "reading": "ちょさくけん", "level": "N2", "meaning": "авторское право"},
    {"word": "感情の模倣", "reading": "かんじょうのもほう", "level": "N1", "meaning": "имитация человеческих эмоций"},
    {"word": "独自の美意識", "reading": "どくじのびいしき", "level": "N1", "meaning": "самобытное эстетическое чувство"},
    {"word": "複言語教育", "reading": "ふくげんごきょういく", "level": "N1", "meaning": "многоязычное образование"},
    {"word": "思考の枠組み", "reading": "しこうのわくぐみ", "level": "N1", "meaning": "каркас и парадигма мышления"},
    {"word": "言語消滅", "reading": "げんごしょうめつ", "level": "N1", "meaning": "исчезновение языков"},
    {"word": "即時性の代償", "reading": "そくじせいのだいしょう", "level": "N1", "meaning": "цена мгновенного доступа к информации"},
    {"word": "思索の停滞", "reading": "しさくのていたい", "level": "N1", "meaning": "застой глубокого размышления"},
    {"word": "余白の価値", "reading": "よはくのかち", "level": "N1", "meaning": "ценность пауз и свободного пространства"}
]

# Быстрый индекс для поиска
_WORD_INDEX: Dict[str, Dict[str, str]] = {item["word"]: item for item in JLPT_DICTIONARY}


def lookup_word(query: str) -> Optional[Dict[str, str]]:
    """
    Ищет точное или частичное совпадение слова в словаре.
    """
    if not query:
        return None
    cleaned = query.strip()
    if cleaned in _WORD_INDEX:
        return _WORD_INDEX[cleaned]

    for item in JLPT_DICTIONARY:
        if item["word"] == cleaned or item["reading"] == cleaned:
            return item

    for item in JLPT_DICTIONARY:
        if item["word"] in cleaned or cleaned in item["word"]:
            return item

    return None


def get_authentic_hiragana(word: str) -> str:
    """
    Возвращает строго хирагану для заданного слова.
    Никаких названий тем, английских слов или смещений индексов.
    """
    if not word:
        return ""
    found = lookup_word(word)
    if found and found.get("reading"):
        return found["reading"]
    return ""
