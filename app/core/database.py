import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import declarative_base, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./dokkai.db"


def normalize_database_url(raw: str) -> str:
    """Clean a DATABASE_URL pasted from a provider dashboard (Neon "Copy snippet", .env, psql).

    Accepts e.g. `psql 'postgresql://…'`, `DATABASE_URL="postgresql://…"`, surrounding quotes,
    spaces and line breaks; returns the bare URL. `postgres://` becomes `postgresql://`.
    """
    s = (raw or "").strip()
    if s[:5].lower() == "psql ":
        s = s[5:].strip()
    if s[:13].upper() == "DATABASE_URL=":
        s = s[13:].strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        s = s[1:-1].strip()
    s = "".join(s.split())  # a connection URL never contains whitespace
    # Pin the installed driver (psycopg2-binary): SQLAlchemy 2.1 made psycopg (v3) the default
    # for plain postgresql://, which is not installed -> "No module named 'psycopg'" on Render.
    for prefix in ("postgres://", "postgresql://", "postgresql+psycopg://"):
        if s.startswith(prefix):
            s = "postgresql+psycopg2://" + s[len(prefix):]
            break
    return s or DEFAULT_DATABASE_URL


def describe_database_url(url: str) -> str:
    """Safe description for logs: never includes the password."""
    try:
        u = make_url(url)
        return f"{u.drivername}://{u.host or ''}/{u.database or ''}"
    except ArgumentError:
        return f"unparseable value starting with {url[:12]!r} (length {len(url)})"


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))
DATABASE_BACKEND = "sqlite" if DATABASE_URL.startswith("sqlite") else "postgresql"

connect_args = {}
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Serverless Postgres (Neon free plan) suspends compute after ~5 min idle and drops
    # open connections: test each pooled connection before use and recycle old ones.
    engine_kwargs = {"pool_pre_ping": True, "pool_recycle": 280}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        echo=False,
        **engine_kwargs
    )
except ArgumentError as exc:
    raise RuntimeError(
        "DATABASE_URL is not a valid database URL: "
        f"{describe_database_url(DATABASE_URL)}. Expected postgresql://user:password@host/db?sslmode=require"
    ) from exc

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
