from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime


TipoMovimentacao = Literal["ENTRADA", "SAIDA", "AJUSTE"]


class EstoqueResponse(BaseModel):
    """Saldo de um produto em uma unidade."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    unidade_id: int
    produto_id: int
    quantidade: int
    qtd_minima: int
    atualizado_em: datetime
    em_alerta: bool = False


class MovimentacaoCreate(BaseModel):
    """Registra entrada, saida ou ajuste de estoque."""
    tipo: TipoMovimentacao
    quantidade: int = Field(..., gt=0, description="Quantidade deve ser positiva")
    motivo: Optional[str] = Field(None, max_length=255)


class MovimentacaoResponse(BaseModel):
    """Resposta de uma movimentacao de estoque."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    estoque_id: int
    tipo: str
    quantidade: int
    motivo: Optional[str] = None
    data_hora: datetime
