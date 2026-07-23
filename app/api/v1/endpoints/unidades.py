from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.schemas.unidade_schema import UnidadeCreate, UnidadeResponse
from app.api.dependencies import get_current_user, require_perfil
from app.domain.models.unidade import Unidade
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=list[UnidadeResponse], summary="Listar unidades ativas")
def listar_unidades(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return db.query(Unidade).filter(Unidade.ativa == True).offset(skip).limit(limit).all()

@router.get("/{unidade_id}", response_model=UnidadeResponse, summary="Buscar unidade")
def buscar_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    unidade = db.query(Unidade).filter(Unidade.id == unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade nao encontrada.")
    return unidade

@router.post("/", response_model=UnidadeResponse, status_code=201, summary="Criar unidade (admin)")
def criar_unidade(
    dados: UnidadeCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN"))
):
    unidade = Unidade(**dados.model_dump())
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade
