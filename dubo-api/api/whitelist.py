"""Allows for overriding the rate limit

Use `fly secrets set WHITELIST_IPS=...`, where ... is a single-quoted string of IP addresses separated by commas

Include all the current IPs and tell Duber before you change this
"""
import json
import os

from contextvars import ContextVar
from fastapi import Request
from slowapi.util import get_remote_address


whitelist_ips = os.getenv('WHITELIST_IPS', '').split(',')


REQUEST_CTX_KEY = "request_context"
_request_ctx_var: ContextVar[str] = ContextVar(REQUEST_CTX_KEY, default=None)

def add_whitelist_middleware(app):

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

def is_request_exempt():
    try:
        return _request_ctx_var.get('rate_limit_whitelisted')
    except:
        return False
