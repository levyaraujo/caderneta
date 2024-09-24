from dataclasses import dataclass
from datetime import datetime

from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.validadores import validar_tipo_da_transacao

@dataclass(frozen=False)
class Transacao:
    id: int
    usuario: Usuario
    valor: float
    tipo: TipoTransacao
    destino: str | None
    descricao: str | None
    caixa: datetime
    competencia: datetime = datetime.now()
    apagado: bool = False


    def __post_init__(self):
        validar_tipo_da_transacao(self.tipo)