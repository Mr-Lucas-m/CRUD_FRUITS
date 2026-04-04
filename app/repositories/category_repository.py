from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryHasFruitsError,
    CategoryNotFoundError,
)
from app.models.category import Category
from app.models.fruit import Fruit
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.fruit import FruitListResponse, FruitResponse


def _get_or_404(db: Session, category_id: str) -> Category:
    cat = db.get(Category, category_id)
    if not cat:
        raise CategoryNotFoundError(category_id)
    return cat


def create_category(db: Session, data: CategoryCreate) -> CategoryResponse:
    cat = Category(**data.model_dump())
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CategoryAlreadyExistsError(data.nome)
    db.refresh(cat)
    return CategoryResponse.model_validate(cat)


def get_category(db: Session, category_id: str) -> CategoryResponse:
    cat = _get_or_404(db, category_id)
    return CategoryResponse.model_validate(cat)


def list_categories(db: Session, page: int, page_size: int) -> CategoryListResponse:
    query = select(Category)
    total: int = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    cats = db.scalars(
        query.order_by(Category.nome).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CategoryListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CategoryResponse.model_validate(c) for c in cats],
    )


def update_category(db: Session, category_id: str, data: CategoryUpdate) -> CategoryResponse:
    cat = _get_or_404(db, category_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CategoryAlreadyExistsError(data.nome or "")
    db.refresh(cat)
    return CategoryResponse.model_validate(cat)


def delete_category(db: Session, category_id: str) -> None:
    cat = _get_or_404(db, category_id)
    count = (
        db.scalar(
            select(func.count())
            .where(Fruit.category_id == category_id)
            .where(Fruit.deleted_at.is_(None))
        )
        or 0
    )
    if count > 0:
        raise CategoryHasFruitsError(category_id)
    db.delete(cat)
    db.commit()


def list_category_fruits(
    db: Session, category_id: str, page: int, page_size: int
) -> FruitListResponse:
    _get_or_404(db, category_id)
    query = (
        select(Fruit)
        .where(Fruit.category_id == category_id)
        .where(Fruit.deleted_at.is_(None))
    )
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
