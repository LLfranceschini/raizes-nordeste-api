from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ProdutoCreate(BaseModel):
    """Dados para cadastrar um produto global da rede."""
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None
    preco_base: float = Field(..., gt=0, description="Preco base em reais")
    categoria: str = Field(..., max_length=50)
    sazonal: bool = False


class ProdutoUpdate(BaseModel):
    """Campos atualizaveis de um produto."""
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = None
    preco_base: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=50)
    sazonal: Optional[bool] = None
    ativo: Optional[bool] = None


class ProdutoResponse(BaseModel):
    """Resposta completa de um produto."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: Optional[str] = None
    preco_base: float
    categoria: str
    sazonal: bool
    ativo: bool
    criado_em: datetime


class CardapioItemResponse(BaseModel):
    """Produto no cardapio de uma unidade com preco efetivo."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    nome_produto: Optional[str] = None
    preco_efetivo: Optional[float] = None
    disponivel: bool


class CardapioUnidadeCreate(BaseModel):
    """Adiciona produto ao cardapio de uma unidade."""
    produto_id: int
    preco_especifico: Optional[float] = Field(
        None, gt=0,
        description="Se nulo, usa o preco_base do produto"
    )
    disponivel: bool = True


class CardapioUnidadeUpdate(BaseModel):
    preco_especifico: Optional[float] = Field(None, gt=0)
    disponivel: Optional[bool] = None
