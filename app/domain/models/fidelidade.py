from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Fidelidade(Base):
    # Programa de pontos do cliente. nivel: BRONZE, PRATA, OURO
    # pontos_disponiveis = pontos_acumulados - pontos_resgatados
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)
    pontos_acumulados = Column(Integer, default=0, nullable=False)
    pontos_resgatados = Column(Integer, default=0, nullable=False)
    pontos_disponiveis = Column(Integer, default=0, nullable=False)
    nivel = Column(String(20), default="BRONZE", nullable=False)
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)

    # Relacionamentos
    cliente = relationship("Usuario", back_populates="fidelidade")
    historico = relationship("HistoricoFidelidade", back_populates="fidelidade")
