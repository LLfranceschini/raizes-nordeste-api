from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone

from app.domain.exceptions.domain_exceptions import (
    EstoqueInsuficienteError,
    PedidoNaoCancelavelError,
    ProdutoIndisponivelError,
    PromocaoInvalidaError,
    ConsentimentoNaoRegistradoError,
)


def _erro(status_code: int, error: str, message: str, path: str, details: list = None):
    """Monta o padrao de erro JSON da API."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "message": message,
            "details": details or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
        }
    )


async def handler_validacao(request: Request, exc: RequestValidationError):
    """Trata erros de validacao do Pydantic (422)."""
    detalhes = [
        {"field": " -> ".join(str(loc) for loc in e["loc"]), "issue": e["msg"]}
        for e in exc.errors()
    ]
    return _erro(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error="ERRO_VALIDACAO",
        message="Um ou mais campos estao invalidos.",
        path=str(request.url),
        details=detalhes,
    )


async def handler_estoque_insuficiente(request: Request, exc: EstoqueInsuficienteError):
    return _erro(409, "ESTOQUE_INSUFICIENTE",
                 str(exc) or "Estoque insuficiente para um ou mais itens.",
                 str(request.url))


async def handler_pedido_nao_cancelavel(request: Request, exc: PedidoNaoCancelavelError):
    return _erro(409, "PEDIDO_NAO_CANCELAVEL",
                 str(exc) or "O pedido nao pode ser cancelado no status atual.",
                 str(request.url))


async def handler_produto_indisponivel(request: Request, exc: ProdutoIndisponivelError):
    return _erro(409, "PRODUTO_INDISPONIVEL",
                 str(exc) or "Produto indisponivel nesta unidade.",
                 str(request.url))


async def handler_promocao_invalida(request: Request, exc: PromocaoInvalidaError):
    return _erro(400, "PROMOCAO_INVALIDA",
                 str(exc) or "Promocao invalida ou expirada.",
                 str(request.url))


async def handler_consentimento_nao_registrado(
    request: Request, exc: ConsentimentoNaoRegistradoError
):
    return _erro(403, "CONSENTIMENTO_NECESSARIO",
                 str(exc) or "Consentimento LGPD necessario para esta operacao.",
                 str(request.url))


async def handler_generico(request: Request, exc: Exception):
    """Captura qualquer excecao nao tratada (500)."""
    return _erro(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="ERRO_INTERNO",
        message="Ocorreu um erro interno. Tente novamente ou contate o suporte.",
        path=str(request.url),
    )
