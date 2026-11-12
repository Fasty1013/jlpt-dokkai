import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dokkai.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Serverless Postgres (Neon free plan) suspends compute after ~5 min idle and drops
    # open connections: test each pooled connection before use and recycle old ones.
    engine_kwargs = {"pool_pre_ping": True, "pool_recycle": 280}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

