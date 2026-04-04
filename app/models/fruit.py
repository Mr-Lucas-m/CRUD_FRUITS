import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Fruit(Base):
    __tablename__ = "fruits"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade_estoque: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Item 2: FK para Category (nullable)
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=True
    )

    # Item 3: Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Item 5: Validações refinadas
    unidade_medida: Mapped[str] = mapped_column(String(20), nullable=False, default="unidade")
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    preco_custo: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    data_atualizacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Fruit id={self.id!r} nome={self.nome!r}>"
