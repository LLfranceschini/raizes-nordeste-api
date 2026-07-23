from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.schemas.estoque_schema import EstoqueResponse, MovimentacaoCreate
from app.infrastructure.repositories import estoque_repository
from app.application.services.estoque_service import movimentar
from app.api.dependencies import require_perfil
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.get("/{unidade_id}", response_model=list[EstoqueResponse],
            summary="Consultar estoque de uma unidade")
def consultar_estoque(
    unidade_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE", "ATENDENTE"))
):
    itens = estoque_repository.listar_por_unidade(db, unidade_id)
    return [
        EstoqueResponse(
            id=i.id, unidade_id=i.unidade_id, produto_id=i.produto_id,
            quantidade=i.quantidade, qtd_minima=i.qtd_minima,
            atualizado_em=i.atualizado_em, em_alerta=i.quantidade <= i.qtd_minima
        ) for i in itens
    ]

@router.post("/{unidade_id}/movimentar", response_model=EstoqueResponse,
             summary="Movimentar estoque")
def movimentar_estoque(
    unidade_id: int,
    produto_id: int,
    dados: MovimentacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_perfil("ADMIN", "GERENTE", "ATENDENTE"))
):
    """Registra ENTRADA, SAIDA ou AJUSTE manual de estoque."""
    estoque = movimentar(db, unidade_id, produto_id,
                         dados.tipo, dados.quantidade, dados.motivo, current_user.id)
    return EstoqueResponse(
        id=estoque.id, unidade_id=estoque.unidade_id, produto_id=estoque.produto_id,
        quantidade=estoque.quantidade, qtd_minima=estoque.qtd_minima,
        atualizado_em=estoque.atualizado_em, em_alerta=estoque.quantidade <= estoque.qtd_minima
    )
