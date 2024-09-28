from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.servicos import criar_transacao


def test_criar_transacao(mock_transacao, session):
    transacao = mock_transacao
    criar_transacao(transacao, session)
    transacao_salva = session.query(Transacao).get(transacao.id)
    assert transacao_salva.id == transacao.id
