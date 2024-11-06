from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.services import criar_usuario
from src.infra.database.uow import UnitOfWork


def test_criar_usuario_service(session):
    uow = UnitOfWork(session_factory=lambda: session)
    usuario = UsuarioModel(
        nome="Levy",
        sobrenome="Araujo",
        telefone="5511900001111",
        email="levy@email.com",
        senha=None,
    )

    usuario_criado = criar_usuario(usuario, uow)
    assert usuario.nome == usuario_criado.nome
    assert usuario.sobrenome == usuario_criado.sobrenome
    assert usuario.telefone == usuario_criado.telefone
    assert usuario.email == usuario_criado.email
