import logging
import traceback

from passlib.context import CryptContext
from pydantic import SecretStr
from stripe import Subscription

from src.dominio.assinatura.services import criar_cliente_stripe, criar_assinatura
from src.dominio.usuario.entidade import Usuario, UsuarioModel
from src.dominio.usuario.exceptions import ErroAoCriarUsuario, UsuarioJaExiste
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64MB in kibibytes
    argon2__time_cost=3,  # Number of iterations
    argon2__parallelism=4,  # Degree of parallelism
    argon2__hash_len=32,  # Length of the hash in bytes
)


class PasswordHasher:
    @staticmethod
    def hash_password(password: str | SecretStr) -> str:
        if isinstance(password, SecretStr):
            password = password.get_secret_value()
        senha_hash: str = pwd_context.hash(password)
        return senha_hash

    @staticmethod
    def verify_password(plain_password: str | SecretStr, hashed_password: str) -> bool:
        if isinstance(plain_password, SecretStr):
            plain_password = plain_password.get_secret_value()
        senha_esta_correta: bool = pwd_context.verify(plain_password, hashed_password)
        return senha_esta_correta


def criar_usuario(usuario: UsuarioModel, uow: UnitOfWork) -> Usuario | None:
    senha_encriptada = PasswordHasher.hash_password(usuario.senha) if usuario.senha else None
    entidade = Usuario(
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        telefone=usuario.telefone,
        email=str(usuario.email),
        senha=senha_encriptada,
    )
    repo_usuario = RepoUsuarioLeitura(session=get_session())
    usuario_existe = repo_usuario.buscar_por_email(str(usuario.email))

    if usuario_existe:
        raise UsuarioJaExiste("O usuário já existe no sistema")

    try:
        with uow:
            uow.repo_escrita.adicionar(entidade)
            uow.commit()

            cliente_stripe = criar_cliente_stripe(entidade)
            _, assinatura = criar_assinatura(cliente_stripe)

        return entidade

    except Exception as e:
        traceback.print_exc()
        raise ErroAoCriarUsuario(f"Erro ao criar o usuario {usuario.email}: {e}")
