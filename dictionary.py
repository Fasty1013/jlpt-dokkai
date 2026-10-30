"""
dictionary.py - Словарь JLPT (N5 - N1) для интерактивного всплывающего словаря (Yomichan-style)
Поддерживает поиск по кандзи, хирагане и подстрокам с выдачей чтения, уровня JLPT и перевода на русский язык.
"""
from typing import Optional, List, Dict

# Большая база частых слов JLPT N5-N1 с чтениями и русскими переводами
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
    {"word": "持続可能", "reading": "じぞくかのう", "level": "N2", "meaning": "устойчивый, способный длиться долго"},
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
    {"word": "持続可能性", "reading": "じぞくかのうせい", "level": "N1", "meaning": "устойчивость, устойчивое развитие"}
]


def lookup_word(query: str) -> Optional[Dict[str, str]]:
    """
    Ищет точное или частичное совпадение слова в словаре.
    """
    if not query:
        return None
    cleaned = query.strip()
    # 1. Точное совпадение по слову или чтению
    for item in JLPT_DICTIONARY:
        if item["word"] == cleaned or item["reading"] == cleaned:
            return item

    # 2. Совпадение подстроки (если выделено длиннее или форма слова)
    for item in JLPT_DICTIONARY:
        if item["word"] in cleaned or cleaned in item["word"]:
            return item

    return None
