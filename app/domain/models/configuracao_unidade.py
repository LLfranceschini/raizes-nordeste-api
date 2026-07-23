from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class ConfiguracaoUnidade(Base):
    # Regras operacionais especificas de cada unidade (horarios, tipo de cozinha)
    __tablename__ = "configuracoes_unidade"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, unique=True)
    horario_abertura = Column(Time, nullable=True)
    horario_fechamento = Column(Time, nullable=True)
    tipo_cozinha = Column(String(20), nullable=False, default="COMPLETA")
    dias_funcionamento = Column(String(50), nullable=True)  # Ex: "SEG,TER,QUA,QUI,SEX,SAB"

    # Relacionamentos
    unidade = relationship("Unidade", back_populates="configuracao")
