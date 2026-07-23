from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Credenciais para autenticacao."""
    email: EmailStr
    senha: str = Field(..., min_length=6, description="Minimo 6 caracteres")


class TokenResponse(BaseModel):
    """Tokens retornados apos login bem-sucedido."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800
    refresh_token: str
    perfil: str


class RefreshTokenRequest(BaseModel):
    """Solicitacao de renovacao do access_token."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Revogacao do refresh_token no logout."""
    refresh_token: str
