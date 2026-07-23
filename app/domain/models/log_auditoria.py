from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class LogAuditoria(Base):
    # Rastreia acoes sensiveis: criacao/cancelamento de pedido, mudanca de status,
    # descontos aplicados, alteracoes de estoque. Essencial para compliance e auditoria
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String(100), nullable=False)       # Ex: PEDIDO_CRIADO, STATUS_ATUALIZADO
    entidade = Column(String(50), nullable=False)    # Ex: pedido, estoque, usuario
    entidade_id = Column(Integer, nullable=True)
    dados_anteriores = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    ip_origem = Column(String(45), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="logs")
