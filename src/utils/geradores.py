import random
import string


def gerar_codigo_bpo(tamanho: int = 6):
    return "".join(random.choices(string.digits, k=tamanho))
