import logging

from fastapi import APIRouter, status, HTTPException

from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.exceptions import UsuarioJaExiste, ErroAoCriarUsuario
from src.dominio.usuario.services import criar_usuario
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork

UsuarioRouter = APIRouter(prefix="/usuario", tags=["usuario"])


@UsuarioRouter.post("", status_code=status.HTTP_201_CREATED)
def usuario_onboard(usuario: UsuarioModel) -> dict:
    uow = UnitOfWork(session_factory=get_session)
    try:
        criar_usuario(usuario, uow)
        return {"message": "Usuario cadastrado com sucesso!"}
    except UsuarioJaExiste as erro:
        logging.info(f"Usuário {usuario.email} já existe no sistema")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    except ErroAoCriarUsuario as erro:
        logging.error(f"Um erro ocorreu ao criar o usuário {usuario.email}: {erro}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário",
        )
