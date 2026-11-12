"""DATABASE_URL handling checks (no database connection is made).

Usage: python tools/db_url_check.py
- normalize_database_url() cleans pasted values (quotes, psql, DATABASE_URL=, whitespace)
  and pins the installed psycopg2 driver (SQLAlchemy 2.1 defaults postgresql:// to psycopg v3);
- importing app.core.database with a Neon-style URL creates a psycopg2 engine;
- a broken value fails with a message that does not contain the password.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import normalize_database_url  # noqa: E402

NEON = "postgresql://neondb_owner:Secr3tPass@ep-x-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
PINNED = NEON.replace("postgresql://", "postgresql+psycopg2://", 1)

failed = []


def check(name, ok, info=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"   {info}" if info and not ok else ""))
    if not ok:
        failed.append(name)


cases = {
    "plain Neon string": NEON,
    "single quotes": f"'{NEON}'",
    "double quotes": f'"{NEON}"',
    "psql prefix": f"psql '{NEON}'",
    "DATABASE_URL= prefix": f"DATABASE_URL='{NEON}'",
    "spaces and newline": f"  {NEON}\n",
    "line break inside": NEON[:40] + "\n" + NEON[40:],
    "postgresql+psycopg://": NEON.replace("postgresql://", "postgresql+psycopg://", 1),
    "postgres:// (Heroku style)": NEON.replace("postgresql://", "postgres://", 1),
}
for name, raw in cases.items():
    got = normalize_database_url(raw)
    check(f"normalize: {name}", got == PINNED, got)

check("normalize: explicit psycopg2 kept", normalize_database_url(PINNED) == PINNED)
check("normalize: sqlite unchanged", normalize_database_url("sqlite:///./dokkai.db") == "sqlite:///./dokkai.db")
check("normalize: empty -> default sqlite", normalize_database_url("") == "sqlite:///./dokkai.db")


def run_import(url: str):
    code = (
        "import app.core.database as d;"
        "print(d.DATABASE_BACKEND, d.engine.dialect.name, d.engine.dialect.driver,"
        " d.engine.pool._pre_ping, d.engine.pool._recycle)"
    )
    env = {**os.environ, "DATABASE_URL": url, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True)


r = run_import(f"'{NEON}'")
check("engine: quoted Neon URL -> postgresql psycopg2, pre_ping, recycle 280",
      r.returncode == 0 and r.stdout.split() == ["postgresql", "postgresql", "psycopg2", "True", "280"],
      (r.stdout + r.stderr)[-400:])

r = run_import("sqlite:///./dokkai.db")
check("engine: sqlite default unchanged (no pre_ping)",
      r.returncode == 0 and r.stdout.split()[:3] == ["sqlite", "sqlite", "pysqlite"] and r.stdout.split()[3] == "False",
      (r.stdout + r.stderr)[-400:])

r = run_import("not a url :: Secr3tPass")
check("engine: broken value -> clear error", r.returncode != 0 and "DATABASE_URL is not a valid database URL" in r.stderr, r.stderr[-400:])
check("engine: error does not leak the password", "Secr3tPass" not in r.stderr.split("RuntimeError")[-1])

print("\nALL PASSED" if not failed else f"\n{len(failed)} FAILED")
sys.exit(1 if failed else 0)
