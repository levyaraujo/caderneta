from datetime import datetime

import pytest
from freezegun import freeze_time

from src.dominio.processamento.entidade import (
    ConstrutorTransacao,
    ClassificadorTexto,
)
from src.dominio.transacao.tipos import TipoTransacao
from tests.parser.dados_teste import DADOS_TESTE_PARSER


def test_classifier_esta_carregando_arquivos_corretos():
    classifier = ClassificadorTexto()
    assert (
        classifier.csv_path
        == "/home/lev0x/Documents/projetos/caderneta/tests/parser/test.csv"
    )
    assert (
        classifier.vectorizer_joblib
        == "/home/lev0x/Documents/projetos/caderneta/tests/parser/vectorizer.joblib"
    )
    assert (
        classifier.classifier_joblib
        == "/home/lev0x/Documents/projetos/caderneta/tests/parser/classifier.joblib"
    )


@pytest.mark.parametrize("mensagem, esperado", DADOS_TESTE_PARSER)
@pytest.mark.integracao
def test_parser_mensagens(mensagem, esperado):
    classifier = ClassificadorTexto()
    tipo, _ = classifier.classificar_mensagem(mensagem)
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo.upper()])
    transacao = parser.parse_message(mensagem)

    assert transacao.tipo == esperado.tipo
    assert transacao.valor == esperado.valor
    assert transacao.metodo_pagamento == esperado.metodo_pagamento
    assert transacao.categoria == esperado.categoria
    assert transacao.mensagem_original == esperado.mensagem_original
    assert transacao.data.replace(second=0, microsecond=0) == esperado.data.replace(
        second=0, microsecond=0
    )
