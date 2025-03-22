import re
import unicodedata

from src.dominio.transacao.exceptions import TipoTransacaoInvalido
from src.dominio.transacao.tipos import TipoTransacao


def validar_email(email: str) -> bool:
    padrao = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if not re.match(padrao, email):
        raise ValueError("Formato de email inválido")

    if len(email) > 254:
        raise ValueError("Email muito longo")

    local_part = email.split("@")[0]
    if len(local_part) > 64:
        raise ValueError("Parte local do email muito longa")

    return True


def validar_telefone(telefone: str) -> bool:
    padrao = r"^(55)?([1-9]{2})(9\d{8})$"
    if not re.match(padrao, telefone):
        raise ValueError(
            "Formato de telefone celular inválido. Use apenas números: 2 ou 3 dígitos de DDD + 9 dígitos do número."
        )
    return True


def validar_tipo_da_transacao(tipo: TipoTransacao) -> None:
    if tipo not in [TipoTransacao.DEBITO, TipoTransacao.CREDITO, "credito", "debito"]:
        raise TipoTransacaoInvalido("O tipo desse transacao deve ser TipoTransacao.DEBITO ou TipoTransacao.CREDITO")


def limpar_texto(texto: str) -> str:
    """
    Normaliza e limpa o texto removendo acentos.
    Args:
        texto (str): O texto a ser limpado.
    Returns:
        str: O texto sem acentos.
    """
    # Normaliza e remove acentos
    texto.replace("r $", "")
    nfkd = unicodedata.normalize("NFKD", texto)
    texto_sem_acentos = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return texto_sem_acentos.strip()
