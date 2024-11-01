import re
import unicodedata

from src.dominio.transacao.exceptions import TipoTransacaoInvalido
from src.dominio.transacao.tipos import TipoTransacao


def validar_email(email: str) -> bool:
    padrao = re.compile(
        r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"
        r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@'
        r"(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\["
        r"(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|"
        r"1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:"
        r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+))"
    )
    if not re.match(padrao, email):
        raise ValueError("Formato de email inválido")
    return True


def validar_telefone(telefone: str) -> bool:
    padrao = r"^(55)?([1-9]{2})(9\d{8})$"
    if not re.match(padrao, telefone):
        raise ValueError(
            "Formato de telefone celular inválido. Use apenas números: 2 ou 3 dígitos de DDD + 9 dígitos do número."
        )
    return True


def validar_tipo_da_transacao(tipo) -> None:
    if tipo not in [TipoTransacao.DEBITO, TipoTransacao.CREDITO, "credito", "debito"]:
        raise TipoTransacaoInvalido(
            "O tipo desse transacao deve ser TipoTransacao.DEBITO ou TipoTransacao.CREDITO"
        )


def limpar_texto(texto: str) -> str:
    """
    Normaliza e limpa o texto removendo acentos.
    Args:
        texto (str): O texto a ser limpado.
    Returns:
        str: O texto sem acentos.
    """
    # Normaliza e remove acentos
    nfkd = unicodedata.normalize("NFKD", texto)
    texto_sem_acentos = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return texto_sem_acentos.strip()
