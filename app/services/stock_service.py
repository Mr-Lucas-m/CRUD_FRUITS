import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InsufficientStockError
from app.repositories import fruit_repository, stock_repository
from app.schemas.stock import (
    StockEntradaRequest,
    StockMovementListResponse,
    StockMovementResponse,
    StockSaidaRequest,
    StockSaldoResponse,
)

logger = structlog.get_logger()


async def entrada(
    db: AsyncSession, fruit_id: str, data: StockEntradaRequest
) -> StockMovementResponse:
    fruit = await fruit_repository.get_fruit_model(db, fruit_id)
    movement = stock_repository.create_movement(
        db, fruit_id, "entrada", data.quantidade, data.motivo
    )
    fruit.quantidade_estoque += data.quantidade
    await db.commit()
    await db.refresh(movement)
    logger.info("stock_entrada", fruit_id=fruit_id, quantidade=data.quantidade)
    return StockMovementResponse.model_validate(movement)


async def saida(
    db: AsyncSession, fruit_id: str, data: StockSaidaRequest
) -> StockMovementResponse:
    fruit = await fruit_repository.get_fruit_model(db, fruit_id)
    if fruit.quantidade_estoque < data.quantidade:
        raise InsufficientStockError(fruit_id, data.quantidade, fruit.quantidade_estoque)
    movement = stock_repository.create_movement(
        db, fruit_id, "saida", data.quantidade, data.motivo
    )
    fruit.quantidade_estoque -= data.quantidade
    await db.commit()
    await db.refresh(movement)
    logger.info("stock_saida", fruit_id=fruit_id, quantidade=data.quantidade)
    return StockMovementResponse.model_validate(movement)


async def historico(
    db: AsyncSession, fruit_id: str, page: int, page_size: int
) -> StockMovementListResponse:
    await fruit_repository.get_fruit(db, fruit_id)
    return await stock_repository.list_movements(
        db, fruit_id, page=page, page_size=page_size
    )


async def saldo(db: AsyncSession, fruit_id: str) -> StockSaldoResponse:
    fruit = await fruit_repository.get_fruit(db, fruit_id)
    last_movement = await stock_repository.get_last_movement(db, fruit_id)
    return StockSaldoResponse(
        fruit_id=fruit_id,
        quantidade_estoque=fruit.quantidade_estoque,
        ultimo_movimento=(
            StockMovementResponse.model_validate(last_movement) if last_movement else None
        ),
    )
