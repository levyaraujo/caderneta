import re


def detectar_metodo_pagamento(texto):
    """
    Detecta método de pagamento a partir de uma string usando expressões regulares.

    Args:
        texto (str): String de entrada para análise

    Returns:
        str: Método de pagamento detectado ou 'desconhecido' se nenhum for encontrado
    """
    # Converte entrada para minúsculo para correspondência sem distinção de maiúsculas/minúsculas
    texto = texto.lower().strip()

    # Padrões para cartões de crédito/débito
    padroes_cartao = {
        "credito": r"\b(crédito|credito|cartão de crédito|cartao de credito)\b",
        "debito": r"\b(débito|debito|cartão de débito|cartao de debito)\b",
        "vale": r"\b(vale refeição|vale alimentação|vr|va|sodexo|alelo|ticket)\b",
        "visa": r"\b(visa|4[0-9]{12}(?:[0-9]{3})?)\b",
        "mastercard": r"\b(mastercard|master card|5[1-5][0-9]{14})\b",
        "elo": r"\b(elo)\b",
        "hipercard": r"\b(hipercard)\b",
    }

    # Padrões para pagamentos digitais
    padroes_digitais = {
        "pix": r"\b(pix|chave pix)\b",
        "paypal": r"\b(paypal|pp)\b",
        "mercadopago": r"\b(mercado pago|mercadopago)\b",
        "picpay": r"\b(picpay)\b",
        "pagbank": r"\b(pagbank|pagseguro)\b",
        "apple_pay": r"\b(apple pay|applepay)\b",
        "google_pay": r"\b(google pay|googlepay|g pay|gpay)\b",
        "samsung_pay": r"\b(samsung pay|samsungpay)\b",
    }

    # Padrões para transferências bancárias
    padroes_banco = {
        "transferencia": r"\b(transferência|transferencia bancária|transferencia bancaria|ted|doc)\b",
        "boleto": r"\b(boleto|boleto bancário|boleto bancario)\b",
    }

    # Outros padrões de pagamento
    outros_padroes = {
        "dinheiro": r"\b(dinheiro|espécie|especie|cash)\b",
        "cheque": r"\b(cheque)\b",
        "vale_presente": r"\b(vale presente|gift card|giftcard)\b",
        "fiado": r"\b(fiado|caderneta|caderninho)\b",
    }

    # Combina todos os padrões
    todos_padroes = {**padroes_cartao, **padroes_digitais, **padroes_banco, **outros_padroes}

    # Verifica cada padrão
    for metodo, padrao in todos_padroes.items():
        if re.search(padrao, texto):
            return metodo

    return "desconhecido"
