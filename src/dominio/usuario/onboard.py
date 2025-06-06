import os
import uuid

import redis
import json
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Optional, Generator

from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.services import criar_usuario, PasswordHasher
from src.infra.database.uow import UnitOfWork
from src.infra.emails import enviar_email_boas_vindas
from src.utils.validadores import validar_email

ENV = os.getenv("ENV", "dev")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "1234") if ENV == "dev" else None


class OnboardingState(Enum):
    INITIAL = auto()
    WAITING_FULL_NAME = auto()
    WAITING_EMAIL = auto()
    WAITING_CODE_CONFIRMATION = auto()
    COMPLETED = auto()


@dataclass
class UserData:
    telefone: str
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[str] = None
    cliente: Optional[uuid.UUID | str] = None
    nome_cliente: Optional[str] = None
    numero_cliente: Optional[str] = None
    token: Optional[str] = None
    tipo: str = "usuario"
    tentativas: int = 5


@dataclass
class UserContext:
    state: OnboardingState
    data: UserData


class Onboard:
    def __init__(
        self, redis_host: str = REDIS_HOST, redis_port: str | int = REDIS_PORT, uow: UnitOfWork = None
    ) -> None:
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=REDIS_PASSWORD)
        self.uow = uow

    def start_onboarding(self, phone_number: str) -> str:
        contexto = self._get_user_context(phone_number)
        if contexto and contexto.data.tipo == "bpo":
            return self.mensagem_inicial_bpo(contexto)
        if not contexto:
            mensagem_boas_vindas = self.mensagem_inicial()
            context = UserContext(
                state=OnboardingState.WAITING_FULL_NAME,
                data=UserData(telefone=phone_number),
            )
            self._save_user_context(phone_number, context)
            return mensagem_boas_vindas
        return self._get_current_question(phone_number)

    def mensagem_inicial(self) -> str:
        mensagem_boas_vindas = f"""
Olá! 👋✨

Seja muito bem-vindo ao *Caderneta* – seu assistente pessoal de finanças! 💸📱

Aqui, você tem o controle do seu dinheiro na palma da mão, direto pelo WhatsApp. Nossa missão é te ajudar a organizar seus gastos, acompanhar sua evolução e alcançar seus objetivos com mais clareza e tranquilidade. 🧘‍♂️📊

Com o *Caderneta*, você pode:
✅ Registrar seus gastos e ganhos de forma simples
✅ Acompanhar seu saldo e hábitos financeiros
✅ Receber resumos e dicas personalizadas

Vamos juntos nessa jornada rumo a uma vida financeira mais leve e inteligente?

Para começar, me diga seu nome completo. 😊
"""
        return mensagem_boas_vindas

    def mensagem_inicial_bpo(self, contexto: UserContext) -> str:
        bpo = (
            f"Além disso, vi aqui que você foi adicionado como BPO pelo cliente *{contexto.data.nome_cliente} "
            f"({contexto.data.numero_cliente})*\nEm breve teremos um dashboard para gerenciar todos os seus clientes!"
        )

        mensagem_boas_vindas = f"""
        Olá! 🚀💼

        Bem-vindo ao *Caderneta* - Seu parceiro inteligente em gestão financeira! 📊💰

        Imagina controlar suas finanças com simplicidade e precisão, direto do seu WhatsApp? Estamos aqui para transformar sua gestão financeira em algo descomplicado e estratégico.

        Com o *Caderneta*, você vai:
        ✅ Acompanhar receitas e despesas em tempo real
        ✅ Gerar relatórios financeiros instantâneos
        ✅ Tomar decisões inteligentes sobre seu negócio

        {bpo}

        Vamos começar? Me diga seu nome completo para personalizar sua experiência. 😊"""
        return mensagem_boas_vindas

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
        elif context.state == OnboardingState.WAITING_CODE_CONFIRMATION:
            return self._confirm_code(context, message)

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

            if context.data.tipo == "bpo":
                context.state = OnboardingState.WAITING_CODE_CONFIRMATION
                self._save_user_context(context.data.telefone, context)
                return f"Para finalizar o cadastro, digite o código de 6 dígitos informado pelo seu cliente.\n\nVocê possui {context.data.tentativas} tentativas restantes"

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

    def _confirm_code(self, context: UserContext, code: str) -> str:
        if PasswordHasher.verify_password(code, context.data.token):
            context.state = OnboardingState.COMPLETED
            # usuario = criar_usuario(UsuarioModel(**asdict(context.data)), uow=self.uow)  # noqa
            self._save_user_context(context.data.telefone, context)
            # enviar_email_boas_vindas(usuario)
            return self._generate_completion_message()

        if context.data.tentativas == 0:
            self._remove_user_context(context)
            return f"O número de tentativas esgotou. O cliente deve realizar o cadastro novamente."

        context.data.tentativas -= 1
        self._save_user_context(context.data.telefone, context)
        return f"Código errado. Tente novamente.\n\nVocê possui {context.data.tentativas} tentativas restantes."

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

    def _save_user_context(self, key: str, context: UserContext) -> str:
        context_dict = {"state": context.state.name, "data": asdict(context.data)}
        self.redis_client.set(key, json.dumps(context_dict), ex=900)

        return key

    def _remove_user_context(self, context: UserContext) -> str:
        self.redis_client.delete(context.data.telefone)

        return f"Contexto do cliente {context.data.telefone} removido com sucesso!"
