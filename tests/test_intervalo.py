import pytest
from datetime import datetime
from src.libs.tipos import Intervalo


def test_intervalo_inicializacao():
    inicio = datetime(2023, 1, 1)
    fim = datetime(2023, 1, 2)
    intervalo = Intervalo(inicio, fim)
    assert intervalo.inicio == inicio
    assert intervalo.fim == fim


def test_intervalo_inicializacao_invalida():
    inicio = datetime(2023, 1, 2)
    fim = datetime(2023, 1, 1)
    with pytest.raises(ValueError):
        Intervalo(inicio, fim)


def test_intervalo_repr():
    inicio = datetime(2023, 1, 1)
    fim = datetime(2023, 1, 2)
    intervalo = Intervalo(inicio, fim)
    assert repr(intervalo) == f"Intervalo({inicio}, {fim})"


def test_intervalo_contem():
    inicio = datetime(2023, 1, 1)
    fim = datetime(2023, 1, 3)
    intervalo = Intervalo(inicio, fim)

    assert intervalo.contem(datetime(2023, 1, 2))
    assert intervalo.contem(inicio)
    assert intervalo.contem(fim)
    assert not intervalo.contem(datetime(2022, 12, 31))
    assert not intervalo.contem(datetime(2023, 1, 4))


def test_intervalo_interseccao():
    intervalo1 = Intervalo(datetime(2023, 1, 1), datetime(2023, 1, 3))
    intervalo2 = Intervalo(datetime(2023, 1, 2), datetime(2023, 1, 4))
    intervalo3 = Intervalo(datetime(2023, 1, 4), datetime(2023, 1, 5))

    interseccao = intervalo1.interseccao(intervalo2)
    assert interseccao.inicio == datetime(2023, 1, 2)
    assert interseccao.fim == datetime(2023, 1, 3)

    assert intervalo1.interseccao(intervalo3) is None


def test_intervalo_uniao():
    intervalo1 = Intervalo(datetime(2023, 1, 1), datetime(2023, 1, 3))
    intervalo2 = Intervalo(datetime(2023, 1, 2), datetime(2023, 1, 4))
    intervalo3 = Intervalo(datetime(2023, 1, 5), datetime(2023, 1, 6))

    uniao = intervalo1.uniao(intervalo2)
    assert uniao.inicio == datetime(2023, 1, 1)
    assert uniao.fim == datetime(2023, 1, 4)

    assert intervalo1.uniao(intervalo3) is None


@pytest.fixture
def intervalo_padrao():
    return Intervalo(datetime(2023, 1, 1), datetime(2023, 1, 3))


def test_intervalo_com_fixture(intervalo_padrao):
    assert intervalo_padrao.contem(datetime(2023, 1, 2))
    assert not intervalo_padrao.contem(datetime(2023, 1, 4))
