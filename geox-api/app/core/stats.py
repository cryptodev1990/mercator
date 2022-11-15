import logging
import random
import time
from string import ascii_letters, digits
from typing import Any, Callable

from datadog.threadstats import ThreadStats
from fastapi import FastAPI, Request

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
worker_id = "".join(
    [random.choice(ascii_letters + digits) for _ in range(settings.worker_id_length)]
)

stats = ThreadStats(
    namespace=f"{settings.app_env}.{settings.app_name}",
    constant_tags=[
        f"app:{settings.app_name}",
        f"version:{settings.version}",
        f"env:{settings.app_env}",
        f"worker:{worker_id}",
    ],
)


def attach_stats_middleware(app: FastAPI):
    """Attaches middleware to FastAPI app to collect default endpoint metrics"""

    @app.middleware("http")
    async def endpoint_stats(request: Request, call_next: Callable) -> Any:
        """Collects default metrics for all endpoints"""
        start_time = time.time()
        response = await call_next(request)
        request_duration_s = time.time() - start_time

        # endpoint path must be extracted after call_next is called
        if "root_path" in request.scope and "route" in request.scope:
            tags = [
                f"endpoint_path:{request.scope['root_path'] + request.scope['route'].path}"
            ]
            stats.timing("endpoints.request_duration_s", request_duration_s, tags=tags)
            stats.increment("endpoints.num_requests", tags=tags)
            stats.increment(
                f"endpoints.response_status_code.{response.status_code // 100}XX",
                tags=tags,
            )
        else:
            logger.warning(
                "Unknown request path for endpoint stats",
                extra={"request_path": request.url.path},
            )
        return response
