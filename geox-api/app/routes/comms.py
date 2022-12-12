"""
Write a FastAPI webhook receiver that sends an email when it receives a post message using the
SendGrid API.

"""
import logging


from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.core.config import get_settings
from app.core.logging import get_logger


logger = get_logger(__name__)


router = APIRouter(
    prefix="/comms",
)


config = get_settings()


class EmailMessage(BaseModel):
    """Message model"""
    subject: str
    body: str
    to_email: str


@router.post("/webhook", include_in_schema=False)
async def webhook(request: Request):
    """Webhook receiver for mail

    Sends an email when it receives a post message using the SendGrid API.
    Email sends from the email address in the config file,

    The config value `email_webhook_secret` prevents unauthorized use of the webhook.
    """
    if not config.email_webhook_secret:
        return JSONResponse(
            status_code=500,
            content={"message": "Server issue, please try again later."}
        )
    token = config.email_webhook_secret.get_secret_value()
    if not request.headers.get("Authorization") == f'Bearer {token}':
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    sg = SendGridAPIClient(api_key=config.sendgrid_api_key)
    res = await request.json()
    email_message = EmailMessage(**res)  # type: ignore
    logger.info(
        {"msg": f"Sending email to {email_message.to_email} with subject {email_message.subject}"})
    try:
        from_email = Email(config.sendgrid_sender_email)
        to_email = To(email_message.to_email)
        subject = email_message.subject
        content = Content("text/html", email_message.body)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code == 202:
            logger.info(
                {"msg": f"Email sent to {email_message.to_email} with subject {email_message.subject}"})
            return JSONResponse(status_code=200, content={"message": "Message sent"})
        else:
            logger.error({"sendgrid_body": response.body,
                         "sendgrid_status": response.status_code,
                          "to_email": email_message.to_email,
                          })
            return JSONResponse(status_code=400, content={"message": "Message not sent"})
    except Exception as e:
        logger.error(e)
        return JSONResponse(status_code=400, content={"message": "Message not sent"})
