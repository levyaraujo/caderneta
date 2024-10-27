import logging
import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from twilio.rest import Client
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
import inspect

from src.dominio.bot.exceptions import ComandoDesconhecido
from src.dominio.transacao.repo import RepoTransacaoLeitura
from src.infra.database.connection import (
    GET_DEFAULT_SESSION_CONTEXT,
    GET_DEFAULT_SESSION,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")


class BotBase(ABC):
    @abstractmethod
    def responder(self, mensagem: str, usuario: str):
        pass


class TwilioBot(BotBase):
    def __init__(self):
        self.__account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.__auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.__bot_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.__cliente = Client(self.__account_sid, self.__auth_token)

    def responder(self, mensagem: str, usuario: str) -> str:
        media_url = mensagem if mensagem.startswith("http") else None
        mensagem = "" if media_url else mensagem

        logger.info(
            f"Sending message from: whatsapp:+{self.__bot_number} to: {usuario} with body: {mensagem}"
        )
        resposta = self.__cliente.messages.create(
            from_=f"whatsapp:+{self.__bot_number}",
            to=usuario,
            body=mensagem,
            media_url=media_url,
        )
        return resposta.body


class CLIBot(BotBase):
    def responder(self, mensagem: str, usuario: str):
        return mensagem


@dataclass
class Comando:
    name: str
    handler: Callable
    description: str
    icon: str
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.aliases = self.aliases


class GerenciadorComandos:
    def __init__(self):
        self.commands: Dict[str, Comando] = {}
        self.prefix = "!"
        self.__session = GET_DEFAULT_SESSION
        self.repo_transacao_leitura: RepoTransacaoLeitura = RepoTransacaoLeitura(
            session=self.__session()
        )

    def comando(
        self,
        name: str,
        description: str,
        icon: str = "",
        aliases: List[str] | None = None,
    ) -> Callable[[Callable], Callable]:
        """Decorator to register commands"""

        def decorator(func: Callable):
            cmd = Comando(name, func, description, icon, aliases or [])
            self.registrar_comando(cmd)
            return func

        return decorator

    def registrar_comando(self, command: Comando):
        """Register a command and its aliases"""
        self.commands[command.name] = command
        for alias in command.aliases or []:
            self.commands[alias] = command

    async def processar_mensagem(self, message: str, **kwargs) -> Optional[str]:
        message = f"!{message}"
        """Handle incoming messages and execute commands"""
        if not message.startswith(self.prefix):
            return None

        message = message[len(self.prefix) :].strip()
        parts = message.split()
        if not parts:
            return None

        command_name, args = self._extract_command_name_and_args(parts)
        if not command_name:
            logger.warning(f"Comando {command_name} não existe")
            raise ComandoDesconhecido("Comando não existe")

        command = self.commands.get(command_name)
        if not command:
            logger.warning(f"Comando {command_name} não existe")
            raise ComandoDesconhecido("Comando não existe")

        try:
            if inspect.iscoroutinefunction(command.handler):
                return await command.handler(*args, **kwargs)
            return command.handler(*args, **kwargs)
        except Exception as e:
            return f"Erro ao executar comando {command_name}: {str(e)}"

    def _extract_command_name_and_args(
        self, parts: List[str]
    ) -> Tuple[Optional[str], List[str]]:
        """Extrai nome do comando (incluindo comandos com múltiplas palavras) e seus argumentos"""
        for i in range(len(parts), 0, -1):
            command_name = " ".join(parts[:i]).lower()
            if command_name in self.commands:
                return command_name, parts[i:]
        return None, []

    def get_help(self) -> str:
        """Gera ajuda listando todos os comandos"""
        help_text = "📔 Comandos disponíveis:\n\n"
        unique_commands = {cmd.name: cmd for cmd in self.commands.values()}
        for cmd in unique_commands.values():
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_text += f"{cmd.icon} *{cmd.name}*: {cmd.description}{aliases}\n"
        return help_text
