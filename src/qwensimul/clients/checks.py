"""Credential-safe reports shared by the standalone inference checks."""

from time import perf_counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CheckService = Literal["qwen", "jev"]
CheckErrorCode = Literal[
    "configuration_error", "unreachable", "model_missing", "timeout",
    "authentication_failed", "access_denied", "rate_limited", "service_error",
    "invalid_response",
]

FAILURE_MESSAGES: dict[CheckErrorCode, str] = {
    "configuration_error": "Check client settings, credentials, and whether the client is closed.",
    "unreachable": "Cannot reach the service. Check its host, network access, and availability.",
    "model_missing": "The configured model is not installed. Download QWEN_MODEL in Ollama and retry.",
    "timeout": "The request timed out. Check service responsiveness or increase its configured timeout.",
    "authentication_failed": "Authentication failed. Check the configured credentials.",
    "access_denied": "Access was denied. Check the account's access to the requested service and model.",
    "rate_limited": "The service rate limit was reached. Wait before retrying.",
    "service_error": "The service rejected or failed the request. Check service status and SDK compatibility.",
    "invalid_response": "The service returned an invalid inference response. Check service and SDK compatibility.",
}


class ConnectionCheckResult(BaseModel):
    """A standalone check outcome without raw requests, responses, or credentials."""

    model_config = ConfigDict(frozen=True, strict=True, hide_input_in_errors=True)

    service: CheckService
    success: bool
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    model: str | None = Field(default=None, min_length=1)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    request_id: str | None = None
    error_code: CheckErrorCode | None = None
    message: str = "The service returned a valid inference response."


def failed_check(
    service: CheckService, started_at: float, error_code: CheckErrorCode
) -> ConnectionCheckResult:
    """
    Purpose: Build a failed report using fixed messages rather than SDK error text.
    Params:
        service: The inference service checked.
        started_at: The perf_counter value recorded before starting the check.
        error_code: The expected failure category.
    Return: A failed connection report with elapsed time and a safe message.
    """
    return ConnectionCheckResult(
        service=service,
        success=False,
        elapsed_seconds=perf_counter() - started_at,
        error_code=error_code,
        message=FAILURE_MESSAGES[error_code],
    )


def http_error_code(status: int | None) -> CheckErrorCode:
    """
    Purpose: Classify common HTTP failures without copying response bodies.
    Params:
        status: The HTTP status code, or None when unavailable.
    Return: A safe failure category; unrecognized statuses are service errors.
    """
    if status == 401:
        return "authentication_failed"
    if status == 403:
        return "access_denied"
    if status == 429:
        return "rate_limited"
    return "service_error"
