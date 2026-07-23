from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.domain.models.log_auditoria import LogAuditoria
from app.infrastructure.repositories import pagamento_repository, pedido_repository
from app.infrastructure.integrations.pagamento_mock import processar_pagamento


def solicitar_pagamento(db: Session, pedido_id: int, usuario_id: int):
    """
    Envia ao gateway mock e processa retorno.
    APROVADO: pedido vai para PAGO e cliente acumula pontos.
    RECUSADO: pedido permanece AGUARDANDO_PAGAMENTO para nova tentativa.
    """
    pagamento = pagamento_repository.buscar_por_pedido_id(db, pedido_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento nao encontrado.")
    pedido = pedido_repository.buscar_por_id(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")
    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(status_code=409,
            detail=f"Pedido com status '{pedido.status}' nao pode ser pago.")

    retorno = processar_pagamento(pedido_id, pagamento.valor, pagamento.forma_pagamento)
    pagamento.ref_externa = retorno["ref_externa"]
    pagamento.payload_retorno = retorno
    pagamento.tentativas = (pagamento.tentativas or 0) + 1
    pagamento.status = retorno["status"]
    pagamento_repository.atualizar(db, pagamento)

    if retorno["status"] == "APROVADO":
        pedido.status = "PAGO"
        pedido_repository.atualizar(db, pedido)
        _acumular_pontos(db, pedido)
        acao = "PAGAMENTO_APROVADO"
    else:
        acao = "PAGAMENTO_RECUSADO"

    _log(db, usuario_id, acao, "pagamento", pagamento.id,
         {"ref": retorno["ref_externa"], "status": retorno["status"]})
    return pagamento


def _acumular_pontos(db, pedido):
    """1 ponto por real gasto. Atualiza nivel do cliente."""
    from app.infrastructure.repositories.fidelidade_repository import (
        criar_ou_buscar, registrar_historico, atualizar
    )
    fidelidade = criar_ou_buscar(db, pedido.cliente_id)
    pontos = int(pedido.total)
    fidelidade.pontos_acumulados += pontos
    fidelidade.pontos_disponiveis += pontos
    if fidelidade.pontos_acumulados >= 1000:
        fidelidade.nivel = "OURO"
    elif fidelidade.pontos_acumulados >= 500:
        fidelidade.nivel = "PRATA"
    atualizar(db, fidelidade)
    registrar_historico(db, fidelidade.id, "ACUMULO", pontos,
                        f"Pontos do pedido #{pedido.id}", pedido.id)


def _log(db, usuario_id, acao, entidade, entidade_id, dados_novos=None):
    db.add(LogAuditoria(usuario_id=usuario_id, acao=acao, entidade=entidade,
                        entidade_id=entidade_id, dados_novos=dados_novos))
    db.commit()
