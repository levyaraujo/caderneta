import inspect
import json
import logging
import os
import re
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from email.generator import Generator
from typing import Callable, Dict, List, Optional, Tuple, Iterator

import httpx

from src.dominio.bot.exceptions import ComandoDesconhecido, ErroAoEnviarMensagemWhatsApp
from src.dominio.transacao.repo import RepoTransacaoLeitura
from src.infra.database.connection import get_session
from src.infra.log import setup_logging

logger = setup_logging()


class BotBase(ABC):
    @abstractmethod
    def responder(self, mensagem: str, usuario: str) -> str | dict:
        pass

    @abstractmethod
    def enviar_mensagem_interativa(self, mensagem: dict) -> str | dict:
        pass


class CLIBot(BotBase):
    def responder(self, mensagem: str, usuario: str) -> str | dict:
        return mensagem

    def enviar_mensagem_interativa(self, mensagem: dict) -> str | dict:
        return mensagem["interactive"]["body"]["text"]


class WhatsAppBot(BotBase):
    def __init__(self) -> None:
        self.__url = os.getenv("WHATSAPP_WEBHOOK_URL")
        self.__token = os.getenv("META_TOKEN")

    def responder(
        self, mensagem: str, telefone: str, wamid: Optional[str] = None, reacao: Optional[str] = None
    ) -> dict:
        if reacao:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": f"{telefone}",
                "type": "reaction",
                "reaction": {"message_id": f"{wamid}", "emoji": reacao},
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": telefone,
                "type": "text",
                "text": {"body": f"{mensagem}"},
            }
            if wamid:
                payload["context"] = {"message_id": wamid}
            if mensagem.startswith("http"):
                payload = {
                    "preview_url": True,
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": telefone,
                    "type": "image",
                    "image": {"link": mensagem},
                }
            if mensagem.startswith("http") and mensagem.endswith(".mp3"):
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": telefone,
                    "type": "audio",
                    "audio": {"link": mensagem},
                }
            if mensagem.startswith("http") and mensagem.endswith(".xlsx"):
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": telefone,
                    "type": "document",
                    "document": {"filename": "Exportação Lançamentos.xls", "link": mensagem},
                }
            if mensagem.startswith("http") and "pdf" in mensagem:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": telefone,
                    "type": "document",
                    "document": {"link": mensagem, "caption": "Aqui está a sua NF-e", "filename": "NF-e Caderneta.pdf"},
                }
        url: str = f"{self.__url}/messages"
        return self.enviar_requisicao(url, payload)

    def enviar_mensagem_interativa(self, mensagem: dict) -> dict:
        url: str = f"{self.__url}/messages"
        return self.enviar_requisicao(url, mensagem)

    def enviar_requisicao(self, url: str, payload: dict) -> dict:
        try:
            headers = {
                "Authorization": f"Bearer {self.__token}",
                "Content-Type": "application/json",
            }
            resposta = httpx.post(url=str(url), data=payload, headers=headers)
            erro = resposta.json().get("error")
            if erro:
                logger.error(json.dumps(erro, indent=2))
                raise ErroAoEnviarMensagemWhatsApp("Houve um erro ao enviar mensagem para o usuário")
            return {"status_code": resposta.status_code, "content": resposta.json()}
        except Exception:
            traceback.print_exc()


@dataclass
class Comando:
    name: str
    handler: Callable
    description: str
    icon: str
    aliases: List[str] = field(default_factory=list)
    oculto: bool = False

    def __post_init__(self) -> None:
        self.aliases = self.aliases


class GerenciadorComandos:
    def __init__(self) -> None:
        self.commands: Dict[str, Comando] = {}
        self.prefix = "!"
        self.repo_transacao_leitura: RepoTransacaoLeitura = RepoTransacaoLeitura(session=get_session())

    def comando(
        self,
        name: str,
        description: str,
        icon: str = "",
        aliases: List[str] | None = None,
        oculto: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Decorator to register commands"""

        def decorator(func: Callable):
            cmd = Comando(name, func, description, icon, aliases or [], oculto)
            self.registrar_comando(cmd)
            return func

        return decorator

    def registrar_comando(self, command: Comando):
        """Register a command and its aliases"""
        self.commands[command.name] = command
        for alias in command.aliases or []:
            self.commands[alias] = command

    async def processar_mensagem(self, message: str, **kwargs) -> str:
        message = f"{self.prefix}{message}"

        message = message[len(self.prefix) :].strip()
        parts = message.split()
        if not parts:
            return ""

        command_name, args = self._extract_command_name_and_args(parts)
        command = self.commands.get(command_name)

        if not command:
            for cmd_name, cmd in self.commands.items():
                try:
                    # Check if the command name is a regex pattern
                    if re.match(cmd_name, command_name):
                        command = cmd
                        break
                except Exception:
                    continue

        if not command:
            if command_name:
                logger.warning(f"Comando {command_name} não existe")
            raise ComandoDesconhecido("Comando não existe")

        try:
            if inspect.iscoroutinefunction(command.handler):
                return await command.handler(*args, **kwargs)
            return command.handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro ao executar comando {command_name}: {str(e)}", exc_info=True)
            traceback.print_exc()
            return f"Erro ao executar comando {command_name}. Tente novamente."

    def _extract_command_name_and_args(self, parts: List[str]) -> Tuple[Optional[str], List[str]]:
        """Extrai nome do comando (incluindo comandos com múltiplas palavras) e seus argumentos"""
        for i in range(len(parts), 0, -1):
            command_name = " ".join(parts[:i]).lower()
            eh_remocao_de_transacao = command_name.startswith("wamid")

            if eh_remocao_de_transacao:
                return command_name, [command_name]

            if command_name in self.commands:
                return command_name, parts[i:]
        return None, []

    def ajuda(self) -> str:
        """Gera ajuda listando todos os comandos"""
        help_text = "Por aqui consigo te ajudar com os seguintes comandos:\n\n"
        unique_commands = {cmd.name: cmd for cmd in self.commands.values()}
        for cmd in unique_commands.values():
            if cmd.oculto is False:
                aliases = f" (Também entendo: *{', '.join(cmd.aliases)}*)" if cmd.aliases else ""
                help_text += f"*{cmd.name}*: {cmd.description}{aliases}\n"

        help_text += "\n\nAlém disso, você pode registrar suas receitas e despesas de forma simples.\nEx: *paguei 1350 aluguel* ou *vendi 2300 de buffet*"
        return help_text
