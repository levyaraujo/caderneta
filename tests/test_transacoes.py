from random import randint
from typing import Dict, List

import pytest
from freezegun import freeze_time
from datetime import datetime

from src.dominio.transacao.services import _calcular_caixa, _calcular_competencia
from src.libs.tipos import Intervalo
from src.dominio.transacao.exceptions import TipoTransacaoInvalido, WamIdInvalido
from src.dominio.transacao.entidade import Transacao, TipoTransacao


def test_criacao_transacao(mock_usuario, transacao_gen):
    transacao = transacao_gen(mock_usuario, 100.0, "Loja A", TipoTransacao.DEBITO)

    assert isinstance(transacao, Transacao)
    assert transacao.usuario == mock_usuario
    assert transacao.valor == 100.0
    assert transacao.destino == "Loja A"
    assert transacao.tipo == TipoTransacao.DEBITO
    assert isinstance(transacao.caixa, datetime)
    assert isinstance(transacao.competencia, datetime)


def test_tipo_transacao_enum():
    assert TipoTransacao.DEBITO.value == "debito"
    assert TipoTransacao.CREDITO.value == "credito"


def test_transacao_campos_opcionais(mock_usuario, transacao_gen):
    transacao = transacao_gen(mock_usuario, 100.0, None, TipoTransacao.CREDITO)

    assert transacao.destino is None
    assert isinstance(transacao.descricao, str)


def test_transacao_com_tipo_errado(mock_usuario, transacao_gen):
    with pytest.raises(TipoTransacaoInvalido) as excinfo:
        transacao_gen(mock_usuario, 100.0, None, "outros")
    assert str(excinfo.value) == "O tipo desse transacao deve ser TipoTransacao.DEBITO ou TipoTransacao.CREDITO"


@freeze_time(datetime(2024, 9, 1))
def test_fluxo_competencia(mock_usuario, transacao_gen):
    usuario = mock_usuario
    transacoes_por_usuario: Dict[int, List[Transacao]] = {usuario.id: []}

    for _ in range(10):
        transacoes_por_usuario[usuario.id].append(
            transacao_gen(
                usuario=usuario,
                valor=150,
                destino="Eletronicos",
                tipo=TipoTransacao.CREDITO,
                caixa=datetime(2024, 9, randint(1, 30)),
            )
        )

    transacoes_por_usuario[usuario.id].append(
        transacao_gen(
            usuario=usuario,
            valor=150,
            destino="Eletronicos",
            tipo=TipoTransacao.DEBITO,
            caixa=datetime(2024, 9, randint(1, 30)),
        )
    )

    for _ in range(15):
        transacoes_por_usuario[usuario.id].append(
            transacao_gen(
                usuario=usuario,
                valor=250,
                destino="Eletronicos",
                tipo=TipoTransacao.CREDITO,
                caixa=datetime(2024, randint(10, 12), randint(1, 30)),
            )
        )

    competencia = _calcular_competencia(
        transacoes_por_usuario[usuario.id],
        Intervalo(inicio=datetime(2024, 9, 1), fim=datetime(2024, 9, 30)),
    )

    assert competencia == 1350


def test_fluxo_caixa(mock_usuario, transacao_gen):
    usuario = mock_usuario
    transacoes_por_usuario: Dict[int, List[Transacao]] = {usuario.id: []}

    for _ in range(10):
        transacoes_por_usuario[usuario.id].append(
            transacao_gen(
                usuario=usuario,
                valor=150,
                destino="Eletronicos",
                tipo=TipoTransacao.CREDITO,
                caixa=datetime(2024, 9, randint(1, 30)),
            )
        )

    transacoes_por_usuario[usuario.id].append(
        transacao_gen(
            usuario=usuario,
            valor=150,
            destino="Eletronicos",
            tipo=TipoTransacao.DEBITO,
            caixa=datetime(2024, 9, randint(1, 30)),
        )
    )

    caixa = _calcular_caixa(
        transacoes_por_usuario[usuario.id],
        Intervalo(inicio=datetime(2024, 9, 1), fim=datetime(2024, 9, 30)),
    )

    assert caixa == 1350


@pytest.mark.parametrize("wamid", ["nada", "ashfasgfuigua", "wamid."])
def test_wamid_transacao_invalido(mock_usuario, wamid):
    usuario = mock_usuario

    with pytest.raises(WamIdInvalido) as excinfo:
        transacao = Transacao(
            usuario=usuario,
            valor=150,
            categoria="aidasasf",
            tipo=TipoTransacao.DEBITO,
            descricao="asodihasjklfnasfr",
            caixa=datetime.now(),
            wamid=wamid,
        )

    assert str(excinfo.value) == f"wamid inválido: {wamid}"
