from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import settings


def criar_access_token(data: dict) -> str:
    """
    Cria um JWT de curta duracao (access token).
    Payload minimo: sub (id do usuario), perfil.
    """
    payload = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expiracao, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def criar_refresh_token(data: dict) -> str:
    """
    Cria um JWT de longa duracao (refresh token).
    Usado para renovar o access token sem novo login.
    """
    payload = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({"exp": expiracao, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um JWT.
    Retorna o payload se valido, None se expirado ou invalido.
    """
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
    """Extrai o ID do usuario do payload do token."""
    payload = decodificar_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    return int(sub)
