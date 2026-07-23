from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.infrastructure.security.jwt_handler import decodificar_token
from app.domain.models.usuario import Usuario

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Extrai e valida o usuario do JWT enviado no header Authorization: Bearer <token>."""
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao autenticado ou token invalido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decodificar_token(token)
    if payload is None or payload.get("type") != "access":
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
    """
    Dependency factory para controle de acesso por perfil (RBAC).
    Uso: Depends(require_perfil("ADMIN", "GERENTE"))
    """
    def verificar_perfil(
        current_user: Usuario = Depends(get_current_user)
    ) -> Usuario:
        if current_user.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Perfis permitidos: {', '.join(perfis)}"
            )
        return current_user
    return verificar_perfil