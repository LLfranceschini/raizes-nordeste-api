from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.infrastructure.database.connection import get_db
from app.application.schemas.pedido_schema import (
    PedidoCreate, PedidoResponse, PedidoStatusUpdate, PedidoMiniResponse
)
from app.application.services import pedido_service
from app.infrastructure.repositories import pedido_repository
from app.api.dependencies import get_current_user, require_perfil
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=PedidoResponse, status_code=201, summary="Criar pedido")
def criar_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria pedido validando cardapio, estoque e aplicando cupom se houver."""
    return pedido_service.criar_pedido(db, dados, current_user.id)

@router.get("/", response_model=list[PedidoMiniResponse], summary="Listar meus pedidos")
def listar_pedidos(
    skip: int = 0, limit: int = 20,
    canal: Optional[str] = Query(None, description="APP, TOTEM, BALCAO, PICKUP, WEB"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return pedido_repository.listar_por_cliente(
        db, current_user.id, skip=skip, limit=limit, canal=canal, status=status
    )

@router.get("/unidade/{unidade_id}", response_model=list[PedidoMiniResponse],
            summary="Pedidos de uma unidade (funcionarios)")
def listar_pedidos_unidade(
    unidade_id: int,
    skip: int = 0, limit: int = 50,
    canal: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE", "ATENDENTE", "COZINHA"))
):
    """Suporta filtro por canal e status. Ex: ?canal=TOTEM&status=EM_PREPARO"""
    return pedido_repository.listar_por_unidade(
        db, unidade_id, skip=skip, limit=limit, canal=canal, status=status
    )

@router.get("/{pedido_id}", response_model=PedidoResponse, summary="Buscar pedido")
def buscar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    pedido = pedido_repository.buscar_por_id(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")
    if current_user.perfil == "CLIENTE" and pedido.cliente_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return pedido

@router.patch("/{pedido_id}/status", response_model=PedidoResponse,
              summary="Atualizar status do pedido")
def atualizar_status(
    pedido_id: int,
    dados: PedidoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_perfil("ADMIN", "GERENTE", "ATENDENTE", "COZINHA"))
):
    """Fluxo: PAGO -> EM_PREPARO -> PRONTO -> ENTREGUE (ou CANCELADO)"""
    return pedido_service.atualizar_status(db, pedido_id, dados, current_user.id)
