import stripe
from stripe import Subscription

from src.dominio.assinatura.services import criar_cliente_stripe, criar_assinatura
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session


def test_criar_cliente(mock_usuario):
    usuario = mock_usuario
    cliente = criar_cliente_stripe(usuario)
    assert isinstance(cliente, stripe.Customer)
    assert cliente.name == f"{usuario.nome} {usuario.sobrenome}"
    assert cliente.email == usuario.email
    assert cliente.phone == usuario.telefone


def test_criar_assinatura(mock_usuario):
    repo_usuario = RepoUsuarioLeitura(session=get_session())
    usuario = mock_usuario
    cliente = criar_cliente_stripe(usuario)
    assinatura_stripe, assinatura = criar_assinatura(cliente)
    repo_usuario.buscar_por_email(usuario.email)
    assert usuario.assinatura.stripe_id == assinatura_stripe.id
    assert isinstance(assinatura_stripe, Subscription)
