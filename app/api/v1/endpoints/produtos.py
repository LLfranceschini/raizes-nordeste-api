from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.schemas.produto_schema import (
    ProdutoCreate, ProdutoResponse, CardapioItemResponse, CardapioUnidadeCreate
)
from app.infrastructure.repositories import produto_repository
from app.api.dependencies import get_current_user, require_perfil
from app.domain.models.usuario import Usuario
from app.domain.models.cardapio_unidade import CardapioUnidade
from app.domain.models.produto import Produto

router = APIRouter()

@router.get("/", response_model=list[ProdutoResponse], summary="Listar produtos")
def listar_produtos(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    return produto_repository.listar_ativos(db, skip=skip, limit=limit)

@router.get("/{produto_id}", response_model=ProdutoResponse, summary="Buscar produto")
def buscar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    produto = produto_repository.buscar_por_id(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado.")
    return produto

@router.post("/", response_model=ProdutoResponse, status_code=201, summary="Criar produto (admin)")
def criar_produto(
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE"))
):
    produto = Produto(**dados.model_dump())
    return produto_repository.criar(db, produto)

@router.get("/unidade/{unidade_id}/cardapio",
            response_model=list[CardapioItemResponse],
            summary="Cardapio de uma unidade")
def cardapio_por_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    """Lista produtos disponiveis no cardapio da unidade com preco efetivo."""
    itens = produto_repository.listar_cardapio_por_unidade(db, unidade_id)
    resultado = []
    for item in itens:
        produto = produto_repository.buscar_por_id(db, item.produto_id)
        resultado.append(CardapioItemResponse(
            id=item.id,
            produto_id=item.produto_id,
            nome_produto=produto.nome if produto else None,
            preco_efetivo=item.preco_especifico or (produto.preco_base if produto else None),
            disponivel=item.disponivel,
        ))
    return resultado

@router.post("/unidade/{unidade_id}/cardapio", status_code=201,
             summary="Adicionar produto ao cardapio (admin)")
def adicionar_ao_cardapio(
    unidade_id: int,
    dados: CardapioUnidadeCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE"))
):
    item = CardapioUnidade(unidade_id=unidade_id, produto_id=dados.produto_id,
                           preco_especifico=dados.preco_especifico, disponivel=dados.disponivel)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Produto adicionado ao cardapio.", "id": item.id}
