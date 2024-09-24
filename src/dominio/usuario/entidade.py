from dataclasses import dataclass
from typing import List

from src.libs.tipos import Intervalo
from src.dominio.transacao.tipos import TipoTransacao
from src.validadores import validar_email, validar_telefone


@dataclass
class Usuario:
    id: int
    nome: str
    sobrenome: str
    telefone: str
    email: str
    senha: str


    def __post_init__(self):
        validar_email(self.email)
        validar_telefone(self.telefone)


    def _calcular_caixa(self, transacoes: List["Transacao"], intervalo: Intervalo):
        transacoes_no_periodo = [transacao for transacao in transacoes if intervalo.contem(transacao.caixa)]

        soma = 0

        for transacao in transacoes_no_periodo:
            soma += transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor

        return soma

    def _calcular_competencia(self, transacoes: List["Transacao"], intervalo: Intervalo):
        transacoes_no_periodo = [transacao for transacao in transacoes if intervalo.contem(transacao.competencia)]

        soma = 0

        for transacao in transacoes_no_periodo:
            soma += transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor

        return soma