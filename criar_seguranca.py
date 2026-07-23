#!/usr/bin/env python3
"""
Script para criar a camada de seguranca do projeto Raizes do Nordeste.
Cria: password_handler, jwt_handler, dependencies, error_handler e main.py
Execute na raiz do projeto: python criar_seguranca.py
"""
import os

def escrever(caminho, conteudo):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"  criado: {caminho}")

print("Criando camada de seguranca...\n")

# ------------------------------------------------------------------
# HASH DE SENHA - bcrypt via passlib
# ------------------------------------------------------------------
escrever("app/infrastructure/security/password_handler.py", """\
from passlib.context import CryptContext

# Contexto bcrypt para hash e verificacao de senhas
# bcrypt e o algoritmo recomendado: lento por design, resistente a brute-force
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    \"\"\"Gera o hash bcrypt de uma senha. Nunca armazene senha em texto puro.\"\"\"
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    \"\"\"Compara a senha em texto puro com o hash armazenado.\"\"\"
    return pwd_context.verify(senha, senha_hash)
""")

# ------------------------------------------------------------------
# JWT HANDLER - criacao e validacao de tokens
# ------------------------------------------------------------------
escrever("app/infrastructure/security/jwt_handler.py", """\
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import settings


def criar_access_token(data: dict) -> str:
    \"\"\"
    Cria um JWT de curta duracao (access token).
    Payload minimo: sub (id do usuario), perfil.
    \"\"\"
    payload = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expiracao, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def criar_refresh_token(data: dict) -> str:
    \"\"\"
    Cria um JWT de longa duracao (refresh token).
    Usado para renovar o access token sem novo login.
    \"\"\"
    payload = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expiracao, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> Optional[dict]:
    \"\"\"
    Decodifica e valida um JWT.
    Retorna o payload se valido, None se expirado ou invalido.
    \"\"\"
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def obter_usuario_id_do_token(token: str) -> Optional[int]:
    \"\"\"Extrai o ID do usuario do payload do token.\"\"\"
    payload = decodificar_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    return int(sub)
""")

# ------------------------------------------------------------------
# DEPENDENCIES - FastAPI dependencies reutilizaveis
# ------------------------------------------------------------------
escrever("app/api/dependencies.py", """\
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.infrastructure.database.connection import get_db
from app.infrastructure.security.jwt_handler import decodificar_token
from app.domain.models.usuario import Usuario

# URL do endpoint de login usada pelo Swagger para autenticacao
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    \"\"\"
    Dependency que extrai e valida o usuario do JWT.
    Usada em todos os endpoints protegidos.
    \"\"\"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao autenticado ou token invalido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodificar_token(token)
    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise credentials_exception

    usuario = db.query(Usuario).filter(
        Usuario.id == int(usuario_id),
        Usuario.ativo == True
    ).first()

    if usuario is None:
        raise credentials_exception

    return usuario


def require_perfil(*perfis: str):
    \"\"\"
    Dependency factory para controle de acesso por perfil (RBAC).

    Uso nos endpoints:
        @router.get("/admin")
        def rota(user = Depends(require_perfil("ADMIN", "GERENTE"))):
            ...
    \"\"\"
    def verificar_perfil(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Perfis permitidos: {', '.join(perfis)}"
            )
        return current_user
    return verificar_perfil
""")

# ------------------------------------------------------------------
# ERROR HANDLER - padrao de erro JSON unico para toda a API
# ------------------------------------------------------------------
escrever("app/api/error_handler.py", """\
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
    \"\"\"Monta o padrao de erro JSON da API.\"\"\"
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
    \"\"\"Trata erros de validacao do Pydantic (422).\"\"\"
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
    \"\"\"Captura qualquer excecao nao tratada (500).\"\"\"
    return _erro(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="ERRO_INTERNO",
        message="Ocorreu um erro interno. Tente novamente ou contate o suporte.",
        path=str(request.url),
    )
""")

# ------------------------------------------------------------------
# ROUTER v1 - agrega todos os endpoints
# ------------------------------------------------------------------
escrever("app/api/v1/router.py", """\
from fastapi import APIRouter

# Importar os routers de cada endpoint aqui conforme forem criados
# from app.api.v1.endpoints.auth import router as auth_router
# from app.api.v1.endpoints.usuarios import router as usuarios_router
# from app.api.v1.endpoints.unidades import router as unidades_router
# from app.api.v1.endpoints.produtos import router as produtos_router
# from app.api.v1.endpoints.estoque import router as estoque_router
# from app.api.v1.endpoints.pedidos import router as pedidos_router
# from app.api.v1.endpoints.pagamentos import router as pagamentos_router
# from app.api.v1.endpoints.fidelidade import router as fidelidade_router
# from app.api.v1.endpoints.promocoes import router as promocoes_router

router = APIRouter()

# Descomentar conforme os endpoints forem implementados:
# router.include_router(auth_router, prefix="/auth", tags=["Autenticacao"])
# router.include_router(usuarios_router, prefix="/usuarios", tags=["Usuarios"])
# router.include_router(unidades_router, prefix="/unidades", tags=["Unidades"])
# router.include_router(produtos_router, prefix="/produtos", tags=["Produtos"])
# router.include_router(estoque_router, prefix="/estoque", tags=["Estoque"])
# router.include_router(pedidos_router, prefix="/pedidos", tags=["Pedidos"])
# router.include_router(pagamentos_router, prefix="/pagamentos", tags=["Pagamentos"])
# router.include_router(fidelidade_router, prefix="/fidelidade", tags=["Fidelidade"])
# router.include_router(promocoes_router, prefix="/promocoes", tags=["Promocoes"])
""")

# ------------------------------------------------------------------
# MAIN.PY - ponto de entrada da API atualizado
# ------------------------------------------------------------------
escrever("app/main.py", """\
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
    \"\"\"Verifica se a API esta no ar. Util para monitoramento.\"\"\"
    return {"status": "ok", "versao": "1.0.0"}
""")

print("\nCamada de seguranca criada com sucesso!")
print("\nArquivos gerados:")
print("  app/infrastructure/security/password_handler.py")
print("  app/infrastructure/security/jwt_handler.py")
print("  app/api/dependencies.py")
print("  app/api/error_handler.py")
print("  app/api/v1/router.py")
print("  app/main.py  (atualizado)")
print("\nProximo passo: criar os endpoints (auth, pedidos, estoque...)")
