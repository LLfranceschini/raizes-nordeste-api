from sqlalchemy.orm import Session
from app.domain.models.estoque import Estoque
from app.domain.models.movimentacao_estoque import MovimentacaoEstoque


def buscar_por_unidade_produto(db: Session, unidade_id: int, produto_id: int):
    return db.query(Estoque).filter(
        Estoque.unidade_id == unidade_id,
        Estoque.produto_id == produto_id
    ).first()


def listar_por_unidade(db: Session, unidade_id: int):
    return db.query(Estoque).filter(Estoque.unidade_id == unidade_id).all()


def criar_ou_buscar(db: Session, unidade_id: int, produto_id: int) -> Estoque:
    estoque = buscar_por_unidade_produto(db, unidade_id, produto_id)
    if not estoque:
        estoque = Estoque(unidade_id=unidade_id, produto_id=produto_id, quantidade=0)
        db.add(estoque)
        db.commit()
        db.refresh(estoque)
    return estoque


def registrar_movimentacao(
    db: Session, estoque_id: int, tipo: str,
    quantidade: int, motivo: str = None, usuario_id: int = None
) -> MovimentacaoEstoque:
    mov = MovimentacaoEstoque(
        estoque_id=estoque_id,
        usuario_id=usuario_id,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def atualizar_quantidade(db: Session, estoque: Estoque) -> Estoque:
    db.commit()
    db.refresh(estoque)
    return estoque
