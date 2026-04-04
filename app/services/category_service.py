import structlog
from sqlalchemy.orm import Session

from app.repositories import category_repository
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.fruit import FruitListResponse

logger = structlog.get_logger()


def create_category(db: Session, data: CategoryCreate) -> CategoryResponse:
    result = category_repository.create_category(db, data)
    logger.info("category_created", category_id=result.id, nome=result.nome)
    return result


def get_category(db: Session, category_id: str) -> CategoryResponse:
    return category_repository.get_category(db, category_id)


def list_categories(db: Session, page: int, page_size: int) -> CategoryListResponse:
    return category_repository.list_categories(db, page=page, page_size=page_size)


def update_category(db: Session, category_id: str, data: CategoryUpdate) -> CategoryResponse:
    return category_repository.update_category(db, category_id, data)


def delete_category(db: Session, category_id: str) -> None:
    category_repository.delete_category(db, category_id)
    logger.info("category_deleted", category_id=category_id)


def list_category_fruits(
    db: Session, category_id: str, page: int, page_size: int
) -> FruitListResponse:
    return category_repository.list_category_fruits(db, category_id, page=page, page_size=page_size)
