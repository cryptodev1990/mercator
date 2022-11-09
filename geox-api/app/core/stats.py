import random
import re
from string import ascii_letters, digits
from typing import Any, Callable

from datadog.threadstats import ThreadStats
from fastapi import FastAPI, Request

from app.core.config import get_settings

# regex to find any character that are invalid for a metric name
invalid_metric_chars_regex = re.compile(r"^[0-9a-zA-Z]")

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

        # replace all invalid characters in the url path with an underscore
        endpoint = invalid_metric_chars_regex.sub("_", request.url.path)

        # collect metrics
        stats.increment(f"{endpoint}.num_requests")
        with stats.timer(f"{endpoint}.request_duration_s"):
            response = await call_next(request)
        stats.increment(
            f"{endpoint}.response_status_code.{response.status_code // 100}XX"
        )
        return response
