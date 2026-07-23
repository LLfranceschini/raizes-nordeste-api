from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.infrastructure.repositories.fidelidade_repository import (
    criar_ou_buscar, registrar_historico, atualizar
)


def obter_saldo(db: Session, cliente_id: int):
    return criar_ou_buscar(db, cliente_id)


def resgatar_pontos(db: Session, cliente_id: int, pontos: int):
    fidelidade = criar_ou_buscar(db, cliente_id)
    if fidelidade.pontos_disponiveis < pontos:
        raise HTTPException(status_code=409,
            detail=f"Pontos insuficientes. Disponivel: {fidelidade.pontos_disponiveis}")
    fidelidade.pontos_resgatados += pontos
    fidelidade.pontos_disponiveis -= pontos
    atualizar(db, fidelidade)
    registrar_historico(db, fidelidade.id, "RESGATE", pontos,
                        f"Resgate de {pontos} pontos")
    return fidelidade


def listar_historico(db: Session, cliente_id: int, skip: int = 0, limit: int = 20):
    fidelidade = criar_ou_buscar(db, cliente_id)
    from app.domain.models.historico_fidelidade import HistoricoFidelidade
    return db.query(HistoricoFidelidade).filter(
        HistoricoFidelidade.fidelidade_id == fidelidade.id
    ).order_by(HistoricoFidelidade.data_hora.desc()).offset(skip).limit(limit).all()
