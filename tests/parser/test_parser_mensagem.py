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
    assert "tests/parser/test.csv" in classifier.csv_path
    assert "tests/parser/vectorizer.joblib" in classifier.vectorizer_joblib
    assert "tests/parser/classifier.joblib" in classifier.classifier_joblib


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
    assert transacao.data.replace(minute=0, second=0, microsecond=0) == esperado.data.replace(
        minute=0, second=0, microsecond=0
    )
