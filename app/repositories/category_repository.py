from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryHasFruitsError,
    CategoryNotFoundError,
)
from app.models.category import Category
from app.models.fruit import Fruit
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.fruit import FruitListResponse, FruitResponse


async def _get_or_404(db: AsyncSession, category_id: str) -> Category:
    cat = await db.get(Category, category_id)
    if not cat:
        raise CategoryNotFoundError(category_id)
    return cat


async def create_category(db: AsyncSession, data: CategoryCreate) -> CategoryResponse:
    cat = Category(**data.model_dump())
    db.add(cat)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise CategoryAlreadyExistsError(data.nome)
    await db.refresh(cat)
    return CategoryResponse.model_validate(cat)


async def get_category(db: AsyncSession, category_id: str) -> CategoryResponse:
    cat = await _get_or_404(db, category_id)
    return CategoryResponse.model_validate(cat)


async def list_categories(db: AsyncSession, page: int, page_size: int) -> CategoryListResponse:
    query = select(Category)
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    result = await db.scalars(
        query.order_by(Category.nome).offset((page - 1) * page_size).limit(page_size)
    )
    cats = result.all()
    return CategoryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CategoryResponse.model_validate(c) for c in cats],
    )


async def update_category(
    db: AsyncSession, category_id: str, data: CategoryUpdate
) -> CategoryResponse:
    cat = await _get_or_404(db, category_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise CategoryAlreadyExistsError(data.nome or "")
    await db.refresh(cat)
    return CategoryResponse.model_validate(cat)


async def delete_category(db: AsyncSession, category_id: str) -> None:
    cat = await _get_or_404(db, category_id)
    count = (
        await db.scalar(
            select(func.count())
            .select_from(Fruit)
            .where(Fruit.category_id == category_id)
            .where(Fruit.deleted_at.is_(None))
        )
        or 0
    )
    if count > 0:
        raise CategoryHasFruitsError(category_id)
    await db.delete(cat)
    await db.commit()


async def list_category_fruits(
    db: AsyncSession, category_id: str, page: int, page_size: int
) -> FruitListResponse:
    await _get_or_404(db, category_id)
    query = (
        select(Fruit)
        .where(Fruit.category_id == category_id)
        .where(Fruit.deleted_at.is_(None))
    )
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
