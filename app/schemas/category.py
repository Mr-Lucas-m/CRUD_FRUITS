from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=80, examples=["Tropical"])
    descricao: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=80)
    descricao: str | None = None


class CategoryResponse(CategoryBase):
    id: str
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CategoryResponse]
