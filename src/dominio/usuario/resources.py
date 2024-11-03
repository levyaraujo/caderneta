import logging

from fastapi import APIRouter, status, HTTPException

from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.exceptions import UsuarioJaExiste, ErroAoCriarUsuario
from src.dominio.usuario.services import criar_usuario

UsuarioRouter = APIRouter(prefix="/usuario", tags=["usuario"])

logger = logging.getLogger("usuario_resources")


@UsuarioRouter.post("", status_code=status.HTTP_201_CREATED)
def usuario_onboard(usuario: UsuarioModel):
    try:
        usuario_criado = criar_usuario(usuario)
        return {"message": "Usuario cadastrado com sucesso!"}
    except UsuarioJaExiste as erro:
        logger.info(f"Usuário {usuario.email} já existe no sistema")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    except ErroAoCriarUsuario as erro:
        logger.error(f"Um erro ocorreu ao criar o usuário {usuario.email}: {erro}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar usuário",
        )
