from enum import Enum

class TipoDesconto(str, Enum):
    PERCENTUAL = "PERCENTUAL"
    FIXO = "FIXO"
