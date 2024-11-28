import os

import redis
import json
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Optional, Generator

from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.services import criar_usuario
from src.infra.database.uow import UnitOfWork
from src.infra.email import enviar_email_boas_vindas
from src.utils.validadores import validar_email

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "1234")


class OnboardingState(Enum):
    INITIAL = auto()
    WAITING_FULL_NAME = auto()
    WAITING_EMAIL = auto()
    COMPLETED = auto()


@dataclass
class UserData:
    telefone: str
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[str] = None


@dataclass
class UserContext:
    state: OnboardingState
    data: UserData


class OnboardingHandler:
    def __init__(
        self, redis_host: str = REDIS_HOST, redis_port: str | int = REDIS_PORT, uow: UnitOfWork = None
    ) -> None:
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=REDIS_PASSWORD)
        self.uow = uow

    def start_onboarding(self, phone_number: str) -> str:
        mensagem_boas_vindas = f"""
Olá, empreendedor! 🚀💼

Bem-vindo ao *Caderneta* - Seu parceiro inteligente em gestão financeira! 📊💰

Imagina controlar suas finanças com simplicidade e precisão, direto do seu WhatsApp? Estamos aqui para transformar sua gestão financeira em algo descomplicado e estratégico.

Com o *Caderneta*, você vai:
- Acompanhar receitas e despesas em tempo real
- Gerar relatórios financeiros instantâneos
- Tomar decisões inteligentes sobre seu negócio

Vamos começar? Me diga seu nome completo para personalizar sua experiência. 😊"""
        if not self._get_user_context(phone_number):
            context = UserContext(
                state=OnboardingState.WAITING_FULL_NAME,
                data=UserData(telefone=phone_number),
            )
            self._save_user_context(phone_number, context)
            return mensagem_boas_vindas
        return self._get_current_question(phone_number)

    def handle_message(self, phone_number: str, message: str) -> str:
        context = self._get_user_context(phone_number)
        if not context:
            return self.start_onboarding(phone_number)

        if context.state == OnboardingState.COMPLETED:
            criar_usuario(UsuarioModel(**asdict(context.data)), uow=self.uow)  # noqa
            return self._generate_completion_message()
        elif context.state == OnboardingState.WAITING_FULL_NAME:
            return self._handle_full_name(context, message)
        elif context.state == OnboardingState.WAITING_EMAIL:
            return self._handle_email(context, message)

        return self._save_user_context(phone_number, context)  # noqa

    def _handle_full_name(self, context: UserContext, name: str) -> str:
        name = name.strip().capitalize()
        if self._validate_full_name(name):
            context.data.nome = name.split()[0]
            context.data.sobrenome = " ".join(part.capitalize() for part in name.split()[1:])
            context.state = OnboardingState.WAITING_EMAIL
            self._save_user_context(context.data.telefone, context)
            return "Ótimo! Agora, por favor me diga seu email:"
        return "Por favor, digite seu nome completo."

    def _handle_email(self, context: UserContext, email: str) -> str:
        try:
            validar_email(email)
            context.data.email = email
            context.state = OnboardingState.COMPLETED
            self._save_user_context(context.data.telefone, context)
            usuario = criar_usuario(UsuarioModel(**asdict(context.data)), uow=self.uow)  # noqa
            enviar_email_boas_vindas(usuario)
            return self._generate_completion_message()
        except ValueError as error:
            return "Por favor, digite um email válido."

    def _validate_full_name(self, name: str) -> bool:
        if not name or not all(char.isalpha() or char.isspace() for char in name):
            return False
        words = name.split()
        return len(words) >= 2 and all(len(word) >= 2 for word in words)

    def _get_current_question(self, phone_number: str) -> str:
        context = self._get_user_context(phone_number)
        if context and hasattr(context, "state"):
            if context.state == OnboardingState.WAITING_FULL_NAME:
                return "Por favor, me diga seu nome completo:"
            elif context.state == OnboardingState.WAITING_EMAIL:
                return "Por favor, me diga seu email:"
            return self._generate_completion_message()
        return ""

    def _generate_completion_message(self) -> str:
        from src.dominio.bot.comandos import bot

        return f"Cadastro concluído com sucesso! ✅\n\nAgora você pode utilizar nossos serviços! 🎉\n\n{bot.ajuda()}"

    def get_user_data(self, phone_number: str) -> Optional[UserData]:
        context = self._get_user_context(phone_number)
        return context.data if context else None

    def is_onboarding_completed(self, phone_number: str) -> bool:
        context = self._get_user_context(phone_number)
        return context.state == OnboardingState.COMPLETED if context else False

    def _get_user_context(self, phone_number: str) -> Optional[UserContext]:
        raw_context = self.redis_client.get(phone_number)
        if raw_context:
            context_dict = json.loads(raw_context)  # noqa
            user_data = UserData(**context_dict["data"])
            return UserContext(state=OnboardingState[context_dict["state"]], data=user_data)
        return None

    def _save_user_context(self, phone_number: str, context: UserContext) -> str:
        context_dict = {"state": context.state.name, "data": asdict(context.data)}  # noqa
        self.redis_client.set(phone_number, json.dumps(context_dict), ex=900)

        return phone_number
