import os
import traceback

import stripe
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from starlette.requests import Request

from src.dominio.assinatura.services import EVENT_HANDLERS
from src.infra.log import setup_logging

logger = setup_logging()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

StripeRouter = APIRouter(prefix="/webhook", tags=["stripe"])


class WebhookResponse(BaseModel):
    status: str
    message: str = ""


@StripeRouter.post("/stripe", status_code=200, response_model=WebhookResponse)
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
