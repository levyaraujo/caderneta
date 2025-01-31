import pytest
from src.utils.datas import *


@pytest.mark.parametrize("mes_ano", ["05/25", "03/2025", "1/25", "1/2025"])
def test_converter_mes_e_ano_para_datetime(mes_ano):
    data_em_datetime = mes_e_ano_para_datetime(mes_ano=mes_ano)
    assert isinstance(data_em_datetime, datetime)


@pytest.mark.parametrize("mes_ano", ["05/25", "03/2025", "1/25", "1/2025"])
def test_criar_intervalo_do_mes(mes_ano):
    data_em_datetime = mes_e_ano_para_datetime(mes_ano=mes_ano)

    intervalo = intervalo_mes_atual(data_em_datetime)

    assert isinstance(intervalo, Intervalo)
