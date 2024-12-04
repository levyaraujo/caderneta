import re
from dataclasses import dataclass, field
from datetime import datetime, date

from const import REGEX_WAMID
from src.dominio.transacao.exceptions import WamIdInvalido
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.utils.formatos import datetime_para_br
from src.utils.validadores import validar_tipo_da_transacao


@dataclass(frozen=False)
class Transacao:
    usuario: Usuario
    valor: float
    tipo: TipoTransacao
    wamid: str
    id: int | None = field(default=None)
    categoria: str | None = field(default=None)
    descricao: str | None = field(default=None)
    caixa: datetime | date = field(default_factory=datetime.now)
    competencia: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        validar_tipo_da_transacao(self.tipo)
        self.wamid_eh_valido()

    def wamid_eh_valido(self) -> None:
        regex = REGEX_WAMID
        if not re.fullmatch(regex, self.wamid):
            raise WamIdInvalido(f"wamid inválido: {self.wamid}")

    def dicionario(self) -> dict:
        """
        Converte a instância de Transacao para um dicionário.

        Returns:
            dict: Dicionário representando a transação
        """
        return {
            "valor": -self.valor if self.tipo == TipoTransacao.DEBITO else self.valor,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "data": datetime_para_br(self.caixa),
        }


@dataclass
class Real:
    valor: float
    moeda: str = "R$"

    def __str__(self) -> str:
        return f"{self.moeda} {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
