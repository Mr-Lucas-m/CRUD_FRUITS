import uuid

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Fruit(Base):
    __tablename__ = "fruits"

    # ── Chave primária (UUID como string para compatibilidade SQLite/Postgres) ──
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade_estoque: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Timestamps gerenciados pelo banco
    data_cadastro: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    data_atualizacao: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Fruit id={self.id!r} nome={self.nome!r}>"
