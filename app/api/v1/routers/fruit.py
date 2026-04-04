from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import get_current_user
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate
from app.services import fruit_service

router = APIRouter(prefix="/fruits", tags=["Frutas"])


# ── GET /fruits/deleted — DEVE VIR ANTES de /{fruit_id}
@router.get(
    "/deleted",
    response_model=FruitListResponse,
    summary="Listar frutas removidas (controle interno)",
    dependencies=[Depends(get_current_user)],
)
def list_deleted(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> FruitListResponse:
    return fruit_service.list_deleted_fruits(db, page=page, page_size=page_size)


# ── POST /fruits
@router.post(
    "/",
    response_model=FruitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar fruta",
)
@limiter.limit("30/minute")
def create(
    request: Request,
    data: FruitCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FruitResponse:
    return fruit_service.create_fruit(db, data)


# ── GET /fruits
@router.get(
    "/",
    response_model=FruitListResponse,
    summary="Listar frutas (paginado)",
)
def list_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    nome: str | None = Query(default=None, description="Filtro parcial por nome"),
    db: Session = Depends(get_db),
) -> FruitListResponse:
    return fruit_service.list_fruits(db, page=page, page_size=page_size, nome_filtro=nome)


# ── GET /fruits/{id}
@router.get(
    "/{fruit_id}",
    response_model=FruitResponse,
    summary="Buscar fruta por ID",
)
def get_one(fruit_id: str, db: Session = Depends(get_db)) -> FruitResponse:
    return fruit_service.get_fruit(db, fruit_id)


# ── PATCH /fruits/{id}
@router.patch(
    "/{fruit_id}",
    response_model=FruitResponse,
    summary="Atualizar fruta (parcial)",
)
@limiter.limit("30/minute")
def update(
    request: Request,
    fruit_id: str,
    data: FruitUpdate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> FruitResponse:
    return fruit_service.update_fruit(db, fruit_id, data)


# ── DELETE /fruits/{id}
@router.delete(
    "/{fruit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover fruta (soft delete)",
)
@limiter.limit("30/minute")
def delete(
    request: Request,
    fruit_id: str,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> None:
    fruit_service.delete_fruit(db, fruit_id)


# ── POST /fruits/{id}/restore
@router.post(
    "/{fruit_id}/restore",
    response_model=FruitResponse,
    summary="Restaurar fruta removida",
    dependencies=[Depends(get_current_user)],
)
@limiter.limit("30/minute")
def restore(
    request: Request,
    fruit_id: str,
    db: Session = Depends(get_db),
) -> FruitResponse:
    return fruit_service.restore_fruit(db, fruit_id)
