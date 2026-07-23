from sqlalchemy.orm import Session
from app.domain.models.pagamento import Pagamento


def criar(db: Session, pagamento: Pagamento) -> Pagamento:
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def buscar_por_pedido_id(db: Session, pedido_id: int):
    return db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido_id
    ).first()


def atualizar(db: Session, pagamento: Pagamento) -> Pagamento:
    db.commit()
    db.refresh(pagamento)
    return pagamento
