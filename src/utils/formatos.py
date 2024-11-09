def formatar_telefone(telefone: str):
    """
    Formata número de telefone para o pdrão brasileiro, com código de país, DDD e 9 adicional

    5511900001111
    """
    return telefone.replace("whatsapp:+", "")[:4] + "9" + telefone[4:]
