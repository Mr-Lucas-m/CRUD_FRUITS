from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StockEntradaRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    motivo: str | None = None


class StockSaidaRequest(BaseModel):
    quantidade: int = Field(..., gt=0)
    motivo: str | None = None


class StockMovementResponse(BaseModel):
    id: str
    fruit_id: str
    tipo: str
    quantidade: int
    motivo: str | None
    data_movimento: datetime

    model_config = ConfigDict(from_attributes=True)


class StockMovementListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[StockMovementResponse]


class StockSaldoResponse(BaseModel):
    fruit_id: str
    quantidade_estoque: int
    ultimo_movimento: StockMovementResponse | None
