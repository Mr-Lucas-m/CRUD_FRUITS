from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UnidadeMedida(str, Enum):
    kg = "kg"
    unidade = "unidade"
    caixa = "caixa"
    duzia = "duzia"


# ── Base
class FruitBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["Manga"])
    preco: Decimal = Field(..., gt=0, decimal_places=2, examples=["4.99"])
    quantidade_estoque: int = Field(..., ge=0, examples=[50])
    category_id: str | None = None
    unidade_medida: UnidadeMedida = UnidadeMedida.unidade
    estoque_minimo: int = Field(default=0, ge=0)
    preco_custo: Decimal | None = Field(default=None, gt=0, decimal_places=2)

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
    category_id: str | None = None
    unidade_medida: UnidadeMedida | None = None
    estoque_minimo: int | None = Field(default=None, ge=0)
    preco_custo: Decimal | None = Field(default=None, gt=0, decimal_places=2)

    @field_validator("nome")
    @classmethod
    def capitalize_nome(cls, v: str | None) -> str | None:
        return v.strip().title() if v else v


# ── Response
class FruitResponse(FruitBase):
    id: str
    data_cadastro: datetime
    data_atualizacao: datetime | None = None
    deleted_at: datetime | None = None
    estoque_baixo: bool = False

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def compute_estoque_baixo(self) -> "FruitResponse":
        self.estoque_baixo = self.quantidade_estoque <= self.estoque_minimo
        return self


# ── Lista paginada
class FruitListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FruitResponse]
