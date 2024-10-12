from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.services import criar_transacao


def test_criar_transacao(mock_transacao, session):
    transacao = mock_transacao
    criar_transacao(transacao, session)
    transacao_salva = session.get(Transacao, transacao.id)
    assert transacao_salva.id == transacao.id
