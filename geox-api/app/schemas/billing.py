from .common import BaseModel


class CheckoutSessionCreate(BaseModel):

    price_id: str
    success_url: str
    cancel_url: str
