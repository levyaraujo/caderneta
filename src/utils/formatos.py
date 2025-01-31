import re
from datetime import datetime, date


def formatar_telefone(telefone: str) -> str:
    """
    Formata número de telefone para o pdrão brasileiro, com código de país, DDD e 9 adicional

    5511900001111
    """
    return telefone.replace("whatsapp:+", "")[:4] + "9" + telefone[4:]


def datetime_para_br(data: datetime | date) -> str:
    return data.strftime("%d/%m/%Y %H:%M:%S")


def is_valid_date_format(date_str):
    pattern = r"^(0?[1-9]|1[0-2])/(?:\d{2}|\d{4})$"
    return bool(re.match(pattern, date_str))
