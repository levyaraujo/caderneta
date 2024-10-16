from collections import defaultdict
from typing import List

from plotly.graph_objs import Layout

from src.dominio.graficos.graficos import GraficoBase
from src.dominio.transacao.entidade import Transacao, Real
from src.dominio.transacao.tipos import TipoTransacao


def criar_grafico_fluxo_de_caixa(transacoes: List[Transacao]):
    grafico = GraficoBase(transacoes=transacoes, titulo="Fluxo de Caixa")
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

    layout = Layout(
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
    )

    grafico.titulo = f"Fluxo de Caixa {transacoes[0].caixa.strftime('%d/%m/%Y')} a {transacoes[-1].caixa.strftime('%d/%m/%Y')}"
    return grafico.criar_grafico_de_linha(
        legendas=legendas, valores=valores, hover_texts=hover_texts, layout=layout
    )


def criar_grafico_receitas(transacoes: List[Transacao]):
    grafico = GraficoBase(transacoes=transacoes, titulo="Receitas por Mês")
    transacoes.sort(key=lambda transacao: transacao.caixa)
    receitas_despesas_por_mes = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0})

    for transacao in transacoes:
        mes = transacao.caixa.strftime("%Y-%m")
        if transacao.tipo == TipoTransacao.CREDITO:
            receitas_despesas_por_mes[mes]["receitas"] += transacao.valor
        else:
            receitas_despesas_por_mes[mes]["despesas"] -= transacao.valor

    legendas = list(receitas_despesas_por_mes.keys())

    grafico.titulo = "Receitas e Despesas por mês"
    return grafico.criar_grafico_barra_empilhada(
        dados=receitas_despesas_por_mes, periodos=legendas
    )
