from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict
from datetime import datetime


class PagamentoMockRequest(BaseModel):
    """Solicitacao de pagamento enviada ao gateway mock."""
    pedido_id: int
    forma_pagamento: str
    valor: float = Field(..., gt=0)


class PagamentoCallbackRequest(BaseModel):
    """Retorno do gateway mock apos processar o pagamento.
    status: APROVADO ou RECUSADO
    """
    ref_externa: str
    status: str = Field(..., description="APROVADO ou RECUSADO")
    payload: Optional[Dict[str, Any]] = None


class PagamentoResponse(BaseModel):
    """Resposta do registro de pagamento."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int
    forma_pagamento: str
    status: str
    valor: float
    ref_externa: Optional[str] = None
    tentativas: int
    data_expiracao: Optional[datetime] = None
    data_hora: datetime
