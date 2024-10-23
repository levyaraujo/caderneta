from datetime import datetime

from src.dominio.processamento.entidade import DadosTransacao
from src.dominio.transacao.tipos import TipoTransacao

ANO_ATUAL = datetime.now().year

DADOS_TESTE_PARSER = [
    (
        "vendi 150 calça cargo credito",
        DadosTransacao(
            acao=TipoTransacao.CREDITO,
            valor=150,
            metodo_pagamento="credito",
            categoria="calça cargo",
            data=datetime.now().date(),
            mensagem_original="vendi 150 calça cargo credito",
        ),
    ),
    (
        "paguei 250 receita federal pix 10/05",
        DadosTransacao(
            acao=TipoTransacao.DEBITO,
            valor=250,
            metodo_pagamento="pix",
            categoria="receita federal",
            data=datetime(year=ANO_ATUAL, month=5, day=10).date(),
            mensagem_original="paguei 250 receita federal pix 10/05",
        ),
    ),
    (
        "insumos paguei 300 ifood, mercadoria credito",
        DadosTransacao(
            acao=TipoTransacao.DEBITO,
            valor=300,
            metodo_pagamento="credito",
            categoria="insumos ifood | mercadoria",
            data=datetime.now().date(),
            mensagem_original="insumos paguei 300 ifood, mercadoria credito",
        ),
    ),
    (
        "vendi 520,75 de marmitas credito 13/10",
        DadosTransacao(
            acao=TipoTransacao.CREDITO,
            valor=520.75,
            metodo_pagamento="credito",
            categoria="marmitas",
            data=datetime(year=ANO_ATUAL, month=10, day=13).date(),
            mensagem_original="vendi 520,75 de marmitas credito 13/10",
        ),
    ),
]
