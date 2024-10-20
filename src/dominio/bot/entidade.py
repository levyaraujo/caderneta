import os
from abc import ABC, abstractmethod
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")


class BotAbstrato(ABC):
    @abstractmethod
    def responder(self, mensagem: str, usuario: str):
        pass


class TwilioBot(BotAbstrato):
    def __init__(self):
        self.__account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.__auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.__bot_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.__cliente = Client(self.__account_sid, self.__auth_token)

    def responder(self, mensagem: str, usuario: str) -> MessageInstance:
        logger.info(
            f"Sending message from: whatsapp:+{self.__bot_number} to: {usuario} with body: {mensagem}"
        )
        resposta = self.__cliente.messages.create(
            from_=f"whatsapp:+{self.__bot_number}",
            to=usuario,
            body=mensagem,
        )
        return resposta
