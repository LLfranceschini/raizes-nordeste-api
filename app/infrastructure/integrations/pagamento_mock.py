import random
import uuid
from datetime import datetime, timezone


def processar_pagamento(pedido_id: int, valor: float, forma_pagamento: str) -> dict:
    ref_externa = f"MOCK-{pedido_id}-{uuid.uuid4().hex[:8].upper()}"

    # FORCAR_RECUSA sempre rejeita (usado em testes)
    if forma_pagamento == "FORCAR_RECUSA":
        aprovado = False
    elif forma_pagamento in ("MOCK", "DINHEIRO"):
        aprovado = True
    else:
        aprovado = random.random() > 0.10

    status = "APROVADO" if aprovado else "RECUSADO"

    return {
        "ref_externa": ref_externa,
        "status": status,
        "valor": valor,
        "forma_pagamento": forma_pagamento,
        "pedido_id": pedido_id,
        "mensagem": "Pagamento aprovado." if aprovado else "Pagamento recusado pela operadora.",
        "gateway": "RaizesPayMock",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
