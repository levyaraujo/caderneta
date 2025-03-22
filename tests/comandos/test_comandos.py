import os
from datetime import datetime
from random import choice
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from const import MENSAGEM_CADASTRO_BPO
from src.dominio.bot.comandos import bot
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto, DadosTransacao, ConstrutorTransacao
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
        await bot.processar_comando(mensagem)

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
    assert await bot.processar_comando(mensagem, nome_usuario="Levy", usuario=usuario, intervalo=intervalo) == esperado


# @pytest.mark.asyncio
# @freeze_time(datetime(2024, 10, 28))
# async def test_grafico_fluxo(mock_usuario, transacao_gen, session):
#     uow = UnitOfWork(session_factory=lambda: session)
#     usuario = mock_usuario
#     with uow:
#         for dia in range(1, 4):
#             transacao = transacao_gen(
#                 usuario,
#                 100.0,
#                 "Loja A",
#                 TipoTransacao.CREDITO,
#                 caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
#             )
#             uow.repo_escrita.adicionar(transacao)
#
#         for dia in range(4, 6):
#             transacao = transacao_gen(
#                 usuario,
#                 100.0,
#                 "Loja B",
#                 TipoTransacao.DEBITO,
#                 caixa=datetime(year=datetime.now().year, month=datetime.now().month, day=dia),
#             )
#             uow.repo_escrita.adicionar(transacao)
#         uow.commit()
#
#     mensagem = "grafico fluxo"
#     intervalo = Intervalo(inicio=datetime(2024, 10, 1), fim=datetime(2024, 10, 31))
#     resposta = await bot.processar_comando(mensagem, nome_usuario="Levy", usuario=usuario, intervalo=intervalo)
#     print(resposta)
#
#     assert resposta.startswith(os.getenv("STATIC_URL"))


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


@pytest.mark.parametrize(
    "comando", [{"mensagem": "paguei 53.78 para receita federal em 2025-03-20 13:42:29", "tipo": "DEBITO"}]
)
def test_comando_transacao_retorna_mensagem_interativa(comando, mock_usuario, session, mock_payload_whatsapp):
    usuario = mock_usuario
    dados_whatsapp = mock_payload_whatsapp
    uow = UnitOfWork(session_factory=lambda: session)
    resposta = comando_criar_transacao(
        usuario, comando["tipo"].upper(), comando["mensagem"], uow, usuario.telefone, dados_whatsapp
    )

    assert isinstance(resposta, dict)


@pytest.mark.parametrize(
    "acao, mensagem, esperado",
    [
        (
            TipoTransacao.DEBITO,
            "paguei 53.78 para receita federal em 2025-03-20 13:42:29",
            DadosTransacao(
                tipo=TipoTransacao.DEBITO,
                valor=53.78,
                metodo_pagamento=None,
                categoria="receita federal",
                data=datetime(2025, 3, 20, 13, 42, 29),
                mensagem_original="paguei 53.78 para receita federal em 2025-03-20 13:42:29",
            ),
        ),
        (
            TipoTransacao.CREDITO,
            "recebi 1.000,50 de salário em 20/03",
            DadosTransacao(
                tipo=TipoTransacao.CREDITO,
                valor=1000.50,
                metodo_pagamento=None,
                categoria="salário",
                data=datetime(datetime.now().year, 3, 20),
                mensagem_original="recebi 1.000,50 de salário em 20/03",
            ),
        ),
        (
            TipoTransacao.DEBITO,
            "gastei 10.500,75 no aluguel em 2025-03-01 08:00:00",
            DadosTransacao(
                tipo=TipoTransacao.DEBITO,
                valor=10500.75,
                metodo_pagamento=None,
                categoria="aluguel",
                data=datetime(2025, 3, 1, 8, 0, 0),
                mensagem_original="gastei 10.500,75 no aluguel em 2025-03-01 08:00:00",
            ),
        ),
        (
            TipoTransacao.DEBITO,
            "paguei 150 no mercado pix em 15/03",
            DadosTransacao(
                tipo=TipoTransacao.DEBITO,
                valor=150.0,
                metodo_pagamento="pix",
                categoria="mercado",
                data=datetime(datetime.now().year, 3, 15),
                mensagem_original="paguei 150 no mercado pix em 15/03",
            ),
        ),
    ],
)
def test_parse_message(acao, mensagem, esperado):
    parser = ConstrutorTransacao(acao)
    resultado = parser.parse_message(mensagem)

    assert resultado.tipo == esperado.tipo
    assert resultado.valor == esperado.valor
    assert resultado.metodo_pagamento == esperado.metodo_pagamento
    assert resultado.categoria == esperado.categoria
    assert resultado.data == esperado.data
    assert resultado.mensagem_original == esperado.mensagem_original


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
        await bot.processar_comando(wamid, nome_usuario="Levy", usuario=usuario, intervalo=intervalo)
        == "Lançamento removido com sucesso! ✅"
    )


@pytest.mark.asyncio
async def test_adicionar_bpo(mock_usuario):
    usuario = mock_usuario
    with patch("src.dominio.bot.comandos.gerar_codigo_bpo", return_value="123456"):
        resposta = await bot.processar_comando("adicionar bpo 94992302731", nome_usuario=usuario.nome, usuario=usuario)

    assert resposta == MENSAGEM_CADASTRO_BPO % (usuario.nome, "123456")
