import os
from datetime import datetime
from random import choice

import pytest
from freezegun import freeze_time

from src.dominio.bot.comandos import bot
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.transacao.tipos import TipoTransacao
from src.infra.database.uow import UnitOfWork
from src.libs.tipos import Intervalo
from tests.comandos.dados_teste import DADOS_TESTE_COMANDOS


@pytest.mark.parametrize(
    "mensagem",
    [
        "listar recebimentos",
        "listar despesas",
        "vendi 150 vestido pix",
        "paguei 850 receita federal",
    ],
)
@pytest.mark.asyncio
async def test_comando_nao_existe(mensagem):
    with pytest.raises(ComandoDesconhecido) as exc_info:
        await bot.processar_mensagem(mensagem)

    assert isinstance(exc_info.value, ComandoDesconhecido)
    assert exc_info.match("Comando não existe")


@pytest.mark.parametrize("mensagem, esperado", DADOS_TESTE_COMANDOS)
@pytest.mark.asyncio
@freeze_time(datetime(2024, 10, 26))
async def test_comandos_validos(mensagem, esperado, mock_usuario, transacao_gen, session):
    uow = UnitOfWork(session_factory=lambda: session)
    usuario = mock_usuario

    with uow:
        for dia in range(1, 4):
            transacao = transacao_gen(
                usuario,
                100.0,
                "Loja A",
                TipoTransacao.CREDITO,
                caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
            )
            uow.repo_escrita.adicionar(transacao)

        for dia in range(4, 6):
            transacao = transacao_gen(
                usuario,
                100.0,
                "Loja B",
                TipoTransacao.DEBITO,
                caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
            )
            uow.repo_escrita.adicionar(transacao)
        uow.commit()

    intervalo = Intervalo(inicio=datetime(2024, 10, 1), fim=datetime(2024, 10, 31))
    assert await bot.processar_mensagem(mensagem, nome_usuario="Levy", usuario=usuario, intervalo=intervalo) == esperado


@pytest.mark.asyncio
@freeze_time(datetime(2024, 10, 28))
async def test_grafico_fluxo(mock_usuario, transacao_gen, session):
    uow = UnitOfWork(session_factory=lambda: session)
    usuario = mock_usuario
    with uow:
        for dia in range(1, 4):
            transacao = transacao_gen(
                usuario,
                100.0,
                "Loja A",
                TipoTransacao.CREDITO,
                caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
            )
            uow.repo_escrita.adicionar(transacao)

        for dia in range(4, 6):
            transacao = transacao_gen(
                usuario,
                100.0,
                "Loja B",
                TipoTransacao.DEBITO,
                caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
            )
            uow.repo_escrita.adicionar(transacao)
        uow.commit()

    mensagem = "grafico fluxo"
    intervalo = Intervalo(inicio=datetime(2024, 10, 1), fim=datetime(2024, 10, 31))
    resposta = await bot.processar_mensagem(mensagem, nome_usuario="Levy", usuario=usuario, intervalo=intervalo)
    print(resposta)

    assert resposta.startswith(os.getenv("STATIC_URL"))
