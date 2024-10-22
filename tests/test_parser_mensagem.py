from datetime import datetime

import pytest

from src.dominio.processamento.entidade import (
    ConstrutorTransacao,
    ClassificadorTexto,
    DadosTransacao,
)
from src.dominio.transacao.tipos import TipoTransacao

ANO_ATUAL = datetime.now().year


@pytest.mark.parametrize(
    "mensagem, esperado",
    [
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
                categoria="ifood, mercadoria",
                data=datetime.now().date(),
                mensagem_original="insumos paguei 300 ifood, mercadoria credito",
            ),
        ),
    ],
)
def test_parser_mensagens(mensagem, esperado):
    classifier = ClassificadorTexto()
    tipo, _ = classifier.classificar_mensagem(mensagem)
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    transacao = parser.parse_message(mensagem)

    assert transacao == esperado
