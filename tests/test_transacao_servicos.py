from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.services import criar_transacao
from src.infra.database.uow import UnitOfWork


def test_criar_transacao(mock_transacao, session):
    transacao = mock_transacao
    uow = UnitOfWork(session_factory=lambda: session)
    criar_transacao(transacao, uow)
    transacao_salva = session.get(Transacao, transacao.id)
    assert transacao_salva.id == transacao.id
