import json
import logging
import traceback
from typing import Coroutine, Any, Callable

from starlette.exceptions import HTTPException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.usuario.onboard import OnboardingHandler
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.whatsapp_api import parse_whatsapp_payload

logger = logging.getLogger("onboard_middleware")


class WhatsAppOnboardMiddleware(BaseHTTPMiddleware):
    """
    Middleware para processar requisições de onboarding de usuários.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Coroutine[Any, Any, Response] | Response:
        if "/bot/whatsapp" not in request.url.path:
            return await call_next(request)

        dados = await request.json()
        dados = parse_whatsapp_payload(dados)
        try:
            request.state.usuario = None

            if not dados:
                return await call_next(request)

            repo = RepoUsuarioLeitura(session=get_session())
            usuario = repo.buscar_por_telefone(dados.telefone)

            if not usuario:
                uow = UnitOfWork(session_factory=get_session)
                bot = WhatsAppBot()
                onboard = OnboardingHandler(uow=uow)
                pergunta_onboard = onboard.handle_message(dados.telefone, dados.mensagem, dados.nome)
                resposta = bot.responder(pergunta_onboard, dados.telefone)
                return JSONResponse(content=resposta)

            request.state.usuario = usuario
            return await call_next(request)

        except Exception:
            traceback.print_exc()
            dados = await request.json()
            dados = parse_whatsapp_payload(dados)
            bot = WhatsAppBot()

            if dados:
                resposta = bot.responder(
                    "Desculpe, ocorreu um erro ao processar sua mensagem.\nPor favor, tente novamente mais tarde.",
                    dados.telefone,
                )
                return JSONResponse(content=resposta)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao processar mensagem")
