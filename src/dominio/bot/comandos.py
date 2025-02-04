import calendar
import logging
import os
import random
import string
from datetime import datetime
from typing import List, Any, Tuple

import dotenv

from const import REGEX_WAMID, MENSAGEM_CADASTRO_BPO
from src.dominio.bot.entidade import GerenciadorComandos
from src.dominio.bpo.onboard import OnboardBPO
from src.dominio.graficos.services import (
    criar_grafico_fluxo_de_caixa,
    criar_grafico_receitas_e_despesas,
    criar_grafico_lucro,
)
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.dominio.usuario.onboard import UserContext, OnboardingState, UserData
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.datas import intervalo_mes_atual, ultima_hora, primeira_hora
from src.utils.geradores import gerar_codigo_bpo
from src.utils.uploader import Uploader
from src.utils.validadores import validar_telefone

bot = GerenciadorComandos()

dotenv.load_dotenv()

STATIC = os.getenv("STATIC_URL")


@bot.comando("ola", "Mostra ajuda", aliases=["oi"])
def saudacao(*args: List[str], **kwargs: Any) -> str:
    nome_usuario = kwargs.get("nome_usuario")
    return f"Olá, {nome_usuario}!\n{bot.ajuda()}"


@bot.comando("ajuda", "Mostra comandos disponíveis")
def ajuda(*args: List[str], **kwargs: Any) -> str:
    ajuda: str = bot.ajuda()
    return ajuda


@bot.comando("listar fluxo", "Lista fluxo de caixa no mês", aliases=["fluxo", "fluxo mm/aa"])
def listar_fluxo(*args: List[str], **kwargs: Any) -> str:
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()
    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(usuario_id=usuario.id, intervalo=intervalo)

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    return "\n".join(
        f"{transacao.caixa.strftime('%d/%m')} "
        f"{'✅' if transacao.tipo == TipoTransacao.CREDITO else '🔻'} "
        f"{Real(transacao.valor)} | *{transacao.categoria}*"
        for transacao in transacoes
    )


@bot.comando("grafico fluxo", "Devolve gráfico de fluxo de caixa do mês", aliases=["grafico fluxo mm/aa"])
def grafico_fluxo(*args: List[str], **kwargs: Any) -> str:
    uploader = Uploader()
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario_ordenando_por_data_e_valor(
        usuario_id=usuario.id, intervalo=intervalo
    )

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    grafico = criar_grafico_fluxo_de_caixa(transacoes=transacoes)
    nome_arquivo = f"{grafico['nome_arquivo']}.png"
    caminho_arquivo: str = uploader.upload_file(nome_arquivo, grafico["dados"])
    return caminho_arquivo


@bot.comando(
    "receitas e despesas", "Devolve gráfico de receitas e despesas mo mês", aliases=["balanco", "balanco mm/aa"]
)
def grafico_balanco(*args: List[str], **kwargs: Any) -> str:
    now = datetime.now()
    uploader = Uploader()
    inicio = primeira_hora(now.replace(day=1))
    ultimo_dia = calendar.monthrange(now.year, now.month)[1]
    fim = ultima_hora(now.replace(day=ultimo_dia))

    if "anual" in args:
        inicio = datetime(year=now.year, month=1, day=1)
        fim = ultima_hora(datetime(year=now.year, month=12, day=31))

    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual(inicio=inicio, fim=fim)

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(usuario_id=usuario.id, intervalo=intervalo)

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    grafico = criar_grafico_receitas_e_despesas(transacoes=transacoes)
    nome_arquivo = f"{grafico['nome_arquivo']}.png"

    caminho_arquivo: str = uploader.upload_file(nome_arquivo, grafico["dados"])

    return caminho_arquivo


@bot.comando("lucro", "Gráfico de lucro, receitas e gastos")
def lucro(*args: List[str], **kwargs: Any) -> str:
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()
    uploader = Uploader()

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(usuario_id=usuario.id, intervalo=intervalo)

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    grafico = criar_grafico_lucro(transacoes=transacoes)
    nome_arquivo = f"{grafico['nome_arquivo']}.png"
    caminho_arquivo: str = uploader.upload_file(nome_arquivo, grafico["dados"])
    return caminho_arquivo


@bot.comando(REGEX_WAMID, "Remove transação por wamid", oculto=True)
def remover_transacao(*args: Tuple[str], **kwargs: Any) -> str:
    wamid_transacao = str(args[0])
    usuario: Usuario = kwargs.get("usuario")
    uow = UnitOfWork(session_factory=get_session)

    try:
        with uow:
            transacao = bot.repo_transacao_leitura.buscar_por_wamid(wamid_transacao, usuario.id)

            uow.repo_escrita.remover(transacao)
            uow.commit()
        return "Lançamento removido com sucesso! ✅"

    except Exception as e:
        logging.error(f"Ocorreu um erro ao remover transação", exc_info=True)
        return "Não foi possível remover a transação."


@bot.comando("exportar", "Exporta lançamento em formato excel")
def exportar(*args: Tuple[str], **kwargs: Any) -> str:
    import pandas as pd
    from io import BytesIO
    from datetime import datetime

    usuario: Usuario = kwargs.get("usuario")

    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(intervalo=intervalo, usuario_id=usuario.id)
    dados = [transacao.dicionario() for transacao in transacoes]

    df = pd.DataFrame(dados)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    excel_bytes = buffer.getvalue()

    nome_do_arquivo = f"lancamentos_{usuario.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls"

    uploader = Uploader()
    url_arquivo: str = uploader.upload_file(nome_do_arquivo, excel_bytes)

    return url_arquivo


@bot.comando("adicionar bpo", "Adiciona um usuário BPO ao usuário", aliases=["add bpo", "adicionar bpo"])
def adicionar_bpo(*args: str, **kwargs: Any) -> str:
    usuario: Usuario = kwargs.get("usuario")

    onboard = OnboardBPO()
    if not args:
        return "Informe o número de WhatsApp do BPO. Ex.: *add bpo 11984033357*"

    try:
        numero_bpo = next(numero for numero in args if validar_telefone(numero))
        codigo_bpo = gerar_codigo_bpo()
        context = UserContext(
            state=OnboardingState.WAITING_FULL_NAME,
            data=UserData(telefone=numero_bpo, cliente=str(usuario.id)),
        )
        onboard._save_user_context(f"bpo_{numero_bpo}", context)

        return MENSAGEM_CADASTRO_BPO % (usuario.nome, codigo_bpo)

    except StopIteration:
        return "Informe um número válido. Ex.: *add bpo 11984033357*"
