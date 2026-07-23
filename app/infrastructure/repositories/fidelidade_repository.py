from sqlalchemy.orm import Session
from app.domain.models.fidelidade import Fidelidade
from app.domain.models.historico_fidelidade import HistoricoFidelidade


def buscar_por_cliente(db: Session, cliente_id: int):
    return db.query(Fidelidade).filter(Fidelidade.cliente_id == cliente_id).first()


def criar_ou_buscar(db: Session, cliente_id: int) -> Fidelidade:
    fidelidade = buscar_por_cliente(db, cliente_id)
    if not fidelidade:
        fidelidade = Fidelidade(cliente_id=cliente_id)
        db.add(fidelidade)
        db.commit()
        db.refresh(fidelidade)
    return fidelidade


def registrar_historico(
    db: Session, fidelidade_id: int, tipo: str,
    pontos: int, descricao: str, pedido_id: int = None
) -> HistoricoFidelidade:
    hist = HistoricoFidelidade(
        fidelidade_id=fidelidade_id,
        pedido_id=pedido_id,
        tipo=tipo,
        pontos=pontos,
        descricao=descricao,
    )
    db.add(hist)
    db.commit()
    db.refresh(hist)
    return hist


def atualizar(db: Session, fidelidade: Fidelidade) -> Fidelidade:
    db.commit()
    db.refresh(fidelidade)
    return fidelidade
