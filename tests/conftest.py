from datetime import datetime
from random import randint

import pytest

from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.orm import iniciar_mapeamento_orm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infra.database.connection import metadata
from src.infra.database.repo import RepoEscrita, RepoLeitura

iniciar_mapeamento_orm()


@pytest.fixture
def usuario():
    return Usuario(
        id=randint(1, 10000),
        nome="Joao",
        sobrenome="Silva",
        telefone="94981362600",
        email="joao@teste.com",
        senha="senha123",
    )


@pytest.fixture(scope="function")
def transacao_gen():
    def make_mock(usuario, valor, destino, tipo, caixa=datetime(2024, 10, 22)):
        return Transacao(
            id=randint(1, 1000),
            usuario=usuario,
            valor=valor,
            destino=destino,
            tipo=tipo,
            descricao="asodihasjklfnasfr",
            caixa=caixa,
        )

    return make_mock


DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    return create_engine(DATABASE_URL, echo=True)


@pytest.fixture(scope="module")
def tables(engine):
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repo_escrita(session):
    return RepoEscrita(session)


@pytest.fixture
def repo_leitura(session):
    return RepoLeitura(session)
