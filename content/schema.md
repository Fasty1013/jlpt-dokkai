# Спецификация контракта данных (Content Data Contract)

## 📌 Обзор
Данный контракт описывает формат хранения учебных материалов для тренажёра **JLPT Dokkai Master**.
Материалы хранятся в формате JSON в директории `content/` с разделением по уровням:
- `content/n3.json` — задания уровня JLPT N3
- `content/n2.json` — задания уровня JLPT N2
- `content/n1.json` — задания уровня JLPT N1

Каждый файл содержит массив объектов заданий (`TextRecord`).

---

## 📐 JSON-схема структуры текста

```json
{
  "slug": "n2-article-001",
  "level": "N2",
  "category": "short | medium | long | info_search | article",
  "title": "若者の間で広がる「デジタルデトックス」：スマホを手放す旅",
  "source_type": "jlpt_official | news_adapted | original",
  "source_note": "NHK World News Feature, 2024",
  "recommended_time_min": 5,
  "body_html": "<div class=\"passage-body\"><p>...</p><p><span id=\"ev-q1\" data-evidence=\"ev-q1\">Ключевое предложение-доказательство</span></p></div>",
  "translation_ru": "Полный связный литературный перевод текста на русский язык...",
  "vocabulary": [
    {
      "word": "過剰",
      "furigana": "かじょう",
      "translation": "избыток, чрезмерность"
    }
  ],
  "needs_manual_review": [],
  "questions": [
    {
      "slug": "n2-article-001-q1",
      "question_number": 1,
      "type": "claim | detail | reference | inference | integrated | info_search",
      "prompt": "筆者が最も主張したいことは何か。",
      "evidence_span_id": "ev-q1",
      "general_explanation": "Подробный разбор сути вопроса на русском языке с указанием доказательства.",
      "options": [
        {
          "option_number": 1,
          "text": "スマートフォンの使用を完全に法律で禁止すべきだ。",
          "is_correct": false,
          "trap_type": "overgeneralization",
          "explanation_ru": "Неверно. Ловушка чрезмерного обобщения (言い過ぎ). Автор не призывает к полному законодательному запрету гаджетов, а лишь рекомендует осознанный отдых."
        },
        {
          "option_number": 2,
          "text": "利便性に依存しすぎず、主体的に情報と距離を置く時間を持つことが大切だ。",
          "is_correct": true,
          "trap_type": null,
          "explanation_ru": "Верно! Главный тезис автора (предложение с id='ev-q1'), акцентирующий важность осознанной дистанции от информационного шума."
        },
        {
          "option_number": 3,
          "text": "地方旅行に行かなければデジタル機器から離れることはできない。",
          "is_correct": false,
          "trap_type": "extreme_condition",
          "explanation_ru": "Неверно. Ловушка ложного категорического условия. Путешествие — лишь один из примеров, а не единственное обязательное условие."
        },
        {
          "option_number": 4,
          "text": "デジタル機器は現代人の健康に一切悪影響を及ぼさない。",
          "is_correct": false,
          "trap_type": "opposite_meaning",
          "explanation_ru": "Неверно. Ловушка противоположного смысла. В тексте прямо говорится о негативном воздействии постоянных уведомлений."
        }
      ]
    }
  ]
}
```

---

## 🔍 Описание полей и валидационные правила

### Уровень текста (`TextRecord`)
| Поле | Тип | Описание и валидация |
| :--- | :--- | :--- |
| `slug` | `string` | Уникальный строковый идентификатор (например, `n3-short-001`). Используется для идемпотентного upsert. |
| `level` | `string` | Одно из: `"N5"`, `"N4"`, `"N3"`, `"N2"`, `"N1"`. |
| `category` | `string` | Категория задания: `"short"`, `"medium"`, `"long"`, `"info_search"`, `"article"`. |
| `title` | `string` | Название текста на японском языке (с русским подзаголовком или без). |
| `source_type` | `string` | Источник: `"jlpt_official"` (официальный JLPT), `"news_adapted"` (адаптация прессы/NHK), `"original"` (оригинальный экзаменационный стиль). |
| `source_note` | `string | null` | Для `"original"` строго `null`. Для официальных/адаптированных — конкретная ссылка/выпуск. |
| `recommended_time_min` | `int` | Экзаменационный норматив времени в минутах (short: 2-3 мин, medium/info: 4-5 мин, long/article: 6-8 мин). |
| `body_html` | `string` | Разметка текста с тегами `<ruby>漢字<rt>かんじ</rt></ruby>` и фрагментами доказательств `<span id="..." data-evidence="...">`. |
| `translation_ru` | `string` | Качественный перевод на русский язык для панели анализа. |
| `vocabulary` | `array` | Список ключевых слов с чтением и переводом для словаря. |
| `needs_manual_review` | `array` | Список спорных или контекстуальных чтений кандзи, требующих дополнительной проверки. |
| `questions` | `array` | Массив вопросов (от 1 до 3 в зависимости от категории). |

### Уровень вопроса (`QuestionRecord`)
| Поле | Тип | Описание и валидация |
| :--- | :--- | :--- |
| `slug` | `string` | Уникальный ID вопроса (например, `n3-short-001-q1`). |
| `question_number` | `int` | Порядковый номер вопроса (1, 2, 3). |
| `type` | `string` | Тип вопроса: `claim` (мысль автора), `detail` (детализация), `reference` (ссылочные слова これ/それ), `inference` (логический вывод), `integrated` (интегрированное понимание), `info_search` (поиск фактов). |
| `prompt` | `string` | Текст вопроса на японском языке. |
| `evidence_span_id` | `string` | ID элемента `<span>` в `body_html`, содержащего прямое доказательство ответа. |
| `general_explanation` | `string` | Общее объяснение логики правильного ответа на русском языке. |
| `options` | `array` | Ровно 4 варианта ответа. Ровно один вариант имеет `is_correct: true`. |

### Уровень варианта ответа (`OptionRecord`)
| Поле | Тип | Описание и валидация |
| :--- | :--- | :--- |
| `option_number` | `int` | Номер варианта (1, 2, 3, 4). |
| `text` | `string` | Текст варианта на японском языке. |
| `is_correct` | `bool` | `true` для верного ответа, `false` для неверных. |
| `trap_type` | `string | null` | Для верного ответа — `null`. Для неверных вариантов — тип дистрактора (`overgeneralization`, `opposite_meaning`, `not_mentioned`, `partial_match`, `extreme_condition`, `subject_swap`, `fact_opinion_confusion`). |
| `explanation_ru` | `string` | Подробный разбор на русском языке с объяснением ловушки. |

