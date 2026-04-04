import structlog
from sqlalchemy.orm import Session

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


def entrada(db: Session, fruit_id: str, data: StockEntradaRequest) -> StockMovementResponse:
    fruit = fruit_repository.get_fruit_model(db, fruit_id)
    movement = stock_repository.create_movement(db, fruit_id, "entrada", data.quantidade, data.motivo)
    fruit.quantidade_estoque += data.quantidade
    db.commit()
    db.refresh(movement)
    logger.info("stock_entrada", fruit_id=fruit_id, quantidade=data.quantidade)
    return StockMovementResponse.model_validate(movement)


def saida(db: Session, fruit_id: str, data: StockSaidaRequest) -> StockMovementResponse:
    fruit = fruit_repository.get_fruit_model(db, fruit_id)
    if fruit.quantidade_estoque < data.quantidade:
        raise InsufficientStockError(fruit_id, data.quantidade, fruit.quantidade_estoque)
    movement = stock_repository.create_movement(db, fruit_id, "saida", data.quantidade, data.motivo)
    fruit.quantidade_estoque -= data.quantidade
    db.commit()
    db.refresh(movement)
    logger.info("stock_saida", fruit_id=fruit_id, quantidade=data.quantidade)
    return StockMovementResponse.model_validate(movement)


def historico(
    db: Session, fruit_id: str, page: int, page_size: int
) -> StockMovementListResponse:
    fruit_repository.get_fruit(db, fruit_id)
    return stock_repository.list_movements(db, fruit_id, page=page, page_size=page_size)


def saldo(db: Session, fruit_id: str) -> StockSaldoResponse:
    fruit = fruit_repository.get_fruit(db, fruit_id)
    last_movement = stock_repository.get_last_movement(db, fruit_id)
    return StockSaldoResponse(
        fruit_id=fruit_id,
        quantidade_estoque=fruit.quantidade_estoque,
        ultimo_movimento=(
            StockMovementResponse.model_validate(last_movement) if last_movement else None
        ),
    )
