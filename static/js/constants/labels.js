/**
 * JLPT Dokkai Master - Domain Labels & Categorization Constants
 */

export const TRAP_LABELS = {
    'overgeneralization': 'Ловушка: Чрезмерное обобщение (言い過ぎ)',
    'opposite_meaning': 'Ловушка: Противоположный смысл (正反対)',
    'not_mentioned': 'Ловушка: В тексте не сказано (言及なし)',
    'partial_match': 'Ловушка: Частичное совпадение (部分一致の罠)',
    'extreme_condition': 'Ловушка: Ложное категорическое условие (極端な限定)',
    'temporal_mismatch': 'Ловушка: Несоответствие времени (時間・順序のズレ)',
    'misinterpretation': 'Ловушка: Неверное толкование причины (因果関係の誤読)',
    'unjustified_extrapolation': 'Ловушка: Необоснованный вывод (飛躍した推論)',
    'perspective_confusion': 'Ловушка: Подмена точки зрения (視点の混同)'
};

export const CATEGORY_NAMES = {
    'short': '短文 (Короткий)',
    'medium': '中文 (Средний)',
    'long': '長文 (Длинный)',
    'info_search': '情報検索 (Поиск информации)',
    'article': '論説文 (Статья / NHK)'
};

export const LEVEL_COLORS = {
    'N5': '#10b981',
    'N4': '#3b82f6',
    'N3': '#8b5cf6',
    'N2': '#f59e0b',
    'N1': '#ef4444'
};

export const JLPT_LEVELS = ['N5', 'N4', 'N3', 'N2', 'N1'];

export const CATEGORY_KEYS = ['short', 'medium', 'long', 'info_search', 'article'];
