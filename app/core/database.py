from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# ── Engine ─────────────────────────────────────────────────────────────────────
connect_args: dict = {}
if "sqlite" in settings.DATABASE_URL:
    # SQLite exige isso em ambiente multi-thread (ex.: uvicorn)
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,      # verifica conexão antes de reutilizar do pool
    echo=settings.APP_DEBUG, # loga SQL apenas em modo debug
)

# Ativa WAL no SQLite para melhor concorrência de leitura/escrita
if "sqlite" in settings.DATABASE_URL:

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _connection_record) -> None:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()


# ── Session factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # evita lazy-load após commit
)


# ── Base declarativa (todos os models herdam daqui) ────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency de injeção para o FastAPI ───────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
