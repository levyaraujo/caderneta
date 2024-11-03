from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.bot.entidade import TwilioBot
from src.dominio.bot.services import responder_usuario
from fastapi import APIRouter, status, Request

from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.validadores import limpar_texto

BotRouter = APIRouter(prefix="/bot", tags=["twilio", "whatsapp"])


@BotRouter.post("/twilio", status_code=status.HTTP_200_OK)
async def twilio_webhook(request: Request):
    uow = UnitOfWork(session_factory=get_session)
    dados = request.state.form_data
    usuario = request.state.user
    twiml = MessagingResponse()
    telefone = dados["From"]
    nome_usuario = dados["ProfileName"]
    mensagem = limpar_texto(dados["Body"])
    bot = TwilioBot()
    resposta = await responder_usuario(
        mensagem, usuario, telefone, nome_usuario, robo=bot, uow=uow
    )
    twiml.message(resposta)
    return str(twiml)
