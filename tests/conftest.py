import base64
import os
import re
import secrets
from datetime import datetime

import pytest

from const import REGEX_WAMID
from src.dominio.bot.entidade import CLIBot
from src.dominio.transacao.entidade import Transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import metadata, GET_DEFAULT_SESSION_CONTEXT, engine
from src.infra.database.repo import RepoEscrita, RepoLeitura
from src.utils.validadores import limpar_texto
from src.utils.whatsapp_api import WhatsAppPayload


@pytest.fixture(scope="function")
def mock_usuario(session):
    usuario = Usuario(
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
def gerar_wamid() -> str:
    random_bytes = secrets.token_bytes(20)
    base64_encoded = base64.b64encode(random_bytes).decode("utf-8")
    wamid = f"wamid.{base64_encoded}"
    wamid_pattern = REGEX_WAMID
    if not re.match(wamid_pattern, wamid):
        raise gerar_wamid()

    return wamid


@pytest.fixture(scope="function")
def transacao_gen(gerar_wamid):
    def make_mock(usuario, valor, destino, tipo, caixa=datetime(2024, 10, 22), wamid=gerar_wamid):
        return Transacao(
            usuario=usuario,
            valor=valor,
            categoria=destino,
            tipo=tipo,
            descricao="asodihasjklfnasfr",
            caixa=caixa,
            wamid=wamid,
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


@pytest.fixture(scope="function", autouse=True)
def clean_tables(session):
    """Roll back database session after each test."""
    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture(scope="session")
def cli_bot():
    return CLIBot()


@pytest.fixture(scope="function")
def mock_payload_whatsapp(gerar_wamid):
    return WhatsAppPayload(
        object="whatsapp_business_account",
        nome="Usuario Teste",
        mensagem=limpar_texto("olá"),
        telefone="9481362600",
        wamid=gerar_wamid,
    )
