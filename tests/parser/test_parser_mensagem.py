import pytest

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
        == "/home/lev0x/Documents/projetos/caderneta/tests/fixtures/test.csv"
    )
    assert (
        classifier.vectorizer_joblib
        == "/home/lev0x/Documents/projetos/caderneta/tests/fixtures/vectorizer.joblib"
    )
    assert (
        classifier.classifier_joblib
        == "/home/lev0x/Documents/projetos/caderneta/tests/fixtures/classifier.joblib"
    )


@pytest.mark.parametrize("mensagem, esperado", DADOS_TESTE_PARSER)
@pytest.mark.integracao
def test_parser_mensagens(mensagem, esperado):
    classifier = ClassificadorTexto()
    tipo, _ = classifier.classificar_mensagem(mensagem)
    parser = ConstrutorTransacao(acao=TipoTransacao[tipo])
    transacao = parser.parse_message(mensagem)

    assert transacao == esperado
