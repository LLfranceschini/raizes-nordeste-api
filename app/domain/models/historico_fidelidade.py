from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class HistoricoFidelidade(Base):
    # Cada linha representa uma operacao de pontos: ACUMULO ou RESGATE
    # pedido_id pode ser None em casos de ajuste manual de pontos
    __tablename__ = "historico_fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    fidelidade_id = Column(Integer, ForeignKey("fidelidade.id"), nullable=False, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=True, index=True)
    tipo = Column(String(20), nullable=False)       # ACUMULO ou RESGATE
    pontos = Column(Integer, nullable=False)
    descricao = Column(String(255), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    fidelidade = relationship("Fidelidade", back_populates="historico")
    pedido = relationship("Pedido", back_populates="historico_fidelidade")
