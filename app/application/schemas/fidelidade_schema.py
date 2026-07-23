from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class FidelidadeResponse(BaseModel):
    """Saldo de pontos do cliente."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    pontos_acumulados: int
    pontos_resgatados: int
    pontos_disponiveis: int
    nivel: str


class HistoricoFidelidadeResponse(BaseModel):
    """Registro de acumulo ou resgate de pontos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    pontos: int
    descricao: Optional[str] = None
    pedido_id: Optional[int] = None
    data_hora: datetime


class ResgateRequest(BaseModel):
    """Solicitacao de resgate de pontos."""
    pontos: int = Field(..., gt=0, description="Quantidade de pontos a resgatar")


class ConsentimentoCreate(BaseModel):
    """Registro de consentimento LGPD do usuario."""
    tipo_consentimento: str = Field(
        ...,
        description="Ex: MARKETING, FIDELIZACAO, DADOS_SENSIVEIS, COMPARTILHAMENTO"
    )
    consentiu: bool
