from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.schemas.pagamento_schema import PagamentoResponse
from app.application.services import pagamento_service
from app.infrastructure.repositories import pagamento_repository
from app.api.dependencies import get_current_user
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.post("/{pedido_id}/processar", response_model=PagamentoResponse,
             summary="Processar pagamento mock")
def processar_pagamento(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Envia ao gateway mock e processa o retorno.
    APROVADO: pedido vai para PAGO e cliente acumula pontos.
    RECUSADO: pedido permanece AGUARDANDO_PAGAMENTO para nova tentativa.
    """
    return pagamento_service.solicitar_pagamento(db, pedido_id, current_user.id)

@router.get("/{pedido_id}", response_model=PagamentoResponse,
            summary="Consultar pagamento de um pedido")
def consultar_pagamento(
    pedido_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user)
):
    pagamento = pagamento_repository.buscar_por_pedido_id(db, pedido_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento nao encontrado.")
    return pagamento
