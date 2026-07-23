from sqlalchemy.orm import Session
from app.domain.models.produto import Produto
from app.domain.models.cardapio_unidade import CardapioUnidade


def buscar_por_id(db: Session, produto_id: int):
    return db.query(Produto).filter(Produto.id == produto_id).first()


def listar_ativos(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Produto).filter(Produto.ativo == True).offset(skip).limit(limit).all()


def criar(db: Session, produto: Produto) -> Produto:
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def buscar_cardapio_unidade(db: Session, unidade_id: int, produto_id: int):
    return db.query(CardapioUnidade).filter(
        CardapioUnidade.unidade_id == unidade_id,
        CardapioUnidade.produto_id == produto_id,
        CardapioUnidade.disponivel == True
    ).first()


def listar_cardapio_por_unidade(db: Session, unidade_id: int):
    return db.query(CardapioUnidade).filter(
        CardapioUnidade.unidade_id == unidade_id,
        CardapioUnidade.disponivel == True
    ).all()
