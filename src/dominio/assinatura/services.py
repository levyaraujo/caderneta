import traceback

from fastapi import Request, HTTPException
from typing import Dict, Any
import stripe
import os
from pydantic import BaseModel

from src.infra.log import setup_logging

logger = setup_logging()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")


class WebhookResponse(BaseModel):
    status: str
    message: str = ""


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


async def handle_subscription_created(subscription: Dict[str, Any]) -> None:
    """Handle new subscription"""
    customer_id = subscription["customer"]
    subscription_id = subscription["id"]
    plan_id = subscription["plan"]["id"]

    logger.info(f"New subscription {subscription_id} for customer {customer_id} to plan {plan_id}")

    # Here you would typically:
    # 1. Update customer status in database
    # await db.subscriptions.insert_one({
    #     "subscription_id": subscription_id,
    #     "customer_id": customer_id,
    #     "plan_id": plan_id,
    #     "status": "active"
    # })

    # 2. Send welcome email
    # await send_welcome_email_async(customer_id)
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


EVENT_HANDLERS = {
    "payment_intent.succeeded": handle_successful_payment,
    "payment_intent.payment_failed": handle_failed_payment,
    "customer.subscription.created": handle_subscription_created,
    "customer.subscription.updated": handle_subscription_updated,
}


async def handle_webhook(request: Request) -> WebhookResponse:
    """
    Handle incoming Stripe webhooks
    """
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="No Stripe signature header")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Get the event type and handler
    event_type = event["type"]
    handler = EVENT_HANDLERS.get(event_type)

    try:
        if handler:
            # Execute the appropriate handler
            await handler(event["data"]["object"])
            return WebhookResponse(status="success", message=f"Handled {event_type} event")
        else:
            # Log unhandled event type
            logger.info(f"Unhandled event type: {event_type}")
            return WebhookResponse(status="success", message=f"Unhandled event type: {event_type}")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
