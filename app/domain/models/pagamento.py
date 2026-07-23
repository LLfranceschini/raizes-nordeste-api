from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Pagamento(Base):
    # Pagamento desacoplado: o sistema apenas registra o retorno do gateway externo (mock)
    # forma_pagamento: PIX, CARTAO_CREDITO, CARTAO_DEBITO, DINHEIRO, MOCK
    # status: PENDENTE, APROVADO, RECUSADO, EXPIRADO
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False,
                       unique=True, index=True)
    forma_pagamento = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default="PENDENTE")
    valor = Column(Float, nullable=False)
    ref_externa = Column(String(100), nullable=True)
    payload_retorno = Column(JSON, nullable=True)   # Resposta completa do gateway mock
    tentativas = Column(Integer, default=0, nullable=False)
    data_expiracao = Column(DateTime(timezone=True), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="pagamento")
