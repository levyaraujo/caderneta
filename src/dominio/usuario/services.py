import logging

from passlib.context import CryptContext
from pydantic import SecretStr

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
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str | SecretStr, hashed_password: str) -> bool:
        if isinstance(plain_password, SecretStr):
            plain_password = plain_password.get_secret_value()
        return pwd_context.verify(plain_password, hashed_password)


def criar_usuario(usuario: UsuarioModel, uow: UnitOfWork) -> UsuarioModel | None:
    senha_encriptada = PasswordHasher.hash_password(usuario.senha) if usuario.senha else None
    entidade = Usuario(
        nome=usuario.nome,
        sobrenome=usuario.sobrenome,
        telefone=usuario.telefone,
        email=usuario.email,
        senha=senha_encriptada,
    )
    repo_usuario = RepoUsuarioLeitura(session=get_session())
    usuario_existe = repo_usuario.buscar_por_email(usuario.email)

    if usuario_existe:
        raise UsuarioJaExiste("O usuário já existe no sistema")

    try:
        with uow:
            uow.repo_escrita.adicionar(entidade)
            uow.commit()
            return usuario
    except Exception as e:
        logging.exception(f"Erro ao criar transacao: {e}")
        raise ErroAoCriarUsuario(f"Erro ao o usuario {usuario.email}: {e}")
