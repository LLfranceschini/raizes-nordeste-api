from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class ConsentimentoLGPD(Base):
    # Registra o consentimento explicito do usuario para cada finalidade de uso de dados
    # tipo_consentimento: MARKETING, FIDELIZACAO, DADOS_SENSIVEIS, COMPARTILHAMENTO
    __tablename__ = "consentimentos_lgpd"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_consentimento = Column(String(50), nullable=False)
    consentiu = Column(Boolean, nullable=False)
    ip_origem = Column(String(45), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="consentimentos")
