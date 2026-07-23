from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Usuario(Base):
    # Centraliza todos os perfis: CLIENTE, ATENDENTE, COZINHA, GERENTE, ADMIN
    # unidade_id e nulo para clientes; obrigatorio para funcionarios
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), nullable=False)
    telefone = Column(String(20), nullable=True)
    cpf = Column(String(11), unique=True, nullable=True, index=True)
    data_nascimento = Column(Date, nullable=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    unidade = relationship("Unidade", back_populates="usuarios")
    refresh_tokens = relationship("RefreshToken", back_populates="usuario")
    fidelidade = relationship("Fidelidade", back_populates="cliente", uselist=False)
    consentimentos = relationship("ConsentimentoLGPD", back_populates="usuario")
    logs = relationship("LogAuditoria", back_populates="usuario")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="usuario")
    # Pedidos onde este usuario e o cliente
    pedidos_como_cliente = relationship(
        "Pedido", foreign_keys="[Pedido.cliente_id]", back_populates="cliente"
    )
    # Pedidos onde este usuario e o atendente (canal BALCAO)
    pedidos_como_atendente = relationship(
        "Pedido", foreign_keys="[Pedido.atendente_id]", back_populates="atendente"
    )
