from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Base
class FruitBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["Manga"])
    preco: Decimal = Field(..., gt=0, decimal_places=2, examples=[["4.99"]])
    quantidade_estoque: int = Field(..., ge=0, examples=[50])

    @field_validator("nome")
    @classmethod
    def capitalize_nome(cls, v: str) -> str:
        return v.strip().title()


# ── Create
class FruitCreate(FruitBase):
    pass


# ── Update (PATCH campos opcionais) 
class FruitUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    preco: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    quantidade_estoque: int | None = Field(default=None, ge=0)

    @field_validator("nome")
    @classmethod
    def capitalize_nome(cls, v: str | None) -> str | None:
        return v.strip().title() if v else v


# ── Response
class FruitResponse(FruitBase):
    id: str
    data_cadastro: datetime
    data_atualizacao: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ── Lista paginada
class FruitListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FruitResponse]
