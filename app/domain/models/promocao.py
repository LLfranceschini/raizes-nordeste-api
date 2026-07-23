from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class Promocao(Base):
    # Campanhas e cupons de desconto. tipo_desconto: PERCENTUAL ou FIXO
    __tablename__ = "promocoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    tipo_desconto = Column(String(20), nullable=False)
    valor_desconto = Column(Float, nullable=False)
    codigo_cupom = Column(String(50), nullable=True, unique=True, index=True)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    unidades = relationship("PromocaoUnidade", back_populates="promocao")
    pedidos_promocao = relationship("PedidoPromocao", back_populates="promocao")
