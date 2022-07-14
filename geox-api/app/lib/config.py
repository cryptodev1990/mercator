import os
from ..core.config import get_settings

# TODO: this should be deprecated. Uses should be replaced with the Settings object

_settings = get_settings()

management_client_id = _settings.AUTH0_MACHINE_CLIENT_ID
management_client_secret = _settings.AUTH0_MACHINE_CLIENT_SECRET
auth_audience = _settings.AUTH0_API_AUDIENCE
auth_domain = _settings.AUTH0_DOMAIN
machine_account_email = "duber+ManagementApi@mercator.tech"
machine_account_sub_id = f"{_settings.AUTH0_MACHINE_CLIENT_ID}@clients"
