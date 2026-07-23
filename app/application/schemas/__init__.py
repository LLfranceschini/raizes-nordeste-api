from app.application.schemas.common import ErroResponse, PaginacaoResponse, DetalheErro
from app.application.schemas.auth_schema import (
    LoginRequest, TokenResponse, RefreshTokenRequest, LogoutRequest
)
from app.application.schemas.usuario_schema import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioMiniResponse
)
from app.application.schemas.unidade_schema import (
    UnidadeCreate, UnidadeUpdate, UnidadeResponse, UnidadeMiniResponse,
    ConfiguracaoUnidadeCreate, ConfiguracaoUnidadeResponse
)
from app.application.schemas.produto_schema import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse,
    CardapioUnidadeCreate, CardapioUnidadeUpdate, CardapioItemResponse
)
from app.application.schemas.estoque_schema import (
    EstoqueResponse, MovimentacaoCreate, MovimentacaoResponse
)
from app.application.schemas.pedido_schema import (
    PedidoCreate, PedidoStatusUpdate, PedidoResponse, PedidoMiniResponse,
    ItemPedidoCreate, ItemPedidoResponse
)
from app.application.schemas.pagamento_schema import (
    PagamentoMockRequest, PagamentoCallbackRequest, PagamentoResponse
)
from app.application.schemas.fidelidade_schema import (
    FidelidadeResponse, HistoricoFidelidadeResponse, ResgateRequest, ConsentimentoCreate
)
from app.application.schemas.promocao_schema import (
    PromocaoCreate, PromocaoUpdate, PromocaoResponse
)
