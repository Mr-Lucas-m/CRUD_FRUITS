from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock_movement import StockMovement
from app.schemas.stock import StockMovementListResponse, StockMovementResponse


def create_movement(
    db: AsyncSession,
    fruit_id: str,
    tipo: str,
    quantidade: int,
    motivo: str | None,
) -> StockMovement:
    """Cria o objeto de movimento e adiciona à sessão sem commitar."""
    movement = StockMovement(
        fruit_id=fruit_id,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo,
    )
    db.add(movement)
    return movement


async def list_movements(
    db: AsyncSession,
    fruit_id: str,
    page: int,
    page_size: int,
) -> StockMovementListResponse:
    query = select(StockMovement).where(StockMovement.fruit_id == fruit_id)
    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    result = await db.scalars(
        query.order_by(StockMovement.data_movimento.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    movements = result.all()
    return StockMovementListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[StockMovementResponse.model_validate(m) for m in movements],
    )


async def get_last_movement(db: AsyncSession, fruit_id: str) -> StockMovement | None:
    return await db.scalar(
        select(StockMovement)
        .where(StockMovement.fruit_id == fruit_id)
        .order_by(StockMovement.data_movimento.desc())
        .limit(1)
    )
