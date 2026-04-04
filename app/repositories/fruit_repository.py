from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import FruitAlreadyExistsError, FruitNotFoundError
from app.models.fruit import Fruit
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate


def _get_or_404(db: Session, fruit_id: str, include_deleted: bool = False) -> Fruit:
    """Busca uma fruta pelo id ou lança 404. Por padrão ignora soft-deleted."""
    fruit = db.get(Fruit, fruit_id)
    if not fruit or (not include_deleted and fruit.deleted_at is not None):
        raise FruitNotFoundError(fruit_id)
    return fruit


# ── Create ─────────────────────────────────────────────────────────────────────
def create_fruit(db: Session, data: FruitCreate) -> FruitResponse:
    fruit = Fruit(**data.model_dump())
    db.add(fruit)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FruitAlreadyExistsError(data.nome)
    db.refresh(fruit)
    return FruitResponse.model_validate(fruit)


# ── Read (único) ───────────────────────────────────────────────────────────────
def get_fruit(db: Session, fruit_id: str) -> FruitResponse:
    fruit = _get_or_404(db, fruit_id)
    return FruitResponse.model_validate(fruit)


def get_fruit_model(db: Session, fruit_id: str, include_deleted: bool = False) -> Fruit:
    """Retorna o ORM model para operações que precisam modificar o objeto."""
    return _get_or_404(db, fruit_id, include_deleted=include_deleted)


# ── Read (lista paginada) ──────────────────────────────────────────────────────
def list_fruits(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    nome_filtro: str | None = None,
) -> FruitListResponse:
    query = select(Fruit).where(Fruit.deleted_at.is_(None))

    if nome_filtro:
        query = query.where(Fruit.nome.ilike(f"%{nome_filtro}%"))

    total: int = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    fruits = db.scalars(
        query.order_by(Fruit.nome).offset((page - 1) * page_size).limit(page_size)
    ).all()

    return FruitListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FruitResponse.model_validate(f) for f in fruits],
    )


def list_deleted_fruits(
    db: Session,
    page: int = 1,
    page_size: int = 20,
) -> FruitListResponse:
    query = select(Fruit).where(Fruit.deleted_at.is_not(None))
    total: int = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    fruits = db.scalars(
        query.order_by(Fruit.nome).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return FruitListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FruitResponse.model_validate(f) for f in fruits],
    )


# ── Update (PATCH parcial) ─────────────────────────────────────────────────────
def update_fruit(db: Session, fruit_id: str, data: FruitUpdate) -> FruitResponse:
    fruit = _get_or_404(db, fruit_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fruit, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FruitAlreadyExistsError(data.nome or "")
    db.refresh(fruit)
    return FruitResponse.model_validate(fruit)


# ── Soft Delete ────────────────────────────────────────────────────────────────
def soft_delete_fruit(db: Session, fruit_id: str) -> None:
    fruit = _get_or_404(db, fruit_id)
    fruit.deleted_at = datetime.now(timezone.utc)
    db.commit()


# ── Restore ────────────────────────────────────────────────────────────────────
def restore_fruit(db: Session, fruit_id: str) -> FruitResponse:
    fruit = _get_or_404(db, fruit_id, include_deleted=True)
    fruit.deleted_at = None
    db.commit()
    db.refresh(fruit)
    return FruitResponse.model_validate(fruit)
