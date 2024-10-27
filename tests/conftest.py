from datetime import datetime
from random import randint

import pytest

from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import metadata, GET_DEFAULT_SESSION_CONTEXT, engine
from src.infra.database.repo import RepoEscrita, RepoLeitura


@pytest.fixture
def mock_usuario(session):
    usuario = Usuario(
        id=randint(1, 10000),
        nome="Usuario",
        sobrenome="Pytest",
        telefone="94981362600",
        email="joao@teste.com",
        senha="senha123",
    )
    session.add(usuario)
    session.commit()
    return usuario


@pytest.fixture(scope="function")
def transacao_gen():
    def make_mock(usuario, valor, destino, tipo, caixa=datetime(2024, 10, 22)):
        return Transacao(
            id=randint(1, 10000),
            usuario=usuario,
            valor=valor,
            categoria=destino,
            tipo=tipo,
            descricao="asodihasjklfnasfr",
            caixa=caixa,
        )

    return make_mock


@pytest.fixture(scope="function")
def mock_transacao(mock_usuario, transacao_gen):
    return transacao_gen(mock_usuario, 100.0, "Loja A", "debito")


@pytest.fixture(scope="module")
def test_engine():
    return engine


@pytest.fixture(scope="module")
def tables(test_engine):
    metadata.create_all(engine)


@pytest.fixture(scope="function")
def session(tables):
    with GET_DEFAULT_SESSION_CONTEXT() as session:
        yield session


@pytest.fixture
def repo_escrita(session):
    return RepoEscrita(session)


@pytest.fixture
def repo_leitura(session):
    return RepoLeitura(session)
