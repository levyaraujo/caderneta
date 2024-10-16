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
    categoria: str | None = field(default=None)
    descricao: str | None = field(default=None)
    caixa: datetime = field(default_factory=datetime.now)
    competencia: datetime = field(default_factory=datetime.now)
    apagado: bool = False

    def __post_init__(self):
        validar_tipo_da_transacao(self.tipo)


@dataclass
class Real:
    valor: float
    moeda: str = "R$"

    def __str__(self):
        return (
            f"{self.moeda} {self.valor:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
