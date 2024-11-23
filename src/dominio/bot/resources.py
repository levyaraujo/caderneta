import json
import logging
import os

from starlette.exceptions import HTTPException
from starlette.responses import Response, JSONResponse

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.bot.services import responder_usuario
from fastapi import APIRouter, status, Request

from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.infra.log import setup_logging

BotRouter = APIRouter(prefix="/bot", tags=["twilio", "whatsapp"])

logger = setup_logging()


@BotRouter.get("/whatsapp", status_code=status.HTTP_200_OK)
async def verificacao_whatsapp_webhook(request: Request, response: Response):
    try:
        params = dict(request.query_params)
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        token_verificacao = os.getenv("WHATSAPP_TOKEN_VERIFICACAO")

        if mode == "subscribe" and token == token_verificacao:
            return JSONResponse(content=int(challenge), status_code=200)
        raise HTTPException(
            status_code=403, detail=f"Verificação do WhatsApp API falhou: {token_verificacao} != {token}"
        )
    except Exception as error:
        logging.error(error)
        return "An internal server error occurred", 500


@BotRouter.post("/whatsapp", status_code=status.HTTP_200_OK)
async def whatsapp_webhook(request: Request):
    uow = UnitOfWork(session_factory=get_session)
    dados = await request.body()
    bot = WhatsAppBot()
    usuario = request.state.usuario
    dados_whatsapp = request.state.dados_whatsapp
    logger.info(f"Dados WhatsApp:\n {json.dumps(dados, indent=2)}")
    resposta = await responder_usuario(
        mensagem=dados_whatsapp.mensagem,
        usuario=usuario,
        uow=uow,
        robo=bot,
        telefone=dados_whatsapp.telefone,
        nome_usuario=dados_whatsapp.nome,
        dados_whatsapp=dados_whatsapp,
    )
    return resposta
