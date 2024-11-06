import logging
import os
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.usuario.onboard import OnboardingHandler, OnboardingState
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork

FRONT = os.getenv("FRONT")

logger = logging.getLogger("onboard_middleware")


class UserOnboardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            dados = await request.form()
            request.state.form_data = dados

            if "/bot" not in request.url.path:
                return await call_next(request)

            usuario_telefone = dados.get("From", "").replace("whatsapp:+", "")
            usuario_telefone = usuario_telefone[:4] + "9" + usuario_telefone[4:]
            mensagem = dados.get("Body", "")

            repo = RepoUsuarioLeitura(session=get_session())

            user = repo.buscar_por_telefone(usuario_telefone)

            if not user:
                uow = UnitOfWork(session_factory=get_session)
                onboard = OnboardingHandler(uow=uow)
                resposta = onboard.handle_message(usuario_telefone, mensagem)
                twiml = MessagingResponse()
                twiml.message(resposta)
                return Response(content=str(twiml), media_type="application/xml")

            request.state.user = user
            return await call_next(request)

        except Exception as e:
            logger.error(traceback.format_exc())
            print(f"Error in middleware: {str(e)}")
            twiml = MessagingResponse()
            twiml.message(
                "Desculpe, ocorreu um erro ao processar sua mensagem.\nPor favor, tente novamente mais tarde."
            )
            return Response(content=str(twiml), media_type="application/xml")
