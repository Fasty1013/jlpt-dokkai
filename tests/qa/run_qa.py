#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repeatable QA Test Orchestrator for JLPT Dokkai Master.
Runs Playwright multi-viewport matrix, collectors, axe-core and Anti-Cheat sniffer.

Usage:
    python tests/qa/run_qa.py --target local
    python tests/qa/run_qa.py --target prod --prod-url https://<service>.onrender.com
    python tests/qa/run_qa.py --quick
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
QA_DIR = PROJECT_ROOT / "tests" / "qa"
DOCS_QA_DIR = PROJECT_ROOT / "docs" / "qa"


def check_server(target: str, url: str) -> bool:
    import urllib.request
    import urllib.error
    import time

    health_url = f"{url.rstrip('/')}/api/health"
    print(f"► Проверка доступности сервера: {health_url}")

    max_wait = 120 if target == "prod" else 5
    interval = 5
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "Dokkai-QA-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode("utf-8"))
                    print(f"✓ Сервер доступен за {elapsed:.1f}с: status={data.get('status')}, texts={data.get('texts_count')}")
                    return True
        except Exception as e:
            if target == "prod" and elapsed < max_wait:
                print(f"⏳ [Холодный старт Render] Пробуждение контейнера... ({elapsed:.1f} с / {max_wait} с)")
                time.sleep(interval)
                continue
            print(f"✗ Не удалось подключиться к {health_url}: {e}")
            break
    return False


def run_tests(target: str, prod_url: str, quick: bool, project_filter: str = "") -> int:
    env = os.environ.copy()
    env["TARGET"] = target
    env["PROD_URL"] = prod_url
    env["LOCAL_URL"] = "http://localhost:8000"

    cmd = ["npx", "playwright", "test"]

    if quick:
        cmd.extend(["--project=desktop_compact", "--project=mobile_small_android_360"])
    elif project_filter:
        cmd.extend([f"--project={project_filter}"])

    print(f"\n{'=' * 65}")
    print(f"🚀 Запуск Playwright QA Matrix (Target: {target.upper()})")
    print(f"Команда: {' '.join(cmd)}")
    print(f"{'=' * 65}\n")

    res = subprocess.run(cmd, cwd=str(QA_DIR), env=env, shell=(sys.platform == "win32"))
    return res.returncode


def main():
    parser = argparse.ArgumentParser(description="JLPT Dokkai QA Test Runner")
    parser.add_argument("--target", choices=["local", "prod"], default="local", help="Целевое окружение (local|prod)")
    parser.add_argument("--prod-url", default=os.getenv("PROD_URL", "https://jlpt-dokkai.onrender.com"), help="URL боевого сервера на Render")
    parser.add_argument("--quick", action="store_true", help="Быстрый прогон (1 мобильный + 1 десктопный экран)")
    parser.add_argument("--project", default="", help="Конкретный проект из playwright.config.ts")
    parser.add_argument("--check-only", action="store_true", help="Только проверить доступность и версию")

    args = parser.parse_args()
    base_url = args.prod_url if args.target == "prod" else "http://localhost:8000"

    print(f"\n🇯🇵 JLPT DOKKAI MASTER — QA AUTOMATED TEST SUITE")
    print(f"Target: {args.target.upper()} ({base_url})")
    if args.target == "prod":
        print(f"🛡️ РЕЖИМ PROD: writes_on_prod = false (ТОЛЬКО ЧТЕНИЕ, запись заблокирована)")

    is_up = check_server(args.target, base_url)
    if not is_up and args.target == "local":
        print("\n⚠️ ВНИМАНИЕ: Локальный сервер на http://localhost:8000 не запущен!")
        print("Запустите его в отдельном окне: python -m uvicorn main:app --host 0.0.0.0 --port 8000\n")
        if not args.check_only:
            sys.exit(1)

    if args.check_only:
        print("✓ Проверка подключения завершена.")
        sys.exit(0 if is_up else 1)

    exit_code = run_tests(args.target, args.prod_url, args.quick, args.project)

    # Печать ссылок на сформированные отчёты
    print(f"\n{'=' * 65}")
    print(f"📊 Отчёты о тестировании сформированы:")
    bugs_json = DOCS_QA_DIR / "bugs.json"
    if bugs_json.exists():
        print(f"  • JSON реестр дефектов: {bugs_json}")
    report_mds = list(DOCS_QA_DIR.glob("REPORT-*.md"))
    if report_mds:
        print(f"  • Markdown отчёт: {report_mds[-1]}")
    print(f"{'=' * 65}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

