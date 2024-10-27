from fastapi import APIRouter, status, Request, HTTPException
from pydantic import BaseModel, EmailStr
import logging

from src.dominio.usuario.entidade import UsuarioModel, UsuarioResposta
from src.dominio.usuario.exceptions import UsuarioJaExiste, ErroAoCriarUsuario
from src.dominio.usuario.services import criar_usuario
from src.infra.database.connection import (
    GET_DEFAULT_SESSION_CONTEXT,
    GET_DEFAULT_SESSION,
)
from src.infra.database.uow import UnitOfWork

UsuarioRouter = APIRouter(prefix="/usuario", tags=["usuario"])

logger = logging.getLogger("usuario_resources")


@UsuarioRouter.post("", status_code=status.HTTP_201_CREATED)
def usuario_onboard(usuario: UsuarioModel) -> UsuarioResposta:
    uow = UnitOfWork(session_factory=GET_DEFAULT_SESSION)
    try:
        usuario_criado = criar_usuario(usuario, uow=uow)
        resposta = UsuarioResposta(**usuario_criado.model_dump())
        return resposta
    except UsuarioJaExiste as erro:
        logger.info(f"Usuário {usuario.email} já existe no sistema")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    except ErroAoCriarUsuario as erro:
        logger.error(f"Um erro ocorreu ao criar o usuário {usuario.email}: {erro}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário",
        )
