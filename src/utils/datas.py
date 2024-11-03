import calendar
from datetime import datetime

from src.libs.tipos import Intervalo


def primeira_hora(data: datetime) -> datetime:
    """
    Recebe um datetime e retorna o datetime com as horas e minutos zerados.
    Exemplo:
        date = datetime(2024, 11, 1, 23, 45, 59)
        return datetime(2024, 11, 1, 0, 0, 0)
    :param data: datetime
    :return: datetime
    """
    if not isinstance(data, datetime):
        raise ValueError("O parâmetro data deve ser um objeto datetime.")

    return data.replace(hour=0, minute=0, second=0, microsecond=0)


def ultima_hora(data: datetime) -> datetime:
    """
    Recebe um datetime e retorna com a última hora do dia.
    Exemplo:
        date = datetime(2024, 11, 1)
        return datetime(2024, 11, 1, 23, 59, 59, 999999)
    :param data: datetime
    :return: datetime
    """

    if not isinstance(data, datetime):
        raise ValueError("O parâmetro data deve ser um objeto datetime.")

    return data.replace(hour=23, minute=59, second=59, microsecond=999999)


def intervalo_mes_atual(inicio: datetime | None = None, fim: datetime | None = None):
    now = datetime.now()

    if not inicio and not fim:
        inicio = primeira_hora(now.replace(day=1))
        ultimo_dia = calendar.monthrange(now.year, now.month)[1]
        fim = ultima_hora(now.replace(day=ultimo_dia))

    return Intervalo(inicio, fim)
