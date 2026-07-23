from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime, time


TipoUnidade = Literal["COMPLETA", "REDUZIDA"]
TipoCozinha = Literal["COMPLETA", "REDUZIDA"]


class ConfiguracaoUnidadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    horario_abertura: Optional[time] = None
    horario_fechamento: Optional[time] = None
    tipo_cozinha: str
    dias_funcionamento: Optional[str] = None


class ConfiguracaoUnidadeCreate(BaseModel):
    horario_abertura: Optional[time] = None
    horario_fechamento: Optional[time] = None
    tipo_cozinha: TipoCozinha = "COMPLETA"
    dias_funcionamento: Optional[str] = Field(
        None, description="Ex: SEG,TER,QUA,QUI,SEX,SAB"
    )


class UnidadeCreate(BaseModel):
    """Dados necessarios para cadastrar uma nova unidade."""
    nome: str = Field(..., min_length=2, max_length=100)
    logradouro: str = Field(..., max_length=200)
    numero: str = Field(..., max_length=10)
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)
    cep: str = Field(..., min_length=8, max_length=8)
    telefone: Optional[str] = Field(None, max_length=20)
    tipo: TipoUnidade = "COMPLETA"


class UnidadeUpdate(BaseModel):
    """Campos atualizaveis de uma unidade."""
    nome: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    tipo: Optional[TipoUnidade] = None
    ativa: Optional[bool] = None


class UnidadeResponse(BaseModel):
    """Resposta completa de uma unidade."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    logradouro: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str
    telefone: Optional[str] = None
    tipo: str
    ativa: bool
    criado_em: datetime
    configuracao: Optional[ConfiguracaoUnidadeResponse] = None


class UnidadeMiniResponse(BaseModel):
    """Versao reduzida para embed em outros recursos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cidade: str
    estado: str
