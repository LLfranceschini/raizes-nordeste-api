from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.infrastructure.database.connection import get_db
from app.application.schemas.promocao_schema import PromocaoCreate, PromocaoResponse
from app.api.dependencies import get_current_user, require_perfil
from app.domain.models.promocao import Promocao
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.get("/", response_model=list[PromocaoResponse], summary="Listar promocoes ativas")
def listar_promocoes(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    hoje = date.today()
    return db.query(Promocao).filter(
        Promocao.ativa == True,
        Promocao.data_inicio <= hoje,
        Promocao.data_fim >= hoje,
    ).all()

@router.get("/{promocao_id}", response_model=PromocaoResponse, summary="Buscar promocao")
def buscar_promocao(
    promocao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    promocao = db.query(Promocao).filter(Promocao.id == promocao_id).first()
    if not promocao:
        raise HTTPException(status_code=404, detail="Promocao nao encontrada.")
    return promocao

@router.post("/", response_model=PromocaoResponse, status_code=201,
             summary="Criar promocao (admin)")
def criar_promocao(
    dados: PromocaoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE"))
):
    promocao = Promocao(
        nome=dados.nome, descricao=dados.descricao,
        tipo_desconto=dados.tipo_desconto, valor_desconto=dados.valor_desconto,
        codigo_cupom=dados.codigo_cupom,
        data_inicio=dados.data_inicio, data_fim=dados.data_fim,
    )
    db.add(promocao)
    db.commit()
    db.refresh(promocao)
    return promocao
