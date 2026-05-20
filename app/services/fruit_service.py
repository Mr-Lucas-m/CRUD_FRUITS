import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import fruit_repository
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate

logger = structlog.get_logger()


async def create_fruit(db: AsyncSession, data: FruitCreate) -> FruitResponse:
    if data.preco_custo is not None and data.preco_custo >= data.preco:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O preço de custo deve ser menor que o preço de venda.",
        )
    result = await fruit_repository.create_fruit(db, data)
    logger.info("fruit_created", fruit_id=result.id, nome=result.nome)
    return result


async def get_fruit(db: AsyncSession, fruit_id: str) -> FruitResponse:
    return await fruit_repository.get_fruit(db, fruit_id)


async def list_fruits(
    db: AsyncSession, page: int, page_size: int, nome_filtro: str | None
) -> FruitListResponse:
    return await fruit_repository.list_fruits(
        db, page=page, page_size=page_size, nome_filtro=nome_filtro
    )


async def list_deleted_fruits(
    db: AsyncSession, page: int, page_size: int
) -> FruitListResponse:
    return await fruit_repository.list_deleted_fruits(db, page=page, page_size=page_size)


async def update_fruit(
    db: AsyncSession, fruit_id: str, data: FruitUpdate
) -> FruitResponse:
    if data.preco_custo is not None:
        current = await fruit_repository.get_fruit(db, fruit_id)
        effective_preco = data.preco if data.preco is not None else current.preco
        if data.preco_custo >= effective_preco:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O preço de custo deve ser menor que o preço de venda.",
            )
    return await fruit_repository.update_fruit(db, fruit_id, data)


async def delete_fruit(db: AsyncSession, fruit_id: str) -> None:
    await fruit_repository.soft_delete_fruit(db, fruit_id)
    logger.info("fruit_soft_deleted", fruit_id=fruit_id)


async def restore_fruit(db: AsyncSession, fruit_id: str) -> FruitResponse:
    result = await fruit_repository.restore_fruit(db, fruit_id)
    logger.info("fruit_restored", fruit_id=fruit_id)
    return result
