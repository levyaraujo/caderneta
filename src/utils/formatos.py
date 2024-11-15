def formatar_telefone(telefone: str):
    """
    Formata número de telefone para o padrão brasileiro, com código de país, DDD e 9 adicional

    5511900001111
    """
    telefone = telefone.replace("whatsapp:+", "").strip()

    if telefone.startswith("55"):
        return telefone[:4] + "9" + telefone[4:]
    return "55" + telefone[0:2] + "9" + telefone[2:]
