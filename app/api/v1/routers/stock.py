from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import get_current_user
from app.schemas.stock import (
    StockEntradaRequest,
    StockMovementListResponse,
    StockMovementResponse,
    StockSaidaRequest,
    StockSaldoResponse,
)
from app.services import stock_service

router = APIRouter(
    prefix="/fruits",
    tags=["Estoque"],
    dependencies=[Depends(get_current_user)],
)


# ── POST /fruits/{id}/stock/entrada
@router.post(
    "/{fruit_id}/stock/entrada",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada de estoque",
)
@limiter.limit("30/minute")
def stock_entrada(
    request: Request,
    fruit_id: str,
    data: StockEntradaRequest,
    db: Session = Depends(get_db),
) -> StockMovementResponse:
    return stock_service.entrada(db, fruit_id, data)


# ── POST /fruits/{id}/stock/saida
@router.post(
    "/{fruit_id}/stock/saida",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar saída de estoque",
)
@limiter.limit("30/minute")
def stock_saida(
    request: Request,
    fruit_id: str,
    data: StockSaidaRequest,
    db: Session = Depends(get_db),
) -> StockMovementResponse:
    return stock_service.saida(db, fruit_id, data)


# ── GET /fruits/{id}/stock/historico
@router.get(
    "/{fruit_id}/stock/historico",
    response_model=StockMovementListResponse,
    summary="Histórico de movimentações de estoque",
)
def stock_historico(
    fruit_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> StockMovementListResponse:
    return stock_service.historico(db, fruit_id, page=page, page_size=page_size)


# ── GET /fruits/{id}/stock/saldo
@router.get(
    "/{fruit_id}/stock/saldo",
    response_model=StockSaldoResponse,
    summary="Saldo atual de estoque",
)
def stock_saldo(fruit_id: str, db: Session = Depends(get_db)) -> StockSaldoResponse:
    return stock_service.saldo(db, fruit_id)
