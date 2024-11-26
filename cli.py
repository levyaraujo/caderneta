import asyncio
import base64
import re
import secrets

import typer
import dotenv
from typing import Optional

from sqlalchemy.testing.plugin.plugin_base import logging

from const import REGEX_WAMID
from src.dominio.usuario.entidade import Usuario
from src.utils.whatsapp_api import WhatsAppPayload

dotenv.load_dotenv(".env")

from src.dominio.usuario.onboard import OnboardingHandler
from src.dominio.bot.entidade import CLIBot
from src.dominio.bot.services import responder_usuario
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.validadores import limpar_texto

app = typer.Typer()

# Constants
USER_COLOR = "\033[94m"  # Blue
BOT_COLOR = "\033[92m"  # Green
RESET_COLOR = "\033[0m"  # Reset
HEADER = """
##################################################
🤖 Caderneta CLI
Escreva 'sair' para sair da conversa
##################################################
"""


def gerar_wamid() -> str:
    """Usaremos essa função para imitar id de mensagem do WhatsApp API"""
    random_bytes = secrets.token_bytes(20)
    base64_encoded = base64.b64encode(random_bytes).decode("utf-8")
    wamid = f"wamid.{base64_encoded}"
    wamid_pattern = REGEX_WAMID
    if not re.match(wamid_pattern, wamid):
        raise gerar_wamid()

    return wamid


class ChatSession:
    def __init__(self, usuario, uow):
        self.usuario = usuario
        self.uow = uow
        self.bot = CLIBot()

    async def run(self):
        """Runs the main chat loop."""
        while True:
            try:
                mensagem = limpar_texto(typer.prompt(f"{USER_COLOR}Você{RESET_COLOR}"))
                dados_whatsapp = WhatsAppPayload(
                    nome=self.usuario.nome,
                    mensagem=mensagem,
                    telefone=self.usuario.telefone,
                    wamid=gerar_wamid(),
                    object="whatsapp_business_account",
                )

                if mensagem.lower() == "sair":
                    typer.echo("Até logo! 👋")
                    raise typer.Exit()

                response = await responder_usuario(
                    mensagem,
                    self.usuario,
                    self.usuario.telefone,
                    self.bot,
                    uow=self.uow,
                    dados_whatsapp=dados_whatsapp,
                )
                typer.echo(f"{BOT_COLOR}{response}{RESET_COLOR}")

            except KeyboardInterrupt:
                typer.echo("\nAté logo! 👋")
                raise typer.Exit()
            except Exception as e:
                logging.error(e, exc_info=True)
                typer.echo(f"Erro durante o chat: {str(e)}")
                if not typer.confirm("Deseja continuar?"):
                    raise typer.Exit()


@app.command()
def chat():
    """Start a chat session with the bot."""
    typer.echo(HEADER)
    uow = UnitOfWork(session_factory=get_session)
    repo = RepoUsuarioLeitura(session=get_session())

    telefone = typer.prompt("Digite seu telefone")
    usuario = repo.buscar_por_telefone(f"55{telefone}")
    mensagem = "olá"

    while not usuario:
        onboard = OnboardingHandler(uow=uow)
        pergunta_onboard = onboard.handle_message(telefone, mensagem)
        mensagem = typer.prompt(pergunta_onboard)
        usuario = repo.buscar_por_telefone(telefone)

    chat_session = ChatSession(usuario, uow)
    asyncio.run(chat_session.run())


if __name__ == "__main__":
    app()
