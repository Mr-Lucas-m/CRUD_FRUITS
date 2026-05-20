from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import FruitAlreadyExistsError, FruitNotFoundError
from app.models.fruit import Fruit
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate


async def _get_or_404(db: AsyncSession, fruit_id: str, include_deleted: bool = False) -> Fruit:
    fruit = await db.get(Fruit, fruit_id)
    if not fruit or (not include_deleted and fruit.deleted_at is not None):
        raise FruitNotFoundError(fruit_id)
    return fruit


# ── Create ─────────────────────────────────────────────────────────────────────
async def create_fruit(db: AsyncSession, data: FruitCreate) -> FruitResponse:
    fruit = Fruit(**data.model_dump())
    db.add(fruit)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise FruitAlreadyExistsError(data.nome)
    await db.refresh(fruit)
    return FruitResponse.model_validate(fruit)


# ── Read (único) ───────────────────────────────────────────────────────────────
async def get_fruit(db: AsyncSession, fruit_id: str) -> FruitResponse:
    fruit = await _get_or_404(db, fruit_id)
    return FruitResponse.model_validate(fruit)


async def get_fruit_model(
    db: AsyncSession, fruit_id: str, include_deleted: bool = False
) -> Fruit:
    return await _get_or_404(db, fruit_id, include_deleted=include_deleted)


# ── Read (lista paginada) ──────────────────────────────────────────────────────
async def list_fruits(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    nome_filtro: str | None = None,
) -> FruitListResponse:
    query = select(Fruit).where(Fruit.deleted_at.is_(None))

    if nome_filtro:
        query = query.where(Fruit.nome.ilike(f"%{nome_filtro}%"))

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0

    result = await db.scalars(
        query.order_by(Fruit.nome).offset((page - 1) * page_size).limit(page_size)
    )
    fruits = result.all()

    return FruitListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FruitResponse.model_validate(f) for f in fruits],
    )


async def list_deleted_fruits(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> FruitListResponse:
    query = select(Fruit).where(Fruit.deleted_at.is_not(None))
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    result = await db.scalars(
        query.order_by(Fruit.nome).offset((page - 1) * page_size).limit(page_size)
    )
    fruits = result.all()
    return FruitListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FruitResponse.model_validate(f) for f in fruits],
    )


# ── Update (PATCH parcial) ─────────────────────────────────────────────────────
async def update_fruit(db: AsyncSession, fruit_id: str, data: FruitUpdate) -> FruitResponse:
    fruit = await _get_or_404(db, fruit_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fruit, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise FruitAlreadyExistsError(data.nome or "")
    await db.refresh(fruit)
    return FruitResponse.model_validate(fruit)


# ── Soft Delete ────────────────────────────────────────────────────────────────
async def soft_delete_fruit(db: AsyncSession, fruit_id: str) -> None:
    fruit = await _get_or_404(db, fruit_id)
    fruit.deleted_at = datetime.now(timezone.utc)
    await db.commit()


# ── Restore ────────────────────────────────────────────────────────────────────
async def restore_fruit(db: AsyncSession, fruit_id: str) -> FruitResponse:
    fruit = await _get_or_404(db, fruit_id, include_deleted=True)
    fruit.deleted_at = None
    await db.commit()
    await db.refresh(fruit)
    return FruitResponse.model_validate(fruit)
