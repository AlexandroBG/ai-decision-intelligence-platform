import os
import time
from typing import Annotated
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware

from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
    HealthResponse,
    MetricsResponse,
)
from app.api.factory import (
    build_runtime_decision_service,
)
from app.api.service import (
    DecisionService,
)
from app.llm.errors import (
    LLMProviderError,
    LLMRateLimitError,
)
from app.observability.context import (
    reset_request_id,
    set_request_id,
)
from app.observability.logging import (
    get_logger,
)
from app.observability.metrics import (
    metrics,
)

APP_VERSION = "0.1.0"
SERVICE_NAME = "decisionai-api"

REQUEST_ID_HEADER = "X-Request-ID"

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

ALLOWED_ORIGINS_ENV = "DECISIONAI_ALLOWED_ORIGINS"


def load_allowed_origins() -> list[str]:
    configured_origins = os.getenv(
        ALLOWED_ORIGINS_ENV,
    )

    if not configured_origins:
        return DEFAULT_ALLOWED_ORIGINS.copy()

    return [
        origin.strip() for origin in configured_origins.split(",") if origin.strip()
    ]


logger = get_logger()


app = FastAPI(
    title="DecisionAI API",
    version=APP_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=load_allowed_origins(),
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=[
        "Content-Type",
    ],
    expose_headers=[
        REQUEST_ID_HEADER,
    ],
)


@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next,
) -> Response:
    request_id = str(uuid4())

    request.state.request_id = request_id

    token = set_request_id(request_id)

    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)

    response.headers[REQUEST_ID_HEADER] = request_id

    return response


@app.middleware("http")
async def log_request(
    request: Request,
    call_next,
) -> Response:
    metrics.increment("requests_total")

    started_at = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started_at) * 1000

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    logger.info(
        ("request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f"),
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next,
) -> Response:
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = "no-referrer"

    return response


def get_decision_service() -> DecisionService:
    return build_runtime_decision_service()


DecisionServiceDependency = Annotated[
    DecisionService,
    Depends(get_decision_service),
]


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=APP_VERSION,
    )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
)
def get_metrics() -> MetricsResponse:
    snapshot = metrics.snapshot()

    return MetricsResponse(**snapshot)


@app.post(
    "/decisions",
    response_model=DecisionResponse,
)
def create_decision(
    request: Request,
    decision_request: DecisionRequest,
    service: DecisionServiceDependency,
) -> DecisionResponse:
    try:
        result = service.decide(request=decision_request)

    except LLMRateLimitError as exc:
        metrics.increment("provider_errors_total")

        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.error(
            ("request_id=%s event=provider_rate_limit status_code=429"),
            request_id,
        )

        raise HTTPException(
            status_code=(status.HTTP_429_TOO_MANY_REQUESTS),
            detail=("AI provider quota or rate limit has been reached."),
        ) from exc

    except LLMProviderError as exc:
        metrics.increment("provider_errors_total")

        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.error(
            ("request_id=%s event=provider_error status_code=503"),
            request_id,
        )

        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=("AI provider is temporarily unavailable."),
        ) from exc

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    if result.status == "completed":
        event = "agent_completed"

        metrics.increment("agent_completed_total")

    else:
        event = "agent_failed"

        metrics.increment("agent_failed_total")

    logger.info(
        ("request_id=%s event=%s steps_used=%s tool_calls=%s evidence_steps=%s"),
        request_id,
        event,
        result.steps_used,
        result.tool_calls,
        len(result.evidence_steps),
    )

    return result
