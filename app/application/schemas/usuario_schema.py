from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date


PerfilUsuario = Literal["CLIENTE", "ATENDENTE", "COZINHA", "GERENTE", "ADMIN"]


class UsuarioCreate(BaseModel):
    """Dados necessarios para criar um novo usuario."""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6, description="Minimo 6 caracteres")
    perfil: PerfilUsuario
    telefone: Optional[str] = Field(None, max_length=20)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    data_nascimento: Optional[date] = None
    unidade_id: Optional[int] = Field(None, description="Obrigatorio para perfis de funcionario")

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("CPF deve conter apenas digitos")
        return v


class UsuarioUpdate(BaseModel):
    """Campos que podem ser atualizados pelo proprio usuario."""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    ativo: Optional[bool] = None


class UsuarioMiniResponse(BaseModel):
    """Versao reduzida para embed em outros recursos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    perfil: str


class UsuarioResponse(BaseModel):
    """Resposta completa de usuario (sem senha_hash)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: str
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    unidade_id: Optional[int] = None
    ativo: bool
    criado_em: datetime
