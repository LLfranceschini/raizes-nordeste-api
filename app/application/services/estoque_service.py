from sqlalchemy.orm import Session
from app.domain.exceptions.domain_exceptions import EstoqueInsuficienteError
from app.infrastructure.repositories import estoque_repository


def verificar_disponibilidade(db: Session, unidade_id: int, produto_id: int, quantidade: int):
    estoque = estoque_repository.buscar_por_unidade_produto(db, unidade_id, produto_id)
    if not estoque or estoque.quantidade < quantidade:
        disponivel = estoque.quantidade if estoque else 0
        raise EstoqueInsuficienteError(
            f"Estoque insuficiente para produto {produto_id}. "
            f"Disponivel: {disponivel}, Solicitado: {quantidade}"
        )
    return estoque


def reservar(db, unidade_id, produto_id, quantidade, usuario_id=None):
    """Deduz estoque ao criar pedido."""
    estoque = verificar_disponibilidade(db, unidade_id, produto_id, quantidade)
    estoque.quantidade -= quantidade
    estoque_repository.registrar_movimentacao(
        db, estoque.id, "RESERVA", quantidade, "Reserva para pedido", usuario_id
    )
    estoque_repository.atualizar_quantidade(db, estoque)


def liberar(db, unidade_id, produto_id, quantidade, usuario_id=None):
    """Devolve estoque ao cancelar pedido."""
    estoque = estoque_repository.criar_ou_buscar(db, unidade_id, produto_id)
    estoque.quantidade += quantidade
    estoque_repository.registrar_movimentacao(
        db, estoque.id, "LIBERACAO", quantidade, "Liberacao por cancelamento", usuario_id
    )
    estoque_repository.atualizar_quantidade(db, estoque)


def movimentar(db, unidade_id, produto_id, tipo, quantidade, motivo, usuario_id):
    """Movimentacao manual: ENTRADA, SAIDA ou AJUSTE."""
    estoque = estoque_repository.criar_ou_buscar(db, unidade_id, produto_id)
    if tipo == "ENTRADA":
        estoque.quantidade += quantidade
    elif tipo == "SAIDA":
        if estoque.quantidade < quantidade:
            raise EstoqueInsuficienteError("Quantidade insuficiente para saida.")
        estoque.quantidade -= quantidade
    elif tipo == "AJUSTE":
        estoque.quantidade = quantidade
    estoque_repository.registrar_movimentacao(
        db, estoque.id, tipo, quantidade, motivo, usuario_id
    )
    estoque_repository.atualizar_quantidade(db, estoque)
    return estoque
