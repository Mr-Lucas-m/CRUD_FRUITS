from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate
from app.repositories import fruit_repository

router = APIRouter(prefix="/fruits", tags=["Frutas"])


# ── POST /fruits
@router.post(
    "/",
    response_model=FruitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar fruta",
)
def create(data: FruitCreate, db: Session = Depends(get_db)) -> FruitResponse:
    """Cadastra uma nova fruta. O nome é único e obrigatório."""
    return fruit_repository.create_fruit(db, data)


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
    """Retorna lista paginada de frutas, com filtro opcional por nome."""
    return fruit_repository.list_fruits(db, page=page, page_size=page_size, nome_filtro=nome)


# ── GET /fruits/{id}
@router.get(
    "/{fruit_id}",
    response_model=FruitResponse,
    summary="Buscar fruta por ID",
)
def get_one(fruit_id: str, db: Session = Depends(get_db)) -> FruitResponse:
    return fruit_repository.get_fruit(db, fruit_id)


# ── PATCH /fruits/{id}
@router.patch(
    "/{fruit_id}",
    response_model=FruitResponse,
    summary="Atualizar fruta (parcial)",
)
def update(fruit_id: str, data: FruitUpdate, db: Session = Depends(get_db)) -> FruitResponse:
    """Atualiza apenas os campos enviados no body."""
    return fruit_repository.update_fruit(db, fruit_id, data)


# ── DELETE /fruits/{id}
@router.delete(
    "/{fruit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover fruta",
)
def delete(fruit_id: str, db: Session = Depends(get_db)) -> None:
    fruit_repository.delete_fruit(db, fruit_id)
