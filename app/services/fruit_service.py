import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories import fruit_repository
from app.schemas.fruit import FruitCreate, FruitListResponse, FruitResponse, FruitUpdate

logger = structlog.get_logger()


def create_fruit(db: Session, data: FruitCreate) -> FruitResponse:
    if data.preco_custo is not None and data.preco_custo >= data.preco:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O preço de custo deve ser menor que o preço de venda.",
        )
    result = fruit_repository.create_fruit(db, data)
    logger.info("fruit_created", fruit_id=result.id, nome=result.nome)
    return result


def get_fruit(db: Session, fruit_id: str) -> FruitResponse:
    return fruit_repository.get_fruit(db, fruit_id)


def list_fruits(
    db: Session, page: int, page_size: int, nome_filtro: str | None
) -> FruitListResponse:
    return fruit_repository.list_fruits(db, page=page, page_size=page_size, nome_filtro=nome_filtro)


def list_deleted_fruits(db: Session, page: int, page_size: int) -> FruitListResponse:
    return fruit_repository.list_deleted_fruits(db, page=page, page_size=page_size)


def update_fruit(db: Session, fruit_id: str, data: FruitUpdate) -> FruitResponse:
    if data.preco_custo is not None:
        current = fruit_repository.get_fruit(db, fruit_id)
        effective_preco = data.preco if data.preco is not None else current.preco
        if data.preco_custo >= effective_preco:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O preço de custo deve ser menor que o preço de venda.",
            )
    return fruit_repository.update_fruit(db, fruit_id, data)


def delete_fruit(db: Session, fruit_id: str) -> None:
    fruit_repository.soft_delete_fruit(db, fruit_id)
    logger.info("fruit_soft_deleted", fruit_id=fruit_id)


def restore_fruit(db: Session, fruit_id: str) -> FruitResponse:
    result = fruit_repository.restore_fruit(db, fruit_id)
    logger.info("fruit_restored", fruit_id=fruit_id)
    return result
