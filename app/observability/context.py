from contextvars import ContextVar, Token

REQUEST_ID_CONTEXT: ContextVar[str] = ContextVar(
    "request_id",
    default="unknown",
)


def get_request_id() -> str:
    return REQUEST_ID_CONTEXT.get()


def set_request_id(
    request_id: str,
) -> Token[str]:
    return REQUEST_ID_CONTEXT.set(request_id)


def reset_request_id(
    token: Token[str],
) -> None:
    REQUEST_ID_CONTEXT.reset(token)
