from datetime import datetime

from src.dominio.processamento.entidade import DadosTransacao
from src.dominio.transacao.tipos import TipoTransacao

now = datetime.now()
zerar_hora = now.replace(hour=0, minute=0, second=0, microsecond=0)

DADOS_TESTE_PARSER = [
    (
        "vendi 150 calça cargo credito",
        DadosTransacao(
            tipo=TipoTransacao.CREDITO,
            valor=150,
            metodo_pagamento="credito",
            destino="CALÇA CARGO",
            data=zerar_hora,
            mensagem_original="vendi 150 calça cargo credito",
        ),
    ),
    (
        "paguei 250 receita federal pix 10/05",
        DadosTransacao(
            tipo=TipoTransacao.DEBITO,
            valor=250,
            metodo_pagamento="pix",
            destino="RECEITA FEDERAL",
            data=zerar_hora.replace(year=now.year, month=5, day=10),
            mensagem_original="paguei 250 receita federal pix 10/05",
        ),
    ),
    (
        "insumos paguei 300 ifood, mercadoria credito",
        DadosTransacao(
            tipo=TipoTransacao.DEBITO,
            valor=300,
            metodo_pagamento="credito",
            destino="INSUMOS IFOOD| MERCADORIA",
            data=zerar_hora.replace(hour=0, minute=0, second=0, microsecond=0),
            mensagem_original="insumos paguei 300 ifood, mercadoria credito",
        ),
    ),
    (
        "vendi 520,75 de marmitas credito 13/10",
        DadosTransacao(
            tipo=TipoTransacao.CREDITO,
            valor=520.75,
            metodo_pagamento="credito",
            destino="MARMITAS",
            data=zerar_hora.replace(year=now.year, month=10, day=13),
            mensagem_original="vendi 520,75 de marmitas credito 13/10",
        ),
    ),
    (
        "vendi 10,500 de marmitas 13/10",
        DadosTransacao(
            tipo=TipoTransacao.CREDITO,
            valor=10500,
            metodo_pagamento=None,
            destino="MARMITAS",
            data=zerar_hora.replace(year=now.year, month=10, day=13),
            mensagem_original="vendi 10,500 de marmitas 13/10",
        ),
    ),
    (
        "paguei 10500 moto",
        DadosTransacao(
            tipo=TipoTransacao.DEBITO,
            valor=10500,
            metodo_pagamento=None,
            destino="MOTO",
            data=zerar_hora,
            mensagem_original="paguei 10500 moto",
        ),
    ),
]
