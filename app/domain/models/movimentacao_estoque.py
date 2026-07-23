from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class MovimentacaoEstoque(Base):
    # Registra cada entrada e saida de estoque para rastreabilidade completa
    # tipo: ENTRADA, SAIDA, AJUSTE, RESERVA (ao criar pedido), LIBERACAO (ao cancelar)
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)
    estoque_id = Column(Integer, ForeignKey("estoque.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    tipo = Column(String(20), nullable=False)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String(255), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    estoque = relationship("Estoque", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")
