from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Estoque(Base):
    # Saldo de cada produto em cada unidade. qtd_minima dispara alerta de reposicao
    __tablename__ = "estoque"
    __table_args__ = (
        UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),
    )

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    quantidade = Column(Integer, default=0, nullable=False)
    qtd_minima = Column(Integer, default=0, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)

    # Relacionamentos
    unidade = relationship("Unidade", back_populates="estoques")
    produto = relationship("Produto", back_populates="estoques")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="estoque")
