import base64
import secrets
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.transacao.services import comando_criar_transacao
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.whatsapp_api import WhatsAppPayload

TransacaoRouter = APIRouter(prefix="/transacao")


class TransacaoRequest(BaseModel):
    amount: float
    discount: float = 0  # Default value of 0
    payment_date: datetime
    institution: str
    user: str

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 50.46,
                "discount": 0,
                "payment_date": "2025-03-20 13:42:29",
                "institution": "V SO DO BRASIL S.A.",
                "user": "5594981362600",
            }
        }


def gerar_wamid() -> str:
    """Usaremos essa função para imitar id de mensagem do WhatsApp API"""
    random_bytes = secrets.token_bytes(20)
    base64_encoded = base64.b64encode(random_bytes).decode("utf-8")
    wamid = f"wamid.{base64_encoded}"

    return wamid


@TransacaoRouter.post("/lambda")
async def criar_transacao_via_lambda(transacao: TransacaoRequest) -> dict:
    usuario = RepoUsuarioLeitura(session=get_session()).buscar_por_telefone(transacao.user)
    destino = f"para {transacao.institution}" if transacao.institution else "outros"
    mensagem = f"paguei {transacao.amount} {destino} em {transacao.payment_date}"
    bot = WhatsAppBot()
    uow = UnitOfWork(session_factory=get_session)
    dados_whatsapp = WhatsAppPayload(
        telefone=transacao.user, mensagem=mensagem, wamid=gerar_wamid(), audio=None, imagem=None, nome="", object=""
    )

    resposta: dict = comando_criar_transacao(
        usuario=usuario,
        tipo="DEBITO",
        mensagem=mensagem,
        uow=uow,
        telefone=transacao.user,
        dados_whatsapp=dados_whatsapp,
    )

    bot.enviar_mensagem_interativa(resposta)

    return resposta
