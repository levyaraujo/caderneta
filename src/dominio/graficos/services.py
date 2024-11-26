from collections import defaultdict
from typing import List, Literal, Dict

from src.dominio.graficos.entidade import GraficoConfig, GraficoFactory
from src.dominio.transacao.entidade import Transacao, Real
from src.dominio.transacao.tipos import TipoTransacao


def criar_grafico_fluxo_de_caixa(transacoes: List[Transacao], formato="png"):
    config = GraficoConfig(titulo="Fluxo de Caixa", formato=formato)
    transacoes.sort(key=lambda transacao: transacao.caixa)

    fluxo_diario = defaultdict(float)
    for transacao in transacoes:
        data = transacao.caixa.date()
        valor = transacao.valor if transacao.tipo == TipoTransacao.CREDITO else -transacao.valor
        fluxo_diario[data] += valor

    datas_ordenadas = sorted(fluxo_diario.keys())
    legendas = datas_ordenadas
    valores = [fluxo_diario[data] for data in datas_ordenadas]

    grafico = GraficoFactory.criar_grafico("linha", config, legendas=legendas, valores=valores)
    return grafico.criar()


def criar_grafico_receitas_e_despesas(transacoes: List[Transacao]):
    config = GraficoConfig(titulo="Receitas e Despesas")
    transacoes.sort(key=lambda transacao: transacao.caixa)
    receitas_despesas_por_mes: Dict[str, Dict[str, float]] = defaultdict(lambda: {"receitas": 0.0, "despesas": 0.0})

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


def criar_grafico_lucro(transacoes: List[Transacao]):
    config = GraficoConfig(titulo="Lucro")
    transacoes.sort(key=lambda transacao: transacao.caixa)

    grafico = GraficoFactory.criar_grafico("lucro", config, transacoes=transacoes)
    return grafico.criar()
