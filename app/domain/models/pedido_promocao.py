from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class PedidoPromocao(Base):
    # Rastreia qual promocao foi aplicada em cada pedido e o valor do desconto efetivo
    __tablename__ = "pedido_promocao"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    promocao_id = Column(Integer, ForeignKey("promocoes.id"), nullable=False, index=True)
    valor_desconto_aplicado = Column(Float, nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="promocoes_aplicadas")
    promocao = relationship("Promocao", back_populates="pedidos_promocao")
