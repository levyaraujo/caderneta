import logging
import traceback
from typing import Any, Optional

from src.dominio.bot.comandos import bot
from src.dominio.bot.entidade import BotBase
from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.processamento.entidade import ClassificadorTexto
from src.dominio.processamento.exceptions import NaoEhTransacao
from src.dominio.transacao.services import comando_criar_transacao
from src.dominio.usuario.entidade import Usuario
from src.infra.database.uow import UnitOfWork
from src.utils.whatsapp_api import WhatsAppPayload


async def responder_usuario(
    mensagem: str,
    usuario: Usuario,
    telefone: str,
    robo: BotBase,
    uow: UnitOfWork,
    dados_whatsapp: Optional[WhatsAppPayload] = None,
) -> Any:
    try:
        resposta = await bot.processar_mensagem(mensagem, nome_usuario=usuario.nome, usuario=usuario, uow=uow)
        return robo.responder(resposta, telefone)

    except ComandoDesconhecido:
        comandos = mensagem.split(" ")
        if len(comandos) == 1:
            return robo.responder(
                f"Comando {comandos[0]} não existe\n\nDigite *ajuda* e veja os comandos disponíveis.", telefone
            )

        try:
            classifier = ClassificadorTexto()
            tipo, _ = classifier.classificar_mensagem(mensagem)
            if tipo == "debito" or tipo == "credito":
                resposta = comando_criar_transacao(usuario, tipo.upper(), mensagem, uow, telefone, dados_whatsapp)

                return robo.enviar_mensagem_interativa(resposta)
        except NaoEhTransacao:
            robo.responder("Não entendi sua mensagem 🫤", telefone)
            robo.responder(bot.ajuda(), telefone)

    except Exception:
        traceback.print_exc()
        return robo.responder("Ocorreu um erro desconhecido. Por favor, tente novamente.", telefone)
