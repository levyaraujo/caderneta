import calendar
import os
from datetime import datetime

import dotenv

from src.dominio.bot.entidade import GerenciadorComandos
from src.dominio.graficos.services import (
    criar_grafico_fluxo_de_caixa,
    criar_grafico_receitas_e_despesas,
)
from src.dominio.transacao.entidade import Real
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.entidade import Usuario
from src.utils.datas import intervalo_mes_atual, ultima_hora, primeira_hora
from src.utils.uploader import Uploader

bot = GerenciadorComandos()

dotenv.load_dotenv()

STATIC = os.getenv("STATIC_URL")


@bot.comando("ola", "Mostra ajuda", aliases=["oi"])
def saudacao(*args, **kwargs):
    nome_usuario = kwargs.get("nome_usuario")
    return f"Olá, {nome_usuario}!\n\n\n{bot.ajuda()}"


@bot.comando("ajuda", "Mostra comandos disponíveis")
def ajuda(*args, **kwargs):
    return bot.ajuda()


@bot.comando("listar fluxo", "Lista fluxo de caixa no mês atual", aliases=["fluxo"])
def listar_fluxo(*args, **kwargs):
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()
    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(
        usuario_id=usuario.id, intervalo=intervalo
    )

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    return "\n".join(
        f"{transacao.caixa.strftime('%d/%m')} "
        f"{'✅' if transacao.tipo == TipoTransacao.CREDITO else '🔻'} "
        f"{Real(transacao.valor)} | *{transacao.categoria}*"
        for transacao in transacoes
    )


@bot.comando("grafico fluxo", "Devolve gráfico de fluxo de caixa do mês atual")
def grafico_fluxo(*args, **kwargs):
    uploader = Uploader()
    usuario: Usuario = kwargs.get("usuario")
    intervalo = kwargs.get("intervalo") or intervalo_mes_atual()

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(
        usuario_id=usuario.id, intervalo=intervalo
    )

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    grafico = criar_grafico_fluxo_de_caixa(transacoes=transacoes)
    nome_arquivo = f"{grafico['nome_arquivo']}.png"
    caminho_arquivo = uploader.upload_file(nome_arquivo, grafico["dados"])
    return caminho_arquivo


@bot.comando(
    "grafico balanco", "Devolve gráfico de receitas e despesas", aliases=["balanco"]
)
def grafico_balanco(*args, **kwargs):
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

    transacoes = bot.repo_transacao_leitura.buscar_por_intervalo_e_usuario(
        usuario_id=usuario.id, intervalo=intervalo
    )

    if not transacoes:
        return "Você ainda não registrou nenhuma despesa ou receita este mês"

    grafico = criar_grafico_receitas_e_despesas(transacoes=transacoes)
    nome_arquivo = f"{grafico['nome_arquivo']}.png"

    caminho_arquivo = uploader.upload_file(nome_arquivo, grafico["dados"])

    return caminho_arquivo
