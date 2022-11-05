# pylint: disable=too-many-locals
import logging
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.crud.organization import (
    add_subscription,
    get_active_organization,
    get_all_org_members,
    get_org_by_subscription_id,
    update_payment_time,
    update_stripe_subscription_status,
)
from app.dependencies import (
    Cache,
    UserConnection,
    get_app_user_connection,
    get_cache,
    get_engine,
    verify_token,
)
from app.schemas.common import BaseModel

logger = logging.getLogger(__name__)


router = APIRouter(tags=["billing"], include_in_schema=False)


# See our keys here: https://dashboard.stripe.com/apikeys
settings = get_settings()
stripe.api_key = settings.stripe_api_key


class CheckoutSession(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str


@router.post("/billing/create-checkout-session", dependencies=[Depends(verify_token)])
async def create_checkout_session(
    checkout_session: CheckoutSession,
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> JSONResponse:
    session = stripe.checkout.Session.create(
        success_url=checkout_session.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=checkout_session.cancel_url,
        client_reference_id=user_conn.user.id,
        mode="subscription",
        line_items=[{"price": checkout_session.price_id, "quantity": 1}],
        subscription_data={"trial_period_days": 14},
    )
    return JSONResponse({"url": session.url})


@router.post("/billing/webhook", dependencies=[Depends(get_engine)])
async def webhook_received(
    request: Request,
    engine: Engine = Depends(get_engine),
    cache: Optional[Cache] = Depends(get_cache),
) -> JSONResponse:
    # To do development work on this webhook, you want to use the Stripe CLI
    # https://stripe.com/docs/stripe-cli
    # or use ngrok
    # See https://dashboard.stripe.com/webhooks/we_1LxitiEKpERrAtCsMdHGmOVq for the webhooks
    webhook_secret = settings.stripe_webhook_secret
    request_data = await request.body()

    if not webhook_secret:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")

    signature = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload=request_data, sig_header=signature, secret=webhook_secret
        )
        data = event["data"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        # NOTE the client_reference_id is the user_id and is set in the create_checkout_session function
        # It is read from the JWT
        # This event pairs a user ID with their subscription ID
        user_id = int(data["object"]["client_reference_id"])

        with engine.begin() as conn:
            if cache:
                cache.delete(f"app:cache:user_org:{user_id}")
            subscription_id = str(data["object"]["subscription"])
            org = get_active_organization(conn, user_id)
            add_subscription(conn, organization_id=org.id, stripe_sub_id=subscription_id)
    elif event_type == "invoice.paid":
        # This event pairs a subscription ID with a payment time
        with engine.begin() as conn:
            subscription_id = str(data["object"]["subscription"])
            # Clear cache for all users in the org
            org = get_org_by_subscription_id(conn, subscription_id)
            users = get_all_org_members(conn, org.id)
            for u in users:
                if cache:
                    cache.delete(f"app:cache:user_org:{u.id}")
            update_payment_time(conn, stripe_sub_id=subscription_id)
            logging.info({"msg": "Payment succeeded."})
    elif event_type.startswith("customer.subscription."):
        # This event pairs a subscription ID with a trial end time
        with engine.begin() as conn:
            subscription_id = str(data["object"]["id"])
            status = data["object"]["status"]
            org = get_org_by_subscription_id(conn, subscription_id)
            users = get_all_org_members(conn, org.id)
            for u in users:
                if cache:
                    cache.delete(f"app:cache:user_org:{u.id}")
            update_stripe_subscription_status(
                conn, stripe_sub_id=subscription_id, status=status
            )
    elif event_type == "invoice.payment_failed":
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
        # TODO take action to notify the user
        logging.warning({"msg": "Payment failed."})
    else:
        return JSONResponse(
            {"msg": f"Unhandled event type {event_type}"},
            status_code=400,
        )

    return JSONResponse({"status": "success"})
