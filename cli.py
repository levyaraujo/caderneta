import asyncio
import typer
import dotenv
from typing import Optional

dotenv.load_dotenv(".env.local")

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


class UserRegistration:
    def __init__(self):
        self.uow = UnitOfWork(session_factory=get_session)
        self.onboard = OnboardingHandler(uow=self.uow)
        self.repo = RepoUsuarioLeitura(session=get_session())

    def find_or_create_user(self, email: Optional[str]) -> Optional[dict]:
        """Handles the user registration/login flow."""
        while True:
            try:
                email = email or typer.prompt("Entre com seu email")
                usuario = self.repo.buscar_por_email(email)

                if usuario:
                    return usuario

                typer.echo("Usuário não encontrado. Iniciando cadastro...")
                usuario = self._handle_registration(email)
                if usuario:
                    return usuario

            except KeyboardInterrupt:
                raise typer.Exit()
            except Exception as e:
                typer.echo(f"Erro durante o cadastro: {str(e)}")
                if not typer.confirm("Deseja tentar novamente?"):
                    raise typer.Exit()

    def _handle_registration(self, email: str) -> Optional[dict]:
        """Handles the new user registration process."""
        try:
            telefone = typer.prompt("Digite seu telefone")

            # Start onboarding
            welcome_msg = self.onboard.start_onboarding(telefone)
            typer.echo(f"{BOT_COLOR}{welcome_msg}{RESET_COLOR}")

            # Get full name
            nome_completo = typer.prompt(f"{USER_COLOR}Você{RESET_COLOR}")
            response = self.onboard.handle_message(telefone, nome_completo)
            typer.echo(f"{BOT_COLOR}{response}{RESET_COLOR}")

            if "Por favor, digite" in response:
                return None

            response = self.onboard.handle_message(telefone, email)
            typer.echo(f"{BOT_COLOR}{response}{RESET_COLOR}")

            if "Cadastro concluído" in response:
                return self.repo.buscar_por_email(email)

            return None

        except Exception as e:
            typer.echo(f"Erro durante o cadastro: {str(e)}")
            return None


class ChatSession:
    def __init__(self, usuario, uow):
        self.usuario = usuario
        self.uow = uow
        self.bot = CLIBot()

    async def run(self):
        """Runs the main chat loop."""
        while True:
            try:
                user_input = limpar_texto(typer.prompt(f"{USER_COLOR}Você{RESET_COLOR}"))

                if user_input.lower() == "sair":
                    typer.echo("Até logo! 👋")
                    raise typer.Exit()

                response = await responder_usuario(
                    user_input, self.usuario, self.usuario.telefone, self.usuario.nome, self.bot, uow=self.uow
                )
                typer.echo(f"{BOT_COLOR}{response}{RESET_COLOR}")

            except KeyboardInterrupt:
                typer.echo("\nAté logo! 👋")
                raise typer.Exit()
            except Exception as e:
                typer.echo(f"Erro durante o chat: {str(e)}")
                if not typer.confirm("Deseja continuar?"):
                    raise typer.Exit()


@app.command()
def chat(email: str = typer.Argument(..., help="Email para acesso ao cli")):
    """Start a chat session with the bot."""
    typer.echo(HEADER)

    # Handle user registration/login
    registration = UserRegistration()
    usuario = registration.find_or_create_user(email)

    if not usuario:
        typer.echo("Não foi possível completar o cadastro. Por favor, tente novamente mais tarde.")
        raise typer.Exit()

    # Start chat session
    uow = UnitOfWork(session_factory=get_session)
    chat_session = ChatSession(usuario, uow)

    try:
        asyncio.run(chat_session.run())
    except Exception as e:
        typer.echo(f"Erro fatal: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
