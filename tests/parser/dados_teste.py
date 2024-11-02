from datetime import datetime

from src.dominio.processamento.entidade import DadosTransacao
from src.dominio.transacao.tipos import TipoTransacao

now = datetime.now()

DADOS_TESTE_PARSER = [
    (
        "vendi 150 calça cargo credito",
        DadosTransacao(
            tipo=TipoTransacao.CREDITO,
            valor=150,
            metodo_pagamento="credito",
            categoria="calça cargo",
            data=datetime.now(),
            mensagem_original="vendi 150 calça cargo credito",
        ),
    ),
    (
        "paguei 250 receita federal pix 10/05",
        DadosTransacao(
            tipo=TipoTransacao.DEBITO,
            valor=250,
            metodo_pagamento="pix",
            categoria="receita federal",
            data=datetime.now().replace(year=now.year, month=5, day=10),
            mensagem_original="paguei 250 receita federal pix 10/05",
        ),
    ),
    (
        "insumos paguei 300 ifood, mercadoria credito",
        DadosTransacao(
            tipo=TipoTransacao.DEBITO,
            valor=300,
            metodo_pagamento="credito",
            categoria="insumos ifood | mercadoria",
            data=datetime.now(),
            mensagem_original="insumos paguei 300 ifood, mercadoria credito",
        ),
    ),
    (
        "vendi 520,75 de marmitas credito 13/10",
        DadosTransacao(
            tipo=TipoTransacao.CREDITO,
            valor=520.75,
            metodo_pagamento="credito",
            categoria="marmitas",
            data=now.replace(year=now.year, month=10, day=13),
            mensagem_original="vendi 520,75 de marmitas credito 13/10",
        ),
    ),
]
