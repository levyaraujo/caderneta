import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

import stripe
from stripe import Customer, Subscription

from src.dominio.assinatura.entidade import Assinatura, StatusAssinatura
from src.dominio.assinatura.repo import RepoAssinaturaLeitura
from src.dominio.bot.entidade import WhatsAppBot
from src.dominio.usuario.entidade import Usuario
from src.dominio.usuario.repo import RepoUsuarioLeitura
from src.infra.database.connection import get_session
from src.infra.database.uow import UnitOfWork
from src.infra.log import setup_logging

logger = setup_logging()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")


async def handle_invoice_paid(invoice: Dict[str, Any]) -> None:
    """Handle paid invoice event"""
    customer_id = invoice["customer"]
    invoice_id = invoice["id"]
    amount_paid = invoice["amount_paid"]
    assinatura_id = invoice["subscription"]

    logger.info(f"Invoice {invoice_id} paid: ${amount_paid / 100:.2f} for customer {customer_id}")

    # Update subscription status
    try:
        uow = UnitOfWork(session_factory=get_session)
        with uow:
            repo_assinatura_leitura = RepoAssinaturaLeitura(session=get_session())
            assinatura = repo_assinatura_leitura.buscar_por_stripe_subscription_id(assinatura_id)
            if assinatura:
                assinatura.registrar_pagamento()
                uow.repo_escrita.adicionar(assinatura)
                uow.commit()
    except Exception as e:
        logger.error(f"Error processing paid invoice: {e}")


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
    """Handle comprehensive subscription updates"""
    customer_id = subscription["customer"]
    cliente = stripe.Customer.retrieve(customer_id)
    subscription_id = subscription["id"]
    status = subscription["status"]

    logger.info(f"Assinatura {subscription_id} atualizada para o usuário {cliente.email}: {status}")

    try:
        uow = UnitOfWork(session_factory=get_session)
        statuses = {
            "active": StatusAssinatura.ATIVA,
            "past_due": StatusAssinatura.PENDENTE,
            "unpaid": StatusAssinatura.EXPIRADA,
        }
        with uow:
            repo_assinatura_leitura = RepoAssinaturaLeitura(session=get_session())
            assinatura = repo_assinatura_leitura.buscar_por_stripe_subscription_id(subscription_id)
            assinatura.status = statuses.get(status, StatusAssinatura.ATIVA)
            if status == "canceled":
                assinatura.cancelar()

            uow.repo_escrita.adicionar(assinatura)
            uow.commit()
    except Exception as e:
        traceback.print_exc()
        logger.error(
            f"Erro ao processar atualização de assinatura para o usuário {cliente.email}: {e}. Status assinatura: {status}"
        )


async def handle_trial_will_end(subscription: Dict[str, Any]) -> None:
    customer_id = subscription["customer"]
    cliente = stripe.Customer.retrieve(customer_id)
    nome = cliente.name.split()[0]

    bot = WhatsAppBot()
    mensagem = f"Olá, {nome}! 👋 Percebemos que seu período de testes está chegando ao fim e queremos ajudar você a aproveitar ao máximo nossa plataforma! 🚀\n\n"
    mensagem += "Nos últimos dias, você teve a oportunidade de experimentar todos os recursos que podem transformar sua rotina. Agora, é hora de decidir se quer continuar essa jornada de sucesso com a gente! 💪\n\n"
    mensagem += "🎁 Como cortesia, estamos oferecendo 15% de desconto na primeira mensalidade se você realizar a contratação nos próximos 3 dias. Não perca essa chance!\n\n"
    mensagem += "Quer saber mais detalhes ou tirar alguma dúvida? Estamos à disposição. Nos envie um email para contato@caderneta.chat"

    bot.responder(mensagem, cliente.phone)


EVENT_HANDLERS = {
    "invoice.paid": handle_invoice_paid,
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


def criar_customer_portal_link(subscription_id: str):
    subscription = stripe.Subscription.retrieve(subscription_id)
    customer_id = subscription["customer"]
    link = stripe.billing_portal.Session.create(customer=customer_id, locale="pt-BR")

    return link
