import traceback

import stripe

from src.dominio.assinatura.entidade import ProvedorPagamento


class Stripe(ProvedorPagamento):
    def __init__(self, api_key: str):
        self.stripe = stripe
        self.stripe.api_key = api_key

    async def create_subscription(self, customer_email: str, payment_method_id: str, price_id: str) -> str:
        try:
            customer = await self.stripe.Customer.create(
                email=customer_email,
                payment_method=payment_method_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )

            subscription = await self.stripe.Subscription.create(
                customer=customer.id, items=[{"price": price_id}], expand=["latest_invoice.payment_intent"]
            )

            return subscription.id

        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Falha ao criar assinatura: {str(e)}")

    async def cancel_subscription(self, subscription_id: str) -> None:
        try:
            await self.stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Falha ao cancelar assinatura: {str(e)}")

    async def reactivate_subscription(self, subscription_id: str) -> None:
        try:
            await self.stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Falha ao reativar assinatura: {str(e)}")

    async def get_subscription_status(self, subscription_id: str) -> str:
        try:
            subscription = await self.stripe.Subscription.retrieve(subscription_id)
            return subscription.status
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Falha ao obter status da assinatura: {str(e)}")
