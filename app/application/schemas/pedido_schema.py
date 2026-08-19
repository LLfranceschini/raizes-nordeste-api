from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Literal
from datetime import datetime


CanalPedido = Literal["APP", "TOTEM", "BALCAO", "PICKUP", "WEB"]
StatusPedido = Literal[
    "AGUARDANDO_PAGAMENTO", "PAGO", "EM_PREPARO",
    "PRONTO", "ENTREGUE", "CANCELADO"
]
FormaPagamento = Literal["PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "DINHEIRO", "MOCK", "FORCAR_RECUSA"]


class ItemPedidoCreate(BaseModel):
    """Item dentro de um pedido."""
    produto_id: int
    quantidade: int = Field(..., gt=0)


class ItemPedidoResponse(BaseModel):
    """Resposta de um item do pedido com preco registrado no momento da compra."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    subtotal: float


class PedidoCreate(BaseModel):
    """Dados para criacao de um novo pedido."""
    unidade_id: int
    canal_pedido: CanalPedido = Field(
        ..., description="Canal de origem: APP, TOTEM, BALCAO, PICKUP ou WEB"
    )
    itens: List[ItemPedidoCreate] = Field(..., min_length=1)
    forma_pagamento: FormaPagamento
    codigo_cupom: Optional[str] = Field(
        None, description="Codigo de cupom de promocao (opcional)"
    )


class PedidoStatusUpdate(BaseModel):
    """Atualizacao de status pelo fluxo da cozinha/entrega."""
    status: StatusPedido
    motivo_cancelamento: Optional[str] = Field(
        None, description="Obrigatorio quando status=CANCELADO"
    )


class PedidoResponse(BaseModel):
    """Resposta completa de um pedido."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    unidade_id: int
    atendente_id: Optional[int] = None
    canal_pedido: str
    status: str
    subtotal: float
    desconto: float
    total: float
    motivo_cancelamento: Optional[str] = None
    itens: List[ItemPedidoResponse] = []
    data_hora: datetime
    data_atualizacao: datetime


class PedidoMiniResponse(BaseModel):
    """Versao reduzida para listagens."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    canal_pedido: str
    status: str
    total: float
    data_hora: datetime
