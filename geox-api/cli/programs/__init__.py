from .organizations.skip_stripe import subscription_whitelist_app
from .users.get_jwt import get_jwt_app

cli_apps = [
    get_jwt_app,
    subscription_whitelist_app,
]
