from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class CardapioUnidade(Base):
    # Controla quais produtos cada unidade oferece e permite preco diferenciado
    # Se preco_especifico for None, usa o preco_base do produto
    __tablename__ = "cardapio_unidade"
    __table_args__ = (
        UniqueConstraint("unidade_id", "produto_id", name="uq_cardapio_unidade_produto"),
    )

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    preco_especifico = Column(Float, nullable=True)
    disponivel = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    unidade = relationship("Unidade", back_populates="cardapios")
    produto = relationship("Produto", back_populates="cardapios")
