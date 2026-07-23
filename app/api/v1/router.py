from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, usuarios, unidades, produtos,
    estoque, pedidos, pagamentos, fidelidade, promocoes
)

router = APIRouter()

router.include_router(auth.router,       prefix="/auth",       tags=["Autenticacao"])
router.include_router(usuarios.router,   prefix="/usuarios",   tags=["Usuarios"])
router.include_router(unidades.router,   prefix="/unidades",   tags=["Unidades"])
router.include_router(produtos.router,   prefix="/produtos",   tags=["Produtos"])
router.include_router(estoque.router,    prefix="/estoque",    tags=["Estoque"])
router.include_router(pedidos.router,    prefix="/pedidos",    tags=["Pedidos"])
router.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
router.include_router(fidelidade.router, prefix="/fidelidade", tags=["Fidelidade"])
router.include_router(promocoes.router,  prefix="/promocoes",  tags=["Promocoes"])
