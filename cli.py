import asyncio

import typer
from typing import Optional

from src.dominio.bot.entidade import CLIBot
from src.dominio.bot.services import responder_usuario
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.utils.validadores import limpar_texto

app = typer.Typer()

USER_COLOR = "\033[94m"  # Blue
BOT_COLOR = "\033[92m"  # Green
RESET_COLOR = "\033[0m"  # Reset to default color


@app.command()
def chat():
    """
    Start a chat session with the bot.
    """
    print("\n")
    print("#" * 50)
    typer.echo("🤖 Caderneta CLI")
    typer.echo("Escreva 'sair' para sair da conversa")
    print("#" * 50)
    print("\n")

    usuario = None
    while not usuario:
        email = typer.prompt("Entre com seu email")
        usuario = RepoUsuarioLeitura(session=get_session()).buscar_por_email(email)
        if not usuario:
            print(f"Usuário {email} não existe. Tente novamente.")

    uow = UnitOfWork(session_factory=get_session)

    bot = CLIBot()

    async def run_chat_session():
        while True:
            user_input = limpar_texto(typer.prompt(f"{USER_COLOR}Você{RESET_COLOR}"))
            if user_input.lower() == "sair":
                typer.echo("Goodbye!")
                raise typer.Exit()
            response = await responder_usuario(user_input, usuario, usuario.telefone, usuario.nome, bot, uow=uow)
            typer.echo(f"{BOT_COLOR}{response}{RESET_COLOR}")

    asyncio.run(run_chat_session())


if __name__ == "__main__":
    app()
