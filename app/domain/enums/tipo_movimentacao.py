from enum import Enum

class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"
    RESERVA = "RESERVA"
    LIBERACAO = "LIBERACAO"
