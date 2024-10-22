import typer
from typing import Optional

from src.dominio.bot.entidade import CLIBot
from src.dominio.bot.services import responder_usuario

app = typer.Typer()

USER_COLOR = "\033[94m"  # Blue
BOT_COLOR = "\033[92m"  # Green
RESET_COLOR = "\033[0m"  # Reset to default color


@app.command()
def chat(
    usuario: Optional[str] = typer.Option(
        "CLI_USER", "--usuario", "-u", help="User identifier"
    ),
):
    """
    Start a chat session with the bot.
    """
    print("\n")
    print("#" * 50)
    typer.echo("🤖 Caderneta CLI")
    typer.echo("Escreva 'sair' para sair da conversa")
    print("#" * 50)
    print("\n")

    bot = CLIBot()

    while True:
        user_input = typer.prompt(f"{USER_COLOR}Você{RESET_COLOR}")

        if user_input.lower() == "sair":
            typer.echo("Goodbye!")
            raise typer.Exit()

        response = responder_usuario(user_input, usuario, bot)
        typer.echo(f"{BOT_COLOR}Bot: {response}{RESET_COLOR}")


if __name__ == "__main__":
    app()
