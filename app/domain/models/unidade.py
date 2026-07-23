from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Unidade(Base):
    # Representa cada lanchonete da rede. tipo: COMPLETA ou REDUZIDA
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    logradouro = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String(8), nullable=False)
    telefone = Column(String(20), nullable=True)
    tipo = Column(String(20), nullable=False, default="COMPLETA")
    ativa = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    usuarios = relationship("Usuario", back_populates="unidade")
    configuracao = relationship("ConfiguracaoUnidade", back_populates="unidade", uselist=False)
    cardapios = relationship("CardapioUnidade", back_populates="unidade")
    estoques = relationship("Estoque", back_populates="unidade")
    pedidos = relationship("Pedido", back_populates="unidade")
    promocoes_unidade = relationship("PromocaoUnidade", back_populates="unidade")
