#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builder for JLPT Benchmark Level References (content/level_refs/*.json).
Compiled by @jlpt-expert.
Note: Official JLPT (JEES) does not publish exhaustive official lists.
These reference lists are indicative standards based on the JLPT Guidelines,
Kyōiku kanji distributions, and open pedagogical corpora.
"""

import json
from pathlib import Path

REFS_DIR = Path(__file__).resolve().parent / "content" / "level_refs"
REFS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Benchmark Kanji Distributions (Cumulative)
KANJI_N5 = set("日一国会人年大十二本中長出三同時行見月分後前生五間上東四今金九入学高円子外八六下気小七山話女北午百書先名川千水半男西電校語土木聞食車何南万毎白天母火右読友左休父雨")
KANJI_N4 = KANJI_N5.union(set("会同社店員駅立買売待言読思使作知持借貸帰歩走送開閉始終好急起寝教習字勉漢英写計図館曜朝昼晩春夏秋冬週多少広安早新古長短高低軽重明暗強弱早暑寒楽親切方公病医者薬質私町道神風海空林森野天池島寺京花手目耳足口首心体") | set("切不元院銀工仕堂広"))
KANJI_N3 = KANJI_N4.union(set("意表理化主代着決全定授受受実現法界政経済商産研部科発題要必役由情成直信願記数平不初交比点利過化当相変加組直指求論調面次") | set("取別注勝消運笑集進宿旅庭線港運暑冷熱払残客招具受渡配払届留") | set("悲喜恥怒苦幸忙暇疲痛痛願望"))
KANJI_N2 = KANJI_N3.union(set("政経済商産研務権党統論規資財価制境設構総領提査際応推視条構態勢責判保率策企展革導維響象域観責評割施協義規態任認企") | set("害障毒震被倒防及救援避警捜補損破裂傷災危険救逃") | set("悩惑憎疑慮悔嫉妬肯否哀慕"))
KANJI_N1 = KANJI_N2.union(set("止揚捨象耽溺普遍葛藤創発熟議隘路萌芽乖離主客二元論傲慢謙虚規範アポリア透徹超越包括契機媒介脱構築包摂射程") | set("傲慢憐憫煩悶憤慨躊躇齟齬猜疑貪欲執着達観俯瞰睥睨陶酔恍惚戦慄震撼辟易躊躇"))

# 2. Grammar Patterns
GRAMMAR_PATTERNS = {
    "N5": [
        "です", "ます", "でした", "ました", "ません", "たい", "たくない", "てください", "ています",
        "から", "ので", "より", "前", "後", "ないでください", "てから", "たり", "があります", "がいます"
    ],
    "N4": [
        "たことがある", "たり〜たり", "〜ば", "〜たら", "〜なら", "〜そうだ", "〜ながら", "〜てしまう",
        "〜やすい", "〜にくい", "〜すぎる", "〜ようと思う", "〜てみる", "〜ておく", "〜てくれる",
        "〜てもらう", "〜てあげる", "〜と言っていた", "〜かもしれない", "〜なければならない"
    ],
    "N3": [
        "わけではない", "わけがない", "に違いない", "はずだ", "ようにする", "ことになる", "ことにする",
        "おかげで", "せいで", "に基づいて", "を中心に", "をはじめ", "に関して", "に対して", "にとって",
        "として", "によって", "たびに", "たとたん", "さえ〜ば", "たとえ〜ても", "べきだ"
    ],
    "N2": [
        "にほかならない", "を踏まえて", "を余儀なくされる", "とは限らない", "にすぎない", "つつある",
        "おそれがある", "を契機に", "をめぐって", "に基づいて", "に際して", "に先立って", "っこない",
        "わけにはいかない", "ものがある", "ことだし", "ばかりか", "どころか", "げ", "っぽい", "向き", "向け"
    ],
    "N1": [
        "極まりない", "を皮切りに", "にたえない", "ならいざ知らず", "たるもの", "を禁じ得ない",
        "と相まって", "であれ", "とあって", "をものともせず", "をおいて", "ならではの",
        "にかまけて", "に即して", "まみれ", "ずくめ", "ごとき", "んばかり", "かたがた", "がてら"
    ]
}

LEVEL_METRICS = {
    "N5": {
        "max_sentence_len": 40,
        "avg_sentence_len_target": 20,
        "kanji_ratio_max": 0.25,
        "text_len_range": (80, 320)
    },
    "N4": {
        "max_sentence_len": 55,
        "avg_sentence_len_target": 26,
        "kanji_ratio_max": 0.32,
        "text_len_range": (150, 480)
    },
    "N3": {
        "max_sentence_len": 75,
        "avg_sentence_len_target": 35,
        "kanji_ratio_max": 0.38,
        "text_len_range": (200, 750)
    },
    "N2": {
        "max_sentence_len": 100,
        "avg_sentence_len_target": 45,
        "kanji_ratio_max": 0.44,
        "text_len_range": (250, 950)
    },
    "N1": {
        "max_sentence_len": 140,
        "avg_sentence_len_target": 55,
        "kanji_ratio_max": 0.52,
        "text_len_range": (300, 1200)
    }
}

ALL_KANJI_SETS = {
    "N5": KANJI_N5,
    "N4": KANJI_N4,
    "N3": KANJI_N3,
    "N2": KANJI_N2,
    "N1": KANJI_N1
}

for lvl in ["N5", "N4", "N3", "N2", "N1"]:
    ref_data = {
        "level": lvl,
        "disclaimer": "Официальных исчерпывающих списков JLPT не существует (позиция JEES). Данный список является научно обоснованным ориентиром для автоматического аудита сложности.",
        "benchmark_kanji": sorted(list(ALL_KANJI_SETS[lvl])),
        "grammar_patterns": GRAMMAR_PATTERNS[lvl],
        "metric_thresholds": LEVEL_METRICS[lvl]
    }
    out_file = REFS_DIR / f"{lvl.lower()}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(ref_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {out_file}: {len(ref_data['benchmark_kanji'])} benchmark kanji, {len(ref_data['grammar_patterns'])} grammar patterns.")

print("All level reference files created successfully.")
