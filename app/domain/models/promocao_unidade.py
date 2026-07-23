from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class PromocaoUnidade(Base):
    # Vincula promocoes a unidades especificas da rede
    __tablename__ = "promocao_unidade"
    __table_args__ = (
        UniqueConstraint("promocao_id", "unidade_id", name="uq_promocao_unidade"),
    )

    id = Column(Integer, primary_key=True, index=True)
    promocao_id = Column(Integer, ForeignKey("promocoes.id"), nullable=False, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, index=True)

    # Relacionamentos
    promocao = relationship("Promocao", back_populates="unidades")
    unidade = relationship("Unidade", back_populates="promocoes_unidade")
