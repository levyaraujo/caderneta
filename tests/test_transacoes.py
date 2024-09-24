import dataclasses
from random import randint

import pytest
from datetime import datetime

from src.libs.tipos import Intervalo
from src.dominio.transacao.excecoes import TipoTransacaoInvalido
from src.dominio.transacao.entidade import Transacao, TipoTransacao


def test_criacao_transacao(usuario, transacao_gen):
    transacao = transacao_gen(usuario, 100.0, "Loja A", TipoTransacao.DEBITO)

    assert isinstance(transacao, Transacao)
    assert isinstance(transacao.id, int)
    assert transacao.usuario == usuario
    assert transacao.valor == 100.0
    assert transacao.destino == "Loja A"
    assert transacao.tipo == TipoTransacao.DEBITO
    assert isinstance(transacao.caixa, datetime)
    assert isinstance(transacao.competencia, datetime)
    assert transacao.apagado is False


def test_transacao_imutabilidade(usuario, transacao_gen):
    transacao = transacao_gen(usuario, 100.0, "Loja A", TipoTransacao.DEBITO)

    with pytest.raises(dataclasses.FrozenInstanceError):
        transacao.valor = 200.0


def test_tipo_transacao_enum():
    assert TipoTransacao.DEBITO.value == "debito"
    assert TipoTransacao.CREDITO.value == "credito"


def test_transacao_campos_opcionais(usuario, transacao_gen):
    transacao = transacao_gen(usuario, 100.0, None, TipoTransacao.CREDITO)

    assert transacao.destino is None
    assert isinstance(transacao.descricao, str)


def test_transacao_com_tipo_errado(usuario, transacao_gen):
    with pytest.raises(TipoTransacaoInvalido) as excinfo:
        transacao_gen(usuario, 100.0, None, "outros")
    assert (
        str(excinfo.value)
        == "O tipo desse transacao deve ser TipoTransacao.DEBITO ou TipoTransacao.CREDITO"
    )


def test_fluxo_competencia(usuario, transacao_gen):
    usuario = usuario
    transacoes_por_usuario = {usuario.id: []}

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

    competencia = usuario._calcular_competencia(
        transacoes_por_usuario[usuario.id],
        Intervalo(inicio=datetime(2024, 9, 1), fim=datetime(2024, 9, 30)),
    )

    assert competencia == 5100


def test_fluxo_caixa(usuario, transacao_gen):
    usuario = usuario
    transacoes_por_usuario = {usuario.id: []}

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

    caixa = usuario._calcular_caixa(
        transacoes_por_usuario[usuario.id],
        Intervalo(inicio=datetime(2024, 9, 1), fim=datetime(2024, 9, 30)),
    )

    assert caixa == 1350
