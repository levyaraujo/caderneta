from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional

from dateutil.relativedelta import relativedelta


class StatusAssinatura(Enum):
    ATIVA = "ativa"
    CANCELADA = "cancelada"
    PENDENTE = "pendente"
    EXPIRADA = "expirada"
    TESTE = "teste"


@dataclass
class Assinatura:
    usuario_id: int
    stripe_id: str
    plano: str
    valor_mensal: float
    data_inicio: datetime
    data_termino: Optional[datetime] = None
    status: StatusAssinatura = StatusAssinatura.TESTE
    id: Optional[int] = field(default=None)
    data_proximo_pagamento: Optional[datetime] = field(default=None)
    data_ultimo_pagamento: Optional[datetime] = field(default=None)
    renovacao_automatica: bool = True

    def __post_init__(self) -> None:
        self._validar_datas()

    def _validar_datas(self) -> None:
        if self.data_termino and self.data_termino < self.data_inicio:
            raise ValueError("Data de término não pode ser anterior à data de início")

        if self.data_ultimo_pagamento and self.data_ultimo_pagamento > datetime.now():
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

    def renovar(self) -> None:
        self.data_ultimo_pagamento = datetime.now()
        self.data_proximo_pagamento = self.data_ultimo_pagamento + relativedelta(months=1)
        self.data_termino = None
        self.renovacao_automatica = True

    def registrar_pagamento(self) -> None:
        data_pagamento = datetime.now()
        self.data_ultimo_pagamento = data_pagamento
        self.data_proximo_pagamento = data_pagamento + relativedelta(months=1)
