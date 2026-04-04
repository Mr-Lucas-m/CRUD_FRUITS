from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import get_current_user
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.schemas.fruit import FruitListResponse
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["Categorias"], dependencies=[Depends(get_current_user)])


# ── POST /categories
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
)
@limiter.limit("30/minute")
def create(request: Request, data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    return category_service.create_category(db, data)


# ── GET /categories
@router.get(
    "/",
    response_model=CategoryListResponse,
    summary="Listar categorias (paginado)",
)
def list_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> CategoryListResponse:
    return category_service.list_categories(db, page=page, page_size=page_size)


# ── GET /categories/{id}
@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Buscar categoria por ID",
)
def get_one(category_id: str, db: Session = Depends(get_db)) -> CategoryResponse:
    return category_service.get_category(db, category_id)


# ── PATCH /categories/{id}
@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Atualizar categoria (parcial)",
)
@limiter.limit("30/minute")
def update(
    request: Request,
    category_id: str,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
) -> CategoryResponse:
    return category_service.update_category(db, category_id, data)


# ── DELETE /categories/{id}
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover categoria",
)
@limiter.limit("30/minute")
def delete(request: Request, category_id: str, db: Session = Depends(get_db)) -> None:
    category_service.delete_category(db, category_id)


# ── GET /categories/{id}/fruits
@router.get(
    "/{category_id}/fruits",
    response_model=FruitListResponse,
    summary="Listar frutas de uma categoria",
)
def list_fruits(
    category_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> FruitListResponse:
    return category_service.list_category_fruits(db, category_id, page=page, page_size=page_size)
