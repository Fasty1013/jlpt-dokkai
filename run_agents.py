#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Orchestrator for JLPT Dokkai Master
Supported Agents:
  - jlpt-expert (Лингвист, методист JLPT, эксперт по кандзи и грамматике)
  - senior-dev  (Senior Software Engineer: архитектура, код, безопасность, тесты)

Usage:
  python run_agents.py                   # Интерактивное меню выбора
  python run_agents.py --expert          # Запуск только @jlpt-expert
  python run_agents.py --dev             # Запуск только @senior-dev
  python run_agents.py --both            # Совместный запуск (Оркестратор: Эксперт + Разработчик)
  python run_agents.py --check           # Быстрая самодиагностика проекта и тесты
  python run_agents.py -b -t "Разбор нового текста N2 из NHK"
"""

import os
import sys
import argparse
import subprocess
import py_compile
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
AGENTS_DIR = BASE_DIR / ".agents" / "agents"

# Terminal ANSI colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

def print_banner():
    banner = f"""{CYAN}{BOLD}
╔═════════════════════════════════════════════════════════════════════╗
║               🇯🇵 JLPT DOKKAI MULTI-AGENT SYSTEM                     ║
║   [@jlpt-expert] Методолог JLPT  ×  [@senior-dev] Senior Engineer   ║
╚═════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def load_agent_prompt(agent_filename: str) -> str:
    path = AGENTS_DIR / agent_filename
    if not path.exists():
        return f"{RED}Файл конфигурации агента не найден: {path}{RESET}"
    return path.read_text(encoding="utf-8")

def run_project_diagnostics() -> bool:
    """Запуск автотестов и статического анализа проекта."""
    print(f"\n{BOLD}{CYAN}--- [Диагностика проекта и автотесты] ---{RESET}")
    all_ok = True

    # 1. Синтаксическая проверка файлов Python
    py_files = ["main.py", "models.py", "schemas.py", "database.py", "dictionary.py", "seed.py", "test_api.py"]
    print(f"{BLUE}► 1. Проверка синтаксиса Python-файлов...{RESET}")
    for fname in py_files:
        fpath = BASE_DIR / fname
        if fpath.exists():
            try:
                py_compile.compile(str(fpath), doraise=True)
                print(f"  {GREEN}✓{RESET} {fname} — синтаксис корректен")
            except Exception as e:
                print(f"  {RED}✗ Ошибка компиляции {fname}:{RESET} {e}")
                all_ok = False

    # 2. Аудит изоляции данных (Anti-Cheat Security Guard)
    print(f"\n{BLUE}► 2. Аудит изоляции данных (Anti-Cheat Security Guard)...{RESET}")
    schemas_path = BASE_DIR / "schemas.py"
    if schemas_path.exists():
        content = schemas_path.read_text(encoding="utf-8")
        forbidden_in_read = ["is_correct", "option_explanation", "general_explanation", "evidence_span_id", "translation_ru"]
        
        # Проверяем пред-экзаменационные схемы OptionReadSchema, QuestionReadSchema, TextReadSchema
        read_schemas_block = ""
        if "class OptionReadSchema" in content and "class SubmitPayloadSchema" in content:
            read_schemas_block = content.split("class OptionReadSchema")[1].split("class SubmitPayloadSchema")[0]
        
        leaks = [f for f in forbidden_in_read if f in read_schemas_block]
        if not leaks:
            print(f"  {GREEN}✓{RESET} Текстовый эндпоинт изолирован. Утечек ответов в схемах чтения не обнаружено.")
        else:
            print(f"  {RED}✗ ВНИМАНИЕ: Обнаружена потенциальная утечка полей в схемах чтения: {leaks}{RESET}")
            all_ok = False

    # 3. Запуск функционального тест-сьюита
    print(f"\n{BLUE}► 3. Запуск системных тестов (test_api.py)...{RESET}")
    test_path = BASE_DIR / "test_api.py"
    if test_path.exists():
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env
        )
        if res.returncode == 0:
            print(f"  {GREEN}✓ Все тесты test_api.py успешно пройдены!{RESET}")
            if res.stdout:
                for line in res.stdout.strip().split("\n")[-3:]:
                    print(f"    {line}")
        else:
            print(f"  {RED}✗ Ошибка выполнения тестов:{RESET}\n{res.stderr or res.stdout}")
            all_ok = False

    return all_ok

def run_jlpt_expert(task: str = ""):
    print(f"\n{MAGENTA}{BOLD}======================================================================{RESET}")
    print(f"{MAGENTA}{BOLD}🥋 АГЕНТ 1: @jlpt-expert (Методолог экзамена JLPT & Лингвист){RESET}")
    print(f"{MAGENTA}{BOLD}======================================================================{RESET}")
    
    config = load_agent_prompt("jlpt-expert.md")
    print(f"{CYAN}Загружен профиль из: .agents/agents/jlpt-expert.md{RESET}")
    if task:
        print(f"\n{BOLD}🎯 Текущая задача:{RESET} {task}")

    print(f"""
{BOLD}Фокус работы @jlpt-expert:{RESET}
1. Разбор грамматических конструкций (文法) уровней N5–N1.
2. Проверка корректности фуриганы (`<ruby>漢字<rt>かんじ</rt></ruby>`).
3. Анализ дистракторов: почему правильный вариант верен, а 3 других — типичные экзаменационные ловушки.
4. Разметка фрагментов-доказательств (`evidence_span_id`) в японском тексте.
5. Адаптация материалов NHK World News под лексический минимум целевого уровня JLPT.
""")
    print(f"{GREEN}Агент готов к обработке запроса.{RESET}")

def run_senior_dev(task: str = ""):
    print(f"\n{BLUE}{BOLD}======================================================================{RESET}")
    print(f"{BLUE}{BOLD}💻 АГЕНТ 2: @senior-dev (Senior Software Engineer & Architect){RESET}")
    print(f"{BLUE}{BOLD}======================================================================{RESET}")
    
    config = load_agent_prompt("senior-dev.md")
    print(f"{CYAN}Загружен профиль из: .agents/agents/senior-dev.md{RESET}")
    if task:
        print(f"\n{BOLD}🎯 Текущая задача:{RESET} {task}")

    print(f"""
{BOLD}Фокус работы @senior-dev:{RESET}
1. Архитектура FastAPI эндпоинтов, Pydantic v2 схем и моделей SQLAlchemy.
2. Поддержка строгой Anti-Cheat изоляции (никаких утечек `is_correct` до `submit`).
3. Фронтенд: Vanilla JS, пошаговый мастер вопросов (Wizard), гибкий таймер, адаптивный UI.
4. Отказоустойчивость: проверка DOM элементов на null, отсутствие блокирующих alert().
5. Инженерия качества: запуск тестов, оптимизация запросов, масштабируемость.
""")
    # Запускаем автодиагностику кода
    is_healthy = run_project_diagnostics()
    if is_healthy:
        print(f"\n{GREEN}{BOLD}✅ Статус системы: ЗЕЛЁНЫЙ (Кодовая база стабильна, тесты пройдены){RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}⚠️ Статус системы: ТРЕБУЕТСЯ ВНИМАНИЕ (Найдены замечания){RESET}")

def run_orchestrator(task: str = ""):
    print(f"\n{YELLOW}{BOLD}======================================================================{RESET}")
    print(f"{YELLOW}{BOLD}🤝 ОРКЕСТРАТОР: Совместный запуск [@jlpt-expert] + [@senior-dev]{RESET}")
    print(f"{YELLOW}{BOLD}======================================================================{RESET}")
    
    if not task:
        task = input(f"\n{BOLD}Введите описание задачи для мультиагентного пайплайна: {RESET}").strip()
        if not task:
            task = "Полный аудит проекта: лингвистическая проверка текстов JLPT и технический код-ревью"

    print(f"\n{BOLD}🎯 Общая задача:{RESET} {task}")
    print(f"\n{CYAN}--- ФАЗА 1: Лингвистический и методологический анализ (@jlpt-expert) ---{RESET}")
    run_jlpt_expert(task)

    print(f"\n{CYAN}--- ФАЗА 2: Архитектурная реализация, аудит и тесты (@senior-dev) ---{RESET}")
    run_senior_dev(task)

    print(f"\n{YELLOW}{BOLD}======================================================================{RESET}")
    print(f"{GREEN}{BOLD}✨ Пайплайн завершён!{RESET}")
    print(f"Вы можете адресовать запросы агентам напрямую в чате через:")
    print(f"  • {MAGENTA}@jlpt-expert{RESET} — для работы с японскими текстами, фуриганой и ловушками JLPT")
    print(f"  • {BLUE}@senior-dev{RESET} — для доработки бэкенда, фронтенда, багфиксов и архитектуры")
    print(f"{YELLOW}{BOLD}======================================================================{RESET}\n")

def interactive_menu():
    print_banner()
    while True:
        print(f"{BOLD}Выберите режим запуска мультиагентной системы:{RESET}")
        print(f"  {MAGENTA}[1]{RESET} Запустить только {BOLD}@jlpt-expert{RESET} (Лингвист-методолог JLPT)")
        print(f"  {BLUE}[2]{RESET} Запустить только {BOLD}@senior-dev{RESET} (Senior Software Engineer)")
        print(f"  {YELLOW}[3]{RESET} Запустить обоих агентов одновременно {BOLD}(Dual Orchestrator){RESET}")
        print(f"  {CYAN}[4]{RESET} Быстрая самодиагностика проекта и автотесты")
        print(f"  {RED}[0]{RESET} Выход")
        
        choice = input(f"\n{BOLD}Введите номер действия [0-4]: {RESET}").strip()
        if choice == "1":
            t = input(f"{BOLD}Введите описание задачи (Enter для пропуска): {RESET}").strip()
            run_jlpt_expert(t)
            break
        elif choice == "2":
            t = input(f"{BOLD}Введите описание задачи (Enter для пропуска): {RESET}").strip()
            run_senior_dev(t)
            break
        elif choice == "3":
            t = input(f"{BOLD}Введите описание задачи (Enter для запуска по умолчанию): {RESET}").strip()
            run_orchestrator(t)
            break
        elif choice == "4":
            run_project_diagnostics()
            break
        elif choice in ("0", "q", "exit"):
            print("Выход из системы.")
            break
        else:
            print(f"{RED}Неверный ввод, выберите пункт от 0 до 4.{RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Запуск мультиагентной системы JLPT Dokkai Master",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-e", "--expert", action="store_true", help="Запустить только @jlpt-expert")
    parser.add_argument("-d", "--dev", action="store_true", help="Запустить только @senior-dev")
    parser.add_argument("-b", "--both", action="store_true", help="Запустить обоих агентов (Оркестратор)")
    parser.add_argument("-c", "--check", action="store_true", help="Выполнить диагностику и запустить автотесты")
    parser.add_argument("-t", "--task", type=str, default="", help="Описание задачи для агента")
    parser.add_argument("-i", "--interactive", action="store_true", help="Открыть интерактивное меню")

    args = parser.parse_args()

    # Если аргументы не указаны или указан флаг -i — запускаем интерактивное меню
    if len(sys.argv) == 1 or args.interactive:
        interactive_menu()
    elif args.both:
        print_banner()
        run_orchestrator(args.task)
    elif args.expert:
        print_banner()
        run_jlpt_expert(args.task)
    elif args.dev:
        print_banner()
        run_senior_dev(args.task)
    elif args.check:
        print_banner()
        run_project_diagnostics()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
