#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Entrypoint for PDF Import Pipeline.
Usage:
  python -m tools.pdf_import textbook.pdf --level N2 --type essay
  python -m tools.pdf_import --list
  python -m tools.pdf_import --review [slug]
  python -m tools.pdf_import --publish [slug]
  python -m tools.pdf_import --reject [slug]
"""

import sys
import argparse
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .pipeline import run_pdf_import_pipeline
from .review import list_staging_drafts, display_draft, publish_draft, reject_draft

def main():
    parser = argparse.ArgumentParser(
        description="JLPT Dokkai Master: Импорт учебников и экзаменационных материалов из PDF",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("pdf_file", nargs="?", default=None, help="Путь к PDF файлу для импорта")
    parser.add_argument("--level", "-l", choices=["N5", "N4", "N3", "N2", "N1"], help="Уровень JLPT (обязательно при импорте файла)")
    parser.add_argument("--type", "--category", "-t", default="short", choices=["short", "medium", "long", "info_search", "article", "essay"], help="Категория/тип материала")
    parser.add_argument("--title", default=None, help="Пользовательское название материала")
    parser.add_argument("--list", action="store_true", help="Показать список всех черновиков в staging")
    parser.add_argument("--review", nargs="?", const="all", help="Просмотреть черновик (укажите slug или оставьте пустым для всех)")
    parser.add_argument("--publish", help="Опубликовать черновик по slug в основную базу данных")
    parser.add_argument("--reject", help="Отклонить и удалить черновик из staging")

    args = parser.parse_args()

    if args.list:
        drafts = list_staging_drafts()
        print(f"\nВсего черновиков в staging: {len(drafts)}")
        if not drafts:
            print("Папка staging пуста.")
            return
        print(f"{'SLUG':<35} | {'LVL':<4} | {'CONF':<6} | {'ЗАГОЛОВОК':<30}")
        print("-" * 80)
        for d in drafts:
            print(f"{d.get('slug', ''):<35} | {d.get('level', ''):<4} | {d.get('confidence', 0):.0%}   | {d.get('title', '')[:30]}")
        return

    if args.review:
        drafts = list_staging_drafts()
        if not drafts:
            print("Нет черновиков для ревью.")
            return
        target = args.review
        for d in drafts:
            if target == "all" or d.get("slug") == target:
                display_draft(d)
        return

    if args.publish:
        publish_draft(args.publish)
        return

    if args.reject:
        reject_draft(args.reject)
        return

    if args.pdf_file:
        if not args.level:
            print("\033[31mОшибка: Для импорта PDF обязательно укажите уровень JLPT (--level N5..N1)\033[0m")
            sys.exit(1)

        pdf_path = Path(args.pdf_file)
        cat = "short" if args.type == "essay" else args.type

        print(f"\nЗапуск конвейера импорта PDF: {pdf_path.name}")
        print(f"Целевой уровень: {args.level} | Категория: {cat}")

        res = run_pdf_import_pipeline(
            file_path=pdf_path,
            level=args.level,
            category=cat,
            title_override=args.title
        )

        if not res["success"]:
            print(f"\n\033[31mИмпорт не выполнен:\033[0m {res['error']}")
            sys.exit(1)

        print("\n\033[32m✓ ИМПОРТ В СТАДИЮ ЧЕРНОВИКОВ (STAGING) УСПЕШНО ЗАВЕРШЁН!\033[0m")
        print(f"  Файл: {res['file_name']} ({res['page_count']} стр.)")
        print(f"  Найдено ключей ответов: {res['answer_keys_found']}")
        print(f"  Создано черновиков: {res['total_drafts_created']}")
        print("\nЧерновики сохранены в `content/staging/` и изолированы от публичного API.")
        print("Для просмотра и утверждения выполните:")
        print(f"  python -m tools.pdf_import --review")
        print(f"  python -m tools.pdf_import --publish [slug]")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
