from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from datetime import date
from app.domain.models.pedido import Pedido
from app.domain.models.item_pedido import ItemPedido
from app.domain.models.pagamento import Pagamento
from app.domain.models.log_auditoria import LogAuditoria
from app.domain.models.unidade import Unidade
from app.domain.models.promocao import Promocao
from app.domain.exceptions.domain_exceptions import (
    PedidoNaoCancelavelError, ProdutoIndisponivelError
)
from app.infrastructure.repositories import pedido_repository, produto_repository
from app.application.services.estoque_service import reservar, liberar
from app.application.schemas.pedido_schema import PedidoCreate, PedidoStatusUpdate

STATUS_CANCELAVEIS = {"AGUARDANDO_PAGAMENTO", "PAGO", "EM_PREPARO"}


def criar_pedido(db: Session, dados: PedidoCreate, cliente_id: int) -> Pedido:
    """
    Fluxo MVP completo:
    1. Valida unidade  2. Valida cardapio e estoque por item
    3. Calcula totais  4. Aplica cupom  5. Cria pedido, itens e pagamento
    6. Reserva estoque  7. Registra log
    """
    unidade = db.query(Unidade).filter(
        Unidade.id == dados.unidade_id, Unidade.ativa == True
    ).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade nao encontrada ou inativa.")

    itens_validados = []
    subtotal = 0.0

    for item_data in dados.itens:
        cardapio = produto_repository.buscar_cardapio_unidade(
            db, dados.unidade_id, item_data.produto_id
        )
        if not cardapio:
            raise ProdutoIndisponivelError(
                f"Produto {item_data.produto_id} nao disponivel nesta unidade."
            )
        produto = produto_repository.buscar_por_id(db, item_data.produto_id)
        preco_unitario = cardapio.preco_especifico or produto.preco_base
        item_subtotal = preco_unitario * item_data.quantidade
        itens_validados.append({
            "produto_id": item_data.produto_id,
            "quantidade": item_data.quantidade,
            "preco_unitario": preco_unitario,
            "subtotal_item": item_subtotal,
        })
        subtotal += item_subtotal

    # Aplica cupom de promocao se informado
    desconto = 0.0
    if dados.codigo_cupom:
        promocao = db.query(Promocao).filter(
            Promocao.codigo_cupom == dados.codigo_cupom,
            Promocao.ativa == True,
            Promocao.data_inicio <= date.today(),
            Promocao.data_fim >= date.today(),
        ).first()
        if promocao:
            if promocao.tipo_desconto == "PERCENTUAL":
                desconto = subtotal * (promocao.valor_desconto / 100)
            else:
                desconto = min(promocao.valor_desconto, subtotal)

    total = subtotal - desconto

    # Cria pedido (sem commit - transacao atomica)
    pedido = Pedido(
        cliente_id=cliente_id,
        unidade_id=dados.unidade_id,
        canal_pedido=dados.canal_pedido,
        status="AGUARDANDO_PAGAMENTO",
        subtotal=round(subtotal, 2),
        desconto=round(desconto, 2),
        total=round(total, 2),
    )
    pedido_repository.criar(db, pedido)

    for item in itens_validados:
        pedido_repository.adicionar_item(db, ItemPedido(
            pedido_id=pedido.id,
            produto_id=item["produto_id"],
            quantidade=item["quantidade"],
            preco_unitario=round(item["preco_unitario"], 2),
            subtotal=round(item["subtotal_item"], 2),
        ))

    db.add(Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=dados.forma_pagamento,
        status="PENDENTE",
        valor=round(total, 2),
    ))

    for item in itens_validados:
        reservar(db, dados.unidade_id, item["produto_id"], item["quantidade"], cliente_id)

    # Commit atomico — se qualquer etapa falhar, tudo e revertido
    pedido_repository.confirmar(db, pedido)
    _log(db, cliente_id, "PEDIDO_CRIADO", "pedido", pedido.id)
    return pedido


def atualizar_status(
    db: Session, pedido_id: int, dados: PedidoStatusUpdate, usuario_id: int
) -> Pedido:
    pedido = pedido_repository.buscar_por_id(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")
    if dados.status == "CANCELADO":
        return cancelar_pedido(db, pedido_id, dados.motivo_cancelamento, usuario_id)
    status_anterior = pedido.status
    pedido.status = dados.status
    pedido = pedido_repository.atualizar(db, pedido)
    _log(db, usuario_id, "STATUS_ATUALIZADO", "pedido", pedido.id,
         {"status": status_anterior}, {"status": dados.status})
    return pedido


def cancelar_pedido(
    db: Session, pedido_id: int, motivo: Optional[str], usuario_id: int
) -> Pedido:
    pedido = pedido_repository.buscar_por_id(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")
    if pedido.status not in STATUS_CANCELAVEIS:
        raise PedidoNaoCancelavelError(
            f"Pedido com status '{pedido.status}' nao pode ser cancelado."
        )
    for item in pedido.itens:
        liberar(db, pedido.unidade_id, item.produto_id, item.quantidade, usuario_id)
    pedido.status = "CANCELADO"
    pedido.cancelado_por = usuario_id
    pedido.motivo_cancelamento = motivo
    pedido_repository.atualizar(db, pedido)
    _log(db, usuario_id, "PEDIDO_CANCELADO", "pedido", pedido.id,
         dados_novos={"motivo": motivo})
    return pedido


def _log(db, usuario_id, acao, entidade, entidade_id,
         dados_anteriores=None, dados_novos=None):
    db.add(LogAuditoria(
        usuario_id=usuario_id, acao=acao, entidade=entidade,
        entidade_id=entidade_id, dados_anteriores=dados_anteriores,
        dados_novos=dados_novos,
    ))
    db.commit()
