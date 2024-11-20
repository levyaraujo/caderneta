from datetime import datetime
from random import randint

import pytest

from src.dominio.transacao.repo import RepoTransacaoLeitura
from src.dominio.usuario.entidade import Usuario
from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacao
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.uow import UnitOfWork
from src.libs.tipos import Intervalo


def test_adicionar_usuario(session):
    uow = UnitOfWork(session_factory=lambda: session)
    with uow:
        usuario = Usuario(
            id=randint(1, 10000),
            nome="John",
            sobrenome="Doe",
            telefone="94981360000",
            email="john@example.com",
            senha="password",
        )
        uow.repo_escrita.adicionar(usuario)
        uow.commit()
    assert session.query(Usuario).filter_by(id=usuario.id).first() is not None


def test_remover_usuario(session, mock_usuario):
    usuario = mock_usuario
    uow = UnitOfWork(session_factory=lambda: session)
    with uow:
        usuario = session.query(Usuario).filter_by(id=usuario.id).first()
        uow.repo_escrita.remover(usuario)
        uow.commit()
    assert session.query(Usuario).filter_by(id=usuario.id).first() is None


def test_adicionar_transacao(session, mock_usuario, gerar_wamid):
    uow = UnitOfWork(session_factory=lambda: session)
    repo_transacao_leitura = RepoTransacaoLeitura(session=session)
    usuario = mock_usuario
    transacao = Transacao(
        usuario=usuario,
        valor=100.0,
        tipo=TipoTransacao.CREDITO,
        categoria="roupas",
        descricao="Test",
        caixa=datetime.now(),
        wamid=gerar_wamid,
    )
    with uow:
        uow.repo_escrita.adicionar(usuario)
        uow.repo_escrita.adicionar(transacao)
        uow.commit()

    assert repo_transacao_leitura.buscar_por_id(entidade=transacao) is not None


def test_buscar_usuario_por_id(session, mock_usuario):
    novo_usuario = mock_usuario

    repo_usuario_leitura = RepoUsuarioLeitura(session=session)

    usuario = repo_usuario_leitura.buscar_por_id(novo_usuario.id)
    assert usuario is not None
    assert usuario.nome == "Usuario"


def test_buscar_transacao_por_intervalo_e_usuario(session, mock_usuario, transacao_gen):
    repo_transacao_leitura = RepoTransacaoLeitura(session=session)
    uow = UnitOfWork(session_factory=lambda: session)
    usuario = mock_usuario
    with uow:
        for _ in range(10):
            transacao = transacao_gen(usuario, 100.0, "Loja A", TipoTransacao.CREDITO)
            uow.repo_escrita.adicionar(transacao)
            uow.commit()

    intervalo = Intervalo(inicio=datetime(2024, 9, 1), fim=datetime(2024, 10, 30))
    transacoes = repo_transacao_leitura.buscar_por_intervalo_e_usuario(intervalo, usuario.id)

    assert all(
        isinstance(transacao.usuario, Usuario) and transacao.usuario.id == usuario.id for transacao in transacoes
    )

    assert all(transacao.usuario == usuario for transacao in transacoes)

    assert all(transacao.tipo == TipoTransacao.CREDITO for transacao in transacoes)


def test_roll_back_sem_commit_uow(session, mock_transacao):
    transacao = mock_transacao
    uow = UnitOfWork(session_factory=lambda: session)
    with uow:
        uow.repo_escrita.adicionar(transacao)

    nova_sessao = session
    assert nova_sessao.query(Transacao).filter_by(id=transacao.id).first() is None


def test_roll_back_exception_uow(session, mock_transacao):
    transacao = mock_transacao
    uow = UnitOfWork(session_factory=lambda: session)
    with pytest.raises(Exception):
        with uow:
            uow.repo_escrita.adicionar(transacao)
            raise Exception

    nova_sessao = session
    assert nova_sessao.query(Transacao).filter_by(id=transacao.id).first() is None
