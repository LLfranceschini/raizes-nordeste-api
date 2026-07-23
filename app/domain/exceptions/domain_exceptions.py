# Exceções de regra de negócio

class EstoqueInsuficienteError(Exception):
    pass

class PedidoNaoCancelavelError(Exception):
    pass

class ProdutoIndisponivelError(Exception):
    pass

class PromocaoInvalidaError(Exception):
    pass

class ConsentimentoNaoRegistradoError(Exception):
    pass
