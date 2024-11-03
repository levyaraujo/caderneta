import redis
import json
from dataclasses import asdict, dataclass
from enum import Enum, auto
from typing import Optional

from src.dominio.usuario.entidade import UsuarioModel
from src.dominio.usuario.services import criar_usuario
from src.utils.validadores import validar_email


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
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

    def start_onboarding(self, phone_number: str) -> str:
        if not self._get_user_context(phone_number):
            context = UserContext(
                state=OnboardingState.WAITING_FULL_NAME,
                data=UserData(telefone=phone_number),
            )
            self._save_user_context(phone_number, context)
            return "Olá! Bem-vindo ao nosso chatbot! 😊\nPara começar, por favor me diga seu nome completo:"
        return self._get_current_question(phone_number)

    def handle_message(self, phone_number: str, message: str) -> str:
        context = self._get_user_context(phone_number)
        if not context:
            return self.start_onboarding(phone_number)

        if context.state == OnboardingState.COMPLETED:
            criar_usuario(UsuarioModel(**asdict(context.data)))  # noqa
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
        if validar_email(email):
            context.data.email = email
            context.state = OnboardingState.COMPLETED
            self._save_user_context(context.data.telefone, context)
            criar_usuario(UsuarioModel(**asdict(context.data)))  # noqa
            return self._generate_completion_message()
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
        return "Cadastro concluído com sucesso! ✅\n\n" "Agora você pode utilizar nossos serviços! 🎉"

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

    def _save_user_context(self, phone_number: str, context: UserContext):
        context_dict = {"state": context.state.name, "data": asdict(context.data)}  # noqa
        self.redis_client.set(phone_number, json.dumps(context_dict))
