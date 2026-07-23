import random
import uuid
from datetime import datetime, timezone


def processar_pagamento(pedido_id: int, valor: float, forma_pagamento: str) -> dict:
    """
    Simula o gateway externo de pagamento.
    MOCK e DINHEIRO: sempre aprovado.
    PIX, CARTAO_CREDITO, CARTAO_DEBITO: 90% de aprovacao.
    """
    ref_externa = f"MOCK-{pedido_id}-{uuid.uuid4().hex[:8].upper()}"
    sempre_aprovado = forma_pagamento in ("MOCK", "DINHEIRO")
    aprovado = sempre_aprovado or random.random() > 0.10
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
