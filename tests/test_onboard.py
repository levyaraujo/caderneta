# tests/test_onboarding_handler.py
import pytest
import json
import redis
from unittest.mock import Mock, patch
from src.dominio.usuario.onboard import OnboardingHandler, OnboardingState, UserContext, UserData
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork


@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    mock_client = Mock(spec=redis.StrictRedis)
    return mock_client


@pytest.fixture
def onboarding_handler(mock_redis):
    """Create an OnboardingHandler with mock Redis and UnitOfWork"""
    with patch("redis.StrictRedis", return_value=mock_redis):
        uow_mock = UnitOfWork(session_factory=get_session)
        handler = OnboardingHandler(uow=uow_mock)
        return handler


def test_start_onboarding_new_user(onboarding_handler, mock_redis):
    """Test starting onboarding for a new user"""
    phone_number = "+5511999999999"

    # Simulate no existing context in Redis
    mock_redis.get.return_value = None

    welcome_message = onboarding_handler.start_onboarding(phone_number)

    # Verify Redis was called to save context
    assert mock_redis.set.called

    # Verify welcome message
    assert "Olá, empreendedor!" in welcome_message

    # Verify context was saved in Redis
    context_dict = json.loads(mock_redis.set.call_args[0][1])
    assert context_dict["state"] == "WAITING_FULL_NAME"
    assert context_dict["data"]["telefone"] == phone_number


def test_handle_full_name_valid(onboarding_handler, mock_redis):
    """Test handling a valid full name"""
    phone_number = "+5511999999999"

    # Simulate existing context in Redis for full name stage
    context = UserContext(state=OnboardingState.WAITING_FULL_NAME, data=UserData(telefone=phone_number))
    mock_redis.get.return_value = json.dumps({"state": "WAITING_FULL_NAME", "data": {"telefone": phone_number}})

    response = onboarding_handler.handle_message(phone_number, "João Silva Santos")

    # Verify Redis was called to update context
    assert mock_redis.set.called

    # Verify response and context update
    assert "Agora, por favor me diga seu email" in response

    # Verify context was updated correctly
    context_dict = json.loads(mock_redis.set.call_args[0][1])
    assert context_dict["state"] == "WAITING_EMAIL"
    assert context_dict["data"]["nome"] == "João"
    assert context_dict["data"]["sobrenome"] == "Silva Santos"


def test_handle_full_name_invalid(onboarding_handler, mock_redis):
    """Test handling an invalid full name"""
    phone_number = "+5511999999999"

    # Simulate existing context in Redis for full name stage
    mock_redis.get.return_value = json.dumps({"state": "WAITING_FULL_NAME", "data": {"telefone": phone_number}})

    response = onboarding_handler.handle_message(phone_number, "João")

    # Verify response asks for full name again
    assert "Por favor, digite seu nome completo" in response

    # Verify Redis was not called to update state
    assert not mock_redis.set.called


def test_handle_email_valid(onboarding_handler, mock_redis):
    """Test handling a valid email"""
    phone_number = "+5511999999999"

    # Simulate existing context in Redis for email stage
    mock_redis.get.return_value = json.dumps(
        {"state": "WAITING_EMAIL", "data": {"telefone": phone_number, "nome": "João", "sobrenome": "Silva Santos"}}
    )

    with patch("src.dominio.usuario.onboard.criar_usuario") as mock_criar_usuario, patch(
        "src.dominio.usuario.onboard.enviar_email_boas_vindas"
    ) as mock_enviar_email:
        response = onboarding_handler.handle_message(phone_number, "joao.silva@example.com")

        # Verify the created user model
        created_user = mock_criar_usuario.call_args[0][0]
        assert created_user.nome == "João"
        assert created_user.sobrenome == "Silva Santos"
        assert created_user.email == "joao.silva@example.com"
        assert created_user.telefone == phone_number

        # Verify email sending was called
        mock_enviar_email.assert_called_once()

    # Verify Redis context update
    assert mock_redis.set.called
    context_dict = json.loads(mock_redis.set.call_args[0][1])
    assert context_dict["state"] == "COMPLETED"


def test_handle_email_invalid(onboarding_handler, mock_redis):
    """Test handling an invalid email"""
    phone_number = "+5511999999999"

    # Simulate existing context in Redis for email stage
    mock_redis.get.return_value = json.dumps(
        {"state": "WAITING_EMAIL", "data": {"telefone": phone_number, "nome": "João", "sobrenome": "Silva Santos"}}
    )

    response = onboarding_handler.handle_message(phone_number, "invalid-email")

    # Verify response asks for valid email
    assert "Por favor, digite um email válido" in response

    # Verify Redis was not called to update state
    assert not mock_redis.set.called


def test_is_onboarding_completed(onboarding_handler, mock_redis):
    """Test checking onboarding completion status"""
    phone_number = "5511999999999"

    # Test completed onboarding
    mock_redis.get.return_value = json.dumps(
        {
            "state": "COMPLETED",
            "data": {
                "telefone": phone_number,
                "nome": "João",
                "sobrenome": "Silva Santos",
                "email": "joao.silva@example.com",
            },
        }
    )
    assert onboarding_handler.is_onboarding_completed(phone_number) == True

    # Test incomplete onboarding
    mock_redis.get.return_value = json.dumps({"state": "WAITING_EMAIL", "data": {"telefone": phone_number}})
    assert onboarding_handler.is_onboarding_completed(phone_number) == False

    # Test no context
    mock_redis.get.return_value = None
    assert onboarding_handler.is_onboarding_completed(phone_number) == False


def test_get_current_question(onboarding_handler, mock_redis):
    """Test getting the current onboarding question"""
    phone_number = "+5511999999999"

    # Test full name stage
    mock_redis.get.return_value = json.dumps({"state": "WAITING_FULL_NAME", "data": {"telefone": phone_number}})
    assert "me diga seu nome completo" in onboarding_handler.start_onboarding(phone_number)

    # Test email stage
    mock_redis.get.return_value = json.dumps(
        {"state": "WAITING_EMAIL", "data": {"telefone": phone_number, "nome": "João"}}
    )
    assert "me diga seu email" in onboarding_handler.start_onboarding(phone_number)
