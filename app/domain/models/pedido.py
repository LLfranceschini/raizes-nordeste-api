from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base


class Pedido(Base):
    # Nucleo do sistema. canal_pedido: APP, TOTEM, BALCAO, PICKUP, WEB (obrigatorio)
    # status: AGUARDANDO_PAGAMENTO > PAGO > EM_PREPARO > PRONTO > ENTREGUE / CANCELADO
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False, index=True)
    atendente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    cancelado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    canal_pedido = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, default="AGUARDANDO_PAGAMENTO")
    subtotal = Column(Float, nullable=False, default=0.0)
    desconto = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    motivo_cancelamento = Column(String(255), nullable=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(),
                              onupdate=func.now(), nullable=False)

    # Relacionamentos - multiplas FK para usuarios requerem foreign_keys explicito
    cliente = relationship("Usuario", foreign_keys=[cliente_id],
                           back_populates="pedidos_como_cliente")
    atendente = relationship("Usuario", foreign_keys=[atendente_id],
                             back_populates="pedidos_como_atendente")
    cancelador = relationship("Usuario", foreign_keys=[cancelado_por])
    unidade = relationship("Unidade", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)
    historico_fidelidade = relationship("HistoricoFidelidade", back_populates="pedido")
    promocoes_aplicadas = relationship("PedidoPromocao", back_populates="pedido")
