from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import datetime


class DetalheErro(BaseModel):
    field: str
    issue: str


class ErroResponse(BaseModel):
    """Padrao de erro unico para toda a API."""
    error: str
    message: str
    details: List[DetalheErro] = []
    timestamp: datetime
    path: str
    request_id: Optional[str] = None


class PaginacaoResponse(BaseModel):
    """Wrapper de paginacao para listagens."""
    total: int
    page: int
    limit: int
    pages: int
    items: List[Any]
