import os

from contextvars import ContextVar
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)


def add_rate_limiter_middleware(app):
    add_whitelist_middleware(app)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


whitelist_ips = os.getenv('WHITELIST_IPS', '').split(',')


REQUEST_CTX_KEY = "request_context"
_request_ctx_var: ContextVar[str] = ContextVar(REQUEST_CTX_KEY, default=None)

def add_whitelist_middleware(app):
    """This middleware adds a `rate_limit_whitelisted` key to the request context
    Allows for overriding the rate limit

    Use `fly secrets set WHITELIST_IPS=...`, where ... is a single-quoted string of IP addresses separated by commas

    NOTE: Include all the current IPs and tell Duber before you change this
    """

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        ip = get_remote_address(request)
        try:
            request_ctx = _request_ctx_var.set(request)
            if ip in whitelist_ips:
                request_ctx.var.set('rate_limit_whitelisted')
            response = await call_next(request)
            _request_ctx_var.reset(request_ctx)
            return response
        except Exception as e:
            raise e

def is_request_exempt() -> bool:
    try:
        return _request_ctx_var.get('rate_limit_whitelisted') is not None
    except:
        return False