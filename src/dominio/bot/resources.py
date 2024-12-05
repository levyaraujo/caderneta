import logging
import os
import traceback
from typing import Any

from starlette.exceptions import HTTPException
from starlette.responses import Response, JSONResponse

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.bot.services import responder_usuario
from fastapi import APIRouter, status, Request

from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork

BotRouter = APIRouter(prefix="/bot", tags=["twilio", "whatsapp"])


@BotRouter.get("/whatsapp", status_code=status.HTTP_200_OK)
async def verificacao_whatsapp_webhook(request: Request, response: Response) -> JSONResponse:
    try:
        params = dict(request.query_params)
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge", "")
        token_verificacao = os.getenv("WHATSAPP_TOKEN_VERIFICACAO")

        if mode == "subscribe" and token == token_verificacao:
            return JSONResponse(content=int(challenge), status_code=200)
        raise HTTPException(
            status_code=403, detail=f"Verificação do WhatsApp API falhou: {token_verificacao} != {token}"
        )
    except Exception as error:
        logging.error(error, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao verificar WhatsApp API")


@BotRouter.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp_webhook(request: Request) -> Any:
    uow = UnitOfWork(session_factory=get_session)
    bot = WhatsAppBot()
    usuario = request.state.usuario
    dados_whatsapp = request.state.dados_whatsapp

    mensagem = dados_whatsapp.mensagem
    if dados_whatsapp.audio:
        bot.responder(mensagem="Aguarde um momento. Estou processando seu áudio...", telefone=dados_whatsapp.telefone)
        audio_url = bot.obter_url_audio(dados_whatsapp.audio)
        audio = bot.download_audio(audio_url)
        mensagem = bot.transcrever_audio(audio)

    resposta = await responder_usuario(
        mensagem=mensagem,
        usuario=usuario,
        uow=uow,
        robo=bot,
        telefone=dados_whatsapp.telefone,
        dados_whatsapp=dados_whatsapp,
    )
    return resposta
