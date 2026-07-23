from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Literal
from datetime import date, datetime


TipoDesconto = Literal["PERCENTUAL", "FIXO"]


class PromocaoCreate(BaseModel):
    """Dados para criar uma campanha de desconto."""
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    tipo_desconto: TipoDesconto
    valor_desconto: float = Field(..., gt=0)
    codigo_cupom: Optional[str] = Field(None, max_length=50)
    data_inicio: date
    data_fim: date
    unidades_ids: Optional[list[int]] = Field(
        None, description="IDs das unidades participantes. Nulo = todas"
    )

    @model_validator(mode="after")
    def validar_datas(self):
        if self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser posterior a data_inicio")
        if self.tipo_desconto == "PERCENTUAL" and self.valor_desconto > 100:
            raise ValueError("Desconto percentual nao pode ser maior que 100")
        return self


class PromocaoUpdate(BaseModel):
    """Campos atualizaveis de uma promocao."""
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)
    valor_desconto: Optional[float] = Field(None, gt=0)
    data_fim: Optional[date] = None
    ativa: Optional[bool] = None


class PromocaoResponse(BaseModel):
    """Resposta completa de uma promocao."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: Optional[str] = None
    tipo_desconto: str
    valor_desconto: float
    codigo_cupom: Optional[str] = None
    data_inicio: date
    data_fim: date
    ativa: bool
