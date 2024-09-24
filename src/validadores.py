import re

from src.dominio.transacao.excecoes import TipoTransacaoInvalido
from src.dominio.transacao.tipos import TipoTransacao


def validar_email(email: str) -> bool:
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(padrao, email):
        raise ValueError("Formato de email inválido")
    return True


def validar_telefone(telefone: str) -> bool:
    # Padrão para celular brasileiro: 10 ou 11 dígitos (2 ou 3 para DDD + 9 para o número)
    padrao = r"^([1-9]{2})(9\d{8})$"
    if not re.match(padrao, telefone):
        raise ValueError(
            "Formato de telefone celular inválido. Use apenas números: 2 ou 3 dígitos de DDD + 9 dígitos do número."
        )
    return True


def validar_tipo_da_transacao(tipo):
    if tipo not in [TipoTransacao.DEBITO, TipoTransacao.CREDITO]:
        raise TipoTransacaoInvalido(
            "O tipo desse transacao deve ser TipoTransacao.DEBITO ou TipoTransacao.CREDITO"
        )
