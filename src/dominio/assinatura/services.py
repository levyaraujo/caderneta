import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

import stripe
from stripe import Customer, Subscription

from src.dominio.assinatura.entidade import Assinatura
from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.usuario.entidade import Usuario
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.infra.log import setup_logging

logger = setup_logging()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")


async def handle_successful_payment(payment_intent: Dict[str, Any]) -> None:
    """Handle successful payment"""
    amount = payment_intent["amount"]
    customer_id = payment_intent["customer"]
    payment_id = payment_intent["id"]

    logger.info(f"Payment {payment_id} succeeded: ${amount / 100:.2f} from customer {customer_id}")

    # Here you would typically:
    # 1. Update your database (use async ORM like SQLAlchemy async or tortoise-orm)
    # await db.payments.update_one({"payment_id": payment_id}, {"status": "succeeded"})

    # 2. Send confirmation email (use async email library)
    # await send_email_async(customer_id, "Payment Successful", "Thank you for your payment...")

    # 3. Fulfill order
    # await fulfill_order(payment_id)
    pass


async def handle_failed_payment(payment_intent: Dict[str, Any]) -> None:
    """Handle failed payment"""
    customer_id = payment_intent["customer"]
    payment_id = payment_intent["id"]
    error = payment_intent.get("last_payment_error", {})

    logger.error(f"Payment {payment_id} failed for customer {customer_id}: {error}")

    # Here you would typically:
    # 1. Update payment status in database
    # await db.payments.update_one({"payment_id": payment_id}, {"status": "failed"})

    # 2. Notify customer
    # await send_notification_async(customer_id, "Payment Failed")
    pass


async def handle_subscription_updated(subscription: Dict[str, Any]) -> None:
    """Handle subscription updates"""
    customer_id = subscription["customer"]
    subscription_id = subscription["id"]
    status = subscription["status"]

    logger.info(f"Subscription {subscription_id} updated for customer {customer_id}: {status}")

    # Here you would typically:
    # 1. Update subscription status in database
    # await db.subscriptions.update_one(
    #     {"subscription_id": subscription_id},
    #     {"status": status}
    # )
    pass


async def handle_trial_will_end(subscription: Dict[str, Any]) -> None:
    customer_id = subscription["customer"]
    cliente = stripe.Customer.retrieve(customer_id)

    bot = WhatsAppBot()
    mensagem = f"Olá, {cliente.name}! 👋 Percebemos que seu período de testes está chegando ao fim e queremos ajudar você a aproveitar ao máximo nossa plataforma! 🚀\n\n"
    mensagem += "Nos últimos dias, você teve a oportunidade de experimentar todos os recursos que podem transformar sua rotina. Agora, é hora de decidir se quer continuar essa jornada de sucesso com a gente! 💪\n\n"
    mensagem += "🎁 Como cortesia, estamos oferecendo 20% de desconto na primeira mensalidade se você realizar a contratação nos próximos 3 dias. Não perca essa chance!\n\n"
    mensagem += "Quer saber mais detalhes ou tirar alguma dúvida? Estamos à disposição. Nos envie um email para contato@caderneta.chat"

    bot.responder(mensagem, cliente.phone)


EVENT_HANDLERS = {
    "payment_intent.succeeded": handle_successful_payment,
    "payment_intent.payment_failed": handle_failed_payment,
    "customer.subscription.updated": handle_subscription_updated,
    "customer.subscription.trial_will_end": handle_trial_will_end,
}


def criar_cliente_stripe(usuario: Usuario) -> Customer:
    cliente_existe = stripe.Customer.list(email=usuario.email, limit=1).get("data")

    if cliente_existe:
        return cliente_existe[0]
    novo_cliente = stripe.Customer.create(
        name=f"{usuario.nome} {usuario.sobrenome}", email=usuario.email, phone=usuario.telefone
    )
    return novo_cliente


def criar_assinatura(cliente: Customer) -> Tuple[Subscription, Assinatura]:
    repo_usuario = RepoUsuarioLeitura(session=get_session())
    usuario = repo_usuario.buscar_por_email(cliente.email)
    PLANO = os.getenv("PLANO_CADERNETA")
    dados = {
        "customer": cliente.id,
        "items": [{"price": PLANO}],
        "trial_period_days": 14,
        "payment_behavior": "allow_incomplete",
    }
    try:
        assinatura_stripe = stripe.Subscription.create(**dados)
        assinatura = criar_assinatura_entidade(assinatura_stripe.id, usuario)
        return assinatura_stripe, assinatura
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)


def criar_assinatura_entidade(id_stripe: str, usuario: Usuario) -> Assinatura:
    uow = UnitOfWork(session_factory=get_session)
    inicio = datetime.now()
    fim_do_teste = inicio + timedelta(days=14)

    with uow:
        assinatura = Assinatura(
            stripe_id=id_stripe,
            usuario_id=usuario.id,
            plano="Caderneta Básico",
            data_inicio=inicio,
            data_ultimo_pagamento=inicio,
            data_proximo_pagamento=fim_do_teste,
            valor_mensal=14.99,
        )
        usuario.assinatura = assinatura

        uow.repo_escrita.adicionar(assinatura)

        uow.commit()
        return assinatura
