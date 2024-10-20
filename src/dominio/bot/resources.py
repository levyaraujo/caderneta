from twilio.twiml.messaging_response import MessagingResponse

from src.dominio.bot.services import responder_usuario
from fastapi import APIRouter, status, Request

BotRouter = APIRouter(prefix="/bot", tags=["twilio", "whatsapp"])


@BotRouter.post("/twilio", status_code=status.HTTP_200_OK)
async def twilio_webhook(request: Request):
    dados = await request.form()
    twiml = MessagingResponse()
    usuario = dados["From"]
    resposta = responder_usuario(dados["Body"], usuario)
    twiml.message(resposta.body)
    return str(twiml)
