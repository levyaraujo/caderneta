import os
from datetime import datetime
from random import choice

import pytest
from freezegun import freeze_time

from src.dominio.bot.comandos import bot
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto
from src.dominio.transacao.services import comando_criar_transacao
from src.dominio.transacao.tipos import TipoTransacao
from src.infra.database.uow import UnitOfWork
from src.libs.tipos import Intervalo
from tests.comandos.dados_teste import DADOS_TESTE_COMANDOS
from tests.conftest import gerar_wamid


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


@pytest.mark.asyncio
@pytest.mark.parametrize("mensagem", ["sakdgafkbasfjh", "nada"])
async def test_integracao_resposta_usuario(mensagem, cli_bot, mock_usuario, session):
    from src.dominio.bot.resources import responder_usuario

    uow = UnitOfWork(session_factory=lambda: session)

    usuario = mock_usuario
    resposta = await responder_usuario(
        mensagem=mensagem, usuario=usuario, telefone=usuario.telefone, robo=cli_bot, uow=uow
    )

    assert resposta == f"Comando {mensagem} não existe\n\nDigite *ajuda* e veja os comandos disponíveis."


@pytest.mark.parametrize("comando", ["vendi 150 vestido"])
def test_comando_transacao_retorna_mensagem_interativa(comando, mock_usuario, session, mock_payload_whatsapp):
    usuario = mock_usuario
    dados_whatsapp = mock_payload_whatsapp
    uow = UnitOfWork(session_factory=lambda: session)
    classificador = ClassificadorTexto()
    tipo, _ = classificador.classificar_mensagem(comando)
    resposta = comando_criar_transacao(usuario, tipo.upper(), comando, uow, usuario.telefone, dados_whatsapp)

    assert isinstance(resposta, dict)


@pytest.mark.asyncio
async def test_remover_transacao_por_wamid(mock_usuario, session, transacao_gen, gerar_wamid):
    uow = UnitOfWork(session_factory=lambda: session)
    usuario = mock_usuario

    wamid = gerar_wamid

    with uow:
        transacao = transacao_gen(
            usuario,
            100.0,
            "Loja A",
            TipoTransacao.CREDITO,
            caixa=datetime.now(),
            wamid=wamid,
        )
        uow.repo_escrita.adicionar(transacao)
        uow.commit()

    intervalo = Intervalo(inicio=datetime(2024, 10, 1), fim=datetime(2024, 10, 31))
    assert (
        await bot.processar_mensagem(wamid, nome_usuario="Levy", usuario=usuario, intervalo=intervalo)
        == "Transação removida com sucesso! ✅"
    )
