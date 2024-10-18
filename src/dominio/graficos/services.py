from collections import defaultdict
from typing import List

from src.dominio.graficos.graficos import GraficoConfig, GraficoFactory
from src.dominio.transacao.entidade import Transacao, Real
from src.dominio.transacao.tipos import TipoTransacao


def criar_grafico_fluxo_de_caixa(transacoes: List[Transacao]):
    config = GraficoConfig(titulo="Fluxo de Caixa", formato="html")
    transacoes.sort(key=lambda transacao: transacao.caixa)
    legendas = [transacao.caixa for transacao in transacoes]
    valores = [
        transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor
        for transacao in transacoes
    ]
    hover_texts = [
        f"Data: {transacao.caixa.strftime('%d/%m/%Y %H:%M')}<br>"
        + f"Valor: {Real(transacao.valor)}<br>"
        + f"Tipo: {transacao.tipo}<br>"
        + f"Categoria: {transacao.categoria}<br>"
        + f"Descrição: {transacao.descricao or 'N/A'}"
        for transacao in transacoes
    ]

    grafico = GraficoFactory.criar_grafico(
        "linha", config, legendas=legendas, valores=valores, hover_texts=hover_texts
    )
    return grafico.criar()


def criar_grafico_receitas_e_despesas(transacoes: List[Transacao]):
    config = GraficoConfig(titulo="Receitas e Despesas", formato="html")
    transacoes.sort(key=lambda transacao: transacao.caixa)
    receitas_despesas_por_mes = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0})

    for transacao in transacoes:
        mes = transacao.caixa.strftime("%Y-%m")
        if transacao.tipo == TipoTransacao.CREDITO:
            receitas_despesas_por_mes[mes]["receitas"] += transacao.valor
        else:
            receitas_despesas_por_mes[mes]["despesas"] -= transacao.valor

    legendas = list(receitas_despesas_por_mes.keys())
    grafico = GraficoFactory.criar_grafico(
        "barra_empilhada", config, legendas=legendas, valores=receitas_despesas_por_mes
    )
    return grafico.criar()
