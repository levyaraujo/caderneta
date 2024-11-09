import logging
import traceback
from typing import Coroutine, Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.usuario.exceptions import UsuarioJaExiste
from src.dominio.usuario.onboard import OnboardingHandler
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.formatos import formatar_telefone

logger = logging.getLogger("onboard_middleware")


class TwilioOnboardMiddleware(BaseHTTPMiddleware):
    """
    Middleware para processar requisições de onboarding de usuários.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Coroutine[Any, Any, Response] | Response:
        try:
            dados = await request.form()
            request.state.form_data = dados

            request.state.usuario = None

            if "/bot/twilio" not in request.url.path:
                return await call_next(request)

            telefone = dados.get("From", "").replace("whatsapp:+", "")
            telefone = formatar_telefone(telefone)
            mensagem = dados.get("Body", "")
            nome_usuario = dados.get("ProfileName", "")

            repo = RepoUsuarioLeitura(session=get_session())

            usuario = repo.buscar_por_telefone(telefone)

            if not usuario:
                uow = UnitOfWork(session_factory=get_session)
                onboard = OnboardingHandler(uow=uow)
                resposta = onboard.handle_message(telefone, mensagem, nome_usuario)
                twiml = MessagingResponse()
                twiml.message(resposta)
                return Response(content=str(twiml), media_type="application/xml")

            request.state.usuario = usuario
            return await call_next(request)

        except UsuarioJaExiste:
            twiml = MessagingResponse()
            twiml.message("Desculpe, mas já existe um usuário com o mesmo email no sistema.")
            return Response(content=str(twiml), media_type="application/xml")

        except Exception as e:
            traceback.print_exc()
            print(f"Error in middleware: {str(e)}")
            twiml = MessagingResponse()
            twiml.message(
                "Desculpe, ocorreu um erro ao processar sua mensagem.\nPor favor, tente novamente mais tarde."
            )
            return Response(content=str(twiml), media_type="application/xml")
