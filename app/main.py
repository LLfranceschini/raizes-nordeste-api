from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.api.error_handler import (
    handler_validacao,
    handler_estoque_insuficiente,
    handler_pedido_nao_cancelavel,
    handler_produto_indisponivel,
    handler_promocao_invalida,
    handler_consentimento_nao_registrado,
    handler_generico,
)
from app.domain.exceptions.domain_exceptions import (
    EstoqueInsuficienteError,
    PedidoNaoCancelavelError,
    ProdutoIndisponivelError,
    PromocaoInvalidaError,
    ConsentimentoNaoRegistradoError,
)

# Inicializacao da aplicacao FastAPI
app = FastAPI(
    title="Raizes do Nordeste API",
    description=(
        "API REST do sistema de gestao da rede de lanchonetes Raizes do Nordeste. "
        "Suporta multiplos canais: APP, TOTEM, BALCAO, PICKUP e WEB."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc (alternativa)
    openapi_url="/openapi.json",
)

# CORS - permite que o front-end acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em producao: listar dominios especificos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos handlers de erro (padrao JSON unico)
app.add_exception_handler(RequestValidationError, handler_validacao)
app.add_exception_handler(EstoqueInsuficienteError, handler_estoque_insuficiente)
app.add_exception_handler(PedidoNaoCancelavelError, handler_pedido_nao_cancelavel)
app.add_exception_handler(ProdutoIndisponivelError, handler_produto_indisponivel)
app.add_exception_handler(PromocaoInvalidaError, handler_promocao_invalida)
app.add_exception_handler(ConsentimentoNaoRegistradoError, handler_consentimento_nao_registrado)
app.add_exception_handler(Exception, handler_generico)

# Registro das rotas da API
app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["Sistema"])
def health_check():
    """Verifica se a API esta no ar. Util para monitoramento."""
    return {"status": "ok", "versao": "1.0.0"}
