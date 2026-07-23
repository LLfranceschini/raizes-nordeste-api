from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.schemas.fidelidade_schema import (
    FidelidadeResponse, HistoricoFidelidadeResponse, ResgateRequest
)
from app.application.services.fidelidade_service import (
    obter_saldo, resgatar_pontos, listar_historico
)
from app.api.dependencies import get_current_user
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=FidelidadeResponse, summary="Consultar saldo de pontos")
def meu_saldo(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return obter_saldo(db, current_user.id)

@router.post("/resgatar", response_model=FidelidadeResponse, summary="Resgatar pontos")
def resgatar(
    dados: ResgateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return resgatar_pontos(db, current_user.id, dados.pontos)

@router.get("/historico", response_model=list[HistoricoFidelidadeResponse],
            summary="Historico de pontos")
def historico(
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return listar_historico(db, current_user.id, skip=skip, limit=limit)
