from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.domain.models.pedido import Pedido
from app.domain.models.item_pedido import ItemPedido


def criar(db: Session, pedido: Pedido) -> Pedido:
    db.add(pedido)
    db.flush()
    return pedido


def adicionar_item(db: Session, item: ItemPedido) -> ItemPedido:
    db.add(item)
    return item


def confirmar(db: Session, pedido: Pedido) -> Pedido:
    db.commit()
    db.refresh(pedido)
    return pedido


def buscar_por_id(db: Session, pedido_id: int):
    return db.query(Pedido).options(
        joinedload(Pedido.itens)
    ).filter(Pedido.id == pedido_id).first()


def listar_por_cliente(
    db: Session, cliente_id: int,
    skip: int = 0, limit: int = 20,
    canal: Optional[str] = None, status: Optional[str] = None
):
    query = db.query(Pedido).filter(Pedido.cliente_id == cliente_id)
    if canal:
        query = query.filter(Pedido.canal_pedido == canal)
    if status:
        query = query.filter(Pedido.status == status)
    return query.order_by(Pedido.data_hora.desc()).offset(skip).limit(limit).all()


def listar_por_unidade(
    db: Session, unidade_id: int,
    skip: int = 0, limit: int = 50,
    canal: Optional[str] = None, status: Optional[str] = None
):
    query = db.query(Pedido).filter(Pedido.unidade_id == unidade_id)
    if canal:
        query = query.filter(Pedido.canal_pedido == canal)
    if status:
        query = query.filter(Pedido.status == status)
    return query.order_by(Pedido.data_hora.desc()).offset(skip).limit(limit).all()


def atualizar(db: Session, pedido: Pedido) -> Pedido:
    db.commit()
    db.refresh(pedido)
    return pedido
