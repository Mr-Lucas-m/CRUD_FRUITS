from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import FruitAlreadyExistsError, FruitNotFoundError
from app.models.fruit import Fruit
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate


def _get_or_404(db: Session, fruit_id: str) -> Fruit:
    """Busca uma fruta pelo id ou lança 404."""
    fruit = db.get(Fruit, fruit_id)
    if not fruit:
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


# ── Read (lista paginada) ──────────────────────────────────────────────────────
def list_fruits(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    nome_filtro: str | None = None,
) -> FruitListResponse:
    query = select(Fruit)

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


# ── Delete ─────────────────────────────────────────────────────────────────────
def delete_fruit(db: Session, fruit_id: str) -> None:
    fruit = _get_or_404(db, fruit_id)
    db.delete(fruit)
    db.commit()
