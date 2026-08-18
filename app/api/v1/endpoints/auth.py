from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.services import auth_service
from app.application.schemas.auth_schema import LoginRequest, TokenResponse, LogoutRequest
from app.api.dependencies import get_current_user
from app.domain.models.usuario import Usuario
from app.application.schemas.auth_schema import LoginRequest, TokenResponse, LogoutRequest, RefreshTokenRequest

router = APIRouter()

@router.post("/login", response_model=TokenResponse, summary="Autenticar usuario")
def login(dados: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Autentica o usuario e retorna access_token + refresh_token."""
    ip = request.client.host if request.client else None
    return auth_service.login(db, dados, ip=ip)

@router.post("/logout", summary="Encerrar sessao")
def logout(
    dados: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Revoga o refresh_token, invalidando a sessao atual."""
    auth_service.logout(db, dados.refresh_token, current_user.id)
    return {"message": "Logout realizado com sucesso."}

@router.post("/refresh", response_model=TokenResponse, summary="Renovar access token")
def refresh_token(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Usa o refresh_token para emitir um novo access_token sem precisar fazer login novamente.
    O refresh_token continua o mesmo — só o access_token é renovado.
    """
    return auth_service.refresh_access_token(db, dados.refresh_token)
