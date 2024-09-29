from dataclasses import dataclass, field
from datetime import datetime

from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.validadores import validar_tipo_da_transacao


@dataclass(frozen=False)
class Transacao:
    usuario: Usuario
    valor: float
    tipo: TipoTransacao
    id: int | None = field(default=None)
    destino: str | None = field(default=None)
    descricao: str | None = field(default=None)
    caixa: datetime = field(default_factory=datetime.now)
    competencia: datetime = field(default_factory=datetime.now)
    apagado: bool = False

    def __post_init__(self):
        validar_tipo_da_transacao(self.tipo)
