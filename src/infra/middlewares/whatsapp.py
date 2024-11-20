import json
import logging
import traceback
from typing import Callable

from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from httpx import Response as HTTPXResponse

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.usuario.onboard import OnboardingHandler
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.whatsapp_api import parse_whatsapp_payload


class WhatsAppOnboardMiddleware(BaseHTTPMiddleware):
    """
    Middleware para processar requisições de onboarding de usuários com deduplicação de webhooks.
    """

    def __init__(self, app):
        super().__init__(app)
        self.bot = WhatsAppBot()

    async def _process_webhook(self, request: Request) -> Response | JSONResponse:
        """Process the webhook data and return appropriate response"""
        try:
            raw_data = await request.body()
            dados = json.loads(raw_data)
            logging.info("Received data: %s", json.dumps(dados, indent=2))

            parsed_data = parse_whatsapp_payload(dados)
            if not parsed_data:
                return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "skipped"})

            repo = RepoUsuarioLeitura(session=get_session())
            usuario = repo.buscar_por_telefone(parsed_data.telefone)

            if not usuario:
                uow = UnitOfWork(session_factory=get_session)
                onboard = OnboardingHandler(uow=uow)
                pergunta_onboard = onboard.handle_message(parsed_data.telefone, parsed_data.mensagem, parsed_data.nome)
                resposta = self.bot.responder(pergunta_onboard, parsed_data.telefone)
                return JSONResponse(content=resposta.get("content"), status_code=resposta.get("status_code"))

            request.state.dados_whatsapp = parsed_data
            request.state.usuario = usuario

        except json.JSONDecodeError:
            logging.error("Invalid JSON payload")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
            logging.error(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing message")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main dispatch method for the middleware"""
        if "/bot/whatsapp" not in request.url.path or request.method == "GET":
            return await call_next(request)

        response = await self._process_webhook(request)
        if response is not None:
            return response

        try:
            return await call_next(request)
        except Exception as e:
            logging.error(f"Error in middleware chain: {str(e)}")
            logging.error(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
