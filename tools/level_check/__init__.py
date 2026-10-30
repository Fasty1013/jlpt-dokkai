"""
JLPT Dokkai Level Check Tool.
Provides text complexity analysis, kanji/grammar audit, and monotonicity verification.
"""

from .analyzer import analyze, check_corpus_monotonicity, clean_japanese_html

__all__ = ["analyze", "check_corpus_monotonicity", "clean_japanese_html"]

