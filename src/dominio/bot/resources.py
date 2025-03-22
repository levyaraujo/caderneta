import logging
import os
import traceback
from typing import Any

from starlette.exceptions import HTTPException
from starlette.responses import Response, JSONResponse

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.bot.services import responder_usuario
from fastapi import APIRouter, status, Request

from src.infra.aws import upload_to_s3
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.validadores import limpar_texto
from src.utils.whatsapp_api import WhatsAppPayload

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
    dados_whatsapp: WhatsAppPayload = request.state.dados_whatsapp

    mensagem = dados_whatsapp.mensagem
    if dados_whatsapp.audio:
        bot.responder(mensagem="Aguarde um momento. Estou processando seu áudio...", telefone=dados_whatsapp.telefone)
        audio_url = bot.obter_url_midia(dados_whatsapp.audio)
        audio = bot.download_audio(audio_url)
        mensagem = limpar_texto(bot.transcrever_audio(audio))

    if dados_whatsapp.imagem:
        try:
            bucket = os.getenv("INVOICE_BUCKET")
            bot.responder(
                mensagem="Aguarde um momento. Estou processando sua imagem...", telefone=dados_whatsapp.telefone
            )
            imagem_url = bot.obter_url_midia(dados_whatsapp.imagem)
            imagem = bot.download_imagem(imagem_url, dados_whatsapp.telefone)
            filename = imagem.split("/")[-1]
            upload_to_s3(imagem, bucket, filename)
            return

        except Exception:
            traceback.format_exc()

    resposta = await responder_usuario(
        mensagem=mensagem,
        usuario=usuario,
        uow=uow,
        robo=bot,
        telefone=dados_whatsapp.telefone,
        dados_whatsapp=dados_whatsapp,
    )
    return resposta
