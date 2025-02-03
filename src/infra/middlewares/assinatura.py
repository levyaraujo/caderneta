import traceback
from typing import Callable, Any

from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.dominio.assinatura.entidade import StatusAssinatura
from src.dominio.assinatura.repo import RepoAssinaturaLeitura
from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.usuario.entidade import Usuario
from src.infra.database.connection import get_session
from src.infra.log import setup_logging

logger = setup_logging()


class AssinaturaMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check user subscription status and handle canceled subscriptions
    """

    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.bot = WhatsAppBot()

    async def _check_subscription_status(self, usuario: Usuario) -> None:
        """
        Check the subscription status for a given user
        If subscription is canceled, send a WhatsApp notification
        """
        try:
            # Retrieve subscription for the user
            repo_assinatura = RepoAssinaturaLeitura(session=get_session())
            assinatura = repo_assinatura.buscar_por_id_usuario(usuario.id)

            # If no subscription exists or is not canceled, continue
            if not assinatura or assinatura.status != StatusAssinatura.CANCELADA:
                return

            # Prepare and send WhatsApp message for canceled subscription
            mensagem = (
                f"Olá, {usuario.nome}! 👋\n\n"
                "Notamos que sua assinatura foi cancelada. 📅\n\n"
                "Sentimos sua falta e gostaríamos de entender o motivo. "
                "Há algo que possamos fazer para melhorar sua experiência?\n\n"
                "Acesse o link abaixo e renove sua assinatura:\n"
                f"https://billing.stripe.com/p/login/4gwdTFckG4s80SI8ww?prefilled_email={usuario.email}"
                "Se quiser tirar dúvidas, entre em contato conosco: contato@caderneta.chat\n\n"
            )

            # Send message via WhatsApp
            self.bot.responder(mensagem, usuario.telefone)

        except Exception as e:
            logger.error(f"Error checking subscription status for user {usuario.id}: {str(e)}")
            traceback.print_exc()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Main dispatch method for the middleware
        Checks subscription status for authenticated routes
        """
        # Skip subscription check for certain routes or methods
        if request.method == "GET" or "/bot/" in request.url.path:
            return await call_next(request)

        # Check if user is authenticated (you might need to adjust this based on your auth mechanism)
        usuario = request.state.usuario
        if usuario:
            await self._check_subscription_status(usuario)

        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error in subscription status middleware: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
