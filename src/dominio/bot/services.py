import logging
import traceback

from src.dominio.bot.comandos import bot
from src.dominio.bot.entidade import BotBase
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto
from src.dominio.processamento.exceptions import NaoEhTransacao
from src.dominio.transacao.services import comando_criar_transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.uow import UnitOfWork

logger = logging.getLogger("bot_services")


async def responder_usuario(
    mensagem: str,
    usuario: Usuario,
    telefone: str,
    nome_usuario: str,
    robo: BotBase,
    uow: UnitOfWork,
):
    try:
        resposta = await bot.processar_mensagem(mensagem, nome_usuario=nome_usuario, usuario=usuario, uow=uow)
        return robo.responder(resposta, telefone)

    except ComandoDesconhecido:
        try:
            classifier = ClassificadorTexto()
            tipo, _ = classifier.classificar_mensagem(mensagem)
            if tipo == "debito" or tipo == "credito":
                resposta = comando_criar_transacao(usuario, tipo.upper(), mensagem, uow)

                return robo.responder(resposta, telefone)
        except NaoEhTransacao:
            robo.responder("Não entendi sua mensagem 🫤", telefone)
            robo.responder(bot.ajuda(), telefone)

    except Exception:
        traceback.print_exc()
        robo.responder("Ocorreu um erro desconhecido. Por favor, tente novamente.", telefone)
