from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.services import auth_service
from app.infrastructure.repositories import usuario_repository
from app.application.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.api.dependencies import get_current_user, require_perfil
from app.domain.models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=201, summary="Cadastrar usuario")
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Cria novo usuario e registra consentimento LGPD automaticamente."""
    return auth_service.registrar_usuario(db, dados)

@router.get("/me", response_model=UsuarioResponse, summary="Meu perfil")
def meu_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UsuarioResponse, summary="Atualizar meu perfil")
def atualizar_perfil(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if dados.nome is not None:
        current_user.nome = dados.nome
    if dados.telefone is not None:
        current_user.telefone = dados.telefone
    return usuario_repository.atualizar(db, current_user)

@router.get("/", response_model=list[UsuarioResponse], summary="Listar usuarios (admin)")
def listar_usuarios(
    skip: int = 0, limit: int = 20,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfil("ADMIN", "GERENTE"))
):
    return usuario_repository.listar(db, skip=skip, limit=limit)
