from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, Protocol


class StatusAssinatura(Enum):
    ATIVA = "ativa"
    CANCELADA = "cancelada"
    PENDENTE = "pendente"
    EXPIRADA = "expirada"
    TESTE = "teste"


@dataclass
class Assinatura:
    usuario_id: int
    plano: str
    valor_mensal: float
    data_inicio: datetime
    data_termino: Optional[datetime] = None
    status: StatusAssinatura = StatusAssinatura.TESTE
    id: Optional[int] = field(default=None)
    data_proximo_pagamento: Optional[datetime] = field(default=None)
    data_ultimo_pagamento: Optional[datetime] = field(default=None)
    renovacao_automatica: bool = True

    def __post_init__(self):
        if self.data_proximo_pagamento is None:
            self.data_proximo_pagamento = self.data_inicio

        self._validar_datas()

    def _validar_datas(self):
        if self.data_termino and self.data_termino < self.data_inicio:
            raise ValueError("Data de término não pode ser anterior à data de início")

        if self.data_ultimo_pagamento and self.data_ultimo_pagamento > datetime.now().date():
            raise ValueError("Data do último pagamento não pode ser futura")

    def cancelar(self) -> None:
        self.status = StatusAssinatura.CANCELADA
        self.data_termino = datetime.now()
        self.renovacao_automatica = False

    def reativar(self) -> None:
        if self.status != StatusAssinatura.CANCELADA:
            raise ValueError("Apenas assinaturas canceladas podem ser reativadas")

        self.status = StatusAssinatura.ATIVA
        self.data_termino = None
        self.renovacao_automatica = True

    def registrar_pagamento(self, data_pagamento: date = None) -> None:
        if data_pagamento is None:
            data_pagamento = datetime.now()

        self.data_ultimo_pagamento = data_pagamento
        self.status = StatusAssinatura.ATIVA

        # Calcula próxima data de pagamento
        from dateutil.relativedelta import relativedelta

        self.data_proximo_pagamento = data_pagamento + relativedelta(months=1)


class ProvedorPagamento(Protocol):
    async def criar_assinatura(self, customer_email: str, payment_method_id: str, price_id: str) -> str:
        """Cria uma assinatur e retorna o id"""
        ...

    async def cancelar_assinatura(self, subscription_id: str) -> None:
        """Cancels subscription"""
        ...

    async def reativar_assinatura(self, subscription_id: str) -> None:
        """Reactivates subscription"""
        ...

    async def obter_status_assinatura(self, subscription_id: str) -> str:
        """Gets current subscription status"""
        ...
