import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import category_repository
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.fruit import FruitListResponse

logger = structlog.get_logger()


async def create_category(db: AsyncSession, data: CategoryCreate) -> CategoryResponse:
    result = await category_repository.create_category(db, data)
    logger.info("category_created", category_id=result.id, nome=result.nome)
    return result


async def get_category(db: AsyncSession, category_id: str) -> CategoryResponse:
    return await category_repository.get_category(db, category_id)


async def list_categories(
    db: AsyncSession, page: int, page_size: int
) -> CategoryListResponse:
    return await category_repository.list_categories(db, page=page, page_size=page_size)


async def update_category(
    db: AsyncSession, category_id: str, data: CategoryUpdate
) -> CategoryResponse:
    return await category_repository.update_category(db, category_id, data)


async def delete_category(db: AsyncSession, category_id: str) -> None:
    await category_repository.delete_category(db, category_id)
    logger.info("category_deleted", category_id=category_id)


async def list_category_fruits(
    db: AsyncSession, category_id: str, page: int, page_size: int
) -> FruitListResponse:
    return await category_repository.list_category_fruits(
        db, category_id, page=page, page_size=page_size
    )
