from datetime import datetime

from src.dominio.usuario.entidade import Usuario
from src.dominio.transacao.entidade import Transacao
from src.dominio.transacao.tipos import TipoTransacao

def test_adicionar_usuario(repo_escrita, session):
    usuario = Usuario(id=1, nome="John", sobrenome="Doe", telefone="94981360000", email="john@example.com", senha="password")
    repo_escrita.adicionar(usuario)
    repo_escrita.commit()
    assert session.query(Usuario).filter_by(id=1).first() is not None

def test_remover_usuario(repo_escrita, session):
    usuario = session.query(Usuario).filter_by(id=1).first()
    repo_escrita.remover(usuario)
    repo_escrita.commit()
    assert session.query(Usuario).filter_by(id=1).first() is None

def test_adicionar_transacao(repo_escrita, session):
    usuario = Usuario(id=2, nome="Jane", sobrenome="Doe", telefone="94981360000", email="jane@example.com", senha="password")
    session.add(usuario)
    session.commit()
    transacao = Transacao(id=1, usuario=usuario, valor=100.0, tipo=TipoTransacao.CREDITO, destino=None, descricao="Test", caixa=datetime.now())
    repo_escrita.adicionar(transacao)
    repo_escrita.commit()
    assert session.query(Transacao).filter_by(id=1).first() is not None

def test_buscar_usuario_por_id(repo_leitura):
    usuario = repo_leitura.buscar_por_id(Usuario, 2)
    assert usuario is not None
    assert usuario.nome == "Jane"

def test_buscar_todas_transacoes(repo_leitura):
    transacoes = list(repo_leitura.buscar_todos(Transacao))
    assert len(transacoes) > 0